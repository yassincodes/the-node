#!/bin/bash
# Build signed + notarized DMG for Adopt. Anyone on the internet: click, open, drag, done.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/dist"
APP="$OUT/The Node.app"
DMG="$OUT/The-Node.dmg"
STAGE="$OUT/dmg-stage"
ENT="$ROOT/apps/mac/entitlements.plist"

bash "$ROOT/apps/mac/build.sh"

SIGN_ID="${MACOS_SIGNING_IDENTITY:-}"
if [[ -z "$SIGN_ID" ]]; then
  echo "  MACOS_SIGNING_IDENTITY not set — building unsigned DMG (Gatekeeper will block strangers)."
  echo "  See apps/mac/APPLE-SETUP.md"
fi

sign_app() {
  local target="$1"
  [[ -z "$SIGN_ID" ]] && return 0
  codesign --force --deep --options runtime --entitlements "$ENT" --sign "$SIGN_ID" "$target"
  codesign --verify --deep --strict "$target"
}

sign_app "$APP"

rm -rf "$STAGE" "$DMG"
mkdir -p "$STAGE"
ditto "$APP" "$STAGE/The Node.app"
ln -s /Applications "$STAGE/Applications"

hdiutil create -volname "The Node" -srcfolder "$STAGE" -ov -format UDZO "$DMG" >/dev/null
rm -rf "$STAGE"

if [[ -n "$SIGN_ID" ]]; then
  codesign --force --sign "$SIGN_ID" "$DMG"
fi

if [[ -n "${APPLE_ID:-}" && -n "${APPLE_APP_SPECIFIC_PASSWORD:-}" && -n "${APPLE_TEAM_ID:-}" && -n "$SIGN_ID" ]]; then
  echo "  Notarizing (Apple checks it — this takes a few minutes)…"
  xcrun notarytool submit "$DMG" \
    --apple-id "$APPLE_ID" \
    --password "$APPLE_APP_SPECIFIC_PASSWORD" \
    --team-id "$APPLE_TEAM_ID" \
    --wait
  xcrun stapler staple "$DMG"
  echo "  Notarized. Adopt works for anyone."
else
  echo "  Skipping notarization (set APPLE_ID, APPLE_APP_SPECIFIC_PASSWORD, APPLE_TEAM_ID)."
fi

mkdir -p "$ROOT/public/downloads"
cp -f "$DMG" "$ROOT/public/downloads/The-Node.dmg"

echo ""
echo "  DMG: $DMG"
echo "  Mirror: public/downloads/The-Node.dmg"
echo ""
