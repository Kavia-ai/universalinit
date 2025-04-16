const express = require("express");
const healthController = require("../controllers/health");

const router = express.Router();
// Health endpoint
router.get("/", healthController.check.bind(healthController));

module.exports = router;
