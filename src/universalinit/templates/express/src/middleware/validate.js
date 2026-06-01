/**
 * Creates an Express middleware that validates req.body for user create.
 * Responds with 400 when invalid.
 *
 * @returns {import('express').RequestHandler}
 */
function validateCreateUserBody() {
  return (req, res, next) => {
    const body = req.body ?? {};

    const errors = [];
    if (typeof body.name !== 'string' || body.name.trim().length === 0) {
      errors.push({ field: 'name', message: 'name is required and must be a non-empty string' });
    }
    if (typeof body.email !== 'string' || body.email.trim().length === 0) {
      errors.push({ field: 'email', message: 'email is required and must be a non-empty string' });
    }

    if (errors.length > 0) {
      return res.status(400).json({
        status: 'error',
        message: 'Invalid request body',
        errors,
      });
    }

    return next();
  };
}

/**
 * Creates an Express middleware that validates req.body for user update (PUT).
 * Requires both name and email, similar to create.
 *
 * @returns {import('express').RequestHandler}
 */
function validateUpdateUserBody() {
  return (req, res, next) => {
    const body = req.body ?? {};

    const errors = [];
    if (typeof body.name !== 'string' || body.name.trim().length === 0) {
      errors.push({ field: 'name', message: 'name is required and must be a non-empty string' });
    }
    if (typeof body.email !== 'string' || body.email.trim().length === 0) {
      errors.push({ field: 'email', message: 'email is required and must be a non-empty string' });
    }

    if (errors.length > 0) {
      return res.status(400).json({
        status: 'error',
        message: 'Invalid request body',
        errors,
      });
    }

    return next();
  };
}

module.exports = {
  validateCreateUserBody,
  validateUpdateUserBody,
};
