# KlipperLCD Enhanced Features Guide

## Overview
This guide documents the enhanced features added to KlipperLCD to make printer calibration and monitoring more accessible directly from the LCD, especially for beginners.

## System Status & Monitoring

### Klipper State Display
**Purpose**: Know the current state of your printer and troubleshoot errors

**Features**:
- Real-time Klipper state (Ready, Error, Shutdown, Starting)
- Error message display when Klipper is in error state
- Color-coded status indicators
- MCU temperature monitoring

**How to Access**:
- Call from console or trigger via new LCD button (when LCD firmware updated)
- Event: `VIEW_SYSTEM_STATUS` (35)

**What You'll See**:
```
System Status:
Ready

MCU Temp: 45.2°C
```

Or if there's an error:
```
System Status:
Error: Probe triggered prior to movement

MCU Temp: 47.1°C
WARNING: High MCU temp!
```

**Recovery Options**:
- `FIRMWARE_RESTART` event (32) - Restart Klipper to clear errors
- Available from error display screen

---

## Bed Mesh Visualization

### View Bed Mesh
**Purpose**: See your bed leveling results visually to understand problem areas

**Features**:
- Text grid display of mesh points
- Min/Max deviation values
- Mesh range calculation
- Quality assessment (Excellent/Good/Fair/Poor)
- Profile name display

**How to Access**:
- After running `BED_MESH_CALIBRATE`
- Event: `VIEW_MESH` (30)
- Console command or new LCD menu item

**Example Output**:
```
Bed Mesh (default):
===================================
 +0.05 +0.02 -0.01
 +0.03  0.00 -0.02
 +0.01 -0.01 -0.03
===================================
Min: -0.030mm  Max: +0.050mm
Range: 0.080mm
Quality: Good
```

**Interpretation**:
- **Green zone** (Range < 0.05mm): Excellent leveling
- **Yellow zone** (Range 0.05-0.10mm): Good leveling
- **Orange zone** (Range 0.10-0.20mm): Fair - consider re-leveling
- **Red zone** (Range > 0.20mm): Poor - re-level immediately

### Mesh Profile Management
**Purpose**: Save and load different mesh profiles

**Features**:
- List saved mesh profiles
- Load specific profile
- Event: `MESH_PROFILE_SELECT` (31)

**Usage**:
```
Available profiles:
- default
- cold_bed
- hot_bed

[Load] [Save Current] [Delete]
```

---

## Pressure Advance

### PA Display & Quick Adjust
**Purpose**: Fine-tune pressure advance during test prints without SSH

**Features**:
- Current PA value display
- Quick adjustment buttons (±0.001, ±0.01)
- Typical range guidance
- Reset to default
- Immediate application (no restart)

**How to Access**:
- From settings menu
- Events: `PA_ADJUST` (33), `PA_RESET` (34)

**Display**:
```
Pressure Advance: 0.0350

Typical ranges:
  Bowden: 0.3 - 0.7
  Direct Drive: 0.02 - 0.1

Status: Typical for direct drive

[-0.01] [-0.001] [+0.001] [+0.01]
[Reset to Default]
```

**Tuning Workflow**:
1. Print PA calibration test
2. Observe corner quality
3. Use quick adjust to fine-tune
4. No firmware restart needed
5. Save when satisfied

---

## Input Shaper

### Shaper Status Display
**Purpose**: See what resonance compensation is active

**Features**:
- X/Y axis shaper type and frequency
- Enabled/disabled status
- Toggle on/off from LCD
- Explanatory help text

**How to Access**:
- Settings menu
- Event: `TOGGLE_INPUT_SHAPER` (36)

**Display**:
```
Input Shaper: ENABLED

X-axis: MZV
  Frequency: 42.5 Hz

Y-axis: MZV
  Frequency: 38.2 Hz

[Disable] [Info]
```

**When to Use**:
- **Always ON**: For best print quality (default)
- **Turn OFF**: If causing surface artifacts or infill issues
- **Info**: Learn what input shaping does

---

## File Metadata Display

### Enhanced File Information
**Purpose**: Know print details before starting

**Features**:
- Estimated print time
- Filament usage (length and weight)
- Layer information (height, count)
- Slicer name and version
- Uses Moonraker metadata (faster than parsing gcode)

**Display Before Print**:
```
benchy.gcode

Time: 3h 24m
Filament: 12.45m
Weight: 35.2g
Layer: 0.2mm
First Layer: 0.28mm
Layers: 312
Slicer: PrusaSlicer 2.6.1

[Print] [Cancel]
```

**During Print**:
- Layer counter: "Layer 45/312"
- More accurate time remaining (uses slicer estimate)

---

## Implementation Details for Developers

### New PrinterData Methods

#### System Status
```python
def get_klipper_state():
    # Returns: {'state': str, 'message': str}
    # States: ready, startup, shutdown, error, unknown

def get_mcu_stats():
    # Returns: {'mcu_temp': float, 'last_stats': dict}

def firmware_restart():
    # POST /printer/firmware_restart
```

