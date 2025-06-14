# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render requires this)
EXPOSE 8080

# Create a simple health check endpoint
RUN echo 'from http.server import HTTPServer, BaseHTTPRequestHandler\nimport threading\nclass HealthHandler(BaseHTTPRequestHandler):\n    def do_GET(self):\n        self.send_response(200)\n        self.end_headers()\n        self.wfile.write(b"Bot is running")\ndef start_health_server():\n    server = HTTPServer(("0.0.0.0", 8080), HealthHandler)\n    server.serve_forever()\nthreading.Thread(target=start_health_server, daemon=True).start()' > health_server.py

# Run the application
CMD ["python", "-c", "exec(open('health_server.py').read()); exec(open('main.py').read())"]
