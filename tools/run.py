#!/usr/bin/env python3
"""Local website only — lonely node, Learn more, Adopt downloads the app."""

import os
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Timer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(ROOT, "public")
PORT = int(os.environ.get("PORT", "5055"))
HOST = "127.0.0.1"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC, **kwargs)

    def log_message(self, fmt, *args):
        print(fmt % args)


def main():
    url = f"http://{HOST}:{PORT}/"
    print(f"\n  Site → {url}")
    print(f"  Adopt downloads the app. Your secrets stay in the app.\n")
    Timer(0.8, lambda: webbrowser.open(url)).start()
    HTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
