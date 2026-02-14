# KlipperLCD TFT Firmware Modification Guide

## Overview
This guide explains how to modify the Neptune 3 Pro LCD firmware (.tft file) using DWIN's DGUS Tool to add buttons and screens for the enhanced KlipperLCD features (bed mesh visualization, pressure advance controls, system status, etc.).

## Prerequisites

### Required Software
- **DGUS Tool** (DWIN screen editor - Windows only)
  - Download from DWIN website or request from LCD manufacturer
  - Compatible with Windows 7, 8, 10, 11
  - Version 7.6.1.5 or newer recommended

### Required Hardware
- Windows 7 (or newer) computer
- Micro SD card (FAT32 formatted, 1-32GB)
- Neptune 3 Pro LCD screen
- Original LCD firmware files as backup

### Required Knowledge
- Basic understanding of touch screen coordinates
- Familiarity with the Neptune 3 Pro LCD interface
- Understanding of the event system (Event IDs 30-36)

## Understanding the Event System

KlipperLCD communicates with the LCD via event codes. The enhanced features use these event IDs:

| Event | ID | Purpose | Data Type |
|-------|----|---------|-----------|
| VIEW_MESH | 30 | Display bed mesh visualization | None |
| MESH_PROFILE_SELECT | 31 | Load mesh profile | String (profile name) |
| FIRMWARE_RESTART | 32 | Restart Klipper firmware | None |
| PA_ADJUST | 33 | Adjust Pressure Advance | Float (adjustment amount) |
| PA_RESET | 34 | Reset PA to default | None |
| VIEW_SYSTEM_STATUS | 35 | Show system status & MCU temp | None |
| TOGGLE_INPUT_SHAPER | 36 | Enable/disable Input Shaper | Boolean (0/1) |

## DGUS Tool Project Structure

The Neptune 3 Pro LCD firmware consists of:

1. **Screen Files (.bmp images)** - Background images for each screen
2. **Font Files (.HZK/.BIN)** - Character sets for text display
3. **Icon Library (.ICL)** - Button icons and graphics
4. **Configuration File (13.bin or T5L.CFG)** - Screen definitions and variables
5. **DGUS_SET file** - DGUS Tool project settings

## Step-by-Step Modification

### Step 1: Backup Original Firmware

