import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class HealthHandler(BaseHTTPRequestHandler):
    """Simple health check handler for Render"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            health_data = {
                "status": "healthy",
                "service": "ZERIL Telegram Bot",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            self.wfile.write(json.dumps(health_data).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

class HealthServer:
    """Health check server for Render deployment"""
    
    def __init__(self, port=8000):
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self):
        """Start health check server in background thread"""
        try:
            self.server = HTTPServer(('0.0.0.0', self.port), HealthHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            logger.info(f"Health server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start health server: {e}")
    
    def stop(self):
        """Stop health check server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Health server stopped")

# Global health server instance
health_server = HealthServer()
