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
    try {
      const input = req.body ?? {};
      const created = shortenerService.createShortLink(input);

      return res.status(201).json({
        status: 'ok',
        data: created,
      });
    } catch (err) {
      if (err && typeof err === 'object' && err.code === 'VALIDATION_ERROR') {
        return res.status(400).json({ status: 'error', message: err.message, details: err.details });
      }
      if (err && typeof err === 'object' && err.code === 'CONFLICT') {
        return res.status(409).json({ status: 'error', message: err.message });
      }

      // Unexpected
      // eslint-disable-next-line no-console
      console.error(err);
      return res.status(500).json({ status: 'error', message: 'Internal Server Error' });
    }
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
    try {
      const domain = typeof req.params.domain === 'string' ? req.params.domain : undefined;
      const slug = req.params.slug;

      const { link, destinationUrl } = shortenerService.resolveRedirect({
        domain,
        slug,
        request: req,
      });

      // NOTE: For an MVP, always use 302; schema includes redirect_status for analytics.
      return res.redirect(302, destinationUrl);
    } catch (err) {
      if (err && typeof err === 'object') {
        if (err.code === 'NOT_FOUND') {
          return res.status(404).json({ status: 'error', message: err.message });
        }
        if (err.code === 'GONE') {
          return res.status(410).json({ status: 'error', message: err.message });
        }
        if (err.code === 'TOO_MANY_REQUESTS') {
          return res.status(429).json({ status: 'error', message: err.message });
        }
        if (err.code === 'VALIDATION_ERROR') {
          return res.status(400).json({ status: 'error', message: err.message, details: err.details });
        }
      }

      // eslint-disable-next-line no-console
      console.error(err);
      return res.status(500).json({ status: 'error', message: 'Internal Server Error' });
    }
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
    try {
      const linkId = req.params.id;
      const from = typeof req.query.from === 'string' ? req.query.from : undefined;
      const to = typeof req.query.to === 'string' ? req.query.to : undefined;

      const stats = shortenerService.getLinkStats({ linkId, from, to });

      return res.status(200).json({
        status: 'ok',
        data: stats,
      });
    } catch (err) {
      if (err && typeof err === 'object') {
        if (err.code === 'NOT_FOUND') {
          return res.status(404).json({ status: 'error', message: err.message });
        }
        if (err.code === 'VALIDATION_ERROR') {
          return res.status(400).json({ status: 'error', message: err.message, details: err.details });
        }
      }

      // eslint-disable-next-line no-console
      console.error(err);
      return res.status(500).json({ status: 'error', message: 'Internal Server Error' });
    }
  }
}

module.exports = new ShortenerController();
