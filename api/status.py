"""
Presence protocol — status beacon.
GET /status  (via rewrite from /api/status)

Returns protocol identity. No node content. No registry.
"""

import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({
            "protocol": "thenode-presence",
            "version": 1,
            "active": True,
            "message": "A light. Nodes announce depth, never content.",
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
