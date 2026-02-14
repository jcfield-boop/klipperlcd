#!/bin/bash
# Deployment script for updating KlipperLCD on remote system
# Run this from your local machine after SSH'ing into the printer

set -e

echo "==================================="
echo "KlipperLCD Update Deployment Script"
echo "==================================="
echo ""

# Check if we're on the remote system
if [ ! -d ~/printer_data ]; then
    echo "ERROR: This script should be run ON the printer (192.168.0.50)"
    echo "Please SSH into the printer first:"
    echo "  ssh biqu@192.168.0.50"
    echo "Then run this script there."
    exit 1
fi

echo "Step 1: Stopping existing KlipperLCD service..."
if systemctl is-active --quiet KlipperLCD.service; then
    sudo systemctl stop KlipperLCD.service
    echo "✓ Service stopped"
else
    echo "⚠ Service was not running"
fi

echo ""
echo "Step 2: Navigating to KlipperLCD directory..."
cd ~/KlipperLCD
echo "✓ Current directory: $(pwd)"

echo ""
echo "Step 3: Checking git remote..."
CURRENT_REMOTE=$(git remote get-url origin)
echo "Current remote: $CURRENT_REMOTE"

# Update remote to point to your fork if needed
EXPECTED_REMOTE="https://github.com/jcfield-boop/klipperlcd.git"
if [ "$CURRENT_REMOTE" != "$EXPECTED_REMOTE" ]; then
    echo "Updating remote to point to your fork..."
    git remote set-url origin "$EXPECTED_REMOTE"
    echo "✓ Remote updated to: $EXPECTED_REMOTE"
fi

echo ""
echo "Step 4: Pulling latest changes from your fork..."
git fetch origin
git pull origin main
echo "✓ Code updated"

echo ""
echo "Step 5: Running installation script..."
chmod +x install.sh
./install.sh

echo ""
echo "==================================="
echo "Deployment Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Edit config: ~/printer_data/config/KlipperLCD.cfg"
echo "2. Or edit via Mainsail: Machine tab → KlipperLCD.cfg"
echo "3. Check service: sudo systemctl status KlipperLCD.service"
echo "4. View logs: journalctl -u KlipperLCD.service -f"
