const crypto = require('crypto');
const { randomUUID } = require('crypto');

const DEFAULT_DOMAIN = process.env.DEFAULT_SHORTENER_DOMAIN || 'sho.rt';
const DEFAULT_ACCOUNT_ID = process.env.DEFAULT_SHORTENER_ACCOUNT_ID || '00000000-0000-0000-0000-000000000000';

/**
 * Minimal in-memory URL shortener store for the Express template.
 *
 * IMPORTANT:
 * - This is intentionally ephemeral (resets on restart).
 * - It is shaped to mirror the provided PostgreSQL schema:
 *   - short_link
 *   - click_event
 *   - link_daily_stats
 *
 * In a real deployment, replace the Maps/arrays with Postgres queries using those tables.
 */
class ShortenerService {
  constructor() {
    /**
     * @type {Map<string, any>} link by id (uuid)
     */
    this.linksById = new Map();

    /**
     * @type {Map<string, string>} unique lookup for (domain, slug) -> link id
     */
    this.linkIdByDomainSlug = new Map();

    /**
     * @type {Array<any>} click_event rows (append-only)
     */
    this.clickEvents = [];

    /**
     * @type {Map<string, {linkId: string, day: string, clicks: number, uniqueVisitors: number, botClicks: number, lastUpdatedAt: string}>}
     * key: `${linkId}|${day}`
     */
    this.dailyStatsByLinkDay = new Map();
  }

  /**
   * @param {string} url
   * @returns {Buffer} sha256 bytes (schema: destination_url_hash bytea)
   */
  _hashUrl(url) {
    return crypto.createHash('sha256').update(url, 'utf8').digest();
  }

