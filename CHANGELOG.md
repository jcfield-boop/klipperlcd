# KlipperLCD Changelog

## [Unreleased]

### Fixed
- **TJC4B25C12785 display stuck on "Waiting for KlipperLCD.service..."**: Added `main.va0.val=1` handshake command to the boot sequence immediately after `com_star`. The TJC TFT firmware requires this flag to be set before it will accept page-switch or variable commands. Without it the display remained on the waiting screen despite all serial writes succeeding.

## [Unreleased] - Enhanced Features Edition

### Added - Phase 1: Enhanced Features (Backend)

#### New PrinterData Methods
- `get_klipper_state()` - Query Klipper state (Ready/Error/Shutdown)
- `get_mcu_stats()` - Retrieve MCU temperature and statistics
- `firmware_restart()` - Restart Klipper firmware
- `get_bed_mesh_data()` - Retrieve bed mesh with min/max/range analysis
- `get_mesh_profiles()` - List saved mesh profiles
- `load_mesh_profile(name)` - Load specific mesh profile
- `get_pressure_advance()` - Get current PA value
- `set_pressure_advance(value)` - Set PA value immediately
- `get_input_shaper_config()` - Get shaper type and frequencies
- `toggle_input_shaper(enabled)` - Enable/disable input shaper
- `get_file_metadata(filename)` - Get slicer metadata for gcode files

#### New Visualization Module (`visualization.py`)
- `format_bed_mesh_grid()` - Text-based bed mesh visualization
- `format_klipper_state()` - System status formatting
- `format_pressure_advance_info()` - PA display with typical ranges
- `format_input_shaper_info()` - Shaper configuration display
- `format_file_metadata()` - File information formatting
- `format_system_stats()` - MCU statistics formatting

#### New LCD Events
- Event 30: `VIEW_MESH` - Display bed mesh visualization
- Event 31: `MESH_PROFILE_SELECT` - Load mesh profile
- Event 32: `FIRMWARE_RESTART` - Restart Klipper
- Event 33: `PA_ADJUST` - Adjust Pressure Advance
- Event 34: `PA_RESET` - Reset PA to configured default
- Event 35: `VIEW_SYSTEM_STATUS` - Show system status
- Event 36: `TOGGLE_INPUT_SHAPER` - Enable/disable shaper

#### Console Shortcuts (Immediate Access)
Users can now access enhanced features via console commands:
- `SHOW_MESH` - Display bed mesh with quality assessment
- `SHOW_STATUS` - View Klipper state and MCU temperature
- `SHOW_PA` - Show Pressure Advance info and typical ranges
- `SHOW_SHAPER` - Display Input Shaper configuration
- `PA_ADJUST <value>` - Fine-tune PA (e.g., `PA_ADJUST 0.001`)
- `PA_RESET` - Reset to configured default PA
- `HELP_LCD` - Show all available shortcuts

All shortcuts are case-insensitive and work alongside standard GCode.

#### Configuration Enhancements

**New `[features]` Section:**
```ini
[features]
# Default Pressure Advance value (PA_RESET returns here)
default_pa = 0.0

# Enable/disable console shortcuts
enable_console_shortcuts = true
```

**Enhanced Config Generation:**
- Comprehensive beginner-friendly comments (~250 lines)
- Detailed explanations for every setting
- Troubleshooting tips included
- Common value examples
- Material-specific guidance

#### Documentation

**New Documents:**
- `FEATURES.md` - Complete features guide with examples
- `TFT_FIRMWARE_GUIDE.md` - Comprehensive DGUS Tool guide
- `TFT_QUICK_START.md` - Fast-track TFT modding guide
- `CHANGELOG.md` - This file

**Updated Documents:**
- `README.md` - Added console shortcuts section
- `KlipperLCD.cfg` - Now includes [features] section

### Enhanced - Existing Features

#### Configuration System
- Auto-generation of config file on first run
- Config file visible in Mainsail (Machine tab)
- Preserves user settings across updates
- Validation and helpful error messages

#### Installation
- Automated dependency checking and installation
- Auto-detects username and paths
- One-command installation via `install.sh`
- Service management integrated

### Technical Details

#### Architecture Changes
- Event-driven callback system for new features
- Visualization layer separate from business logic
- Configuration-driven defaults (not hardcoded)
- Backward compatible with existing LCD firmware

#### API Integration
- Direct Moonraker REST API usage
- Klipper object query support
- Metadata extraction from gcode files
- Real-time printer state monitoring

