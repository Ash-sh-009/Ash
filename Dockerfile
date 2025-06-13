FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg curl && \
    rm -rf /var/lib/apt/lists/*

# ... rest unchanged ...
