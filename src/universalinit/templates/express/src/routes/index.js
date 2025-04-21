const express = require('express');
const healthController = require('../controllers/health');

const router = express.Router();
// Health endpoint

/**
 * @swagger
 * /:
 *   get:
 *     summary: Health endpoint
 *     responses:
 *       200:
 *         description: Success
 */
router.get('/', healthController.check.bind(healthController));

module.exports = router;
