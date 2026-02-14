#!/bin/bash
# Test KlipperLCD Enhanced Features
# Run this on your printer to verify everything works

echo "=============================================="
echo "  KlipperLCD Enhanced Features Test"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if service is running
echo -n "1. Checking KlipperLCD service... "
if systemctl is-active --quiet KlipperLCD.service; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
    echo "   Start with: sudo systemctl start KlipperLCD.service"
    exit 1
fi

# Check config file exists
echo -n "2. Checking config file... "
if [ -f ~/printer_data/config/KlipperLCD.cfg ]; then
    echo -e "${GREEN}✓ Found${NC}"
else
    echo -e "${RED}✗ Missing${NC}"
    echo "   Run: cd ~/KlipperLCD && python3 main.py --generate-config ~/printer_data/config/KlipperLCD.cfg"
    exit 1
fi

# Check for [features] section
echo -n "3. Checking [features] section... "
if grep -q "\[features\]" ~/printer_data/config/KlipperLCD.cfg; then
    echo -e "${GREEN}✓ Found${NC}"
    DEFAULT_PA=$(grep "default_pa" ~/printer_data/config/KlipperLCD.cfg | cut -d'=' -f2 | tr -d ' ')
    echo "   Default PA: $DEFAULT_PA"
else
    echo -e "${YELLOW}⚠ Missing${NC}"
    echo "   Update your config to get latest features"
fi

# Check Python dependencies
echo -n "4. Checking Python dependencies... "
MISSING_DEPS=""
python3 -c "import serial" 2>/dev/null || MISSING_DEPS="${MISSING_DEPS}python3-serial "
python3 -c "import requests" 2>/dev/null || MISSING_DEPS="${MISSING_DEPS}python3-requests "
python3 -c "from PIL import Image" 2>/dev/null || MISSING_DEPS="${MISSING_DEPS}python3-pil "

if [ -z "$MISSING_DEPS" ]; then
    echo -e "${GREEN}✓ All installed${NC}"
else
    echo -e "${RED}✗ Missing: $MISSING_DEPS${NC}"
    echo "   Install with: sudo apt-get install $MISSING_DEPS"
fi

# Check Moonraker connectivity
echo -n "5. Checking Moonraker connection... "
if curl -s http://127.0.0.1:80/printer/info > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Connected${NC}"
else
    echo -e "${RED}✗ Cannot connect${NC}"
    echo "   Check Moonraker is running: systemctl status moonraker"
fi

# Check serial port
echo -n "6. Checking LCD serial port... "
SERIAL_PORT=$(grep "serial_port" ~/printer_data/config/KlipperLCD.cfg | cut -d'=' -f2 | tr -d ' ')
if [ -e "$SERIAL_PORT" ]; then
    echo -e "${GREEN}✓ Found: $SERIAL_PORT${NC}"
else
    echo -e "${RED}✗ Missing: $SERIAL_PORT${NC}"
    echo "   Check with: ls /dev/tty*"
fi

echo ""
echo "=============================================="
echo "  Console Shortcuts Available:"
echo "=============================================="
echo ""
echo "Type these commands in your LCD console:"
echo ""
echo "  SHOW_MESH      - View bed mesh visualization"
echo "  SHOW_STATUS    - System status & MCU temp"
echo "  SHOW_PA        - Pressure Advance info"
echo "  SHOW_SHAPER    - Input Shaper config"
echo "  PA_ADJUST 0.001  - Fine-tune PA (+/-)"
echo "  PA_RESET       - Reset to default PA"
echo "  HELP_LCD       - Show all commands"
echo ""
echo "=============================================="
echo "  How to Test:"
echo "=============================================="
echo ""
echo "1. On your LCD, tap center top to open console"
echo "2. Type: HELP_LCD"
echo "3. Try: SHOW_STATUS"
echo "4. Watch logs: journalctl -u KlipperLCD.service -f"
echo ""

# Check recent logs for errors
echo "Recent log entries (last 5):"
echo "--------------------------------------------"
journalctl -u KlipperLCD.service -n 5 --no-pager
echo "--------------------------------------------"
echo ""

# Summary
echo "=============================================="
echo "  Summary:"
echo "=============================================="
if systemctl is-active --quiet KlipperLCD.service && [ -f ~/printer_data/config/KlipperLCD.cfg ]; then
    echo -e "${GREEN}✓ KlipperLCD is ready to use!${NC}"
    echo ""
    echo "Enhanced features are available via console shortcuts."
    echo "Open the console on your LCD and try: HELP_LCD"
else
    echo -e "${RED}✗ Some issues detected${NC}"
    echo "Review the checks above and fix any errors."
fi
echo ""
