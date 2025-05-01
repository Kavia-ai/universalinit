#!/bin/bash

. venv/bin/activate

PORT=3000

while lsof -iTCP:$PORT -sTCP:LISTEN -n -P >/dev/null
do
  echo "Port $PORT is in use. Trying $((PORT+1))..."
  PORT=$((PORT+1))
done

echo "Found free port: $PORT"

python manage.py migrate 
python manage.py runserver 0.0.0.0:$PORT