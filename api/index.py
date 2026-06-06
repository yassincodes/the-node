"""
Presence protocol — Vercel entrypoint.
GET  /status   — protocol beacon
POST /presence — node announces depth (ack only in v1)
"""

import json
from http.server import BaseHTTPRequestHandler


def _json(handler, data, status=200):
    body = json.dumps(data).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path.endswith("status"):
            _json(self, {
                "protocol": "thenode-presence",
                "version": 1,
                "active": True,
                "message": "A light. Nodes announce depth, never content.",
            })
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
