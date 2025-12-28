FROM python:3.11-slim

WORKDIR /app

# Copy your project files
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install scrapyrt

# Expose internal port 9080 (optional, internal only)
EXPOSE 9080

# Start Scrapyrt
CMD ["scrapyrt", "-p", "9080"]
