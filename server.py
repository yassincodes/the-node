"""
The Node — Local Server

  ./thenode serve     — presence on this machine only. Wi-Fi cannot reach it.
  ./thenode receive   — open a 5-minute encrypted window to accept ONE share.
                        Shows a pairing code. Wi-Fi closes when done.

GET  /status  — signed presence (depth only, no entries)
POST /share   — receive one entry (verified + rate limited)
"""

import json
import os
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from node.core import is_active
from node.presence import sign_presence
from node.share import receive

PORT = 5050
ROOT = os.path.dirname(os.path.abspath(__file__))
PRESENCE_PAGE = os.path.join(ROOT, "presence", "index.html")

_SHARE_WINDOW = 60
_share_hits: dict[str, list[float]] = {}
_shutdown_flag = False


def _client_ip(handler) -> str:
    forwarded = handler.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return handler.client_address[0]


def _is_local(ip: str) -> bool:
    return ip in ("127.0.0.1", "::1", "localhost")


def _rate_ok(ip: str, max_hits: int) -> bool:
    now = time.time()
    hits = [t for t in _share_hits.get(ip, []) if now - t < _SHARE_WINDOW]
    if len(hits) >= max_hits:
        _share_hits[ip] = hits
        return False
    hits.append(now)
    _share_hits[ip] = hits
    return True


def make_handler(*, pairing_code: str = None, network_open: bool = False):
    """Build a handler: local-only serve, or temporary receive window."""

    class NodeHandler(BaseHTTPRequestHandler):
        pairing_code = pairing_code
        network_open = network_open

        def do_GET(self):
            if self.path == "/status":
                self.handle_status()
            elif self.path in ("/", "/index.html"):
                if self.network_open:
                    self.send_response(404)
                    self.end_headers()
                    return
                self.handle_presence()
            else:
                self.send_response(404)
                self.end_headers()

        def handle_presence(self):
            try:
                with open(PRESENCE_PAGE, "rb") as f:
                    body = f.read()
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)

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
            self.respond(sign_presence())

        def _share_allowed(self) -> bool:
            ip = _client_ip(self)
            if self.network_open:
                from node.session import check
                token = self.headers.get("X-Node-Session", "")
                return check(token, self.pairing_code or "")
            return _is_local(ip)

        def handle_share(self):
            global _shutdown_flag
            ip = _client_ip(self)
            limit = 5 if self.network_open else 10
            if not _rate_ok(ip, limit):
                self.respond({"ok": False, "error": "rate limit"}, status=429)
                return
            if not self._share_allowed():
                self.respond({"ok": False, "error": "forbidden"}, status=403)
                return
            length = int(self.headers.get("Content-Length", 0))
            if length > 65536:
                self.respond({"ok": False, "error": "payload too large"}, status=413)
                return
            body = self.rfile.read(length) if length else b""
            try:
                package = json.loads(body)
            except json.JSONDecodeError:
                self.respond({"ok": False, "error": "invalid json"}, status=400)
                return
            result = receive(package)
            code = 200 if result.get("ok") else 400
            self.respond(result, status=code)
            if self.network_open and result.get("ok"):
                _shutdown_flag = True

        def respond(self, data, status=200):
            body = json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format, *args):
            pass

    return NodeHandler


def _local_ip() -> str:
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "?"
    finally:
        s.close()


def _wrap_tls(httpd):
    from node.tls import ssl_context
    ctx = ssl_context()
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)


def run():
    """Presence page — this machine only. Not on Wi-Fi."""
    httpd = HTTPServer(("127.0.0.1", PORT), make_handler())
    print(f"Node on this machine only — Wi-Fi cannot reach this.")
    print(f"  http://localhost:{PORT}/")
    print(f"  http://localhost:{PORT}/status")
    print("\n  To receive from another device:  ./thenode receive")
    print("Press Ctrl+C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


def run_receive(minutes: int = 5):
    """Temporary encrypted window — pairing code required."""
    global _shutdown_flag
    _shutdown_flag = False

    from node.session import new_code
    code = new_code()
    ip = _local_ip()

    httpd = HTTPServer(
        ("0.0.0.0", PORT),
        make_handler(pairing_code=code, network_open=True),
    )
    _wrap_tls(httpd)

    deadline = time.time() + minutes * 60

    print(f"\n  Ready to receive one entry.")
    print(f"\n  Pairing code:  {code}")
    print(f"  Give this code only to the person sending.\n")
    print(f"  They run:")
    print(f"    ./thenode share <entry-id> {ip} {code}\n")
    print(f"  Encrypted. Closes in {minutes} min or after one entry arrives.")
    print("  Press Ctrl+C to cancel.\n")

    def watchdog():
        global _shutdown_flag
        while time.time() < deadline and not _shutdown_flag:
            time.sleep(0.5)
        _shutdown_flag = True
        threading.Thread(target=httpd.shutdown, daemon=True).start()

    threading.Thread(target=watchdog, daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    print("\n  Window closed. Wi-Fi port shut.")


if __name__ == "__main__":
    if "--receive" in sys.argv:
        run_receive()
    else:
        run()
