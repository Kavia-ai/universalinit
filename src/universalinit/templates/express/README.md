# Minimal Express API (Template)

## Overview
This template is a minimal Express.js REST API scaffold with a small but extensible project structure. It includes CORS, JSON request parsing, a built-in health check endpoint, and Swagger UI documentation served from the running app.

## Prerequisites
You need the following installed locally:
- Node.js (LTS recommended)
- npm (ships with Node.js)

## Setup
First, install dependencies.

```bash
npm install
```

Then start the API.

### Run in development (auto-reload)
```bash
npm run dev
```

### Run in production mode
```bash
npm start
```

By default the server listens on `http://0.0.0.0:3000`.

## Environment variables
This template reads the following environment variables at runtime.

### Required
This template does not currently require any environment variables to start successfully.

### Optional
- `PORT`: The port the server listens on. Defaults to `3000`.
- `HOST`: The host interface to bind to. Defaults to `0.0.0.0`.
- `NODE_ENV`: Used in the health response payload. Defaults to `development`.

## API documentation (Swagger)
The template serves Swagger UI at:

- `GET /docs`

The Swagger UI is configured to set the OpenAPI `servers` URL dynamically based on the incoming request host/protocol, which helps when running behind proxies or on non-default ports.

## Endpoint reference

### Health check
#### `GET /`
Returns a basic health payload.

**Response: 200**
```json
{
  "status": "ok",
  "message": "Service is healthy",
  "timestamp": "2026-01-01T00:00:00.000Z",
  "environment": "development"
}
```

## Project structure
```text
src/
  app.js              # Express app wiring (middleware, /docs, routes, error handler)
  server.js           # HTTP server startup + graceful shutdown handling
  controllers/
    health.js         # Health controller
  services/
    health.js         # Health service (payload creation)
  routes/
    index.js          # Route definitions (currently only GET /)
swagger.js            # swagger-jsdoc configuration (OpenAPI spec)
```

## Notes on authentication
This template currently exposes a public health endpoint and Swagger UI. It does not yet include user authentication routes or middleware (for example login/signup, JWT issuance, or an auth guard). If you extend this template to add authentication, consider documenting:
- How users are stored (database model)
- Password hashing approach (e.g., bcrypt)
- Token strategy (e.g., JWT access + refresh tokens)
- Which routes require authentication, and how to send credentials (typically `Authorization: Bearer <token>`)
- Any new required environment variables (e.g., `JWT_SECRET`, token TTLs, database connection strings)
