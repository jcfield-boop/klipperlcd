#!/bin/bash
# Debug Macro Setup Issues

echo "=============================================="
echo "  Macro Setup Debugger"
echo "=============================================="
echo ""

echo "1. Checking if macro files exist in config..."
echo ""
if [ -f ~/printer_data/config/filament_macros.cfg ]; then
    echo "  ✓ filament_macros.cfg EXISTS"
    echo "    Size: $(wc -l < ~/printer_data/config/filament_macros.cfg) lines"
else
    echo "  ✗ filament_macros.cfg MISSING!"
    echo "    Need to copy it: cp ~/KlipperLCD/filament_macros.cfg ~/printer_data/config/"
fi

if [ -f ~/printer_data/config/useful_macros.cfg ]; then
    echo "  ✓ useful_macros.cfg EXISTS"
    echo "    Size: $(wc -l < ~/printer_data/config/useful_macros.cfg) lines"
else
    echo "  ✗ useful_macros.cfg MISSING!"
    echo "    Need to copy it: cp ~/KlipperLCD/useful_macros.cfg ~/printer_data/config/"
fi
echo ""

echo "2. Checking printer.cfg includes..."
echo ""
if grep -q "^\[include filament_macros.cfg\]" ~/printer_data/config/printer.cfg; then
    echo "  ✓ [include filament_macros.cfg] FOUND"
else
    echo "  ✗ [include filament_macros.cfg] NOT FOUND or commented out"
fi

if grep -q "^\[include useful_macros.cfg\]" ~/printer_data/config/printer.cfg; then
    echo "  ✓ [include useful_macros.cfg] FOUND"
else
    echo "  ✗ [include useful_macros.cfg] NOT FOUND or commented out"
fi
echo ""

echo "3. Showing first 30 lines of printer.cfg:"
echo "----------------------------------------"
head -30 ~/printer_data/config/printer.cfg
echo "----------------------------------------"
echo ""

echo "4. Checking Klipper status..."
echo ""
systemctl is-active klipper && echo "  ✓ Klipper is RUNNING" || echo "  ✗ Klipper is NOT RUNNING"
echo ""

echo "5. Checking for Klipper errors (last 30 lines):"
echo "----------------------------------------"
journalctl -u klipper -n 30 --no-pager | grep -i "error\|warn\|include"
echo "----------------------------------------"
echo ""

echo "6. Testing if macro is loaded (checking for FILAMENT_LOAD):"
echo ""
if journalctl -u klipper -n 200 --no-pager | grep -q "gcode_macro FILAMENT_LOAD"; then
    echo "  ✓ FILAMENT_LOAD macro was loaded"
else
    echo "  ✗ FILAMENT_LOAD macro not found in logs"
fi
echo ""

echo "=============================================="
echo "  Summary"
echo "=============================================="
echo ""
echo "If files are missing, run:"
echo "  cp ~/KlipperLCD/filament_macros.cfg ~/printer_data/config/"
echo "  cp ~/KlipperLCD/useful_macros.cfg ~/printer_data/config/"
echo ""
echo "If includes are missing, edit printer.cfg:"
echo "  nano ~/printer_data/config/printer.cfg"
echo "  Add at top:"
echo "    [include filament_macros.cfg]"
echo "    [include useful_macros.cfg]"
echo ""
echo "Then restart:"
echo "  sudo systemctl restart klipper"
echo ""