#### Bed Mesh
```python
def get_bed_mesh_data():
    # Returns: {
    #   'points': [[z1, z2, ...], ...],
    #   'min': float,
    #   'max': float,
    #   'range': float,
    #   'profile_name': str
    # }

def get_mesh_profiles():
    # Returns: ['default', 'cold_bed', ...]

def load_mesh_profile(name: str):
    # POST BED_MESH_PROFILE LOAD=name
```

#### Pressure Advance
```python
def get_pressure_advance():
    # Returns: float (current PA value)

def set_pressure_advance(value: float):
    # POST SET_PRESSURE_ADVANCE ADVANCE=value
```

#### Input Shaper
```python
def get_input_shaper_config():
    # Returns: {
    #   'shaper_type_x': str,
    #   'shaper_freq_x': float,
    #   'shaper_type_y': str,
    #   'shaper_freq_y': float
    # }

def toggle_input_shaper(enabled: bool):
    # Enable/disable by setting freq to 0
```

#### File Metadata
```python
def get_file_metadata(filename: str):
    # Returns: {
    #   'estimated_time': int,
    #   'filament_total': float,
    #   'filament_weight_total': float,
    #   'layer_height': float,
    #   'first_layer_height': float,
    #   'layer_count': int,
    #   'slicer': str,
    #   'slicer_version': str,
    #   'thumbnails': list
    # }
```

### New LCD Events

| Event | Value | Purpose | Data |
|-------|-------|---------|------|
| VIEW_MESH | 30 | Display bed mesh | None |
| MESH_PROFILE_SELECT | 31 | Load mesh profile | Profile name (str) |
| FIRMWARE_RESTART | 32 | Restart Klipper | None |
| PA_ADJUST | 33 | Adjust PA value | Adjustment amount (float) |
| PA_RESET | 34 | Reset PA to default | None |
| VIEW_SYSTEM_STATUS | 35 | Show system status | None |
| TOGGLE_INPUT_SHAPER | 36 | Enable/disable shaper | Boolean (0=off, 1=on) |

### Visualization Module

The `visualization.py` module provides formatting functions:

```python
from visualization import (
    format_bed_mesh_grid,      # Mesh as text grid
    format_klipper_state,      # System status
    format_pressure_advance_info,  # PA with context
    format_input_shaper_info,  # Shaper config
    format_file_metadata,      # File details
    format_system_stats        # MCU stats
)
```

All functions return formatted strings ready for LCD display.

---

## Future Enhancements (Roadmap)

### Phase 3: Z-Offset Wizard
- Step-by-step first layer calibration
- Paper test guidance
- Test square printing
- Save to config

### Phase 4: PA Tuning Wizard
- Generate tuning tower gcode
- Visual line comparison guide
- Automatic PA calculation
- Apply and save

### Phase 5: More Visualizations
- Temperature history graphs
- Print statistics tracking
- Filament usage totals

---

## Troubleshooting

### "No mesh data available"
**Cause**: Bed mesh hasn't been calibrated yet
**Solution**: Run `BED_MESH_CALIBRATE` from console or LCD

### "Error getting [data]"
**Cause**: Moonraker API connection issue
**Solution**:
- Check Moonraker is running: `systemctl status moonraker`
- Verify network connection
- Check config: `moonraker_host` and `moonraker_port` in KlipperLCD.cfg

### High MCU Temperature Warning
**Cause**: Raspberry Pi or MCU running hot
**Solution**:
- Check cooling - ensure case has ventilation
- Reduce overclock settings if applicable
- Monitor with `watch -n 1 vcgencmd measure_temp`

### Input Shaper Disabled After Toggle
**Cause**: No shaper configuration in Klipper
**Solution**: Run input shaper calibration first or manually configure in printer.cfg

---

## Tips for Beginners

### Bed Leveling
1. Heat bed to printing temperature before mesh calibration
2. Clean build surface
3. Run `BED_MESH_CALIBRATE`
4. Check mesh range - aim for < 0.1mm
5. If range > 0.2mm, manually adjust bed screws and repeat

### Pressure Advance
1. Start with 0.0 for direct drive, 0.4 for bowden
2. Print PA test pattern
3. Use quick adjust to fine-tune
4. Look for smooth corners without bulging or gaps
5. Save final value to printer.cfg when satisfied

### Input Shaper
- Leave ENABLED for best quality
- Only disable if you see surface artifacts
- Requires ADXL345 accelerometer for calibration
- Reduces ringing/ghosting significantly

### System Status
- Check after any Klipper error
- MCU temp should stay below 60°C normally
- "Error" state requires `FIRMWARE_RESTART` to clear
- Red status = action needed

---

## LCD Firmware Updates

To fully utilize these features, the LCD firmware (.tft file) needs new screens and buttons. Current implementation exposes features via:
- Console commands
- Programmatic events
- Main.py callbacks

LCD firmware updates coming in future release to add:
- "View Mesh" button in leveling menu
- System status indicator on main screen
- PA adjustment screen
- Input shaper toggle in settings

---

## Support & Feedback

These enhancements are designed to make Klipper more accessible from the LCD. If you have questions or suggestions:

1. Check this guide first
2. Review logs: `journalctl -u KlipperLCD.service -f`
3. Test features from console before LCD integration
4. Report issues with detailed error messages

Remember: This is Phase 1 of planned enhancements. Wizards and more advanced features coming in future updates!
