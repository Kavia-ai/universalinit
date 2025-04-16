```
project-root/
├── .env                    # Environment variables
├── package.json            # Project dependencies and scripts
├── src/
│   ├── app.js              # Express app setup
│   ├── server.js           # Server startup file
│   ├── config/             # Configuration files
│   │   └── index.js        # Exports configuration
│   ├── routes/             # API routes
│   │   └── index.js        # Routes setup
│   ├── controllers/        # Request handlers
│   │   └── health.js       # Health endpoint controller
│   ├── middleware/         # Custom middleware
│   │   └── index.js        # Middleware setup
│   └── services/           # Business logic
│       └── health.js       # Health service
```