"""
Presence protocol — Vercel entrypoint.
GET  /status     — protocol beacon
GET  /layer      — human-facing truth layers (env or local layers/*.json)
POST /presence   — node announces depth (ack only in v1)

Layers are for people on the site — not in git/static HTML so top-down scrapers miss them.
Browsers load via X-TheNode-Portal: human (set by public/layer.js).
"""

import json
import os
from http.server import BaseHTTPRequestHandler

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_HTML_PATH = os.path.join(_ROOT, "public", "index.html")
_DOWNLOADS_DIR = os.path.join(_ROOT, "public", "downloads")
_ALLOWED_DOWNLOADS = frozenset(
    {"The-Node.dmg", "the-node-mac.zip", "the-node-win.zip", "Adopt.command", "install.sh"}
)
_LAYERS_DIR = os.path.join(_ROOT, "layers")
_PORTAL_HEADER = "x-thenode-portal"
_HUMAN = "human"


def _bootstrap_env():
    if os.environ.get("THENODE_LAYERS") or os.environ.get("THENODE_DEEP_LAYER"):
        return
    env_path = os.path.join(_ROOT, ".env")
    if not os.path.isfile(env_path):
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            if key in ("THENODE_LAYERS", "THENODE_DEEP_LAYER"):
                os.environ[key] = val.strip().strip('"').strip("'")
                return


_bootstrap_env()


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


def _load_layers_file(name):
    path = os.path.join(_LAYERS_DIR, f"{name}.json")
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _all_layers():
    raw = os.environ.get("THENODE_LAYERS", "").strip()
    if not raw:
        raw = os.environ.get("THENODE_DEEP_LAYER", "").strip()
        if raw:
            try:
                legacy = json.loads(raw)
                if legacy.get("sections"):
                    return {"learn": legacy}
                return legacy
            except json.JSONDecodeError:
                return {}
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}
    out = {}
    for name in ("learn", "history"):
        data = _load_layers_file(name)
        if data:
            out[name] = data
    return out


def _page_payload(page):
    layers = _all_layers()
    data = layers.get(page) or {}
    sections = []
    for item in data.get("sections") or []:
        title = (item.get("title") or "").strip()
        paragraphs = [p.strip() for p in (item.get("paragraphs") or []) if p and str(p).strip()]
        if not title or not paragraphs:
            continue
        block = {"title": title, "paragraphs": paragraphs}
        if item.get("dim"):
            block["dim"] = item["dim"]
        if item.get("list"):
            block["list"] = [str(x).strip() for x in item["list"] if str(x).strip()]
        sections.append(block)
    payload = {"page": page, "sections": sections}
    tagline = (data.get("tagline") or "").strip()
    if tagline:
        payload["tagline"] = tagline
    return payload


def _is_human_portal(handler):
    return handler.headers.get(_PORTAL_HEADER, "").lower() == _HUMAN


def _layer_response(handler, query):
    if not _is_human_portal(handler):
        return {"page": query, "sections": [], "note": "human portal only"}
    page = "learn"
    if "page=" in query:
        for part in query.split("&"):
            if part.startswith("page="):
                page = part[5:].split("&")[0] or "learn"
    if page not in ("learn", "history"):
        page = "learn"
    return _page_payload(page)


def _html_body():
    try:
        with open(_HTML_PATH, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return b"<html><body><p>thenode-presence</p><a href='/status'>/status</a></body></html>"


def _download_name(path):
    name = path.rsplit("/", 1)[-1]
    return name if name in _ALLOWED_DOWNLOADS else None


def _download_body(name):
    path = os.path.join(_DOWNLOADS_DIR, name)
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return f.read()


def _download_type(name):
    if name.endswith(".dmg"):
        return "application/x-apple-diskimage"
    if name.endswith(".zip"):
        return "application/zip"
    if name.endswith(".command"):
        return "application/x-sh"
    if name.endswith(".sh"):
        return "text/plain; charset=utf-8"
    return "application/octet-stream"


class handler(BaseHTTPRequestHandler):
    def _path(self):
        return self.path.split("?")[0].rstrip("/") or "/"

    def _query(self):
        if "?" in self.path:
            return self.path.split("?", 1)[1]
        return ""

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-TheNode-Portal")
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
        if path.endswith("layer"):
            body = json.dumps(_layer_response(self, self._query())).encode()
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
        name = _download_name(path)
        if name:
            body = _download_body(name)
            if body is not None:
                self.send_response(200)
                self.send_header("Content-Type", _download_type(name))
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
        if path.endswith("layer"):
            _json(self, _layer_response(self, self._query()))
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
        name = _download_name(path)
        if name:
            body = _download_body(name)
            if body is not None:
                self.send_response(200)
                self.send_header("Content-Type", _download_type(name))
                self.send_header("Content-Disposition", f'attachment; filename="{name}"')
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
