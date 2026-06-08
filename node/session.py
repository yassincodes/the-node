"""One-time pairing codes for receive window."""

import secrets


def new_code() -> str:
    """8-character code — easy to read aloud."""
    return secrets.token_hex(4).upper()


def check(given: str, expected: str) -> bool:
    if not given or not expected:
        return False
    return secrets.compare_digest(given.strip().upper(), expected.strip().upper())
