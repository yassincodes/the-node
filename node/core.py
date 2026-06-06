"""
The Node — Core
Activation, key generation, and local storage.
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes


NODE_DIR = Path.home() / ".thenode"
DATA_FILE = NODE_DIR / "data.json"
KEY_FILE = NODE_DIR / "private.pem"
PUB_FILE = NODE_DIR / "public.pem"
ID_FILE = NODE_DIR / "node_id.txt"


def _ensure_data_file():
    """Create an empty store if keys exist but data.json does not."""
    NODE_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        with open(DATA_FILE, "w") as f:
            json.dump({"entries": []}, f)


def activate():
    """
    Activate the node. Generates a local keypair.
    Private key never leaves this device.
    """
    if is_active():
        _ensure_data_file()
        print("Node already active.")
        return load_node_id()

    NODE_DIR.mkdir(exist_ok=True)

    # Generate keypair
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Save private key — stays on device only
    with open(KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Save public key — this is what other nodes see
    public_key = private_key.public_key()
    with open(PUB_FILE, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    # Generate node ID from public key
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    node_id = hashlib.sha256(pub_bytes).hexdigest()[:16]

    with open(ID_FILE, "w") as f:
        f.write(node_id)

    # Initialize empty data store
    with open(DATA_FILE, "w") as f:
        json.dump({"entries": []}, f)

    print(f"Node activated. ID: {node_id}")
    return node_id


def is_active():
    return KEY_FILE.exists() and ID_FILE.exists()


def load_node_id():
    if not ID_FILE.exists():
        return None
    return ID_FILE.read_text().strip()


def load_private_key():
    with open(KEY_FILE, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


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
    """Find one entry by its id."""
    for entry in read(limit=9999):
        if entry["id"] == entry_id:
            return entry
    return None


def verify_entry(entry: dict, public_key) -> bool:
    """Verify an entry's signature against a given public key."""
    signature = bytes.fromhex(entry["signature"])
    public_key.verify(
        signature,
        entry["content"].encode(),
        padding.PKCS1v15(),
        hashes.SHA256(),
    )
    return True


def store_received(entry: dict, origin_node_id: str, origin_public_key: str):
    """
    Store an entry received from another node.
    Original signature and content are kept. Origin is recorded.
    """
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

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    for existing in data["entries"]:
        if existing["id"] == received["id"] and existing.get("source") == received["source"]:
            return None  # already have this

    data["entries"].append(received)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return received["id"]


def store(text: str, source: str = "computer"):
    """
    Store a piece of natural language input.
    Signs it with the private key so origin is verifiable.
    source: 'computer' (conscious input)
    """
    if not is_active():
        print("Node not active. Run ./setup.sh first.")
        return

    _ensure_data_file()
    private_key = load_private_key()

    # Sign the content
    signature = private_key.sign(
        text.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    entry = {
        "id": hashlib.sha256(text.encode()).hexdigest()[:8],
        "timestamp": datetime.utcnow().isoformat(),
        "source": source,
        "content": text,
        "signature": signature.hex()
    }

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    data["entries"].append(entry)

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Stored. Entry ID: {entry['id']}")
    return entry["id"]


def verify(entry: dict) -> bool:
    """Verify an entry — local entries use your key, shared entries use origin key."""
    if entry.get("origin_public_key"):
        pub = serialization.load_pem_public_key(entry["origin_public_key"].encode())
    else:
        pub = load_public_key()
    return verify_entry(entry, pub)


def verify_all() -> tuple[int, int]:
    """Verify all stored entries. Returns (valid_count, invalid_count)."""
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
    """Read the last N entries from your node."""
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
    return data["entries"][-limit:]


def status():
    """Show the current state of your node."""
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
Storage: {DATA_FILE}
Active:  True
""")
