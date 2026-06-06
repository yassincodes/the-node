"""
The Node — Share
One entry. One node. Your explicit choice.

Nothing transfers automatically. You pick the entry, you pick the
destination (an IP you saw during discover), you run share.

The entry travels with its original signature and the sender's public
key. The receiver verifies both before storing. If the signature fails,
the entry is rejected.
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
    """
    Accept a shared entry. Verify signature and origin. Store or reject.
    Called by the local server when another node POSTs to /share.
    """
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


def send(entry_id: str, host: str) -> str:
    """
    Send one entry to another node at host.
    The receiver must be running: ./thenode serve
    """
    if not is_active():
        return "Node not active. Run ./setup.sh first."

    entry = get_entry(entry_id)
    if not entry:
        return f"No entry with id: {entry_id}"

    if entry.get("source", "").startswith("node:"):
        return "You can only share entries that are yours."

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

    url = f"http://{host}:{SHARE_PORT}/share"
    body = json.dumps(package).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read())
    except urllib.error.HTTPError as e:
        return f"Share failed: {e.code} {e.reason}"
    except urllib.error.URLError:
        return (
            f"Could not reach {host}.\n"
            "Is the other node running?  ./thenode serve"
        )
    except Exception as e:
        return f"Share failed: {e}"

    if not result.get("ok"):
        return f"Rejected: {result.get('error', 'unknown')}"

    if result.get("status") == "already had this entry":
        return f"Node at {host} already had entry {entry_id}."

    return f"Entry {entry_id} shared with {host}. They stored it from node {load_node_id()}."
