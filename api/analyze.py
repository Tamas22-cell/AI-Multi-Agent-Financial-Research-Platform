import json
import math
from pathlib import Path
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from orchestrator import Orchestrator


def _sanitize_json(value):
    """Recursively replace NaN/Infinity values with JSON-safe null."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(key): _sanitize_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize_json(item) for item in value]
    # Handle numpy/pandas scalar values without importing them here.
    try:
        if hasattr(value, "item"):
            return _sanitize_json(value.item())
    except Exception:
        pass
    return value


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path

        if path in ("/", "/index.html"):
            try:
                body = (Path(__file__).resolve().parent.parent / "index.html").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
            except Exception as exc:
                self._json_error(exc)
            return

        if path in ("/api/analyze", "/api/analyze.py"):
            try:
                output = _sanitize_json(Orchestrator().run())
                body = json.dumps(output, default=str, allow_nan=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
            except Exception as exc:
                self._json_error(exc)
            return

        body = b"Not found"
        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def _json_error(self, exc):
        body = json.dumps({"status": "error", "error": str(exc)}, allow_nan=False).encode("utf-8")
        self.send_response(500)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
