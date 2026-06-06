"""
The Node — Local Presence Server
Runs on localhost:5050.

It answers one question: is this node here?

It serves presence, never content. No entries, no previews, no counts —
nothing about what the node stores. Existence and the node ID are already
public (the ID is broadcast by discovery). Your stored life is not, and
this server never touches it.
"""

import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import HTTPServer, BaseHTTPRequestHandler
from node.core import load_node_id, is_active


class NodeHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/status":
            self.handle_status()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_status(self):
        if not is_active():
            self.respond({"active": False})
            return
        # Presence only: that the node exists, and its public ID. Nothing else.
        self.respond({"active": True, "node_id": load_node_id()})

    def respond(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # Silent — no noise in terminal


def run():
    server = HTTPServer(("localhost", 5050), NodeHandler)
    print("Node presence server running at http://localhost:5050")
    print("Open presence/index.html in your browser.")
    print("Serves presence only — never your stored entries.")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    run()
