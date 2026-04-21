#!/bin/bash

# Build Android APK for Task Dashboard
# This script builds the Android APK using buildozer

echo "Building Android APK for Task Dashboard..."

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo "buildozer not found. Installing..."
    pip install buildozer
fi

# Clean previous build
echo "Cleaning previous build..."
buildozer android clean

# Build debug APK
echo "Building debug APK..."
buildozer android debug

echo "Build complete! APK should be in bin/ directory"