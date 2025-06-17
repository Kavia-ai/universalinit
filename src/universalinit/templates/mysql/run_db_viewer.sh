#!/bin/bash

echo "Starting Database Viewer..."

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the server with environment variables
npm start > db_visualizer_server.log 2>&1 </dev/null &
