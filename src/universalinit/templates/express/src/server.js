const app = require('./app');
const config = require('./config');

let { port, host } = config;

function startServer(portToTry) {
  const server = app.listen(portToTry, () => {
    console.log(`✅ Server running in http://${host}:${portToTry}`);
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      startServer(portToTry + 1);
    } else {
      console.error('❌ Server error:', err);
      process.exit(1);
    }
  });
  // Graceful shutdown
  process.on('SIGTERM', () => {
    console.log('SIGTERM signal received: closing HTTP server');
    server.close(() => {
      console.log('HTTP server closed');
      process.exit(0);
    });
  });

  return server;
}

const server = startServer(port);

module.exports = server;
