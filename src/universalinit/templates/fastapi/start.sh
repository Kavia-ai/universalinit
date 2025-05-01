#!/bin/bash

. venv/bin/activate

PORT=3000

while lsof -iTCP:$PORT -sTCP:LISTEN -n -P >/dev/null
do
  echo "Port $PORT is in use. Trying $((PORT+1))..."
  PORT=$((PORT+1))
done

echo "Found free port: $PORT"

uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
