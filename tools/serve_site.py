#!/usr/bin/env python3
"""Local preview: public/ static files + /layer and /status API."""

import json
import mimetypes
import os
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Timer
from urllib.parse import unquote

mimetypes.add_type("application/zip", ".zip")
mimetypes.add_type("application/x-sh", ".command")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, "public")
sys.path.insert(0, ROOT)

import importlib.util

_spec = importlib.util.spec_from_file_location("api_index", os.path.join(ROOT, "api", "index.py"))
_api = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_api)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(fmt % args)

    def _path(self):
        return unquote(self.path.split("?")[0])

    def _query(self):
        return self.path.split("?", 1)[1] if "?" in self.path else ""

    def _send(self, code, body, ctype):
        data = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self._path().rstrip("/") or "/"

        if path.endswith("/layer"):
            payload = _api._layer_response(self, self._query())
            self._send(200, json.dumps(payload), "application/json")
            return

        if path.endswith("/status"):
            self._send(200, json.dumps(_api._status_payload()), "application/json")
            return

        rel = path.lstrip("/") or "index.html"
        if rel == "":
            rel = "index.html"
        filepath = os.path.normpath(os.path.join(PUBLIC, rel))
        if not filepath.startswith(PUBLIC) or not os.path.isfile(filepath):
            self.send_error(404)
            return
        ctype = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
        with open(filepath, "rb") as f:
            self._send(200, f.read(), ctype)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "X-TheNode-Portal")
        self.end_headers()


def main():
    port = int(os.environ.get("PORT", "5055"))
    host = "127.0.0.1"
    url = f"http://{host}:{port}/"
    print(f"\n  Site → {url}")
    print("  Adopt downloads the app.\n")
    Timer(0.8, lambda: webbrowser.open(url)).start()
    HTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