1. If you haven't already, **save your current working .tft file** (e.g., `20240125.tft`)
2. Copy it to a safe location as backup
3. Extract the .tft file (it's a renamed .zip archive):
   - Rename `20240125.tft` to `20240125.zip`
   - Extract to a working folder (e.g., `C:\Neptune3Pro_LCD\`)

### Step 2: Install and Open DGUS Tool

1. Install DGUS Tool on your Windows 7 machine
2. Launch DGUS Tool
3. Click **"Open Project"** or **"New Project"**
4. If opening existing: Navigate to extracted firmware folder and open `DGUS_SET` file
5. If creating new: Select **T5L** or **DMG** series (check your LCD model - Neptune 3 Pro typically uses T5L)

### Step 3: Understand Current Screen Layout

The Neptune 3 Pro LCD typically has these screens:
- **Boot Screen** (startup logo)
- **Main Screen** (temperature, status, navigation)
- **Print Screen** (active print monitoring)
- **Settings Screen** (configuration options)
- **File Browser** (gcode file selection)
- **Console Screen** (command input/output)
- **Leveling/Probe Screen** (bed leveling tools)

**Important:** Document which screen IDs are currently used before adding new ones.

### Step 4: Design New Screens

We'll add screens for:

#### A. **Bed Mesh Screen** (Recommended Screen ID: 20)

**Purpose:** Display bed mesh visualization and statistics

**Layout:**
```
┌─────────────────────────────┐
│   Bed Mesh Visualization    │  (Title text)
├─────────────────────────────┤
│                             │
│   [Mesh grid text area]     │  (Text variable showing formatted mesh)
│   [Min/Max/Range values]    │
│   [Quality assessment]      │
│                             │
├─────────────────────────────┤
│  [Load Profile] [Refresh]   │  (Buttons)
│  [Back]                     │
└─────────────────────────────┘
```

**Variables to add:**
- **Text Display VP Address 0x3000** (Read/Write, Text type)
  - Size: 40x20 characters
  - For displaying mesh grid

**Buttons to add:**
- **Refresh Button** - Sends Event 30 (VIEW_MESH)
  - Touch area: Define coordinates
  - Action: Send data to 0x1001 value=30

- **Back Button** - Returns to previous screen
  - Touch area: Define coordinates
  - Action: Jump to screen (Main or Settings)

#### B. **System Status Screen** (Recommended Screen ID: 21)

**Purpose:** Show Klipper state and MCU temperature

**Layout:**
```
┌─────────────────────────────┐
│      System Status          │  (Title)
├─────────────────────────────┤
│                             │
│  Klipper State: [Ready]     │  (Variable display)
│  MCU Temp: [45.2°C]         │  (Variable display)
│                             │
│  [Error message area]       │  (Conditional display)
│                             │
├─────────────────────────────┤
│  [Firmware Restart] [Back]  │  (Buttons)
└─────────────────────────────┘
```

**Variables to add:**
- **Text Display VP Address 0x3100** (Read/Write, Text type)
  - For system status output

**Buttons to add:**
- **View Status Button** - Sends Event 35 (VIEW_SYSTEM_STATUS)
  - Action: Send data to 0x1001 value=35

- **Firmware Restart Button** - Sends Event 32 (FIRMWARE_RESTART)
  - Action: Send data to 0x1001 value=32
  - **Warning:** Should show confirmation popup

#### C. **Pressure Advance Screen** (Recommended Screen ID: 22)

**Purpose:** Display and adjust PA value

**Layout:**
```
┌─────────────────────────────┐
│    Pressure Advance         │
├─────────────────────────────┤
│  Current PA: 0.0350         │  (Variable display)
│                             │
│  Typical Ranges:            │
│    Bowden: 0.3 - 0.7        │
│    Direct: 0.02 - 0.1       │
├─────────────────────────────┤
│  [-0.01] [-0.001]           │  (Adjustment buttons)
│  [+0.001] [+0.01]           │
│                             │
│  [Reset]  [Back]            │
└─────────────────────────────┘
```

**Variables to add:**
- **Text Display VP Address 0x3200** (Read/Write, Text type)
  - For PA info display

**Buttons to add:**
- **-0.01 Button** - Sends Event 33 with data=-0.01
  - Action: Send data to 0x1001 value=33, then send -0.01 to data VP

- **-0.001 Button** - Sends Event 33 with data=-0.001

- **+0.001 Button** - Sends Event 33 with data=+0.001

- **+0.01 Button** - Sends Event 33 with data=+0.01

- **Show PA Button** - Requests PA display
  - This would send console command or trigger PA display

- **Reset Button** - Sends Event 34 (PA_RESET)

#### D. **Input Shaper Screen** (Recommended Screen ID: 23)

**Purpose:** View and toggle Input Shaper

**Layout:**
```
┌─────────────────────────────┐
│     Input Shaper            │
├─────────────────────────────┤
│  Status: ENABLED            │  (Variable display)
│                             │
│  X-axis: MZV @ 42.5 Hz      │
│  Y-axis: MZV @ 38.2 Hz      │
│                             │
├─────────────────────────────┤
│  [Enable]  [Disable]        │  (Toggle buttons)
│  [Back]                     │
└─────────────────────────────┘
```

**Variables to add:**
- **Text Display VP Address 0x3300** (Read/Write, Text type)
  - For shaper config display

**Buttons to add:**
- **Enable Button** - Sends Event 36 with data=1
  - Action: Send data to 0x1001 value=36, then send 1 to data VP

- **Disable Button** - Sends Event 36 with data=0

### Step 5: Add Navigation Buttons to Existing Screens

**To Main Screen:**
Add buttons to access new features:

- **"Calibration" or "Tools" Button**
  - Jump to a new Tools Menu screen (Screen ID: 24)

**To Settings Screen:**
Add buttons for:
- **System Status** - Jump to Screen 21
- **Input Shaper** - Jump to Screen 23

**New Tools Menu Screen (ID: 24):**
```
┌─────────────────────────────┐
│      Calibration Tools      │
├─────────────────────────────┤
│                             │
│  [Bed Mesh]                 │  -> Screen 20
│  [Pressure Advance]         │  -> Screen 22
│  [System Status]            │  -> Screen 21
│  [Input Shaper]             │  -> Screen 23
│                             │
│  [Back]                     │
└─────────────────────────────┘
```

### Step 6: DGUS Tool Implementation

#### Creating a New Screen

1. **In DGUS Tool Project:**
   - Click **"Add Screen"** or duplicate existing screen
   - Assign Screen ID (e.g., 20 for Bed Mesh)
   - Set screen size (typically 480x320 for Neptune 3 Pro)

2. **Create Background Image:**
   - Use image editing software (Photoshop, GIMP, Paint.NET)
   - Create 480x320 pixel BMP image
   - Design screen layout with text labels and button areas
   - Save as `20.bmp` (matching screen ID)
   - Import into DGUS Tool project

3. **Add Text Display Variable:**
   - Click **"Add Variable Display"**
   - Set Type: **Text**
   - Set VP Address: **0x3000** (or next available)
   - Set position on screen (X, Y coordinates)
   - Set size (character width/height)
   - Set font (select from loaded fonts)
   - Configure as **Read/Write**

4. **Add Touch Buttons:**
   - Click **"Add Touch Control"**
   - Draw touch area on screen
   - Set Action Type:
     - **Return Key Code** for sending events
     - **Jump Screen** for navigation

   For Event Buttons:
   - Action: **Return Key Code**
   - Key Code VP Address: **0x1001** (common event address)
   - Key Value: **30** (for VIEW_MESH event)

   For Navigation Buttons:
   - Action: **Jump Screen**
   - Target Screen ID: (e.g., 0 for main screen)

5. **Configure Event Data (for PA_ADJUST):**
   - Some events need numeric data (like adjustment amount)
   - Add hidden numeric variable VP (e.g., 0x3201)
   - Button writes value to this VP, then triggers event
   - KlipperLCD reads both event code and data VP

#### Button Action Examples in DGUS Tool

**Simple Event Button (VIEW_MESH):**
```
Touch Area: X=10, Y=250, Width=100, Height=40
Action Type: Return Key Code
VP Address: 0x1001
Key Value: 30
```

**Navigation Button (Back to Main):**
```
Touch Area: X=370, Y=250, Width=100, Height=40
Action Type: Jump Screen
Target Screen: 0 (Main screen ID)
```

**Adjustment Button (PA +0.001):**
```
Touch Area: X=200, Y=150, Width=60, Height=40
Action 1: Write Data - VP=0x3201, Value=0.001 (as hex)
Action 2: Return Key Code - VP=0x1001, Value=33
```

### Step 7: Build and Generate TFT File

1. **Save Project** in DGUS Tool

2. **Generate Configuration:**
   - Click **"Generate"** or **"Build"** button
   - DGUS Tool creates **13.bin** and **T5LCFG.txt** files

3. **Collect All Files:**
   - Ensure all necessary files are in DWIN_SET folder:
     - `13.bin` (or `T5L.CFG`)
     - `0.bmp`, `1.bmp`, `2.bmp`... (all screen backgrounds)
     - `20.bmp`, `21.bmp`, `22.bmp`, `23.bmp`, `24.bmp` (new screens)
     - Font files (`.HZK`, `.BIN`)
     - Icon library (`.ICL`)

4. **Create TFT File:**
   - Select all files in DWIN_SET folder
   - Create ZIP archive
   - Rename from `.zip` to `.tft`
   - Name it descriptively: `klipperlcd_enhanced.tft`

### Step 8: Flash TFT to LCD

1. **Prepare SD Card:**
   - Format micro SD card as FAT32
   - Copy `klipperlcd_enhanced.tft` to root of SD card

2. **Flash LCD:**
   - Power off Neptune 3 Pro LCD
   - Insert SD card into LCD (back cover must be removed)
   - Power on LCD
   - Wait for "Update Successed!" message
   - Power off and remove SD card

3. **Test New Features:**
   - Power on LCD
   - Navigate to new screens
   - Test each button
   - Monitor KlipperLCD service logs: `journalctl -u KlipperLCD.service -f`

## Troubleshooting

### "Update Failed" on LCD
- Ensure SD card is FAT32 formatted
- Ensure .tft file is in root directory (not in subfolder)
- Try different SD card (some LCDs are picky)
- Verify .tft file is properly formatted ZIP archive

### Buttons Don't Trigger Events
- Check VP address matches in DGUS Tool (0x1001 recommended)
- Verify event ID values (30-36 for new features)
- Check KlipperLCD logs for received events
- Ensure touch area coordinates are correct

### Text Not Displaying
- Verify VP address is correctly configured in DGUS Tool
- Check text variable is set to Read/Write mode
- Ensure font files are included in .tft
- Check character encoding matches (ASCII vs UTF-8)

### Screen Shows Garbled Graphics
- Verify .bmp files are correct resolution (480x320)
- Ensure .bmp files are in correct color depth (typically 16-bit or 24-bit)
- Check screen ID numbering doesn't conflict

## Advanced: Using Console Shortcuts (Immediate Solution)

While creating custom TFT firmware, you can use console shortcuts NOW:

**Available Commands:**
- `SHOW_MESH` - View bed mesh
- `SHOW_STATUS` - System status
- `SHOW_PA` - Pressure Advance info
- `SHOW_SHAPER` - Input Shaper config
- `PA_ADJUST 0.001` - Adjust PA up by 0.001
- `PA_ADJUST -0.01` - Adjust PA down by 0.01
- `PA_RESET` - Reset PA to 0.0
- `HELP_LCD` - Show command list

**How to Use:**
1. On LCD, tap center top of main screen to open console
2. Type command (use on-screen keyboard)
3. View results in console output area

## VP Address Reference

Suggested VP addresses for new features (verify availability in your firmware):

| Feature | VP Address | Type | Size | Purpose |
|---------|-----------|------|------|---------|
| Event Code | 0x1001 | Word | 2 bytes | Event ID (30-36) |
| Mesh Display | 0x3000 | Text | 800 bytes | Mesh grid text |
| Status Display | 0x3100 | Text | 400 bytes | System status |
| PA Display | 0x3200 | Text | 400 bytes | PA info |
| PA Adjustment | 0x3201 | Float | 4 bytes | Adjustment value |
| Shaper Display | 0x3300 | Text | 400 bytes | Shaper info |
| Shaper Toggle | 0x3301 | Word | 2 bytes | Enable/disable flag |

## Resources

- **DWIN DGUS Tool:** Contact DWIN or LCD supplier
- **Neptune 3 Pro LCD Specs:** Elegoo support documentation
- **KlipperLCD GitHub:** https://github.com/jcfield-boop/klipperlcd
- **Moonraker API Docs:** https://moonraker.readthedocs.io/

## Next Steps After TFT Creation

1. Test all new screens and buttons
2. Share your custom .tft with the community
3. Consider contributing back to KlipperLCD repo
4. Document any screen layout improvements
5. Plan Phase 2 enhancements (wizards, more visualizations)

## Support

If you create a working enhanced .tft file:
- Consider sharing it in the KlipperLCD discussions
- Document your screen layout for others
- Report any issues with event handling

Good luck with your TFT modding! The console shortcuts will get you started immediately while you work on the full UI integration.
