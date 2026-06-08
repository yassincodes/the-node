#!/usr/bin/env python3
"""
Simplest test — one command. Website opens + demo node runs in ~/.thenode-try
(not your real node). No choices.
"""

import os
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO_PASS = "trynode88"
SITE = "http://127.0.0.1:5055/"
DEMO_DIR = Path.home() / ".thenode-try"

os.environ["THENODE_HOME"] = str(DEMO_DIR)
sys.path.insert(0, str(ROOT))


def _venv_python():
    v = ROOT / ".venv" / "bin" / "python"
    return str(v) if v.exists() else sys.executable


def _ensure_deps():
    venv = ROOT / ".venv"
    if not (venv / "bin" / "pip").exists():
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    subprocess.run(
        [str(venv / "bin" / "pip"), "install", "-q", "-r", str(ROOT / "requirements.txt")],
        check=True,
    )


def _site_up():
    try:
        with urllib.request.urlopen(SITE, timeout=1) as r:
            return r.status == 200
    except Exception:
        return False


def _start_site():
    if _site_up():
        return
    subprocess.Popen(
        [_venv_python(), str(ROOT / "tools" / "serve_site.py")],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(20):
        if _site_up():
            return
        time.sleep(0.25)


def _demo_activate():
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    import hashlib

    from node import vault
    from node.core import ID_FILE, PUB_FILE, is_active, load_node_id

    if is_active():
        return load_node_id()

    vault.create_vault(DEMO_PASS)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    vault.save_private_key_pem(pem)
    public_key = private_key.public_key()
    pub_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    PUB_FILE.write_bytes(pub_pem)
    vault._secure_file(PUB_FILE)
    node_id = hashlib.sha256(
        public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    ).hexdigest()[:16]
    ID_FILE.write_text(node_id)
    vault._secure_file(ID_FILE)
    vault.save_data({"entries": []})
    from node.tls import ensure_tls_material
    ensure_tls_material()
    return node_id


def _demo_run():
    from node import vault
    from node.core import read, status, store
    from routing.router import route

    vault._fernet = vault.unlock(DEMO_PASS)
    store("I am testing the node. This is my first honest entry.")
    entries = read(limit=3)
    print("\n  --- your demo node ---\n")
    status()
    print("\n  last entry:")
    for e in entries[:1]:
        print(f"    {e['content']}\n")

    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2):
            print("  asking locally (Ollama)...\n")
            print(f"  {route('what did I just store?')}\n")
    except Exception:
        print("  (Ollama not running — skip ask, or install from ollama.ai)\n")


def main():
    print("\n  The Node — simplest test\n")
    _ensure_deps()
    _start_site()
    webbrowser.open(SITE)
    print(f"  1. Browser → {SITE}")
    node_id = _demo_activate()
    print(f"  2. Demo node ready (sandbox ~/.thenode-try, id {node_id})")
    _demo_run()
    print("  Done. Site is open. Demo node is real but separate from a future ./setup.sh node.")
    print("  When ready for yours: ./setup.sh\n")


if __name__ == "__main__":
    main()
