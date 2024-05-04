#!/bin/bash

# Check if running as root, if not, restart with sudo
if [ $EUID != 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

# Define paths
BIN_PATH="/usr/local/bin/automagic-fan"
SERVICE_PATH="/lib/systemd/system/automagic-fan.service"
CONFIG_PATH="/etc/automagic-fan"

echo "Removing automagic-fan..."

# Stop and disable service
systemctl stop automagic-fan
systemctl disable automagic-fan

# Remove files and directories
rm -rf "$BIN_PATH" /usr/bin/automagic-fan 2>/dev/null
rm -f "$SERVICE_PATH"
rm -rf "$CONFIG_PATH"

# Reload systemd
echo "Reloading services..."
systemctl daemon-reload

echo "Automagic-Fan uninstalled successfully!"
 
