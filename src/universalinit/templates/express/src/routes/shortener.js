const express = require('express');
const shortenerController = require('../controllers/shortener');
const { asyncHandler, validateCreateShortLinkBody, validateShortLinkStatsRequest } = require('../middleware');

const router = express.Router();

/**
 * @swagger
 * /api/short-links:
 *   post:
 *     summary: Create a short link
 *     description: >
 *       Creates a new short link record (domain+slug -> destination_url). This template implementation uses an in-memory store but is aligned to
 *       the PostgreSQL schema (short_link, click_event, link_daily_stats).
 *     tags:
 *       - URL Shortener
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required: [destinationUrl]
 *             properties:
 *               accountId:
 *                 type: string
 *                 format: uuid
 *                 description: Owner account id (schema: short_link.account_id). If omitted, a demo account is used.
 *               domain:
 *                 type: string
 *                 description: Short-link domain (schema: short_link.domain). If omitted, DEFAULT_SHORTENER_DOMAIN is used.
 *                 example: sho.rt
 *               slug:
 *                 type: string
 *                 description: Custom alias (schema: short_link.slug). If omitted, a random slug is generated.
 *                 example: my-campaign
 *               destinationUrl:
 *                 type: string
 *                 description: Destination URL (schema: short_link.destination_url).
 *                 example: https://example.com/landing
 *               expiresAt:
 *                 type: string
 *                 format: date-time
 *                 nullable: true
 *                 description: Optional expiration timestamp (schema: short_link.expires_at).
 *               maxClicks:
 *                 type: integer
 *                 nullable: true
 *                 description: Optional total click cap (schema: short_link.max_clicks).
 *               isActive:
 *                 type: boolean
 *                 description: Enable/disable link (schema: short_link.is_active).
 *               tags:
 *                 type: array
 *                 items: { type: string }
 *                 nullable: true
 *                 description: Optional tags (schema: short_link.tags).
 *               utmSource:
 *                 type: string
 *                 nullable: true
 *                 description: Optional default UTM source (schema: short_link.utm_source).
 *               utmMedium:
 *                 type: string
 *                 nullable: true
 *                 description: Optional default UTM medium (schema: short_link.utm_medium).
 *               utmCampaign:
 *                 type: string
 *                 nullable: true
 *                 description: Optional default UTM campaign (schema: short_link.utm_campaign).
 *               metadata:
 *                 type: object
 *                 nullable: true
 *                 description: Arbitrary metadata (schema: short_link.metadata).
 *     responses:
 *       201:
 *         description: Short link created
 *       400:
 *         description: Invalid input
 *       409:
 *         description: Slug already exists for the domain
 */
router.post(
  '/short-links',
  validateCreateShortLinkBody(),
  asyncHandler(shortenerController.create.bind(shortenerController))
);

/**
 * @swagger
 * /r/{slug}:
 *   get:
 *     summary: Redirect by slug (default domain)
 *     description: Resolves the short link and issues an HTTP redirect. Also records a click_event.
 *     tags:
 *       - URL Shortener
 *     parameters:
 *       - name: slug
 *         in: path
 *         required: true
 *         schema: { type: string }
 *     responses:
 *       302:
 *         description: Redirect to destination URL
 *       404:
 *         description: Link not found
 *       410:
 *         description: Link expired/inactive/deleted
 *       429:
 *         description: Click limit reached
 */
router.get('/r/:slug', shortenerController.redirect.bind(shortenerController));

/**
 * @swagger
 * /r/{domain}/{slug}:
 *   get:
 *     summary: Redirect by domain and slug
 *     description: Resolves the short link and issues an HTTP redirect. Also records a click_event.
 *     tags:
 *       - URL Shortener
 *     parameters:
 *       - name: domain
 *         in: path
 *         required: true
 *         schema: { type: string }
 *       - name: slug
 *         in: path
 *         required: true
 *         schema: { type: string }
 *     responses:
 *       302:
 *         description: Redirect to destination URL
 *       404:
 *         description: Link not found
 *       410:
 *         description: Link expired/inactive/deleted
 *       429:
 *         description: Click limit reached
 */
router.get('/r/:domain/:slug', shortenerController.redirect.bind(shortenerController));

/**
 * @swagger
 * /api/links/{id}/stats:
 *   get:
 *     summary: Get stats for a short link
 *     description: >
 *       Returns basic analytics aligned to the schema. Uses link_daily_stats for time series and click_event for totals.
 *     tags:
 *       - URL Shortener
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         schema: { type: string, format: uuid }
 *       - name: from
 *         in: query
 *         required: false
 *         schema: { type: string, example: "2026-01-01" }
 *         description: Start day (inclusive) in YYYY-MM-DD
 *       - name: to
 *         in: query
 *         required: false
 *         schema: { type: string, example: "2026-01-31" }
 *         description: End day (inclusive) in YYYY-MM-DD
 *     responses:
 *       200:
 *         description: Stats response
 *       400:
 *         description: Invalid range or parameters
 *       404:
 *         description: Link not found
 */
router.get(
  '/api/links/:id/stats',
  validateShortLinkStatsRequest(),
  asyncHandler(shortenerController.stats.bind(shortenerController))
);

module.exports = router;
