"""
Presence protocol — Vercel entrypoint.
GET  /           — presence page
GET  /status     — protocol beacon
POST /presence   — node announces depth (ack only in v1)
"""

import json
import os
from http.server import BaseHTTPRequestHandler

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_HTML_PATH = os.path.join(_ROOT, "public", "index.html")


def _json(handler, data, status=200):
    body = json.dumps(data).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _status_payload():
    return {
        "protocol": "thenode-presence",
        "version": 1,
        "active": True,
        "message": "A light. Nodes announce depth, never content.",
    }


def _html_body():
    try:
        with open(_HTML_PATH, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return b"<html><body><p>thenode-presence</p><a href='/status'>/status</a></body></html>"


class handler(BaseHTTPRequestHandler):
    def _path(self):
        return self.path.split("?")[0].rstrip("/") or "/"

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_HEAD(self):
        path = self._path()
        if path.endswith("status"):
            body = json.dumps(_status_payload()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return
        if path in ("/", "/api/index", "/index.html"):
            body = _html_body()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        path = self._path()
        if path.endswith("status"):
            _json(self, _status_payload())
            return
        if path in ("/", "/api/index", "/index.html"):
            body = _html_body()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        if not path.endswith("presence"):
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        try:
            data = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            _json(self, {"ok": False, "error": "invalid json"}, 400)
            return

        node_id = data.get("node_id")
        record = data.get("record")
        if not node_id or not isinstance(record, dict):
            _json(self, {"ok": False, "error": "need node_id and record"}, 400)
            return

        _json(self, {
            "ok": True,
            "protocol": "thenode-presence",
            "version": 1,
            "seen": node_id,
            "stored": False,
            "note": "v1 acknowledges only. Registry not built yet.",
        })
