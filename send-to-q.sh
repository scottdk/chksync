#!/bin/bash
# This script builds the chksync application and uploads it to a remote server.

cd /home/scott/bin/dev/chksync
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.spec chksync-static
echo "Building chksync application..."
/home/scott/bin/dev/venv/bin/pyinstaller --onefile chksync.py
echo "========================================================="
echo "Verifying PyInstaller binary..."
file dist/chksync
ldd dist/chksync | head -5
echo "Creating static binary..."
if /home/scott/bin/dev/venv/bin/staticx dist/chksync chksync-static; then
    echo "Static binary created successfully"
else
    echo "staticx failed, trying alternative approach..."
    echo "Copying regular PyInstaller binary instead..."
    cp dist/chksync chksync-static
    chmod +x chksync-static
fi
echo "========================================================="
echo "Uploading chksync-static to remote server..."
echo "put chksync-static bin/chksync" | sftp dockuser@10.0.0.5
echo "========================================================="