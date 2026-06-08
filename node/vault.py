"""
The Node — Vault
Passphrase-derived encryption at rest (Argon2id → Fernet).
Only the salt is stored in ~/.thenode/.vault — never the key.
"""

import base64
import getpass
import json
import os
import stat
import sys
from pathlib import Path

from typing import Optional

from argon2.low_level import Type, hash_secret_raw
from cryptography.fernet import Fernet, InvalidToken

NODE_DIR = Path(os.environ.get("THENODE_HOME", str(Path.home() / ".thenode"))).expanduser()
VAULT_FILE = NODE_DIR / ".vault"
DATA_ENC = NODE_DIR / "data.enc"
KEY_ENC = NODE_DIR / "private.enc"
DATA_FILE = NODE_DIR / "data.json"
KEY_FILE = NODE_DIR / "private.pem"

VAULT_VERSION = 2
SALT_LEN = 16
KEY_LEN = 32
ARGON2_TIME = 3
ARGON2_MEMORY = 65536
ARGON2_PARALLELISM = 4
MIN_PASSPHRASE_LEN = 8
VERIFY_PLAINTEXT = b"thenode-vault-v2"

_fernet: Optional[Fernet] = None


class VaultError(Exception):
    pass


class WrongPassphrase(VaultError):
    pass


