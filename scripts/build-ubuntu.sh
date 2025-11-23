#!/usr/bin/env bash
# Build script for Ubuntu (bash) using Nuitka
#
# Usage:
#   ./scripts/build-ubuntu.sh          # uses `python` from PATH
#   ./scripts/build-ubuntu.sh --onefile  # pass extra nuitka args
#
# Notes:
#  - Ensure `nuitka` is installed in the selected Python environment:
#      python -m pip install nuitka
#  - Extra arguments passed to this script are forwarded to Nuitka.

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$DIR/.."
SRC_DIR="$PROJECT_ROOT/src"
BUILD_DIR="$PROJECT_ROOT/build"

if [ ! -d "$SRC_DIR" ]; then
  echo "Source folder not found: $SRC_DIR" >&2
  exit 1
fi

echo "Cleaning build folder: $BUILD_DIR"
rm -rf "$BUILD_DIR"

ENTRYPOINT="$SRC_DIR/main.py"
if [ ! -f "$ENTRYPOINT" ]; then
  echo "Entrypoint not found: $ENTRYPOINT" >&2
  exit 1
fi

echo "Building $ENTRYPOINT with Nuitka..."

python -m nuitka --standalone --output-dir="$BUILD_DIR" --remove-output --show-progress --follow-imports "$ENTRYPOINT" "$@"

echo "Build finished. Output located in: $BUILD_DIR"
echo "Run the produced executable from the standalone folder (check subfolder next to main binary)."
