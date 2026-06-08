#!/bin/bash
# Build The Node on this Mac. Run via: curl -fsSL …/install.sh | bash
set -e
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

REPO="https://github.com/yassincodes/the-node.git"
BRANCH="main"
BUILD="$HOME/.thenode-build"
INSTALL="$HOME/Applications/The Node"

echo ""
echo "  The Node"
echo "  ────────"
echo ""
echo "  Building on your machine…"
echo ""

if ! command -v git >/dev/null 2>&1; then
  echo "  Git required. Run: xcode-select --install"
  exit 1
fi

rm -rf "$BUILD"
mkdir -p "$BUILD"
git clone --depth 1 --branch "$BRANCH" "$REPO" "$BUILD/the-node"

cd "$BUILD/the-node"
bash apps/mac/build.sh

mkdir -p "$INSTALL"
rm -rf "$INSTALL/The Node.app"
ditto "dist/The Node.app" "$INSTALL/The Node.app"

echo ""
echo "  Done — Applications → The Node"
echo "  Opening…"
echo ""

open "$INSTALL/The Node.app"
