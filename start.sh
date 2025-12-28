#!/bin/bash

# Use the PORT environment variable from Cloud Run
PORT=${PORT:-8080}  # default to 8080 if not set

# Start Scrapyrt on Cloud Run port
scrapyrt -p $PORT &

echo "Waiting for Scrapyrt to start..."
while ! nc -z localhost $PORT; do
  sleep 0.5
done
echo "Scrapyrt is ready!"

# Start Flask on same port (optional, but Cloud Run allows only one process per $PORT)
# If you want Flask to serve on same container, change Flask app to listen on $PORT
python flask_app.py
