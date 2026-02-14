# Step-by-Step TFT Firmware Modding Guide
## For Neptune 3 Pro LCD - Enhanced KlipperLCD Features

**What You're Creating:** Custom LCD firmware with buttons to access bed mesh, pressure advance, and system status features.

**Time Required:** 1-2 hours for first time (30min once you know the process)

**Difficulty:** Beginner-friendly (if you follow the steps!)

---

## PHASE 1: Setup on Windows 7 Laptop

### Step 1.1: Get DGUS Tool

**Download DGUS Tool:**
- Official source: http://www.dwin-global.com/download/
- Look for "DGUS Tool V7.621" or newer
- Alternative: Search for "DWIN DGUS Tool download"

**Install DGUS Tool:**
1. Extract the downloaded ZIP
2. Run `DGUS_Tool_Setup.exe`
3. Follow installation wizard
4. Default install path is fine: `C:\DGUS_Tool\`

### Step 1.2: Copy Files to Windows

Transfer this entire folder to your Windows 7 laptop (USB drive):
- `20240129.tft` - Original firmware (BACKUP!)
- `LCD_program.HMI` - DGUS project file
- `TFT_FIRMWARE_GUIDE.md` - Full reference
- `TFT_QUICK_START.md` - Quick reference
- `STEP_BY_STEP.md` - This file

**On Windows 7:**
1. Create folder: `C:\Neptune3Pro_LCD\`
2. Copy all files there
3. **Make a backup copy of 20240129.tft!**

### Step 1.3: Extract the TFT Firmware

The `.tft` file is actually a DWIN proprietary container. DGUS Tool can read it directly!

**Option A: Open HMI Project File (RECOMMENDED)**
1. Launch DGUS Tool
2. File → Open Project
3. Navigate to `C:\Neptune3Pro_LCD\`
4. Select `LCD_program.HMI`
5. DGUS Tool will load the entire project!

**Option B: If HMI file doesn't work**
The .tft file contains compiled firmware. You'll need to:
1. Contact Elegoo support for source files
2. OR reverse engineer (advanced, not recommended)
3. OR work with what we have in the HMI file

---

## PHASE 2: Understanding Current Screen Layout

### Step 2.1: Explore Existing Screens

Once DGUS Tool is open:

**Left Panel: Screen List**
- You'll see numbered screens (0, 1, 2, 3, etc.)
- Each screen is a separate LCD page

**What to Look For:**
- Screen 0: Usually main/boot screen
- Screen 1-5: Main interface, printing, files
- Screen 10+: Settings, menus

**Take Notes:**
- Highest screen number used: ________
- Which screens are for what: ________

**TIP:** Our new screens will start at ID 20 to avoid conflicts!

### Step 2.2: Check Current VP Addresses

**View → Variable List** (or similar menu)
- This shows all Variable Pointer (VP) addresses in use
- VP addresses are like memory addresses the LCD uses

**What to Check:**
- Is 0x1001 used? (common event address)
- Are 0x3000-0x3400 free? (we need these)

**If addresses are taken:** Add 0x1000 to our recommended addresses
- Example: Use 0x4000 instead of 0x3000

---

## PHASE 3: Create Your First Enhanced Screen

### **RECOMMENDATION: Start with System Status Screen (Easiest!)**

We'll create a simple screen to show Klipper status and MCU temperature.

### Step 3.1: Create New Screen

**In DGUS Tool:**
1. Right-click in screen list → **Add Screen** (or File → New Screen)
2. Screen ID: **21** (System Status)
3. Screen Size: **480x320** (Neptune 3 Pro standard)
4. Click OK

You now have a blank screen!

### Step 3.2: Create Background Image

**On Windows:**
1. Open Paint (or any image editor)
2. Create new image: 480 x 320 pixels
3. Fill with background color (black or dark gray recommended)
4. Add text labels:
   ```
   Y=10:  "System Status"  (title)
   Y=280: "[ View Status ] [ Back ]"  (button labels)
   ```
5. Save as: `C:\Neptune3Pro_LCD\21.bmp`

**TIP:** Keep it simple! The background is just visual design. Real data comes from variables.

### Step 3.3: Import Background to DGUS Tool

**In DGUS Tool:**
1. Double-click Screen 21 (to open it)
2. Look for **"Background Image"** or **"Set Background"** option
3. Browse to `21.bmp`
4. Click OK

Your screen now has the background!

### Step 3.4: Add Text Display Variable

This is where the magic happens - this displays data FROM KlipperLCD.

**In DGUS Tool:**
1. Find **"Add Control"** or toolbar with icons
2. Select **"Text Variable"** or **"Variable Display"**
3. Click and drag on the screen to create a text box
   - Position: X=10, Y=40
   - Size: About 450 pixels wide, 200 pixels tall

**Configure the Text Variable:**
- **VP Address:** `0x3100` (System Status VP)
- **Type:** Text / ASCII String
- **Display Mode:** Read/Write or Display
- **Font:** Select a readable font (usually "ASCII_32" or similar)
- **Max Characters:** 200 (enough for status text)
- **Background:** Transparent or match screen background
- **Text Color:** White or bright color

**Click OK to save**

### Step 3.5: Add "View Status" Button

**Add Touch Button:**
1. Select **"Touch Control"** or **"Button"** tool
2. Draw a button area where you wrote "[ View Status ]"
   - Position: X=10, Y=270
   - Size: Width=200, Height=40

**Configure Button Action:**
- **Action Type:** Return Key Code (or Send Event/Data)
- **VP Address:** `0x1001` (Event code address)
- **Key Value:** `35` (VIEW_SYSTEM_STATUS event)

**Click OK**

### Step 3.6: Add "Back" Button

**Add Navigation Button:**
1. Add another Touch Control
2. Draw button where you wrote "[ Back ]"
   - Position: X=270, Y=270
   - Size: Width=200, Height=40

**Configure Back Button:**
- **Action Type:** Jump Screen
- **Target Screen:** `0` (main screen - adjust if different)

**Click OK**

---

## PHASE 4: Add Navigation to Existing Screens

Your new screen is ready, but you need a way to GET to it!

### Step 4.1: Find the Settings or Main Screen

**In DGUS Tool:**
1. Look through screens to find "Settings" or "Menu" screen
2. Common screen IDs: 3, 4, 5, 10
3. Look for a screen with existing buttons

### Step 4.2: Add "System Status" Button

**On the settings screen:**
1. Find empty space for a new button
2. Add Touch Control
3. Draw button area

**Configure:**
- **Action Type:** Jump Screen
- **Target Screen:** `21` (your System Status screen)

**Optional:** Add icon or text label to the background image for this button

---

## PHASE 5: Build and Test

### Step 5.1: Generate Firmware Files

**In DGUS Tool:**
1. **File → Generate** (or similar - might be called "Build" or "Compile")
2. DGUS Tool will create configuration files
3. Look for output folder (usually same folder as project)

**Expected Output Files:**
- `13.bin` or `T5L.CFG` (main config)
- `*.bmp` files (all screen images)
- Other `.BIN` or `.HZK` font files

### Step 5.2: Create TFT File

**Important:** The .tft file is a container for all these files.

**Method 1: DGUS Tool Export (if available)**
- Look for **File → Export → TFT File**
- Or **Tools → Create TFT Package**

**Method 2: Manual ZIP Method**
1. Select ALL generated files in the output folder:
   - 13.bin (or T5L.CFG)
   - All .bmp files (0.bmp, 1.bmp, 21.bmp, etc.)
   - All font files (.HZK, .BIN)
   - Any .ICL icon library files
2. Create ZIP archive (right-click → Send to → Compressed folder)
3. Rename `archive.zip` → `klipperlcd_enhanced_v1.tft`

**CRITICAL:** Files must be in the ROOT of the ZIP, NOT in a subfolder!

### Step 5.3: Test on LCD

**Prepare SD Card:**
1. Format micro SD card as **FAT32**
   - Right-click drive → Format → FAT32
   - Allocation size: Default
2. Copy `klipperlcd_enhanced_v1.tft` to SD card ROOT
3. Safely eject SD card

**Flash LCD:**
1. **Power OFF** Neptune 3 Pro completely
2. Remove LCD back cover (4 screws)
3. Insert SD card into LCD's micro SD slot
4. **Power ON** LCD
5. LCD will show update progress
6. Wait for **"Update Successed!"** message
7. **Power OFF**, remove SD card
8. **Power ON** to test

### Step 5.4: Test the New Feature

**On LCD:**
1. Navigate to Settings (or wherever you added the button)
2. Tap "System Status" button
3. You should jump to Screen 21
4. Tap "View Status" button
5. This sends Event 35 to KlipperLCD

**On Printer (via SSH):**
```bash
# Watch KlipperLCD logs
journalctl -u KlipperLCD.service -f
```

**Expected:**
- Log shows: "Received event 35"
- LCD screen shows: "System Status: Ready" and "MCU Temp: XX.X°C"

**If nothing happens:**
- Check logs for errors
- Verify VP address 0x1001 is correct
- Verify event value 35 is sent

---

## PHASE 6: Add More Screens (Once First One Works!)

### Screen Priority Order:

1. ✅ **System Status** (Screen 21) - Just completed!
2. **Tools Menu** (Screen 24) - Navigation hub
3. **Bed Mesh** (Screen 20) - Most useful feature
4. **Pressure Advance** (Screen 22) - Fine-tuning
5. **Input Shaper** (Screen 23) - Advanced

### Quick Reference for Next Screens:

**Screen 20: Bed Mesh**
- VP Address: 0x3000 (text display)
- Event: 30 (VIEW_MESH)
- Large text area needed (40x20 chars)

**Screen 22: Pressure Advance**
- VP Address: 0x3200 (text display)
- VP Address: 0x3201 (adjustment value - float)
- Events: 33 (PA_ADJUST), 34 (PA_RESET)
- Multiple buttons for +/- adjustments

**Screen 24: Tools Menu**
- Just navigation buttons
- Jump to screens 20, 21, 22, 23

---

## Troubleshooting

### "Update Failed" on LCD
- **Cause:** SD card format or file structure
- **Fix:**
  - Reformat SD as FAT32
  - Ensure .tft file in ROOT of SD
  - Try different SD card
  - Check file size < 32MB

### Button Does Nothing
- **Cause:** Wrong VP address or event code
- **Fix:**
  - Check logs: `journalctl -u KlipperLCD.service -f`
  - Verify VP 0x1001 is used
  - Verify event value matches (35 for status)
  - Check button action type is "Return Key Code"

### Text Not Showing
- **Cause:** VP mismatch or font issue
- **Fix:**
  - Verify VP 0x3100 matches in DGUS Tool and code
  - Check text variable is "Read/Write" mode
  - Verify font files included in .tft
  - Try different font

### Screen is Garbled
- **Cause:** BMP resolution mismatch
- **Fix:**
  - Verify ALL .bmp files are 480x320
  - Check color depth (16-bit or 24-bit)
  - Regenerate background images

### Can't Open HMI File
- **Cause:** DGUS Tool version mismatch
- **Fix:**
  - Try newer DGUS Tool version
  - Try opening directly from DGUS Tool (File → Open)
  - Check file isn't corrupted (re-copy from Mac)

---

## Next Steps After Success

### Share Your Work!
- Post your custom .tft file to KlipperLCD discussions
- Share screenshots of your screen layouts
- Help other users with TFT modding

### Enhance Further:
- Add custom icons to buttons
- Create better-looking backgrounds
- Add more features from FEATURES.md
- Implement wizards (Phase 2 features)

### Learn More:
- Read `TFT_FIRMWARE_GUIDE.md` for detailed VP address mappings
- Study DGUS Tool documentation
- Join DWIN / Neptune 3 Pro communities

---

## Quick Command Reference

**Test features via console (while building TFT):**
```
SHOW_STATUS    # Test if backend works
SHOW_MESH      # View bed mesh
HELP_LCD       # See all commands
```

**Monitor logs on printer:**
```bash
journalctl -u KlipperLCD.service -f
```

**Restart service after config changes:**
```bash
sudo systemctl restart KlipperLCD.service
```

---

## Contact & Support

**You're working on:**
- Neptune 3 Pro LCD (480x320 DWIN T5L screen)
- KlipperLCD Enhanced Fork
- Adding 5 new feature screens

**If stuck:**
1. Check logs first
2. Re-read relevant section of this guide
3. Check `TFT_FIRMWARE_GUIDE.md` for details
4. Test features via console first (to verify backend works)

**Remember:**
- Start simple (one screen at a time)
- Test often (flash after each screen)
- Keep backups (original .tft, working versions)
- Document what works (for future reference)

Good luck! You're adding professional-grade features to your LCD! 🚀
