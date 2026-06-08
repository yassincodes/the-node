#!/bin/bash
# Build The Node on this Mac — nothing downloaded from the internet except source code.
# The app is created here, so Apple has no quarantine flag on it.
set -e
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

REPO="https://github.com/yassincodes/the-node.git"
BRANCH="main"
BUILD="$HOME/.thenode-build"
INSTALL="$HOME/Applications/The Node"

clear
echo ""
echo "  The Node"
echo "  ────────"
echo ""
echo "  Building on your machine (about a minute)…"
echo ""

if ! command -v git >/dev/null 2>&1; then
  echo "  Git is required. Install Xcode Command Line Tools:"
  echo "  xcode-select --install"
  echo ""
  read -r -p "Press Enter to close…"
  exit 1
fi

rm -rf "$BUILD"
mkdir -p "$BUILD"
git clone --depth 1 --branch "$BRANCH" "$REPO" "$BUILD/the-node"

cd "$BUILD/the-node"
bash apps/mac/build.sh

mkdir -p "$INSTALL"
rm -rf "$INSTALL/The Node.app"
ditto "dist/The Node.app" "$INSTALL/"

echo ""
echo "  Done. The Node is in Applications."
echo "  Double-click it anytime — no Apple gate."
echo ""
echo "  Opening now…"
echo ""

open "$INSTALL/The Node.app"

read -r -p "Press Enter to close…"
