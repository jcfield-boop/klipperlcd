# Mainsail Macros Setup Guide

## What Are Macros?

Macros are **custom buttons in Mainsail** that run pre-defined GCode sequences. Instead of typing commands, you just click a button!

## Quick Setup (5 minutes)

### Step 1: Add Filament Macros

```bash
ssh biqu@192.168.0.50

# Copy filament macros
cp ~/KlipperLCD/filament_macros.cfg ~/printer_data/config/

# Edit printer.cfg
nano ~/printer_data/config/printer.cfg
```

**Add at the TOP:**
```ini
[include filament_macros.cfg]
```

Save: `Ctrl+X`, `Y`, `Enter`

### Step 2: Add Useful Macros (Optional)

```bash
# Still in SSH
cp ~/KlipperLCD/useful_macros.cfg ~/printer_data/config/

# Edit printer.cfg again
nano ~/printer_data/config/printer.cfg
```

**Add this line too:**
```ini
[include useful_macros.cfg]
```

Save and exit.

### Step 3: Restart Klipper

**In Mainsail:**
- Click "Restart" button (top right corner)

**Or via SSH:**
```bash
sudo systemctl restart klipper
```

**Done!** Check Mainsail dashboard → You'll see all the macro buttons!

---

## What Macros You'll Get

### **From filament_macros.cfg (Essential):**

| Macro | What It Does |
|-------|--------------|
| **FILAMENT_LOAD** | Heat nozzle to 200°C and load filament |
| **FILAMENT_UNLOAD** | Heat nozzle to 200°C and unload filament |
| **FILAMENT_CHANGE** | Pause print, swap filament, resume |
| **FILAMENT_LOAD_PLA** | Load at PLA temp (200°C) |
| **FILAMENT_LOAD_PETG** | Load at PETG temp (230°C) |
| **FILAMENT_LOAD_ABS** | Load at ABS temp (245°C) |
| **PURGE_FILAMENT** | Quick nozzle purge (must be hot) |

### **From useful_macros.cfg (Quality of Life):**

**Print Management:**
- `START_PRINT` - Smart print start (use in slicer!)
- `END_PRINT` - Smart print end (use in slicer!)
- `PAUSE_PRINT` - Pause with smart parking
- `RESUME_PRINT` - Resume from pause
- `CANCEL_PRINT` - Cancel and clean up

**Bed Leveling:**
- `LEVEL_BED` - Full auto bed level sequence
- `LOAD_MESH` - Load saved mesh profile
- `SAVE_MESH` - Save current mesh

**Temperature Presets:**
- `PREHEAT_PLA` - 200°C / 60°C
- `PREHEAT_PETG` - 230°C / 80°C
- `PREHEAT_ABS` - 245°C / 100°C
- `COOLDOWN` - Turn everything off

**Movement:**
- `HOME_ALL` - Home all axes
- `CENTER_XY` - Move to bed center
- `PARK_FRONT` - Park for easy access
- `PARK_REAR` - Park at rear

**Maintenance:**
- `NOZZLE_CLEAN` - Heat and purge for cleaning
- `PID_TUNE_HOTEND` - Auto-tune hotend PID
- `PID_TUNE_BED` - Auto-tune bed PID
- `CHECK_PROBE` - Test probe accuracy

**Calibration:**
- `Z_UP` - Raise nozzle 0.01mm
- `Z_DOWN` - Lower nozzle 0.01mm
- `FIRST_LAYER_CAL` - Print test squares
- `TEST_EXTRUSION` - Check extruder accuracy

**Info:**
- `GET_TEMPS` - Show current temperatures
- `GET_POSITION` - Show nozzle position

---

## How to Use Macros

### In Mainsail:

1. **Open Mainsail in browser**
2. **Look at Dashboard**
3. **Find "Macros" section** (usually right side)
4. **Click any button!**

**Example:**
- Need to load filament? Click `FILAMENT_LOAD_PLA`
- Done printing? Click `COOLDOWN`
- Level bed? Click `LEVEL_BED`

### Via Console:

You can also type macro names directly:
```
PREHEAT_PLA
FILAMENT_LOAD
CENTER_XY
```

---

## Recommended Workflow

### **Daily Printing:**

1. **Click `PREHEAT_PLA`** - Heats while you prepare
2. **Click `FILAMENT_LOAD`** - Loads filament automatically
3. **Start your print from Mainsail**
4. **When done, click `COOLDOWN`**

### **Bed Leveling:**

1. **Click `LEVEL_BED`** - Does everything automatically
2. **Click `SAVE_MESH`** - Saves the mesh
3. **Done!** - Mesh loads automatically each print

### **Filament Change:**

1. **Click `FILAMENT_UNLOAD`** - Removes old filament
2. **Click `FILAMENT_LOAD_PETG`** - Loads new at PETG temp
3. **Done!**

### **First Layer Tuning:**

