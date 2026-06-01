const { HttpError } = require('./errors');

/**
 * @param {any} v
 * @returns {boolean}
 */
function isPlainObject(v) {
  return typeof v === 'object' && v !== null && !Array.isArray(v);
}

/**
 * @param {any} value
 * @param {string} field
 * @param {Array<{field: string, message: string}>} details
 */
function requireNonEmptyString(value, field, details) {
  if (typeof value !== 'string' || value.trim().length === 0) {
    details.push({ field, message: `${field} is required and must be a non-empty string` });
  }
}

/**
 * PUBLIC_INTERFACE
 * Validate request body for creating a short link.
 *
 * Validates:
 * - destinationUrl required, must be a valid absolute URL
 * - domain/slug optional but must be non-empty strings when provided
 * - expiresAt optional but must be ISO date-time when provided (string)
 * - maxClicks optional but must be a non-negative number when provided
 */
function validateCreateShortLinkBody() {
  return (req, res, next) => {
    const body = req.body;

    if (!isPlainObject(body)) {
      return next(
        new HttpError(400, 'Invalid request body', {
          code: 'VALIDATION_ERROR',
          details: [{ field: 'body', message: 'body must be a JSON object' }],
        })
      );
    }

    /** @type {Array<{field: string, message: string}>} */
    const details = [];

    requireNonEmptyString(body.destinationUrl, 'destinationUrl', details);
    if (typeof body.destinationUrl === 'string' && body.destinationUrl.trim().length > 0) {
      try {
        // eslint-disable-next-line no-new
        new URL(body.destinationUrl);
      } catch {
        details.push({ field: 'destinationUrl', message: 'destinationUrl must be a valid URL' });
      }
    }

    if (body.domain !== undefined) {
      if (typeof body.domain !== 'string' || body.domain.trim().length === 0) {
        details.push({ field: 'domain', message: 'domain must be a non-empty string when provided' });
      }
    }

    if (body.slug !== undefined) {
      if (typeof body.slug !== 'string' || body.slug.trim().length === 0) {
        details.push({ field: 'slug', message: 'slug must be a non-empty string when provided' });
      }
    }

    if (body.expiresAt !== undefined && body.expiresAt !== null) {
      if (typeof body.expiresAt !== 'string' || !Number.isFinite(Date.parse(body.expiresAt))) {
        details.push({ field: 'expiresAt', message: 'expiresAt must be an ISO date-time string' });
      }
    }

    if (body.maxClicks !== undefined && body.maxClicks !== null) {
      const v = Number(body.maxClicks);
      if (!Number.isFinite(v) || v < 0) {
        details.push({ field: 'maxClicks', message: 'maxClicks must be a number >= 0' });
      }
    }

    if (details.length > 0) {
      return next(new HttpError(400, 'Invalid request body', { code: 'VALIDATION_ERROR', details }));
    }

    return next();
  };
}

/**
 * PUBLIC_INTERFACE
 * Validate stats request params/query:
 * - id must be a UUID
 * - from/to optional but must be YYYY-MM-DD when provided
 * - from must be <= to when both provided
 */
function validateShortLinkStatsRequest() {
  return (req, res, next) => {
    const linkId = req.params.id;
    const from = typeof req.query.from === 'string' ? req.query.from : undefined;
    const to = typeof req.query.to === 'string' ? req.query.to : undefined;

    /** @type {Array<{field: string, message: string}>} */
    const details = [];

    if (typeof linkId !== 'string' || !/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(linkId)) {
      details.push({ field: 'id', message: 'id must be a valid UUID' });
    }

    if (from !== undefined && !/^\d{4}-\d{2}-\d{2}$/.test(from)) {
      details.push({ field: 'from', message: 'from must be YYYY-MM-DD' });
    }
    if (to !== undefined && !/^\d{4}-\d{2}-\d{2}$/.test(to)) {
      details.push({ field: 'to', message: 'to must be YYYY-MM-DD' });
    }
    if (from && to && from > to) {
      details.push({ field: 'range', message: 'from must be <= to' });
    }

    if (details.length > 0) {
      return next(new HttpError(400, 'Invalid request parameters', { code: 'VALIDATION_ERROR', details }));
    }

    return next();
  };
}

module.exports = {
  validateCreateShortLinkBody,
  validateShortLinkStatsRequest,
};
