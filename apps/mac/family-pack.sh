#!/bin/bash
# Build a folder you copy to a USB stick — for mom, brother, anyone in the room.
# Built on your Mac, hand-delivered: no download, no quarantine, no Terminal for them.
set -e
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PACK="$ROOT/dist/The Node"

bash "$ROOT/apps/mac/build.sh"

rm -rf "$PACK"
mkdir -p "$PACK"
ditto "$ROOT/dist/Install The Node.app" "$PACK/Install The Node.app"
cp "$ROOT/apps/mac/start-here-usb.html" "$PACK/Start Here.html"

xattr -cr "$PACK" 2>/dev/null || true

echo ""
echo "  Ready: $PACK"
echo ""
echo "  1. Copy the folder \"The Node\" to a USB stick"
echo "  2. On their Mac: open the USB → double-click Start Here"
echo "  3. They click Install. You’re done."
echo ""