def _secure_dir():
    NODE_DIR.mkdir(exist_ok=True)
    try:
        os.chmod(NODE_DIR, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    except OSError:
        pass


def _secure_file(path: Path):
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def derive_fernet(passphrase: str, salt: bytes) -> Fernet:
    raw = hash_secret_raw(
        secret=passphrase.encode("utf-8"),
        salt=salt,
        time_cost=ARGON2_TIME,
        memory_cost=ARGON2_MEMORY,
        parallelism=ARGON2_PARALLELISM,
        hash_len=KEY_LEN,
        type=Type.ID,
    )
    key = base64.urlsafe_b64encode(raw)
    return Fernet(key)


def _vault_meta() -> Optional[dict]:
    if not VAULT_FILE.exists():
        return None
    try:
        return json.loads(VAULT_FILE.read_text())
    except json.JSONDecodeError:
        return None


def _is_legacy_stored_key() -> bool:
    """Old format: raw Fernet key bytes in .vault."""
    if not VAULT_FILE.exists():
        return False
    return _vault_meta() is None


def _legacy_fernet() -> Fernet:
    return Fernet(VAULT_FILE.read_bytes())


def _write_vault_meta(salt: bytes, f: Fernet):
    verifier = base64.b64encode(f.encrypt(VERIFY_PLAINTEXT)).decode("ascii")
    meta = {
        "v": VAULT_VERSION,
        "salt": base64.b64encode(salt).decode("ascii"),
        "verifier": verifier,
        "argon2": {
            "time": ARGON2_TIME,
            "memory": ARGON2_MEMORY,
            "parallelism": ARGON2_PARALLELISM,
        },
    }
    VAULT_FILE.write_text(json.dumps(meta, indent=2))
    _secure_file(VAULT_FILE)


def _check_verifier(f: Fernet, meta: dict):
    raw = meta.get("verifier")
    if not raw:
        return False
    try:
        return f.decrypt(base64.b64decode(raw)) == VERIFY_PLAINTEXT
    except InvalidToken:
        return False


def _verify_fernet(f: Fernet):
    meta = _vault_meta()
    if meta and _check_verifier(f, meta):
        return
    if KEY_ENC.exists():
        f.decrypt(KEY_ENC.read_bytes())
        _backfill_verifier(f, meta)
        return
    if DATA_ENC.exists():
        f.decrypt(DATA_ENC.read_bytes())
        _backfill_verifier(f, meta)
        return
    raise WrongPassphrase("Wrong passphrase.")


def _backfill_verifier(f: Fernet, meta: Optional[dict]):
    """Upgrade older vaults that have KEY_ENC but no verifier field yet."""
    if meta is None or meta.get("verifier"):
        return
    salt = base64.b64decode(meta["salt"])
    updated = {
        **meta,
        "verifier": base64.b64encode(f.encrypt(VERIFY_PLAINTEXT)).decode("ascii"),
    }
    VAULT_FILE.write_text(json.dumps(updated, indent=2))
    _secure_file(VAULT_FILE)


def prompt_new_passphrase() -> str:
    while True:
        p1 = getpass.getpass("Choose a passphrase: ")
        p2 = getpass.getpass("Confirm passphrase: ")
        if p1 != p2:
            print("Passphrases do not match. Try again.")
            continue
        if len(p1) < MIN_PASSPHRASE_LEN:
            print(f"Use at least {MIN_PASSPHRASE_LEN} characters.")
            continue
        return p1


def prompt_passphrase() -> str:
    return getpass.getpass("Passphrase: ")


def create_vault(passphrase: str):
    """New node: store salt + verifier, set in-memory Fernet for this process."""
    global _fernet
    _secure_dir()
    salt = os.urandom(SALT_LEN)
    _fernet = derive_fernet(passphrase, salt)
    _write_vault_meta(salt, _fernet)


def unlock(passphrase: str) -> Fernet:
    meta = _vault_meta()
    if meta is None:
        raise VaultError("Vault not initialized. Run ./setup.sh")
    salt = base64.b64decode(meta["salt"])
    f = derive_fernet(passphrase, salt)
    try:
        _verify_fernet(f)
    except InvalidToken as e:
        raise WrongPassphrase("Wrong passphrase.") from e
    except WrongPassphrase:
        raise
    return f


def migrate_legacy_stored_key():
    """Upgrade old .vault that held a raw Fernet key → passphrase + salt."""
    global _fernet
    if not _is_legacy_stored_key():
        return
    old = _legacy_fernet()
    private_pem = None
    data = {"entries": []}
    if KEY_ENC.exists():
        private_pem = old.decrypt(KEY_ENC.read_bytes())
    if DATA_ENC.exists():
        data = json.loads(old.decrypt(DATA_ENC.read_bytes()))
    print("\n  Upgrade: set a passphrase for your vault.")
    print("  (Your data stays the same — only how it is locked changes.)\n")
    passphrase = prompt_new_passphrase()
    create_vault(passphrase)
    if private_pem:
        save_private_key_pem(private_pem)
    save_data(data)
    print("  Vault upgraded to passphrase protection.\n")


def migrate_plain_files():
    """Legacy plain data.json / private.pem → encrypted."""
    _secure_dir()
    if not VAULT_FILE.exists() and not _is_legacy_stored_key():
        raise VaultError("Vault not initialized.")
    if _is_legacy_stored_key() and _fernet is None:
        migrate_legacy_stored_key()
        return
    if KEY_FILE.exists() and not KEY_ENC.exists():
        save_private_key_pem(KEY_FILE.read_bytes())
        KEY_FILE.unlink(missing_ok=True)
    if DATA_FILE.exists() and not DATA_ENC.exists():
        with open(DATA_FILE, "r") as f:
            save_data(json.load(f))
        DATA_FILE.unlink(missing_ok=True)
    for name in (VAULT_FILE, DATA_ENC, KEY_ENC):
        if name.exists():
            _secure_file(name)


def require_unlock():
    """Prompt for passphrase and derive key (once per process)."""
    global _fernet
    migrate_legacy_stored_key()
    if _fernet is not None:
        return
    if not VAULT_FILE.exists() and not KEY_FILE.exists():
        raise VaultError("Node not active. Run ./setup.sh first.")
    if _is_legacy_stored_key():
        migrate_legacy_stored_key()
        return
    try:
        _fernet = unlock(prompt_passphrase())
    except WrongPassphrase:
        print("Wrong passphrase.")
        sys.exit(1)


def _active_fernet() -> Fernet:
    if _fernet is None:
        raise VaultError("Vault locked.")
    return _fernet


def vault_ready() -> bool:
    return VAULT_FILE.exists() and KEY_ENC.exists()


def encrypt_bytes(data: bytes) -> bytes:
    return _active_fernet().encrypt(data)


def decrypt_bytes(token: bytes) -> bytes:
    return _active_fernet().decrypt(token)


def save_encrypted(path: Path, payload: bytes):
    path.write_bytes(encrypt_bytes(payload))
    _secure_file(path)


def load_encrypted(path: Path) -> bytes:
    return decrypt_bytes(path.read_bytes())


def save_data(data: dict):
    save_encrypted(DATA_ENC, json.dumps(data, indent=2).encode())


def load_data() -> dict:
    require_unlock()
    migrate_plain_files()
    if DATA_ENC.exists():
        return json.loads(load_encrypted(DATA_ENC))
    return {"entries": []}


def save_private_key_pem(pem: bytes):
    save_encrypted(KEY_ENC, pem)


def load_private_key_pem() -> bytes:
    require_unlock()
    migrate_plain_files()
    if KEY_ENC.exists():
        return load_encrypted(KEY_ENC)
    raise FileNotFoundError("private key missing")


def migrate_legacy():
    """Called from core on activate-if-already-active."""
    migrate_legacy_stored_key()
    migrate_plain_files()
