#!/bin/bash
# One-time setup. Run this once after downloading the-node.
set -e
cd "$(dirname "$0")"

echo ""
echo "  Setting up your node..."
echo ""

if ! command -v python3 >/dev/null 2>&1; then
  echo "  Python 3 is required."
  echo "  Install it from: https://www.python.org/downloads/"
  echo "  On Mac, you can also run: xcode-select --install"
  exit 1
fi

python3 -m venv .venv 2>/dev/null || true
if [ ! -f ".venv/bin/pip" ]; then
  python3 -m venv .venv
fi
.venv/bin/pip install -q -r requirements.txt
.venv/bin/python main.py activate

echo ""
echo "  Done. Your node is ready."
echo ""
echo "  Try this now:"
echo ""
echo "    ./thenode store \"something from your day\""
echo "    ./thenode read"
echo ""
echo "  Any time:"
echo ""
echo "    ./thenode          — status and what to try"
echo "    ./thenode help     — all commands"
echo ""
echo "  Optional (so ask can answer): install Ollama from https://ollama.ai"
echo "  Then run: ollama pull llama3.2"
echo ""
