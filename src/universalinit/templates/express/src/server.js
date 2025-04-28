// src/server.js
const app = require('./app');
const config = require('./config');

const { port, host} = config;

// Start the server
const server = app.listen(port, host, () => {
  console.log(`Server running on host ${host}, on port ${port}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server');
  server.close(() => {
    console.log('HTTP server closed');
    process.exit(0);
  });
});

module.exports = server;