  /**
   * @param {string} s
   * @returns {string}
   */
  _normalizeSlug(s) {
    return s
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9-_]/g, '-') // keep URL-safe-ish chars
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  }

  /**
   * @returns {string}
   */
  _generateSlug() {
    // 8 chars base62-ish from random bytes
    const raw = crypto.randomBytes(6).toString('base64url'); // includes - _
    return this._normalizeSlug(raw).slice(0, 10) || crypto.randomBytes(5).toString('hex');
  }

  /**
   * Extract a privacy-preserving "visitor" notion aligned with the schema.
   * The schema has visitor_id + ip_hash. For this template, we compute ip_hash and
   * also compute a visitor fingerprint from ip_hash + UA to approximate uniques.
   *
   * @param {import('express').Request} req
   * @returns {{ipHash: Buffer|null, visitorFingerprint: string|null, userAgent: string|null, referer: string|null, refererHost: string|null, isBot: boolean}}
   */
  _extractRequestAnalytics(req) {
    const xff = req.headers['x-forwarded-for'];
    const ipRaw =
      typeof xff === 'string'
        ? xff.split(',')[0].trim()
        : Array.isArray(xff) && xff.length > 0
          ? String(xff[0]).trim()
          : req.ip;

    const ipHash = ipRaw ? crypto.createHash('sha256').update(ipRaw, 'utf8').digest() : null;

    const userAgent = typeof req.headers['user-agent'] === 'string' ? req.headers['user-agent'] : null;
    const uaLower = (userAgent || '').toLowerCase();
    const isBot = /\bbot\b|\bcrawl\b|\bspider\b|slurp|facebookexternalhit|whatsapp/i.test(uaLower);

    const referer = typeof req.headers.referer === 'string' ? req.headers.referer : null;
    let refererHost = null;
    if (referer) {
      try {
        refererHost = new URL(referer).host;
      } catch {
        refererHost = null;
      }
    }

    const visitorFingerprint =
      ipHash && userAgent
        ? crypto.createHash('sha256').update(Buffer.concat([ipHash, Buffer.from(userAgent, 'utf8')])).digest('hex')
        : null;

    return { ipHash, visitorFingerprint, userAgent, referer, refererHost, isBot };
  }

  /**
   * Validate and normalize create payload.
   *
   * @param {any} input
   */
  _validateCreateInput(input) {
    /** @type {Array<{field: string, message: string}>} */
    const details = [];

    const destinationUrl = input?.destinationUrl;
    if (typeof destinationUrl !== 'string' || destinationUrl.trim().length === 0) {
      details.push({ field: 'destinationUrl', message: 'destinationUrl is required' });
    } else {
      try {
        // eslint-disable-next-line no-new
        new URL(destinationUrl);
      } catch {
        details.push({ field: 'destinationUrl', message: 'destinationUrl must be a valid URL' });
      }
    }

    const domain = input?.domain;
    if (domain !== undefined && (typeof domain !== 'string' || domain.trim().length === 0)) {
      details.push({ field: 'domain', message: 'domain must be a non-empty string when provided' });
    }

    const slug = input?.slug;
    if (slug !== undefined && (typeof slug !== 'string' || slug.trim().length === 0)) {
      details.push({ field: 'slug', message: 'slug must be a non-empty string when provided' });
    }

    const expiresAt = input?.expiresAt;
    if (expiresAt !== undefined && expiresAt !== null) {
      const ts = Date.parse(expiresAt);
      if (!Number.isFinite(ts)) details.push({ field: 'expiresAt', message: 'expiresAt must be an ISO date-time' });
    }

    const maxClicks = input?.maxClicks;
    if (maxClicks !== undefined && maxClicks !== null) {
      const v = Number(maxClicks);
      if (!Number.isFinite(v) || v < 0) details.push({ field: 'maxClicks', message: 'maxClicks must be >= 0' });
    }

    if (details.length) {
      const err = new Error('Invalid request body');
      err.code = 'VALIDATION_ERROR';
      err.details = details;
      throw err;
    }
  }

  /**
   * Create a short link (schema: short_link).
   *
   * @param {any} input
   * @returns {any}
   */
  createShortLink(input) {
    this._validateCreateInput(input);

    const nowIso = new Date().toISOString();

    const accountId = typeof input.accountId === 'string' && input.accountId ? input.accountId : DEFAULT_ACCOUNT_ID;
    const domain = typeof input.domain === 'string' && input.domain.trim() ? input.domain.trim() : DEFAULT_DOMAIN;

    const slugInput = typeof input.slug === 'string' && input.slug.trim() ? input.slug : null;
    const slug = this._normalizeSlug(slugInput || this._generateSlug());

    if (!slug) {
      const err = new Error('slug is invalid');
      err.code = 'VALIDATION_ERROR';
      err.details = [{ field: 'slug', message: 'slug must produce a non-empty normalized value' }];
      throw err;
    }

    const key = `${domain}|${slug}`;
    if (this.linkIdByDomainSlug.has(key)) {
      const err = new Error('A short link with this domain and slug already exists');
      err.code = 'CONFLICT';
      throw err;
    }

    const destinationUrl = input.destinationUrl.trim();
    const linkId = randomUUID();

    const link = {
      // Schema fields
      id: linkId,
      accountId,
      createdAt: nowIso,
      updatedAt: nowIso,
      deletedAt: null,

      domain,
      slug,

      destinationUrl,
      destinationUrlHash: this._hashUrl(destinationUrl).toString('hex'), // represent bytea as hex for JSON

      isActive: typeof input.isActive === 'boolean' ? input.isActive : true,
      expiresAt: input.expiresAt ?? null,
      maxClicks: input.maxClicks ?? null,

      requireHttps: typeof input.requireHttps === 'boolean' ? input.requireHttps : true,
      passwordHash: input.passwordHash ?? null,
      secretTokenHash: input.secretTokenHash ?? null,

      tags: Array.isArray(input.tags) ? input.tags.filter((t) => typeof t === 'string') : null,

      utmSource: input.utmSource ?? null,
      utmMedium: input.utmMedium ?? null,
      utmCampaign: input.utmCampaign ?? null,

      metadata: typeof input.metadata === 'object' && input.metadata !== null ? input.metadata : {},
    };

    this.linksById.set(linkId, link);
    this.linkIdByDomainSlug.set(key, linkId);

    return {
      ...link,
      shortUrl: `https://${domain}/${slug}`,
    };
  }

  /**
   * Find link by domain+slug.
   *
   * @param {{domain?: string, slug: string}} input
   * @returns {any|null}
   */
  _getLinkByDomainSlug(input) {
    const domain = input.domain || DEFAULT_DOMAIN;
    const slug = this._normalizeSlug(input.slug);
    const key = `${domain}|${slug}`;
    const id = this.linkIdByDomainSlug.get(key);
    if (!id) return null;
    return this.linksById.get(id) ?? null;
  }

  /**
   * @param {any} link
   * @returns {number} total click count (schema: click_event rows)
   */
  _countClicks(link) {
    return this.clickEvents.reduce((acc, e) => (e.linkId === link.id ? acc + 1 : acc), 0);
  }

  /**
   * Resolve a redirect and record click_event + update rollup.
   *
   * @param {{domain?: string, slug: string, request: import('express').Request}} input
   * @returns {{link: any, destinationUrl: string}}
   */
  resolveRedirect(input) {
    const link = this._getLinkByDomainSlug({ domain: input.domain, slug: input.slug });
    if (!link) {
      const err = new Error('Short link not found');
      err.code = 'NOT_FOUND';
      throw err;
    }

    // Apply "gone" rules from the spec fields: deleted_at, is_active, expires_at
    if (link.deletedAt) {
      const err = new Error('Short link has been deleted');
      err.code = 'GONE';
      throw err;
    }
    if (!link.isActive) {
      const err = new Error('Short link is not active');
      err.code = 'GONE';
      throw err;
    }
    if (link.expiresAt) {
      const exp = Date.parse(link.expiresAt);
      if (Number.isFinite(exp) && Date.now() > exp) {
        const err = new Error('Short link has expired');
        err.code = 'GONE';
        throw err;
      }
    }

    // Apply max_clicks cap if configured (schema: short_link.max_clicks)
    if (link.maxClicks !== null && link.maxClicks !== undefined) {
      const max = Number(link.maxClicks);
      if (Number.isFinite(max)) {
        const current = this._countClicks(link);
        if (current >= max) {
          const err = new Error('Short link has reached its maximum number of clicks');
          err.code = 'TOO_MANY_REQUESTS';
          throw err;
        }
      }
    }

    // require_https is a link-level policy; for template we only validate destination URL scheme if set
    if (link.requireHttps) {
      try {
        const u = new URL(link.destinationUrl);
        if (u.protocol !== 'https:') {
          const err = new Error('Destination URL is not HTTPS but requireHttps is enabled');
          err.code = 'GONE';
          throw err;
        }
      } catch {
        // Should not happen for validated data; treat as not found/gone.
        const err = new Error('Destination URL invalid');
        err.code = 'GONE';
        throw err;
      }
    }

    // Append click_event aligned record
    const now = new Date();
    const day = now.toISOString().slice(0, 10); // YYYY-MM-DD (UTC)
    const analytics = this._extractRequestAnalytics(input.request);

    const event = {
      // schema: click_event
      id: this.clickEvents.length + 1, // mimic bigserial
      linkId: link.id,
      occurredAt: now.toISOString(),

      visitorId: null, // not modeled in this MVP
      requestId: null,

      ipHash: analytics.ipHash ? analytics.ipHash.toString('hex') : null,
      userAgent: analytics.userAgent,

      referer: analytics.referer,
      refererHost: analytics.refererHost,

      countryCode: null,
      region: null,
      city: null,

      deviceType: null,
      osName: null,
      browserName: null,

      isBot: analytics.isBot,

      redirectStatus: 302,
      errorCode: null,
      edgePop: null,

      extra: {},
      // local-only field for rollups
      _visitorFingerprint: analytics.visitorFingerprint,
    };

    this.clickEvents.push(event);

    // Update link_daily_stats rollup (schema: link_daily_stats)
    const statsKey = `${link.id}|${day}`;
    const existing = this.dailyStatsByLinkDay.get(statsKey) || {
      linkId: link.id,
      day,
      clicks: 0,
      uniqueVisitors: 0,
      botClicks: 0,
      lastUpdatedAt: now.toISOString(),
      // local-only set
      _uniqueVisitorFingerprints: new Set(),
    };

    existing.clicks += 1;
    if (event.isBot) existing.botClicks += 1;

    if (event._visitorFingerprint) {
      existing._uniqueVisitorFingerprints.add(event._visitorFingerprint);
      existing.uniqueVisitors = existing._uniqueVisitorFingerprints.size;
    }

    existing.lastUpdatedAt = now.toISOString();
    this.dailyStatsByLinkDay.set(statsKey, existing);

    return { link, destinationUrl: link.destinationUrl };
  }

  /**
   * Get analytics/stats for a link.
   *
   * Uses:
   * - click_event for totals
   * - link_daily_stats for day time-series (if present)
   *
   * @param {{linkId: string, from?: string, to?: string}} input
   */
  getLinkStats(input) {
    const link = this.linksById.get(input.linkId);
    if (!link) {
      const err = new Error('Link not found');
      err.code = 'NOT_FOUND';
      throw err;
    }

    const fromDay = input.from;
    const toDay = input.to;

    if (fromDay !== undefined && !/^\d{4}-\d{2}-\d{2}$/.test(fromDay)) {
      const err = new Error('from must be YYYY-MM-DD');
      err.code = 'VALIDATION_ERROR';
      err.details = [{ field: 'from', message: 'from must be YYYY-MM-DD' }];
      throw err;
    }
    if (toDay !== undefined && !/^\d{4}-\d{2}-\d{2}$/.test(toDay)) {
      const err = new Error('to must be YYYY-MM-DD');
      err.code = 'VALIDATION_ERROR';
      err.details = [{ field: 'to', message: 'to must be YYYY-MM-DD' }];
      throw err;
    }
    if (fromDay && toDay && fromDay > toDay) {
      const err = new Error('from must be <= to');
      err.code = 'VALIDATION_ERROR';
      err.details = [{ field: 'range', message: 'from must be <= to' }];
      throw err;
    }

    const inRange = (day) => {
      if (fromDay && day < fromDay) return false;
      if (toDay && day > toDay) return false;
      return true;
    };

    const events = this.clickEvents.filter((e) => e.linkId === link.id);

    const totalClicks = events.length;
    const totalBotClicks = events.reduce((acc, e) => (e.isBot ? acc + 1 : acc), 0);

    const totalsUnique = (() => {
      const set = new Set();
      for (const e of events) {
        if (e._visitorFingerprint) set.add(e._visitorFingerprint);
      }
      return set.size;
    })();

    const daily = [];
    for (const s of this.dailyStatsByLinkDay.values()) {
      if (s.linkId !== link.id) continue;
      if (!inRange(s.day)) continue;

      daily.push({
        day: s.day,
        clicks: s.clicks,
        uniqueVisitors: s.uniqueVisitors,
        botClicks: s.botClicks,
      });
    }
    daily.sort((a, b) => (a.day < b.day ? -1 : a.day > b.day ? 1 : 0));

    return {
      link: {
        id: link.id,
        domain: link.domain,
        slug: link.slug,
        destinationUrl: link.destinationUrl,
        isActive: link.isActive,
        expiresAt: link.expiresAt,
        maxClicks: link.maxClicks,
        createdAt: link.createdAt,
      },
      totals: {
        clicks: totalClicks,
        uniqueVisitors: totalsUnique,
        botClicks: totalBotClicks,
      },
      daily,
    };
  }
}

module.exports = new ShortenerService();
