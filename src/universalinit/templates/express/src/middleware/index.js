// This file exports middleware as the application grows
const { validateCreateUserBody, validateUpdateUserBody } = require('./validate');
const { asyncHandler } = require('./async');
const { HttpError, errorHandler } = require('./errors');
const { validateCreateShortLinkBody, validateShortLinkStatsRequest } = require('./shortenerValidation');

module.exports = {
  validateCreateUserBody,
  validateUpdateUserBody,
  asyncHandler,
  HttpError,
  errorHandler,
  validateCreateShortLinkBody,
  validateShortLinkStatsRequest,
};
