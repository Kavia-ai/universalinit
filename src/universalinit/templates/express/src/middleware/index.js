// This file exports middleware as the application grows
const { validateCreateUserBody, validateUpdateUserBody } = require('./validate');

module.exports = {
  validateCreateUserBody,
  validateUpdateUserBody,
};
