let config = {
  port: 5900, // Default port
  host: 'localhost', // Default host
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
