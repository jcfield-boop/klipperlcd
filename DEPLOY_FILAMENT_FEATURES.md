# Quick Deploy: Filament Change Features

## What You're Getting

🎯 **Three new console shortcuts on your LCD:**
- `LOAD_FILAMENT` - Auto-heat and load filament
- `UNLOAD_FILAMENT` - Auto-heat and unload filament
- `CHANGE_FILAMENT` - Pause print, swap filament, resume

Plus **full macro support** in Mainsail with material presets!

## 5-Minute Deployment

### Step 1: Update KlipperLCD Code (2 minutes)

```bash
ssh biqu@192.168.0.50

# Pull latest code
cd ~/KlipperLCD
git pull

# Restart service
sudo systemctl restart KlipperLCD.service

# Verify it's running
sudo systemctl status KlipperLCD.service
```

### Step 2: Add Klipper Macros (2 minutes)

**Still on SSH:**

```bash
# Copy macro file to config
cp ~/KlipperLCD/filament_macros.cfg ~/printer_data/config/

# Edit printer.cfg
nano ~/printer_data/config/printer.cfg
```

**Add this line at the TOP of printer.cfg:**
```ini
[include filament_macros.cfg]
```

**Save and exit:** `Ctrl+X`, `Y`, `Enter`

**Restart Klipper:**
- Go to Mainsail in browser
- Click "Restart" button (firmware restart)
- OR via SSH: `sudo systemctl restart klipper`

### Step 3: Test! (1 minute)

**On your LCD:**
1. Tap center top to open console
2. Type: `HELP_LCD`
3. You should see the new commands!
4. Try: `LOAD_FILAMENT`

**In Mainsail:**
1. Look at Dashboard → Macros section
2. You should see: FILAMENT_LOAD, FILAMENT_UNLOAD, etc.
3. Click one to test!

## Usage Examples

### Load Filament for First Print

**On LCD Console:**
```
LOAD_FILAMENT
```

**What happens:**
1. Nozzle heats to 200°C automatically
2. LCD shows: "Insert filament now"
3. Insert filament into extruder
4. Filament feeds automatically (50mm)
5. Purges 10mm
6. Ready to print!

### Unload Filament After Print

**On LCD Console:**
```
UNLOAD_FILAMENT
```

**What happens:**
1. Nozzle heats to 200°C
2. Filament retracts 60mm
3. LCD shows: "Safe to remove"
4. Pull filament out
5. Nozzle cools down

### Change Filament Mid-Print

**On LCD Console:**
```
CHANGE_FILAMENT
```

**What happens:**
1. Print pauses
2. Nozzle moves to park position (front-left)
3. Old filament unloads
4. LCD shows: "Insert new filament"
5. Insert new filament
6. Press RESUME button on LCD
7. New filament loads and purges
8. Print continues!

## Material-Specific Shortcuts

**In Mainsail, use these macros for specific materials:**

- `FILAMENT_LOAD_PLA` - Loads at 200°C
- `FILAMENT_LOAD_PETG` - Loads at 230°C
- `FILAMENT_LOAD_ABS` - Loads at 245°C

Click the macro button in Mainsail dashboard!

## Customization

### If You Have Bowden Extruder

**Edit the macros:**
```bash
nano ~/printer_data/config/filament_macros.cfg
```

**Change these lines:**
```ini
[gcode_macro FILAMENT_LOAD]
gcode:
    {% set DISTANCE = params.DISTANCE|default(100)|int %}  # Change 50 to 100

[gcode_macro FILAMENT_UNLOAD]
gcode:
    {% set DISTANCE = params.DISTANCE|default(100)|int %}  # Change 60 to 100
```

**Bowden needs more distance** because filament travels through the tube!

### If Your Material Needs Different Temp

**Use parameters when calling:**
```gcode
FILAMENT_LOAD TEMP=225        # Load at 225°C
FILAMENT_UNLOAD TEMP=235      # Unload at 235°C
```

Or **create custom preset:**
```ini
[gcode_macro FILAMENT_LOAD_MYSTIC_BLUE_PLA]
gcode:
    FILAMENT_LOAD TEMP=205    # Your specific PLA brand
```

## Troubleshooting

### "Nozzle too cold" Error

**Solution:** Macros auto-heat! Just wait 30 seconds.

### Filament Won't Feed

**Try:**
```gcode
FILAMENT_LOAD TEMP=210 DISTANCE=80
```
(Increase temp by 10°C, increase distance)

### Filament Oozing After Load

**Edit macro to reduce purge:**
```ini
G1 E10 F150      # Change to G1 E5 F150 (purge less)
```

### Can't Find Macros in Mainsail

**Check:**
1. Did you add `[include filament_macros.cfg]` to printer.cfg?
2. Did you restart Klipper?
3. Look in Mainsail Dashboard → Macros section

## What Each Command Does

| Command | Heats To | Feeds/Retracts | Purges | Cools Down |
|---------|----------|----------------|--------|------------|
| LOAD_FILAMENT | 200°C | +50mm | +10mm | Yes (if idle) |
| UNLOAD_FILAMENT | 200°C | -60mm | No | Yes |
| CHANGE_FILAMENT | Current | -60mm, then +50mm | +10mm | No (printing) |

## Advanced: Multi-Color Prints

**In your slicer (PrusaSlicer):**
1. Right-click layer → Add custom GCode
2. Type: `M600` or `FILAMENT_CHANGE`
3. Slice and print!

**During print:**
- Printer pauses at that layer
- Automatically unloads old color
- Prompts you to insert new color
- Automatically loads and purges
- Continues printing!

## Next Steps

1. ✅ Test LOAD_FILAMENT with scrap filament
2. ✅ Test UNLOAD_FILAMENT
3. ✅ Adjust distances if needed (bowden vs direct)
4. ✅ Try a multi-color print!
5. ✅ Print the quick reference card (in FILAMENT_CHANGE_GUIDE.md)

## Full Documentation

See `FILAMENT_CHANGE_GUIDE.md` for:
- Detailed configuration options
- Advanced workflows
- Safety tips
- Troubleshooting guide
- Quick reference card to print

---

**That's it! You now have professional filament management on your Neptune 3 Pro!** 🎉

Type `HELP_LCD` on your LCD console to see all available commands!
