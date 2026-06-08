#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
APP="$DIR/The Node.app"
[ -d "$APP" ] || { osascript -e 'display alert "The Node.app not found."'; exit 1; }
xattr -cr "$APP" 2>/dev/null
xattr -cr "$DIR/Adopt.command" 2>/dev/null
open "$APP"
