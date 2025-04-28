// src/server.js
const app = require('./app');
const config = require('./config');

const { port, host} = config;


// Start the server
function startServer(port) {
  const server = app.listen(port, host, () => {
    console.log(`Server running on host ${host}, on port ${port}`);
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.log(`Port ${port} is in use, trying ${port + 1}...`);
      const newPort = port + 1;
      config.setPort(newPort); // Update the port in the config
      startServer(newPort); // Try the next port
    } else {
      console.error('Server error:', err);
    }
  });
};

startServer(port);

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server');
  server.close(() => {
    console.log('HTTP server closed');
    process.exit(0);
  });
});

// module.exports = server;
