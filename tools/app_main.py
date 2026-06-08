#!/usr/bin/env python3
"""Mac app entry — unlock vault, open browser, run local server (foreground)."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from node import vault


def main():
    phrase = os.environ.get("THENODE_UNLOCK", "").strip()
    if not phrase:
        sys.exit("No passphrase.")
    vault._fernet = vault.unlock(phrase)
    import server
    server.run()


if __name__ == "__main__":
    main()
