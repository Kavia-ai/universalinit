const fs = require('fs');
const path = require('path');
const swaggerSpec = require('./swagger');

fs.writeFileSync(
  path.join(__dirname, 'openapi.json'),
  JSON.stringify(swaggerSpec, null, 2)
);
