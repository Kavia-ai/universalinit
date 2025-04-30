#!/bin/bash

PORT=3000

while sudo lsof -iTCP:$PORT -sTCP:LISTEN -n -P >/dev/null
do
  echo "Port $PORT is in use. Trying $((PORT+1))..."
  PORT=$((PORT+1))
done

echo "Found free port: http://localhost:$PORT"

CI=true npm start -- --port $PORT
