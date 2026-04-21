#!/usr/bin/env bash
set -e

echo "Creating virtual environment for build..."
python3 -m venv .venv_build
source .venv_build/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Building macOS executable with PyInstaller..."
pyinstaller --onefile --add-data "templates:templates" --add-data "static:static" app.py

echo "Build complete. Find the executable in dist/"
