const shortenerService = require('../services/shortener');

/**
 * URL Shortener controller.
 *
 * Implements:
 * - Create short link
 * - Resolve and redirect by (domain, slug)
 * - Stats endpoint backed by rollups (link_daily_stats) and raw events (click_event)
 */
class ShortenerController {
  /**
   * Create a short link.
   *
   * @param {import('express').Request} req
   * @param {import('express').Response} res
   */
  create(req, res) {
    const input = req.body ?? {};
    const created = shortenerService.createShortLink(input);

    return res.status(201).json({
      status: 'ok',
      data: created,
    });
  }

  /**
   * Redirect by domain + slug. Also appends a click_event.
   *
   * Route supports:
   * - GET /r/:slug (uses default domain)
   * - GET /r/:domain/:slug
   *
   * @param {import('express').Request} req
   * @param {import('express').Response} res
   */
  redirect(req, res) {
    const domain = typeof req.params.domain === 'string' ? req.params.domain : undefined;
    const slug = req.params.slug;

    const { destinationUrl } = shortenerService.resolveRedirect({
      domain,
      slug,
      request: req,
    });

    // NOTE: For an MVP, always use 302; schema includes redirect_status for analytics.
    return res.redirect(302, destinationUrl);
  }

  /**
   * Return stats for a given link.
   *
   * Route supports:
   * - GET /api/links/:id/stats?from=YYYY-MM-DD&to=YYYY-MM-DD
   *
   * @param {import('express').Request} req
   * @param {import('express').Response} res
   */
  stats(req, res) {
    const linkId = req.params.id;
    const from = typeof req.query.from === 'string' ? req.query.from : undefined;
    const to = typeof req.query.to === 'string' ? req.query.to : undefined;

    const stats = shortenerService.getLinkStats({ linkId, from, to });

    return res.status(200).json({
      status: 'ok',
      data: stats,
    });
  }
}

module.exports = new ShortenerController();
