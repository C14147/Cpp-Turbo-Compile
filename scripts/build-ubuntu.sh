#!/usr/bin/env bash
# Build script for Ubuntu (bash) using PyInstaller
#
# Usage:
#   ./scripts/build-ubuntu.sh          # uses `python` from PATH
#   ./scripts/build-ubuntu.sh --onefile  # pass extra PyInstaller args
#
# Notes:
#  - Ensure `pyinstaller` is installed in the selected Python environment:
#      python -m pip install pyinstaller
#  - Extra arguments passed to this script are forwarded to PyInstaller.

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

echo "Building $ENTRYPOINT with PyInstaller..."

mkdir -p "$BUILD_DIR"

# Default to onedir; if --onefile provided, create single exe
pyinstaller_args=(--clean --noconfirm --distpath "$BUILD_DIR" --workpath "$BUILD_DIR/build_work" --specpath "$BUILD_DIR/spec")

for a in "$@"; do
  if [ "$a" = "--onefile" ] || [ "$a" = "-F" ]; then
    pyinstaller_args+=(--onefile)
  else
    pyinstaller_args+=("$a")
  fi
done

python -m PyInstaller "${pyinstaller_args[@]}" "$ENTRYPOINT"

echo "Build finished. Output located in: $BUILD_DIR"
echo "Run the produced executable from the dist folder inside $BUILD_DIR."
