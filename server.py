"""
The Node — Local Server
Runs on 0.0.0.0:5050 — reachable on your local network.

GET  /status  — presence only: {active, node_id}
POST /share   — receive one entry from another node (explicit, verified)

Your stored entries are never listed here. Share only accepts what
another node sends, and only while you run serve.
"""

import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import HTTPServer, BaseHTTPRequestHandler
from node.core import load_node_id, is_active
from node.share import receive

PORT = 5050


class NodeHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/status":
            self.handle_status()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/share":
            self.handle_share()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_status(self):
        if not is_active():
            self.respond({"active": False})
            return
        self.respond({"active": True, "node_id": load_node_id()})

    def handle_share(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        try:
            package = json.loads(body)
        except json.JSONDecodeError:
            self.respond({"ok": False, "error": "invalid json"}, status=400)
            return
        result = receive(package)
        code = 200 if result.get("ok") else 400
        self.respond(result, status=code)

    def respond(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def run():
    server = HTTPServer(("0.0.0.0", PORT), NodeHandler)
    print(f"Node listening on port {PORT} (local network)")
    print("  GET  /status  — presence")
    print("  POST /share   — receive a shared entry")
    print("Open presence/index.html for the presence page.")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    run()
