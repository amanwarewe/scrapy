# # #!/usr/bin/env bash
# # set -e

# # PORT=${PORT:-9080}

# # echo "Starting Scrapyrt on port $PORT"
# # echo "Working directory: $(pwd)"

# # exec scrapyrt -p $PORT



# # #!/usr/bin/env bash
# # set -e

# # PORT=${PORT:-8080}  # always use the env variable from Cloud Run

# # echo "Starting Scrapyrt on port $PORT"
# # echo "Working directory: $(pwd)"

# # # start Scrapyrt in foreground on the correct port
# # exec scrapyrt -p $PORT

# #!/bin/bash

# # 1. Start Scrapyrt in the background on port 9080
# # We use 9080 internally so it doesn't conflict with Flask
# scrapyrt -p 9080 -i 127.0.0.1 &

# # 2. Start the Flask app in the foreground on the port GCP expects (usually 8080)
# python flask_app.py


#!/bin/sh

# 1. Start Scrapyrt in the background on all interfaces
scrapyrt -p 9080 -i 0.0.0.0 &

# 2. Wait for Scrapyrt to initialize
sleep 3

# 3. Start the Flask app
# Use gunicorn for production, or stick to python if your script handles the $PORT
python flask_app.py