### For TFT Firmware Modders

#### Screen Layout Specifications
Detailed specifications for 5 new screens:
- Screen 20: Bed Mesh Visualization
- Screen 21: System Status
- Screen 22: Pressure Advance Control
- Screen 23: Input Shaper Configuration
- Screen 24: Calibration Tools Menu

#### VP Address Mappings
```
Event Code:        0x1001 (Word)
Mesh Display:      0x3000 (Text, 800 bytes)
Status Display:    0x3100 (Text, 400 bytes)
PA Display:        0x3200 (Text, 400 bytes)
PA Adjustment:     0x3201 (Float, 4 bytes)
Shaper Display:    0x3300 (Text, 400 bytes)
Shaper Toggle:     0x3301 (Word, 2 bytes)
```

#### DGUS Tool Instructions
- Complete step-by-step screen creation guide
- Button configuration examples
- Touch area coordinate specifications
- Build and flash procedures
- Troubleshooting common issues

### Usage Examples

#### Bed Mesh Visualization
```
> SHOW_MESH
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

#### Pressure Advance Tuning
```
> SHOW_PA
Pressure Advance: 0.0350

Typical ranges:
  Bowden: 0.3 - 0.7
  Direct Drive: 0.02 - 0.1

Status: Typical for direct drive

> PA_ADJUST 0.001
Pressure Advance adjusted to: 0.0360
```

#### System Status Check
```
> SHOW_STATUS
System Status:
Ready

MCU Temp: 45.2°C
```

### Migration Guide

#### For Existing Users

**No Action Required!**
- Existing `KlipperLCD.cfg` files work unchanged
- New `[features]` section auto-added with defaults
- All existing functionality preserved
- Update via `git pull` in KlipperLCD directory

**Optional: Regenerate Config**
To get new comments and [features] section:
```bash
cd ~/KlipperLCD
python3 main.py --generate-config ~/printer_data/config/KlipperLCD.cfg.new
# Review differences, merge if desired
```

#### For New Users

Run the automated installer:
```bash
cd ~/KlipperLCD
chmod +x install.sh
./install.sh
```

Config file automatically generated at `~/printer_data/config/KlipperLCD.cfg`

### Roadmap - Future Phases

#### Phase 2: Wizards (Planned)
- Z-Offset Calibration Wizard
- Pressure Advance Tuning Wizard
- First Layer Calibration Guide

#### Phase 3: Advanced Visualizations (Planned)
- Temperature history graphs
- Print statistics tracking
- Filament usage totals

#### Phase 4: Community
- Share custom .tft firmware files
- Community-contributed screen layouts
- Translation support

### Known Limitations

- Custom LCD firmware (buttons) requires DGUS Tool (Windows only)
- Console shortcuts available immediately
- TFT modding is optional (console provides full access)
- Input Shaper calibration still requires ADXL345 accelerometer

### Credits

**Original KlipperLCD:** [joakimtoe/KlipperLCD](https://github.com/joakimtoe/KlipperLCD)

**Enhanced Features Fork:** [jcfield-boop/klipperlcd](https://github.com/jcfield-boop/klipperlcd)

**Contributors:**
- Configuration abstraction and enhanced features
- Console shortcuts implementation
- TFT firmware documentation
- Beginner-friendly config comments

### Support

**Documentation:**
- `README.md` - Installation and basic usage
- `FEATURES.md` - Complete features guide
- `TFT_FIRMWARE_GUIDE.md` - Custom firmware creation
- `TFT_QUICK_START.md` - Fast-track modding

**Getting Help:**
1. Check logs: `journalctl -u KlipperLCD.service -f`
2. Review config: `~/printer_data/config/KlipperLCD.cfg`
3. Test console shortcuts: Type `HELP_LCD` in console
4. Check Moonraker: `systemctl status moonraker`

**Reporting Issues:**
- Include KlipperLCD service logs
- Include config file (redact API keys)
- Describe expected vs actual behavior
- Note which feature is affected

---

## Version History

### v2.0.0-enhanced (Current)
- Complete configuration abstraction
- Enhanced features backend (bed mesh, PA, shaper, status)
- Console shortcuts for immediate access
- TFT firmware modding documentation
- Beginner-friendly configuration

### v1.0.0 (Original - joakimtoe)
- Neptune 3 Pro LCD support
- Basic Klipper integration
- Thumbnail support
- Console functionality
- Material presets
