# # FROM python:3.11-slim

# # WORKDIR /app/endpoint

# # COPY . /app

# # RUN pip install --upgrade pip \
# #  && pip install -r /app/requirements.txt \
# #  && pip install scrapyrt

# # RUN chmod +x /app/start.sh

# # CMD ["/app/start.sh"]



# # FROM python:3.11-slim

# # WORKDIR /app/endpoint

# # COPY . /app

# # RUN pip install --upgrade pip \
# #  && pip install -r /app/requirements.txt \
# #  && pip install scrapyrt

# # # Make start.sh executable
# # RUN chmod +x /app/start.sh

# # # Optional for local testing
# # EXPOSE 9080

# # CMD ["/app/start.sh"]


# FROM python:3.11-slim

# WORKDIR /app/endpoint

# COPY . /app

# RUN pip install --upgrade pip \
#     && pip install -r /app/requirements.txt \
#     && pip install scrapyrt

# EXPOSE 8080

# CMD ["scrapyrt", "-p", "8080"]


# FROM python:3.11-slim

# # Set working directory to where scrapy.cfg is located
# WORKDIR /app/endpoint

# # Copy the entire project into /app
# COPY . /app

# # Install dependencies
# RUN pip install --no-cache-dir --upgrade pip \
#     && pip install -r /app/requirements.txt \
#     && pip install scrapyrt

# # Use the PORT environment variable provided by GCP, defaulting to 8080
# # -i 0.0.0.0 is CRITICAL for Cloud Run to accept external traffic
# CMD ["sh", "-c", "scrapyrt -p ${PORT:-8080} -i 0.0.0.0"]



FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install -r requirements.txt \
    && pip install scrapyrt

# Copy the rest of the project
COPY . .

# Move into the endpoint folder where scrapy.cfg is
WORKDIR /app/endpoint

# Make the script executable
RUN chmod +x /app/start.sh

# Tell Docker to run the script
# We point to /app/start.sh because that's where the file is
CMD ["/bin/bash", "/app/start.sh"]