/**
 * Error utilities and centralized Express error middleware.
 *
 * This template uses a small HttpError class plus an error handler that converts
 * thrown/rejected errors into consistent JSON responses.
 */

/**
 * PUBLIC_INTERFACE
 * Represents an HTTP error with an explicit status code and optional details.
 */
class HttpError extends Error {
  /**
   * @param {number} statusCode HTTP status code
   * @param {string} message Error message for clients
   * @param {object} [options]
   * @param {string} [options.code] Application-specific error code
   * @param {any} [options.details] Optional structured details for clients
   */
  constructor(statusCode, message, options = {}) {
    super(message);
    this.name = 'HttpError';
    this.statusCode = statusCode;
    this.code = options.code;
    this.details = options.details;
  }
}

/**
 * PUBLIC_INTERFACE
 * Express error-handling middleware.
 *
 * Converts known HttpError instances (and select legacy template error shapes)
 * to JSON responses, and falls back to a safe 500 otherwise.
 *
 * @param {any} err
 * @param {import('express').Request} req
 * @param {import('express').Response} res
 * @param {import('express').NextFunction} next
 */
function errorHandler(err, req, res, next) {
  // If response was already started, delegate to Express default handler.
  if (res.headersSent) return next(err);

  // Legacy compatibility: some services/controllers may throw {code, details}
  // errors. Map those to status codes where reasonable.
  if (err && typeof err === 'object' && !(err instanceof Error)) {
    const code = err.code;
    if (code === 'VALIDATION_ERROR') {
      return res.status(400).json({
        status: 'error',
        message: err.message || 'Invalid request',
        details: err.details,
      });
    }
    if (code === 'CONFLICT') {
      return res.status(409).json({
        status: 'error',
        message: err.message || 'Conflict',
      });
    }
  }

  if (err instanceof HttpError) {
    return res.status(err.statusCode).json({
      status: 'error',
      message: err.message,
      code: err.code,
      details: err.details,
    });
  }

  // eslint-disable-next-line no-console
  console.error(err);

  return res.status(500).json({
    status: 'error',
    message: 'Internal Server Error',
  });
}

module.exports = {
  HttpError,
  errorHandler,
};
