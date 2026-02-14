#!/bin/bash
# KlipperLCD Installation Script
# Automates the installation and configuration of KlipperLCD service

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect current user and home directory
CURRENT_USER=$(whoami)
USER_HOME=$(eval echo ~$CURRENT_USER)

# Installation paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CONFIG_DIR="${USER_HOME}/printer_data/config"
CONFIG_FILE="${CONFIG_DIR}/KlipperLCD.cfg"
SERVICE_NAME="KlipperLCD.service"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}"

print_info "KlipperLCD Installation Script"
echo "================================"
echo "User: ${CURRENT_USER}"
echo "Home: ${USER_HOME}"
echo "Install Dir: ${SCRIPT_DIR}"
echo "Config Dir: ${CONFIG_DIR}"
echo ""

# Check if running as root (for systemd installation)
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root or with sudo"
    print_info "The script will ask for sudo password when needed"
    exit 1
fi

# Create config directory if it doesn't exist
if [ ! -d "${CONFIG_DIR}" ]; then
    print_warn "Config directory doesn't exist, creating: ${CONFIG_DIR}"
    mkdir -p "${CONFIG_DIR}"
fi

# Generate or update configuration file
if [ -f "${CONFIG_FILE}" ]; then
    print_warn "Config file already exists: ${CONFIG_FILE}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Keeping existing config file"
    else
        print_info "Generating new config file..."
        python3 "${SCRIPT_DIR}/main.py" --generate-config "${CONFIG_FILE}"
    fi
else
    print_info "Generating config file: ${CONFIG_FILE}"
    python3 "${SCRIPT_DIR}/main.py" --generate-config "${CONFIG_FILE}"
fi

# Generate systemd service file
print_info "Generating systemd service file..."

cat > /tmp/${SERVICE_NAME} <<EOF
[Unit]
Description=KlipperLCD Service - LCD interface for Klipper 3D printers
After=moonraker.service

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${SCRIPT_DIR}
Restart=always
RestartSec=5
ExecStart=/usr/bin/env python3 ${SCRIPT_DIR}/main.py --config ${CONFIG_FILE}

[Install]
WantedBy=multi-user.target
EOF

# Install service file
print_info "Installing service file (requires sudo)..."
sudo cp /tmp/${SERVICE_NAME} ${SERVICE_FILE}
sudo chmod 644 ${SERVICE_FILE}
rm /tmp/${SERVICE_NAME}

# Reload systemd
print_info "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Ask if user wants to enable and start the service
echo ""
read -p "Do you want to enable KlipperLCD service to start on boot? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    print_info "Service not enabled"
else
    print_info "Enabling KlipperLCD service..."
    sudo systemctl enable ${SERVICE_NAME}
fi

echo ""
read -p "Do you want to start KlipperLCD service now? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    print_info "Service not started"
else
    # Stop service if already running
    if systemctl is-active --quiet ${SERVICE_NAME}; then
        print_info "Stopping existing KlipperLCD service..."
        sudo systemctl stop ${SERVICE_NAME}
    fi

    print_info "Starting KlipperLCD service..."
    sudo systemctl start ${SERVICE_NAME}

    # Wait a moment and check status
    sleep 2
    if systemctl is-active --quiet ${SERVICE_NAME}; then
        print_info "KlipperLCD service started successfully!"
    else
        print_error "KlipperLCD service failed to start"
        print_info "Check status with: sudo systemctl status ${SERVICE_NAME}"
        print_info "Check logs with: journalctl -u ${SERVICE_NAME} -f"
    fi
fi

# Print summary
echo ""
echo "================================"
print_info "Installation complete!"
echo ""
echo "Configuration file: ${CONFIG_FILE}"
echo "  - Edit this file to customize settings"
echo "  - File is visible in Mainsail configuration editor"
echo ""
echo "Useful commands:"
echo "  Start service:    sudo systemctl start ${SERVICE_NAME}"
echo "  Stop service:     sudo systemctl stop ${SERVICE_NAME}"
echo "  Restart service:  sudo systemctl restart ${SERVICE_NAME}"
echo "  Service status:   sudo systemctl status ${SERVICE_NAME}"
echo "  View logs:        journalctl -u ${SERVICE_NAME} -f"
echo "  Edit config:      nano ${CONFIG_FILE}"
echo ""
echo "After editing config, restart the service to apply changes:"
echo "  sudo systemctl restart ${SERVICE_NAME}"
echo "================================"
