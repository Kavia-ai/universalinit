let config = {
  port: process.env.PORT || 5900, // Default port
  host: process.env.HOST || 'localhost', // Default host
};

function setPort(newPort) {
  config.port = newPort;
}

function getConfig() {
  return config;
}

module.exports = {
  ...config,
  setPort,
  getConfig,
};