#!/bin/bash
# Build The Node.app + friendly installer zip for Adopt.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/dist"
APP="$OUT/The Node.app"
INSTALLER="$OUT/Install The Node.app"
ZIP="$ROOT/public/downloads/the-node-mac.zip"

rm -rf "$APP" "$INSTALLER"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources/engine"

cp "$ROOT/apps/mac/Info.plist" "$APP/Contents/Info.plist"
cp "$ROOT/apps/mac/launch" "$APP/Contents/MacOS/launch"
cp "$ROOT/apps/mac/terminal-run" "$APP/Contents/Resources/terminal-run"
chmod +x "$APP/Contents/MacOS/launch" "$APP/Contents/Resources/terminal-run"

rsync -a "$ROOT/" "$APP/Contents/Resources/engine/" \
  --exclude '.git' --exclude '.venv' --exclude 'dist' --exclude '__pycache__' \
  --exclude '.env' --exclude 'layers/learn.json' --exclude 'layers/history.json' \
  --exclude '.thenode-try' --exclude 'node_modules' --exclude 'public/downloads'

rm -rf "$APP/Contents/Resources/engine/.venv"

osacompile -o "$INSTALLER" "$ROOT/apps/mac/installer.applescript"
mkdir -p "$INSTALLER/Contents/Resources"
ditto "$APP" "$INSTALLER/Contents/Resources/The Node.app"
cp "$ROOT/apps/mac/start-here.html" "$OUT/Start Here.html"

if command -v codesign >/dev/null 2>&1; then
  codesign --force --deep --sign - "$APP" 2>/dev/null || true
  codesign --force --deep --sign - "$INSTALLER" 2>/dev/null || true
fi

xattr -cr "$APP" "$INSTALLER" 2>/dev/null || true

mkdir -p "$ROOT/public/downloads"
rm -f "$ZIP"
(cd "$OUT" && zip -rq "$ZIP" "Install The Node.app" "Start Here.html")

echo ""
echo "  Built: $APP"
echo "  Adopt: $ZIP"
echo ""
