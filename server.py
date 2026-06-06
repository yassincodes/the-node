"""
The Node — Local Server
Runs on localhost:5050
Feeds the presence page with live data from your node.
"""

import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from http.server import HTTPServer, BaseHTTPRequestHandler
from node.core import load_node_id, read, is_active, DATA_FILE


class NodeHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/status":
            self.handle_status()
        elif self.path == "/entries":
            self.handle_entries()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_status(self):
        if not is_active():
            self.respond({"active": False})
            return

        entries = read(limit=9999)
        last = entries[-1]["content"][:60] + "..." if entries else None

        self.respond({
            "active": True,
            "node_id": load_node_id(),
            "entries": len(entries),
            "last_entry": last
        })

    def handle_entries(self):
        entries = read(limit=20)
        self.respond({"entries": entries})

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
    print("Node server running at http://localhost:5050")
    print("Open presence/index.html in your browser.")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    run()
