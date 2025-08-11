#!/bin/bash
# Build and Deploy Script for chksync
# This script builds the chksync application using PyInstaller and uploads it to a remote server.
# 
# Usage: ./build-and-deploy.sh [remote_host]
# Example: ./build-and-deploy.sh user@10.0.0.5
#
# Features:
# - Cleans previous builds
# - Creates PyInstaller executable
# - Attempts static binary creation with staticx
# - Uploads binary to remote server via SFTP

# Set default remote host or use parameter
REMOTE_HOST="${1:-user@10.0.0.5}"

echo "Building chksync application..."
echo "Remote host: $REMOTE_HOST"
echo "Working directory: $(pwd)"
echo "========================================================="

echo "Cleaning previous builds..."
rm -rf build/ dist/ *.spec chksync-static

echo "Building chksync application..."
if ! command -v pyinstaller &> /dev/null; then
    echo "Error: pyinstaller not found in PATH"
    echo "Please install pyinstaller or activate your virtual environment"
    exit 1
fi

pyinstaller --onefile chksync.py
if [ $? -ne 0 ]; then
    echo "Error: PyInstaller build failed"
    exit 1
fi
echo "========================================================="
echo "Verifying PyInstaller binary..."
file dist/chksync
ldd dist/chksync | head -5
echo "Creating static binary..."
if command -v staticx &> /dev/null; then
    if staticx dist/chksync chksync-static; then
        echo "Static binary created successfully"
    else
        echo "staticx failed, trying alternative approach..."
        echo "Copying regular PyInstaller binary instead..."
        cp dist/chksync chksync-static
        chmod +x chksync-static
    fi
else
    echo "staticx not found, using regular PyInstaller binary..."
    cp dist/chksync chksync-static
    chmod +x chksync-static
fi

echo "========================================================="
echo "Uploading chksync-static to remote server: $REMOTE_HOST"
if echo "put chksync-static bin/chksync" | sftp "$REMOTE_HOST"; then
    echo "Upload successful!"
else
    echo "Upload failed!"
    exit 1
fi
echo "========================================================="
echo "Build and deployment completed successfully!"
echo "========================================================="