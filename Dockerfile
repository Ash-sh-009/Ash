FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies + Python requirements in one layer
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    pip install --no-cache-dir python-telegram-bot[ext]==20.3 requests==2.31.0 && \
    rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Explicit startup command
CMD ["python", "main.py"]
