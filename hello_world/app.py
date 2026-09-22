"""The HTTP handler realizing the canonical hello-world contract."""
from __future__ import annotations

import json
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def make_handler(greeting: str):
    class HelloHandler(BaseHTTPRequestHandler):
        server_version = "hello-world/1.0"

        def _json(self, code: int, payload: dict) -> None:
            body = json.dumps(payload).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):  # noqa: N802 (http.server API)
            if self.path == "/":
                self._json(200, {"message": greeting, "hostname": socket.gethostname()})
            elif self.path == "/health":
                self._json(200, {"status": "ok"})
            elif self.path == "/boom":
                # Deliberate 500 — the failure endpoint later probes/self-healing drills use.
                self._json(500, {"error": "boom"})
            else:
                self._json(404, {"error": "not found", "path": self.path})

        def _not_allowed(self):
            self._json(405, {"error": "method not allowed", "method": self.command})

        # The contract serves GET only; every write method is 405.
        do_POST = _not_allowed  # noqa: N815
        do_PUT = _not_allowed  # noqa: N815
        do_DELETE = _not_allowed  # noqa: N815
        do_PATCH = _not_allowed  # noqa: N815

        def log_message(self, *args):  # keep the manual-ops lab output clean
            pass

    return HelloHandler


def make_server(host: str, port: int, greeting: str) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), make_handler(greeting))
