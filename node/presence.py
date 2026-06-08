"""
The Node — Signed presence
Proves the announcer holds the private key matching the node ID.
"""

import json

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from node.core import load_node_id, load_private_key, load_public_key, public_key_pem
from node.memory import stake


def _payload(node_id: str, record: dict) -> bytes:
    return json.dumps(
        {"node_id": node_id, "record": record},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()


def sign_presence(record: dict = None) -> dict:
    """Build signed presence — depth only, no entry content."""
    node_id = load_node_id()
    record = record if record is not None else stake()
    private_key = load_private_key()
    signature = private_key.sign(
        _payload(node_id, record),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return {
        "active": True,
        "node_id": node_id,
        "record": record,
        "public_key": public_key_pem(),
        "presence_signature": signature.hex(),
    }


def verify_presence(package: dict) -> bool:
    """Verify a presence package against its public key."""
    node_id = package.get("node_id")
    record = package.get("record")
    signature_hex = package.get("presence_signature")
    public_key_pem_str = package.get("public_key")
    if not all([node_id, record is not None, signature_hex, public_key_pem_str]):
        return False
    pub = serialization.load_pem_public_key(public_key_pem_str.encode())
    from node.core import node_id_from_public_key
    if node_id_from_public_key(pub) != node_id:
        return False
    signature = bytes.fromhex(signature_hex)
    pub.verify(
        signature,
        _payload(node_id, record),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return True
