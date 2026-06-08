#!/bin/bash
# Windows adopt package — engine + Adopt.bat
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/public/downloads"
ZIP="$OUT/the-node-win.zip"
STAGE="$ROOT/dist/win-stage"

rm -rf "$STAGE" "$ZIP"
mkdir -p "$STAGE" "$OUT"

rsync -a "$ROOT/" "$STAGE/" \
  --exclude '.git' --exclude '.venv' --exclude 'dist' --exclude '__pycache__' \
  --exclude '.env' --exclude 'layers/learn.json' --exclude 'layers/history.json' \
  --exclude 'node_modules' --exclude 'public/downloads'

cd "$STAGE"
zip -rq "$ZIP" . -x "*.DS_Store"
rm -rf "$STAGE"
echo "  Built: $ZIP"
