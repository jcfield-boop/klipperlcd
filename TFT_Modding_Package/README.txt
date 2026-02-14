===============================================================================
  Neptune 3 Pro LCD - Enhanced KlipperLCD TFT Modding Package
===============================================================================

WHAT'S IN THIS PACKAGE:

1. 20240129.tft          - Original firmware (BACKUP THIS!)
2. LCD_program.HMI       - DGUS Tool project file
3. STEP_BY_STEP.md       - Follow this first! Complete walkthrough
4. SCREEN_LAYOUTS.txt    - Exact coordinates and settings
5. TFT_FIRMWARE_GUIDE.md - Detailed reference guide
6. TFT_QUICK_START.md    - Quick reference once you know the process
7. README.txt            - This file

===============================================================================
QUICK START (30 seconds)
===============================================================================

Mac User (Transfer to Windows):
1. Copy this entire folder to USB drive
2. Move to Windows 7 laptop
3. Open STEP_BY_STEP.md and follow from "PHASE 1"

Windows User (Ready to Mod):
1. Install DGUS Tool (download from dwin-global.com)
2. Open STEP_BY_STEP.md
3. Start with "PHASE 2"

===============================================================================
WHAT YOU'RE CREATING
===============================================================================

You're adding 5 new screens to your Neptune 3 Pro LCD:

Screen 20: Bed Mesh Visualization
  - View mesh grid with min/max/range
  - Quality assessment
  - Refresh mesh data

Screen 21: System Status  <-- START HERE (EASIEST!)
  - Klipper state (Ready/Error)
  - MCU temperature
  - Error messages

Screen 22: Pressure Advance Control
  - View current PA value
  - Adjust with +/- buttons
  - Reset to default
  - Fine-tune while printing

Screen 23: Input Shaper Status
  - View X/Y shaper config
  - Enable/disable shaper
  - See frequencies

Screen 24: Calibration Tools Menu
  - Navigation hub
  - Access all new features
  - Link from main screen

===============================================================================
RECOMMENDATION: Start with Screen 21 (System Status)
===============================================================================

Why Screen 21 first?
- Simplest layout (one text area, two buttons)
- Easy to test (just tap "View Status")
- Builds confidence before complex screens
- Proves your setup works

Once Screen 21 works, add others in this order:
1. Screen 24 (Tools Menu) - navigation
2. Screen 20 (Bed Mesh) - most useful
3. Screen 22 (Pressure Advance) - fine-tuning
4. Screen 23 (Input Shaper) - advanced

===============================================================================
FILES YOU NEED
===============================================================================

BEFORE YOU START:
- Download DGUS Tool (Windows only)
- Install on Windows 7 laptop
- Have micro SD card ready (FAT32 formatted)

WHAT YOU'LL MODIFY:
- LCD_program.HMI (open in DGUS Tool)
- Create new screen background images (.bmp files)
- Add buttons and variables
- Generate new .tft file
- Flash to LCD

===============================================================================
HELPFUL TIPS
===============================================================================

1. BACKUP EVERYTHING
   - Keep original 20240129.tft safe
   - Save working versions as you progress
   - Name them: klipperlcd_v1.tft, klipperlcd_v2.tft, etc.

2. TEST INCREMENTALLY
   - Add one screen, flash, test
   - Don't add all 5 screens at once
   - Easier to debug if something breaks

3. USE THE CONSOLE FIRST
   - Before creating TFT, test features via console
   - Commands: SHOW_STATUS, SHOW_MESH, SHOW_PA
   - Proves backend works before modifying LCD

4. MONITOR LOGS
   - SSH into printer: ssh biqu@192.168.0.50
   - Watch logs: journalctl -u KlipperLCD.service -f
   - See events received from LCD buttons

5. KEEP NOTES
   - Document what screen IDs you use
   - Note which VP addresses are taken
   - Write down what works (for future reference)

===============================================================================
TROUBLESHOOTING QUICK REFERENCE
===============================================================================

"Update Failed" on LCD:
  - Reformat SD card as FAT32
  - Ensure .tft file is in ROOT (not in folder)
  - Try different SD card

Button doesn't work:
  - Check logs: journalctl -u KlipperLCD.service -f
  - Verify VP address 0x1001
  - Check event code matches (35 for status, etc.)

Text doesn't display:
  - Verify VP address matches (0x3100 for status)
  - Check text variable is "Read/Write" mode
  - Try different font

Screen is blank:
  - Check background .bmp is 480x320 pixels
  - Verify all .bmp files included in .tft
  - Try simpler background (solid color)

===============================================================================
SUPPORT & RESOURCES
===============================================================================

Documentation:
- STEP_BY_STEP.md     - Full walkthrough (read this!)
- SCREEN_LAYOUTS.txt  - Copy/paste coordinates
- TFT_FIRMWARE_GUIDE  - Deep dive reference

GitHub:
- https://github.com/jcfield-boop/klipperlcd
- Original: https://github.com/joakimtoe/KlipperLCD

Community:
- Klipper Discord
- Reddit r/klippers
- Elegoo user groups

===============================================================================
YOUR SETUP
===============================================================================

Printer: Elegoo Neptune 3 Pro
LCD: 480x320 DWIN T5L Touch Screen
Firmware: KlipperLCD Enhanced Fork
Controller: BTT CB1 / Raspberry Pi
OS: Armbian / Raspberry Pi OS

===============================================================================
TIME ESTIMATE
===============================================================================

First time through:
- Phase 1 (Setup): 30 minutes
- Phase 2 (Understanding): 30 minutes
- Phase 3 (Create Screen 21): 45 minutes
- Phase 4 (Add navigation): 15 minutes
- Phase 5 (Build & test): 30 minutes
Total: ~2.5 hours

After you know the process:
- Add new screen: 15-30 minutes
- Test and iterate: 15 minutes
Total: ~30-45 minutes per screen

===============================================================================
GETTING STARTED NOW
===============================================================================

1. Copy this folder to: C:\Neptune3Pro_LCD\
2. Open STEP_BY_STEP.md (use Notepad or Markdown viewer)
3. Follow instructions starting at "PHASE 1"
4. Have fun! You're adding pro features to your printer! 🚀

Questions? Check the troubleshooting sections in the guides first.

Good luck!
===============================================================================
