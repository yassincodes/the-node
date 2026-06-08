#!/usr/bin/env python3
"""Pack layers/*.json into one THENODE_LAYERS line for .env / Vercel."""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYERS = os.path.join(ROOT, "layers")


def main():
    out = {}
    for name in ("learn", "history"):
        path = os.path.join(LAYERS, f"{name}.json")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                out[name] = json.load(f)
    if not out:
        print("No layers/*.json found.", file=sys.stderr)
        sys.exit(1)
    line = "THENODE_LAYERS=" + json.dumps(out, separators=(",", ":"), ensure_ascii=False)
    print(line)


if __name__ == "__main__":
    main()
