"""
The Node — Core
Activation, key generation, and local storage.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from node import vault


NODE_DIR = vault.NODE_DIR
DATA_FILE = vault.DATA_FILE  # legacy path reference
KEY_FILE = vault.KEY_FILE
PUB_FILE = NODE_DIR / "public.pem"
ID_FILE = NODE_DIR / "node_id.txt"


def _migrate():
    vault.migrate_legacy()


def activate(passphrase: str = None):
    """
    Activate the node. Generates a local keypair.
    Private key never leaves this device.
    """
    if is_active():
        vault.migrate_legacy()
        print("Node already active.")
        return load_node_id()

    if passphrase is None:
        print("\n  Your node will be encrypted with a passphrase.")
        print("  You will enter it each time you use ./thenode\n")
        passphrase = vault.prompt_new_passphrase()
    else:
        if len(passphrase) < vault.MIN_PASSPHRASE_LEN:
            raise ValueError(f"Passphrase must be at least {vault.MIN_PASSPHRASE_LEN} characters.")

    vault.create_vault(passphrase)

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

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

    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    node_id = hashlib.sha256(pub_bytes).hexdigest()[:16]

    ID_FILE.write_text(node_id)
    vault._secure_file(ID_FILE)

    vault.save_data({"entries": []})

    from node.tls import ensure_tls_material
    ensure_tls_material()

    print(f"Node activated. ID: {node_id}")
    return node_id


def is_active():
    if not ID_FILE.exists() or not PUB_FILE.exists():
        return False
    if vault.vault_ready():
        return True
    # Legacy plain key until first migrate
    return KEY_FILE.exists()


def load_node_id():
    if not ID_FILE.exists():
        return None
    return ID_FILE.read_text().strip()


def load_private_key():
    pem = vault.load_private_key_pem()
    return serialization.load_pem_private_key(pem, password=None)


def load_public_key():
    with open(PUB_FILE, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def public_key_pem() -> str:
    return PUB_FILE.read_text()


def node_id_from_public_key(public_key) -> str:
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(pub_bytes).hexdigest()[:16]


def get_entry(entry_id: str):
    for entry in read(limit=9999):
        if entry["id"] == entry_id:
            return entry
    return None


def verify_entry(entry: dict, public_key) -> bool:
    signature = bytes.fromhex(entry["signature"])
    public_key.verify(
        signature,
        entry["content"].encode(),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return True


def _save_data(data: dict):
    vault.save_data(data)


def _load_data() -> dict:
    vault.require_unlock()
    return vault.load_data()


def store_received(entry: dict, origin_node_id: str, origin_public_key: str):
    if not is_active():
        return None

    received = {
        "id": entry["id"],
        "timestamp": entry["timestamp"],
        "source": f"node:{origin_node_id}",
        "content": entry["content"],
        "signature": entry["signature"],
        "origin_public_key": origin_public_key,
        "received_at": datetime.utcnow().isoformat(),
    }

    data = _load_data()
    for existing in data["entries"]:
        if existing["id"] == received["id"] and existing.get("source") == received["source"]:
            return None

    data["entries"].append(received)
    _save_data(data)
    return received["id"]


def store(text: str, source: str = "computer"):
    if not is_active():
        print("Node not active. Run ./setup.sh first.")
        return

    private_key = load_private_key()
    signature = private_key.sign(
        text.encode(),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )

    entry = {
        "id": hashlib.sha256(text.encode()).hexdigest()[:8],
        "timestamp": datetime.utcnow().isoformat(),
        "source": source,
        "content": text,
        "signature": signature.hex(),
    }

    data = _load_data()
    data["entries"].append(entry)
    _save_data(data)

    print(f"Stored. Entry ID: {entry['id']}")
    return entry["id"]


def verify(entry: dict) -> bool:
    if entry.get("origin_public_key"):
        pub = serialization.load_pem_public_key(entry["origin_public_key"].encode())
    else:
        pub = load_public_key()
    return verify_entry(entry, pub)


def verify_all() -> tuple[int, int]:
    entries = read(limit=9999)
    valid = 0
    invalid = 0
    for entry in entries:
        try:
            verify(entry)
            valid += 1
        except Exception:
            invalid += 1
    return valid, invalid


def read(limit: int = 10):
    data = _load_data()
    return data.get("entries", [])[-limit:]


def status():
    if not is_active():
        print("Node not active. Run ./setup.sh first.")
        return

    from node.memory import stake

    node_id = load_node_id()
    s = stake()

    print(f"""
--- Node Status ---
ID:      {node_id}
Record:  {s['entries']} entries · {s['span_days']} days · {s['verified']}/{s['entries'] or 0} verified
Since:   {s['since'] or '—'}
Storage: {vault.DATA_ENC} (encrypted)
Active:  True
""")
