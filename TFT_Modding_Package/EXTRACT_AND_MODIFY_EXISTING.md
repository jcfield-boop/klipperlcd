# Extract and Modify Existing DWIN Firmware

## Goal: Edit the 20240129.tft file and add new screens to it

## The Challenge

The `.tft` file is **compiled/binary format**. To edit it, we need to:
1. Extract/decompile it to source files
2. Edit the source files (add screens)
3. Recompile to new .tft

## Tools to Try

### Option 1: DWIN DGUS SDK/Tools

**Try different DGUS Tool versions:**

Some .tft files only work with specific DGUS Tool versions.

**Download multiple versions:**
1. DGUS Tool V7.6.2.1 (newest)
2. DGUS Tool V7.6.1.5
3. DGUS Tool V7.6.0.0
4. DGUS Tool V7.5.x (older, might work better)

**How to get them:**
- http://www.dwin-global.com/download/
- Search "DGUS Tool old versions download"
- Check Internet Archive

**Try opening 20240129.tft in each version:**
- Some versions can import .tft directly
- Look for: File → Import TFT or File → Decompile

### Option 2: DWIN_Unpack Tools

**Search GitHub for DWIN unpacker:**

```bash
# On Mac
cd /Users/jamesfield/3D/klipperlcd/LCD

# Search for tools
# GitHub: "DWIN unpacker" or "DWIN TFT extract"
```

**Known tools (search these names):**
- `dwin-ico-tools` - Extract icons/images
- `dwin-t5l-decoder` - Decode T5L format
- `tft-extract` - Generic TFT extractors

### Option 3: Manual Hex Analysis

The .tft file has a structure. We can try to understand it:

**File Structure (observed):**
```
Offset 0x00-0x03: Header "BT" signature
Offset 0x10-0x11: Screen resolution (0x01E0 = 480, 0x0110 = 272)
Offset 0x2C-...:  Screen data (compressed?)
```

**On your Mac, let's analyze:**

```bash
cd /Users/jamesfield/3D/klipperlcd/LCD

# Check if any embedded files
strings -n 10 20240129.tft > tft_strings.txt

# Look for screen names, image headers, etc.
cat tft_strings.txt | less

# Check for ZIP/PNG/BMP headers
xxd 20240129.tft | grep "504b 0304"  # ZIP signature
xxd 20240129.tft | grep "8950 4e47"  # PNG signature
xxd 20240129.tft | grep "424d"       # BMP signature
```

### Option 4: Try on Windows with HxD Hex Editor

**Download HxD (free hex editor):**
- https://mh-nexus.de/en/hxd/
- Windows version works on Windows 7

**Manual extraction:**
1. Open 20240129.tft in HxD
2. Look for patterns:
   - BMP headers: `42 4D` (might be screen images)
   - Screen data blocks
   - Font data
3. Extract sections manually
4. Reconstruct in DGUS Tool

### Option 5: Contact DWIN/Elegoo

**Email DWIN Tech Support:**
- support@dwin-global.com
- Ask: "How to decompile/edit existing .tft file"
- Mention: "DWIN BT format, TJC4827 display"

**Email Elegoo Support:**
- support@elegoo.com
- Ask: "Neptune 3 Pro LCD firmware source files"
- Request: "DGUS project files for modification"

They might provide:
- Source DGUS project
- Decompiler tool
- Modification instructions

## Practical Approach: Try This on Windows Now

### Step A: Multiple DGUS Versions

**On Windows 7:**

1. **Install DGUS Tool V7.6.2.1** (if you haven't)

2. **Try opening the .tft:**
   - File → Open (try selecting 20240129.tft directly)
   - File → Import → TFT File
   - Tools → Decompile
   - Look for any "Import" or "Convert" options

3. **If that fails, try:**
   - File → New Project
   - Device → T5L or DMG series (480x272)
   - Tools → Import Background
   - See if you can import parts of the .tft

### Step B: Check HMI File More Carefully

You said `LCD_program.HMI` didn't work. Let's try again:

**In DGUS Tool:**
1. File → Open
2. Navigate to `LCD_program.HMI`
3. Select file type: "All Files (*.*)" or "HMI Project (*.HMI)"
4. Try opening

**Check file size:**
- If HMI is >10MB, it might contain the project
- If HMI is <1MB, might be corrupted/incomplete

**Try different approach:**
1. Create new blank project for TJC4827 (480x272)
2. Save it
3. Look at folder structure DGUS Tool creates
4. Copy files from extracted HMI location
5. Reload project

### Step C: Look for DWIN_SET Folder

Some .tft files are actually containers. Try this:

**On Windows:**
1. Rename `20240129.tft` to `20240129.zip`
2. Try opening with WinRAR, 7-Zip, or WinZip
3. If it extracts, look for `DWIN_SET` folder inside
4. That folder contains source files!

**If extraction fails:**
Try different extraction tools:
- 7-Zip (free, powerful)
- WinRAR
- Universal Extractor

## If Nothing Works: Hybrid Approach

**Create new screens alongside existing ones:**

1. **Identify unused screen IDs:**
   - Current firmware probably uses screens 0-10
   - You can add screens 20-25 (your new ones)

2. **Create minimal DGUS project:**
   - Only your 5 new screens
   - Match resolution: 480x272
   - Match serial settings

3. **Merge the projects:**
   - Extract screen .bmp files from yours
   - Manually add to original firmware folder
   - Edit config file to include new screens

**This is advanced and risky!**

## Realistic Assessment

### Easy Path ✅
- Use console shortcuts (works now!)
- Add Mainsail macros
- Actually use your printer

### Medium Path ⚠️
- Try different DGUS versions
- Contact Elegoo for source files
- Wait for community solution

### Hard Path ❌
- Reverse engineer .tft format
- Manually hex edit
- High risk of bricking LCD

## What I Recommend

**Do this RIGHT NOW on Windows:**

1. **Install 7-Zip** (free)
2. **Rename 20240129.tft → 20240129.zip**
3. **Try extracting with 7-Zip**
4. **See what's inside!**

Then:

**If it extracts:**
🎉 You have source files! Follow original DGUS guide!

**If it doesn't extract:**
📧 Email Elegoo: "Please provide Neptune 3 Pro LCD source files for modification"

**While waiting:**
✅ Use console shortcuts that work perfectly right now!

---

## Commands to Run Right Now

**On Windows (Command Prompt):**
```cmd
cd C:\Neptune3Pro_LCD

# Try extracting
"C:\Program Files\7-Zip\7z.exe" x 20240129.tft -oextracted

# Check what's inside
dir extracted

# If DWIN_SET exists:
dir extracted\DWIN_SET
```

**Try that and tell me what you find!**

If you see folders like `DWIN_SET` or files like `*.bmp`, `13.bin`, `T5L.CFG`, we're in business! 🎯

If not, we need to either:
1. Get source files from Elegoo
2. Use a different approach
3. Stick with awesome console shortcuts that already work

Let me know what 7-Zip shows!
