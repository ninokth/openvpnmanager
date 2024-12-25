#!/bin/bash
#exec > >(tee -a install_debug.log) 2>&1
#set -e
# set -x


# echo "Install script" 

if [ "$(id -u)" -ne 0 ] ; then
    echo "Run this script with sudo" >&2
    exit 1
fi

# Determine the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Paths
SCRIPT_PATH="$SCRIPT_DIR/openvpnManager.py"
INSTALL_PATH="/usr/local/bin/openvpnManager"

# Ensure source file exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Source script not found at $SCRIPT_PATH"
    exit 1
fi

# Make script executable
chmod +x "$SCRIPT_PATH"

# Create symlink
sudo ln -sf "$SCRIPT_PATH" "$INSTALL_PATH"

# Verify symlink
if [ ! -L "$INSTALL_PATH" ]; then
    echo "Error: Failed to create symlink at $INSTALL_PATH"
    exit 1
fi

echo "Symlink created successfully:"
ls -l "$INSTALL_PATH"
