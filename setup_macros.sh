#!/bin/bash
# Setup Macros for Mainsail
# Run this on your printer: bash setup_macros.sh

echo "=============================================="
echo "  KlipperLCD Macros Setup"
echo "=============================================="
echo ""

# Check current situation
echo "1. Checking current config directory..."
echo ""
echo "Files in ~/printer_data/config/:"
ls -la ~/printer_data/config/*.cfg 2>/dev/null || echo "  No .cfg files found (besides printer.cfg)"
echo ""

echo "2. Files in ~/KlipperLCD/:"
ls -la ~/KlipperLCD/*.cfg 2>/dev/null || echo "  No .cfg files found"
echo ""

echo "3. Current [include] statements in printer.cfg:"
grep -i "^\[include" ~/printer_data/config/printer.cfg 2>/dev/null || echo "  No includes found"
echo ""

echo "=============================================="
echo "  Ready to Setup?"
echo "=============================================="
echo ""
echo "This will:"
echo "  1. Copy filament_macros.cfg to ~/printer_data/config/"
echo "  2. Copy useful_macros.cfg to ~/printer_data/config/"
echo "  3. Show you what to add to printer.cfg"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Copy files
echo ""
echo "Copying macro files..."

if [ -f ~/KlipperLCD/filament_macros.cfg ]; then
    cp ~/KlipperLCD/filament_macros.cfg ~/printer_data/config/
    echo "  ✓ Copied filament_macros.cfg"
else
    echo "  ✗ filament_macros.cfg not found in ~/KlipperLCD/"
fi

if [ -f ~/KlipperLCD/useful_macros.cfg ]; then
    cp ~/KlipperLCD/useful_macros.cfg ~/printer_data/config/
    echo "  ✓ Copied useful_macros.cfg"
else
    echo "  ✗ useful_macros.cfg not found in ~/KlipperLCD/"
fi

echo ""
echo "=============================================="
echo "  Next Steps:"
echo "=============================================="
echo ""
echo "Add these lines to the TOP of ~/printer_data/config/printer.cfg:"
echo ""
echo "  [include filament_macros.cfg]"
echo "  [include useful_macros.cfg]"
echo ""
echo "Then restart Klipper:"
echo "  - In Mainsail: Click 'Restart' button"
echo "  - Or SSH: sudo systemctl restart klipper"
echo ""
echo "To edit printer.cfg now:"
echo "  nano ~/printer_data/config/printer.cfg"
echo ""
echo "=============================================="
