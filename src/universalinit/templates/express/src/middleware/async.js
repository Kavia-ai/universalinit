/**
 * Async wrapper for Express route handlers.
 *
 * Ensures thrown/rejected errors are passed to next(err) so centralized error
 * middleware can handle them.
 */

/**
 * PUBLIC_INTERFACE
 * Wrap an Express handler and forward errors to next().
 *
 * @param {(req: import('express').Request, res: import('express').Response, next: import('express').NextFunction) => any} handler
 * @returns {(req: import('express').Request, res: import('express').Response, next: import('express').NextFunction) => void}
 */
function asyncHandler(handler) {
  return (req, res, next) => {
    Promise.resolve(handler(req, res, next)).catch(next);
  };
}

module.exports = {
  asyncHandler,
};
