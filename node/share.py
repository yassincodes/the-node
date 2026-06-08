"""
The Node — Share
One entry. One node. Your explicit choice.

Receiver runs:  ./thenode receive
Sender runs:    ./thenode share <entry-id> <host> <pairing-code>
"""

import json
import urllib.request
import urllib.error

from cryptography.hazmat.primitives import serialization

from node.core import (
    is_active,
    load_node_id,
    public_key_pem,
    get_entry,
    verify_entry,
    node_id_from_public_key,
    store_received,
)

SHARE_PORT = 5050


def receive(package: dict) -> dict:
    if not is_active():
        return {"ok": False, "error": "node not active"}

    origin_node_id = package.get("from_node_id")
    origin_public_key_pem = package.get("public_key")
    entry = package.get("entry")

    if not origin_node_id or not origin_public_key_pem or not entry:
        return {"ok": False, "error": "incomplete package"}

    try:
        pub = serialization.load_pem_public_key(origin_public_key_pem.encode())
    except Exception:
        return {"ok": False, "error": "invalid public key"}

    if node_id_from_public_key(pub) != origin_node_id:
        return {"ok": False, "error": "node id does not match public key"}

    try:
        verify_entry(entry, pub)
    except Exception:
        return {"ok": False, "error": "signature verification failed"}

    stored_id = store_received(entry, origin_node_id, origin_public_key_pem)
    if stored_id is None:
        return {"ok": True, "status": "already had this entry"}

    return {"ok": True, "entry_id": stored_id, "from": origin_node_id}


def _is_local(host: str) -> bool:
    return host.strip().lower() in ("127.0.0.1", "localhost", "::1")


def send(entry_id: str, host: str, pairing_code: str = None) -> str:
    if not is_active():
        return "Node not active. Run ./setup.sh first."

    entry = get_entry(entry_id)
    if not entry:
        return f"No entry with id: {entry_id}"

    if entry.get("source", "").startswith("node:"):
        return "You can only share entries that are yours."

    local = _is_local(host)
    if not local and not pairing_code:
        return (
            "Need a pairing code.\n"
            "The other person runs:  ./thenode receive\n"
            "Then you run:  ./thenode share <entry-id> <their-ip> <code>"
        )

    package = {
        "from_node_id": load_node_id(),
        "public_key": public_key_pem(),
        "entry": {
            "id": entry["id"],
            "timestamp": entry["timestamp"],
            "source": entry["source"],
            "content": entry["content"],
            "signature": entry["signature"],
        },
    }

    scheme = "http" if local else "https"
    url = f"{scheme}://{host}:{SHARE_PORT}/share"
    headers = {"Content-Type": "application/json"}
    if pairing_code:
        headers["X-Node-Session"] = pairing_code.strip().upper()

    req = urllib.request.Request(
        url,
        data=json.dumps(package).encode(),
        headers=headers,
        method="POST",
    )

    ctx = None
    if not local:
        from node.tls import client_context
        ctx = client_context()

    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            result = json.loads(response.read())
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return "Rejected — wrong pairing code or receive window closed."
        return f"Share failed: {e.code} {e.reason}"
    except urllib.error.URLError:
        return (
            f"Could not reach {host}.\n"
            "Is the other node running  ./thenode receive  ?"
        )
    except Exception as e:
        return f"Share failed: {e}"

    if not result.get("ok"):
        return f"Rejected: {result.get('error', 'unknown')}"

    if result.get("status") == "already had this entry":
        return f"Node at {host} already had entry {entry_id}."

    return f"Entry {entry_id} shared. They stored it from node {load_node_id()}."
