#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python 3 installation
if ! command_exists python3; then
    echo "Python 3 is not installed..."
    sudo apt update
    sudo apt install -y python3-dev
fi

# Check if running as root, if not, restart with sudo
if [ "$EUID" -ne 0 ]; then
    echo "This script requires superuser privileges. Restarting with sudo..."
    exec sudo "$0" "$@"
fi

echo "Setting up files to /usr/local/bin/automagic-fan/..."
sudo rm -rf /usr/local/bin/automagic-fan/
sudo mkdir -p /usr/local/bin/automagic-fan
sudo cp fan-control.py /usr/local/bin/automagic-fan/
echo "Files settled."

echo "Adding service to /lib/systemd/system/..."
sudo cp automagic-fan.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/automagic-fan.service
echo "Service added."

echo "Creating config at /etc/automagic-fan/..."
sudo mkdir -p /etc/automagic-fan/
sudo cp config.json /etc/automagic-fan/
sudo chmod 664 /etc/automagic-fan/config.json
echo "Config created."

echo "Starting and enabling service..."
sudo systemctl daemon-reload
sudo systemctl start automagic-fan
sudo systemctl enable automagic-fan
echo "Service started and enabled."

echo "Automagic-fan installed successfully!"
echo ""
echo "To configure, edit /etc/automagic-fan/config.json (requires sudo)"