1. **Click `FIRST_LAYER_CAL`** - Prints test squares
2. **Click `Z_DOWN`** if too close (can't squish)
3. **Click `Z_UP`** if too far (not sticking)
4. **Repeat until perfect**

---

## Customization

### Change Temperatures:

Edit `useful_macros.cfg`:
```ini
[gcode_macro PREHEAT_PLA]
gcode:
    M104 S205              # Change from 200 to 205
    M140 S65               # Change from 60 to 65
```

### Change Park Position:

```ini
[gcode_macro PARK_FRONT]
gcode:
    G1 X50 Y5 Z50 F6000    # Change X50 to your preferred position
```

### Add Your Own Macro:

```ini
[gcode_macro MY_CUSTOM_MACRO]
description: Does something awesome
gcode:
    M117 Hello World!
    # Add your GCode here
```

---

## Slicer Integration

### PrusaSlicer / SuperSlicer:

**Printer Settings → Custom G-code:**

**Start G-code:**
```gcode
START_PRINT BED_TEMP=[first_layer_bed_temperature] EXTRUDER_TEMP=[first_layer_temperature]
```

**End G-code:**
```gcode
END_PRINT
```

**Benefits:**
- Auto bed leveling before each print
- Purge line prevents first layer issues
- Clean print end sequence
- Smart parking

### Cura:

**Settings → Printer → Manage Printers → Machine Settings:**

**Start G-code:**
```gcode
START_PRINT BED_TEMP={material_bed_temperature_layer_0} EXTRUDER_TEMP={material_print_temperature_layer_0}
```

**End G-code:**
```gcode
END_PRINT
```

---

## Tips & Tricks

### **Organize Macros in Mainsail:**

Mainsail shows macros alphabetically. You can rename them to group:

```ini
[gcode_macro 1_FILAMENT_LOAD_PLA]     # Shows first
[gcode_macro 2_FILAMENT_UNLOAD]       # Shows second
[gcode_macro 9_EMERGENCY_STOP]        # Shows last
```

### **Hide Macros from Mainsail:**

Add underscore prefix:
```ini
[gcode_macro _INTERNAL_HELPER]        # Won't show in Mainsail
```

### **Add Parameters:**

```ini
[gcode_macro HEAT_NOZZLE]
gcode:
    {% set TEMP = params.TEMP|default(200)|int %}
    M104 S{TEMP}
```

Use: `HEAT_NOZZLE TEMP=230`

### **Make Macros Safer:**

Check conditions before running:
```ini
[gcode_macro SAFE_HOME]
gcode:
    {% if "xyz" not in printer.toolhead.homed_axes %}
        G28                    # Only home if not already homed
    {% else %}
        RESPOND MSG="Already homed!"
    {% endif %}
```

---

## Troubleshooting

### **Macros Don't Show in Mainsail:**

**Check:**
1. Did you add `[include ...]` to printer.cfg?
2. Did you restart Klipper?
3. Any errors in Mainsail console?
4. Check: Settings → Macros → Make sure they're not hidden

### **Macro Errors:**

**Common issues:**
- Typo in macro name
- Missing `gcode:` line
- Indentation wrong (must use spaces, not tabs)
- Missing parameters

**Debug:**
- Check Mainsail console for error messages
- SSH: `journalctl -u klipper -f` for detailed logs

### **Macro Runs But Does Wrong Thing:**

**Fix:**
- Edit the .cfg file
- Save
- Restart Klipper
- Try again

---

## Essential vs Optional

### **Must Have (Add These First):**
✅ `filament_macros.cfg` - Makes filament changes effortless
✅ `START_PRINT` / `END_PRINT` - Better print quality

### **Really Useful:**
⭐ `PREHEAT_*` - Saves time
⭐ `LEVEL_BED` - Convenience
⭐ `PAUSE` / `RESUME` - Better control

### **Nice to Have:**
💡 `FIRST_LAYER_CAL` - For tuning
💡 `PID_TUNE_*` - Once in a while
💡 `TEST_*` - Troubleshooting

### **Rarely Needed:**
⚙️ `TEST_SPEED` - Advanced tuning
⚙️ `CHECK_PROBE` - If having issues

---

## Quick Reference Card

**Print this and tape to your desk!**

```
┌──────────────────────────────────────────┐
│   MAINSAIL MACROS QUICK REFERENCE        │
├──────────────────────────────────────────┤
│                                          │
│  DAILY USE:                              │
│   PREHEAT_PLA → FILAMENT_LOAD → Print   │
│   After print → COOLDOWN                 │
│                                          │
│  FILAMENT CHANGE:                        │
│   FILAMENT_UNLOAD → FILAMENT_LOAD_PETG  │
│                                          │
│  BED LEVELING:                           │
│   LEVEL_BED → SAVE_MESH                  │
│                                          │
│  FIRST LAYER TOO CLOSE:                  │
│   Z_DOWN (repeat until good)             │
│                                          │
│  FIRST LAYER TOO FAR:                    │
│   Z_UP (repeat until good)               │
│                                          │
│  CLEAN NOZZLE:                           │
│   NOZZLE_CLEAN → Remove blob             │
│                                          │
└──────────────────────────────────────────┘
```

---

## Next Steps

1. ✅ **Add filament_macros.cfg** - Essential!
2. ✅ **Add useful_macros.cfg** - Quality of life!
3. ✅ **Restart Klipper**
4. ✅ **Try clicking macros in Mainsail**
5. ✅ **Update your slicer start/end gcode**
6. 🎨 **Customize to your liking**

**That's it! You now have professional macro buttons in Mainsail!** 🎉

Happy clicking! 🖱️
