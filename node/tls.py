"""
TLS for the temporary receive window (pairing code required).
Self-signed cert generated on activate. Nodes on your Wi-Fi only.
"""

import datetime
import ipaddress
import os
import stat
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from node.core import NODE_DIR, load_node_id

CERT_FILE = NODE_DIR / "node.crt"
TLS_KEY_FILE = NODE_DIR / "node.tls.key"


def _secure(path: Path):
    try:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def ensure_tls_material():
    """Generate a self-signed cert if missing."""
    NODE_DIR.mkdir(exist_ok=True)
    if CERT_FILE.exists() and TLS_KEY_FILE.exists():
        return

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    node_id = load_node_id() or "thenode"
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, f"node-{node_id}"),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=3650))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            ]),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )
    TLS_KEY_FILE.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    CERT_FILE.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    _secure(TLS_KEY_FILE)
    _secure(CERT_FILE)


def ssl_context():
    import ssl
    ensure_tls_material()
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERT_FILE, TLS_KEY_FILE)
    return ctx


def client_context():
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx
