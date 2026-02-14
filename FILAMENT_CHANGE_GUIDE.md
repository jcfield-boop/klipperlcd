# Filament Change Support for KlipperLCD

## Overview

Added comprehensive filament change support with:
- **LCD Console shortcuts** - Type commands on your LCD
- **Klipper macros** - Work from LCD, Mainsail, or console
- **Material presets** - PLA, PETG, ABS temperatures
- **Mid-print changes** - Pause, swap filament, resume

## Features

### 1. Basic Operations
- **Load Filament** - Heat nozzle, insert filament, auto-feed
- **Unload Filament** - Heat nozzle, retract filament completely
- **Change Filament** - Pause print, swap filament, resume

### 2. Smart Features
- Auto-heating to correct temperature
- Slow initial feed for grip
- Purge after loading
- Anti-ooze retract
- Auto-cooldown when done

### 3. Material Presets
- PLA: 200°C
- PETG: 230°C
- ABS: 245°C

## Installation

### Step 1: Update KlipperLCD Code

The code changes have already been made to:
- `lcd.py` - Added events 37, 38, 39
- `main.py` - Added event handlers and console shortcuts

**Deploy to printer:**
```bash
ssh biqu@192.168.0.50
cd ~/KlipperLCD
git pull
sudo systemctl restart KlipperLCD.service
```

### Step 2: Add Klipper Macros

**Copy macros to printer:**
```bash
# From your Mac:
scp filament_macros.cfg biqu@192.168.0.50:~/printer_data/config/
```

**Edit printer.cfg:**
```bash
ssh biqu@192.168.0.50
nano ~/printer_data/config/printer.cfg
```

**Add at the top:**
```ini
[include filament_macros.cfg]
```

**Restart Klipper:**
- In Mainsail: Click "Restart" button
- Or SSH: `sudo systemctl restart klipper`

### Step 3: Test!

**From LCD console:**
```
HELP_LCD           # See new commands
LOAD_FILAMENT      # Try loading
```

## Usage

### From LCD Console

**Load Filament:**
```
Type on LCD: LOAD_FILAMENT
```
1. Nozzle heats to 200°C
2. Insert filament when prompted
3. Filament feeds automatically
4. Purges to ensure flow
5. Done!

**Unload Filament:**
```
Type on LCD: UNLOAD_FILAMENT
```
1. Nozzle heats to 200°C
2. Filament retracts automatically
3. Remove when prompted
4. Done!

**Change Filament During Print:**
```
Type on LCD: CHANGE_FILAMENT
```
1. Print pauses
2. Nozzle moves to park position
3. Old filament unloads
4. Insert new filament
5. Press Resume on LCD
6. New filament loads
7. Print continues!

### From Mainsail/Fluidd

**Available Macros:**
- `FILAMENT_LOAD` - Basic load
- `FILAMENT_UNLOAD` - Basic unload
- `FILAMENT_CHANGE` - Mid-print change
- `FILAMENT_LOAD_PLA` - Load at 200°C
- `FILAMENT_LOAD_PETG` - Load at 230°C
- `FILAMENT_LOAD_ABS` - Load at 245°C
- `PURGE_FILAMENT` - Quick purge

**Click the macro in Mainsail dashboard to run!**

### Advanced Usage (with Parameters)

**Custom temperature:**
```gcode
FILAMENT_LOAD TEMP=230
```

**Custom distance:**
```gcode
FILAMENT_LOAD DISTANCE=80     # Load 80mm instead of 50mm
FILAMENT_UNLOAD DISTANCE=100  # Unload 100mm instead of 60mm
```

**Custom park position:**
```gcode
FILAMENT_CHANGE X=50 Y=50 Z_LIFT=20
```

**Combine parameters:**
```gcode
FILAMENT_LOAD TEMP=235 DISTANCE=70
```

## Configuration

### Adjust Default Distances

**Edit filament_macros.cfg:**
```ini
[gcode_macro FILAMENT_LOAD]
gcode:
    {% set DISTANCE = params.DISTANCE|default(50)|int %}  # Change 50 to your preference
```

**Common adjustments:**
- **Bowden setup:** Increase to 100-400mm (length of bowden tube + 50mm)
- **Direct drive:** Keep 50mm (already optimal)
- **Long retraction:** Increase unload to 80-100mm

### Adjust Default Temperatures

**Edit the material preset macros:**
```ini
[gcode_macro FILAMENT_LOAD_PLA]
gcode:
    FILAMENT_LOAD TEMP=205  # Change from 200 to 205
```

### Adjust Park Position

**Edit FILAMENT_CHANGE macro:**
```ini
{% set PARK_X = params.X|default(10)|int %}   # Change 10 to X position
{% set PARK_Y = params.Y|default(10)|int %}   # Change 10 to Y position
{% set PARK_Z_LIFT = params.Z_LIFT|default(10)|int %}  # Change 10 to Z lift
```

**Recommended park positions:**
- **Neptune 3 Pro:** X=10, Y=10 (front-left corner)
- **Small printers:** X=5, Y=5
- **Large printers:** X=20, Y=20

## Workflow Examples

### Example 1: Start of Day - Load New Spool

**On LCD:**
```
1. Type: LOAD_FILAMENT
2. Wait for heating
3. Insert filament when beep/prompt
4. Watch filament extrude
5. Remove purge blob
6. Ready to print!
```

### Example 2: End of Day - Remove Filament

**On LCD:**
```
1. Type: UNLOAD_FILAMENT
2. Wait for heating
3. Wait for retraction
4. Pull filament out
5. Store filament
6. Done!
```

### Example 3: Multi-Color Print

**In Slicer (PrusaSlicer/Cura):**
```
Add M600 command at layer change
  OR
Use "Change Filament" feature
```

**During Print:**
1. Printer pauses at M600 or FILAMENT_CHANGE
2. Old filament unloads automatically
3. LCD shows: "Insert new filament"
4. Insert new color
5. Press RESUME on LCD
6. New filament loads and purges
7. Print continues!

### Example 4: Runout During Print

**When filament runs out:**
```
1. Press PAUSE on LCD
2. Type: CHANGE_FILAMENT
3. Follow prompts
4. Print resumes seamlessly!
```

## Troubleshooting

### Filament Won't Feed

**Symptoms:** Motor turns but filament doesn't move

**Solutions:**
- Increase TEMP by 5-10°C
- Increase load DISTANCE
- Check extruder gear tension
- Verify nozzle isn't clogged

**Try:**
```gcode
FILAMENT_LOAD TEMP=210 DISTANCE=80
```

### Filament Won't Retract

**Symptoms:** Filament stuck, won't pull back

**Solutions:**
- Increase TEMP by 10°C
- Heat soak for 30 seconds before unload
- Pull manually while motor retracts

**Try:**
```gcode
FILAMENT_UNLOAD TEMP=220
```

### Oozing After Load

**Symptoms:** Plastic drips from nozzle

**Solutions:**
- Reduce purge amount
- Increase retract after load
- Lower temperature

**Edit macro:**
```ini
G1 E10 F150      # Reduce from 10 to 5
G1 E-1 F1800     # Increase from -1 to -2
```

### Print Doesn't Resume After Change

**Symptoms:** Paused but won't resume

**Solutions:**
- Press RESUME button on LCD or Mainsail
- Check for error in console
- Restart print if stuck

### Nozzle Too Cold Warning

**Symptoms:** "Nozzle too cold" message

**Solutions:**
- Wait for heating to complete
- Temperature sensor issue (check thermistor)
- Target temp too low

## Advanced Features

### Custom Filament Change Position

**For Neptune 3 Pro with specific needs:**

```ini
[gcode_macro FILAMENT_CHANGE]
gcode:
    # Park at back-right corner instead
    G1 X210 Y210 F6000

    # Or center of bed
    G1 X110 Y110 F6000
```

### Multiple Extruders (Future)

**If you add a second extruder:**

```ini
[gcode_macro FILAMENT_LOAD_T1]
gcode:
    T1  # Select extruder 1
    FILAMENT_LOAD TEMP=200
```

### Filament Sensor Integration

**If you add a filament sensor:**

```ini
[filament_switch_sensor filament_sensor]
pause_on_runout: True
runout_gcode:
    FILAMENT_CHANGE  # Auto-trigger filament change on runout!
```

### Color Change Layers

**In your slicer, add at specific layer:**

```gcode
M600  # Standard filament change command
; or
FILAMENT_CHANGE  # KlipperLCD command
```

## Console Shortcuts Reference

**All available commands:**
```
LOAD_FILAMENT       - Load filament (200°C default)
UNLOAD_FILAMENT     - Unload filament (200°C default)
CHANGE_FILAMENT     - Change during print

# Also available via Mainsail:
FILAMENT_LOAD       - Same as LOAD_FILAMENT
FILAMENT_UNLOAD     - Same as UNLOAD_FILAMENT
FILAMENT_CHANGE     - Same as CHANGE_FILAMENT
FILAMENT_LOAD_PLA   - Load at PLA temp (200°C)
FILAMENT_LOAD_PETG  - Load at PETG temp (230°C)
FILAMENT_LOAD_ABS   - Load at ABS temp (245°C)
PURGE_FILAMENT      - Quick purge (must be hot already)
```

## Safety Notes

- ⚠️ **Hot nozzle!** Don't touch during/after operation
- ⚠️ **Watch first time** - Verify distances are appropriate
- ⚠️ **Test before print** - Try load/unload before important prints
- ⚠️ **Clean nozzle** - Remove purge blobs to avoid print contamination
- ⚠️ **Monitor temperature** - Don't exceed material max temps

## Benefits Over Manual Changes

**Manual method:**
1. Heat nozzle (remember temp)
2. Wait for heat
3. Manually extrude/retract
4. Guess correct distance
5. Deal with oozing
6. Cool down manually

**With macros:**
1. Type: `LOAD_FILAMENT`
2. Done!

**Saves:** Time, guesswork, oozing, burned fingers!

## Next Steps

### After Installation:

1. ✅ Test LOAD_FILAMENT with scrap filament
2. ✅ Test UNLOAD_FILAMENT
3. ✅ Adjust distances if needed
4. ✅ Try material presets
5. ✅ Test CHANGE_FILAMENT during practice print

### Optional Enhancements:

- Add filament runout sensor
- Add LCD buttons for filament ops (requires TFT mod)
- Create custom temps for your specific brands
- Add bed heating during filament changes

## Support

**Issues?**
- Check logs: `journalctl -u KlipperLCD.service -f`
- Verify macros loaded: Look in Mainsail macros section
- Test from console first before LCD

**Questions?**
- Klipper docs: https://www.klipper3d.org/G-Codes.html
- Check [include] worked: Look for macros in Mainsail

---

## Quick Reference Card

**Print this and tape to your printer!**

```
┌─────────────────────────────────────────┐
│   FILAMENT CHANGE QUICK REFERENCE       │
├─────────────────────────────────────────┤
│                                         │
│  LOAD NEW FILAMENT:                     │
│    LCD > Console > LOAD_FILAMENT        │
│                                         │
│  REMOVE FILAMENT:                       │
│    LCD > Console > UNLOAD_FILAMENT      │
│                                         │
│  CHANGE DURING PRINT:                   │
│    LCD > Console > CHANGE_FILAMENT      │
│    Wait for prompts                     │
│    Press RESUME when new fil inserted   │
│                                         │
│  TEMPERATURES:                          │
│    PLA: 200°C   PETG: 230°C            │
│    ABS: 245°C   TPU: 220°C             │
│                                         │
│  TROUBLESHOOTING:                       │
│    Won't feed? Increase temp 10°C       │
│    Oozing? Clean nozzle before print    │
│    Stuck? Heat and pull manually        │
│                                         │
└─────────────────────────────────────────┘
```

Happy printing! 🎉
