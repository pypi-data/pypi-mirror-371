# cors_server.py
import http.server
import socketserver

PORT = 8000  # Change this if you want a different port

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to every response
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow all origins
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')  # Allow common methods
        self.send_header('Access-Control-Allow-Headers', 'Origin, Content-Type, Accept, Authorization')  # Allow common headers
        self.send_header('Access-Control-Max-Age', '86400')  # Cache preflight for 24 hours
        super().end_headers()

    def do_OPTIONS(self):
        # Handle preflight CORS requests (required for non-GET requests)
        self.send_response(200, "OK")
        self.end_headers()  # This will include the CORS headers above

# Start the server
with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
    print(f"Serving at http://localhost:{PORT} with CORS enabled for all origins")
    httpd.serve_forever()
