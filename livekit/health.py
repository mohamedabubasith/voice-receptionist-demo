"""Minimal HTTP health server — keeps HF Space alive and satisfies port 7860 requirement."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass  # suppress access logs


def start(port: int = 7860) -> None:
    server = HTTPServer(("", port), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
