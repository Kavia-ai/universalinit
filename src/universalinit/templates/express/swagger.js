const swaggerJSDoc = require('swagger-jsdoc');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Express URL Shortener API',
      version: '1.0.0',
      description:
        'Express API for a URL shortener with click analytics (template implementation uses in-memory storage, aligned to the provided PostgreSQL schema).',
    }
  },
  apis: ['./src/routes/*.js'], // Path to the API docs
};

const swaggerSpec = swaggerJSDoc(options);
module.exports = swaggerSpec;
