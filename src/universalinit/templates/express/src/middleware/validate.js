function validateCreateUserBody() {
  return (req, res, next) => {
    const { firstName, lastName, email } = req.body ?? {};

    if (!firstName || typeof firstName !== 'string') {
      return res.status(400).json({
        status: 'error',
        message: 'firstName is required and must be a string',
      });
    }

    if (!lastName || typeof lastName !== 'string') {
      return res.status(400).json({
        status: 'error',
        message: 'lastName is required and must be a string',
      });
    }

    if (!email || typeof email !== 'string') {
      return res.status(400).json({
        status: 'error',
        message: 'email is required and must be a string',
      });
    }

    // Minimal email format check
    if (!email.includes('@')) {
      return res.status(400).json({
        status: 'error',
        message: 'email must be a valid email address',
      });
    }

    return next();
  };
}

function validateUpdateUserBody() {
  return (req, res, next) => {
    const { firstName, lastName, email } = req.body ?? {};

    if (!firstName || typeof firstName !== 'string') {
      return res.status(400).json({
        status: 'error',
        message: 'firstName is required and must be a string',
      });
    }

    if (!lastName || typeof lastName !== 'string') {
      return res.status(400).json({
        status: 'error',
        message: 'lastName is required and must be a string',
      });
    }

    if (!email || typeof email !== 'string') {
      return res.status(400).json({
        status: 'error',
        message: 'email is required and must be a string',
      });
    }

    if (!email.includes('@')) {
      return res.status(400).json({
        status: 'error',
        message: 'email must be a valid email address',
      });
    }

    return next();
  };
}

module.exports = {
  validateCreateUserBody,
  validateUpdateUserBody,
};
