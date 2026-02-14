# Nextion-Compatible Hardware Solution

## What You Have

**Hardware:** Nextion-compatible LCD (confirmed by board markings)
**Current Firmware:** DWIN format (BT signature, .tft file)
**Problem:** Can't edit DWIN firmware with available tools

## The Solution: Flash Nextion Firmware!

Since your hardware is Nextion-compatible, you can **replace** the DWIN firmware with Nextion firmware that you CAN edit!

## Step-by-Step: Replace Firmware with Nextion

### Step 1: Identify Exact LCD Model

**Open your LCD back cover and photograph the board.**

Look for markings like:
- `NX4832K035` (3.5" Nextion)
- `NX4827T043` (4.3" Nextion)
- `NX8048K050` (5.0" Nextion)
- `T5L` or `DMG` (DWIN models)

**Neptune 3 Pro typically uses:** 3.5" or 4.3" display

**Most likely model:** NX4832K035 (480x320, 3.5")

### Step 2: Download Nextion Editor

**Official Nextion Editor:**
- Website: https://nextion.tech/nextion-editor/
- Download Windows version
- Install on your Windows 7 laptop

**Version:** Get latest stable (should work on Windows 7)

### Step 3: Create New Nextion Project

**In Nextion Editor:**

1. **File → New**
2. **Device Model:**
   - Select: `NX4832K035` (or your identified model)
   - Resolution: 480x320
   - Series: Basic or Enhanced (check your board)

3. **Your project opens with blank screen**

### Step 4: Design Screen 21 (System Status) in Nextion

#### Add Components:

**Page 0 (Rename to "SystemStatus"):**

1. **Add Text Component** (for title):
   - Name: `t_title`
   - Text: "System Status"
   - Position: X=10, Y=10
   - Font: Size 24, Bold
   - Color: White

2. **Add Text Area Component** (for data display):
   - Name: `t_status`
   - Position: X=10, Y=50
   - Size: W=460, H=200
   - Font: Size 16
   - Background: Black
   - Text color: White
   - Scrolling: Enabled

3. **Add Button** "View Status":
   - Name: `b_view`
   - Text: "View Status"
   - Position: X=10, Y=265
   - Size: W=220, H=45

4. **Add Button** "Back":
   - Name: `b_back`
   - Text: "Back"
   - Position: X=250, Y=265
   - Size: W=220, H=45

#### Add Code to Buttons:

**b_view Touch Release Event:**
```c
// Send event code 35 via serial
// Nextion format: Send value to KlipperLCD
print "VIEW_STATUS"  // Or send byte code
// KlipperLCD will need to parse this
```

**b_back Touch Release Event:**
```c
page 0  // Go to main page (adjust to your main page number)
```

### Step 5: Configure Serial Communication

**In Nextion Editor:**

Settings → Serial:
- Baud: 115200 (match KlipperLCD)
- Data bits: 8
- Stop bits: 1
- Parity: None

### Step 6: Compile and Upload

**Compile:**
1. File → Compile (or press F5)
2. Save as: `klipperlcd_nextion.tft`

**Upload to LCD:**
1. Copy `klipperlcd_nextion.tft` to FAT32 SD card
2. Power off Neptune 3 Pro
3. Insert SD in LCD
4. Power on
5. LCD flashes Nextion firmware
6. Power off, remove SD
7. Test!

## Important: Modify KlipperLCD for Nextion Protocol

The current KlipperLCD code expects DWIN protocol. You'll need to modify it for Nextion protocol.

### Nextion vs DWIN Protocol Differences:

**DWIN (current):**
- Binary protocol
- Event codes as bytes
- VP addresses for variables

**Nextion:**
- ASCII protocol
- Commands end with `0xFF 0xFF 0xFF`
- Component names instead of VP addresses
- Touch events return component ID

### Code Changes Needed in lcd.py:

**Option A: Add Nextion Mode (Recommended)**

```python
# lcd.py
class LCD:
    def __init__(self, port, baud=115200, protocol='DWIN'):
        self.protocol = protocol  # 'DWIN' or 'NEXTION'

    def write(self, data):
        if self.protocol == 'NEXTION':
            # Nextion needs 3x 0xFF terminator
            self.ser.write(f"{data}\xff\xff\xff".encode())
        else:
            # Original DWIN code
            self.ser.write(data.encode())

    def write_console(self, text):
        if self.protocol == 'NEXTION':
            # Write to text component
            self.write(f't_status.txt="{text}"')
        else:
            # Original DWIN console code
            # ... existing code
```

**Option B: Create Nextion Adapter Script**

Keep KlipperLCD as-is, create adapter:

```python
# nextion_adapter.py
import serial

class NextionAdapter:
    """Translates between KlipperLCD events and Nextion protocol"""

    def __init__(self, dwin_port, nextion_port):
        self.dwin = serial.Serial(dwin_port, 115200)  # to KlipperLCD
        self.nextion = serial.Serial(nextion_port, 115200)  # to LCD

    def run(self):
        while True:
            # Read from Nextion
            if self.nextion.in_waiting:
                nextion_data = self.parse_nextion()
                # Convert to DWIN format
                dwin_data = self.nextion_to_dwin(nextion_data)
                # Send to KlipperLCD
                self.dwin.write(dwin_data)

            # Read from KlipperLCD
            if self.dwin.in_waiting:
                dwin_data = self.dwin.read()
                # Convert to Nextion format
                nextion_cmd = self.dwin_to_nextion(dwin_data)
                # Send to LCD
                self.nextion.write(nextion_cmd)
```

## Simpler Alternative: Nextion Standalone Mode

**Create Nextion project that directly calls Moonraker:**

Instead of going through KlipperLCD, make Nextion talk to Moonraker directly!

**Nextion HTTP Requests (if Enhanced series):**
```c
// On button press
// Nextion can make HTTP requests (Enhanced series only)
get "http://192.168.0.50/printer/objects/query?mcu"
```

**Problem:** Basic Nextion series can't do HTTP

**Solution:** Use Nextion + ESP8266 bridge (more complex)

## Easiest Path: Stick with Console Shortcuts

**Honestly?** The console shortcuts are working perfectly. Here's why TFT modding might not be worth it:

### Console Shortcuts (What You Have):
✅ Works NOW
✅ All features accessible
✅ No firmware risk
✅ Easy to update
✅ Zero hardware changes

### Custom Nextion TFT (What You'd Get):
⚠️ Requires firmware replacement
⚠️ Need to modify KlipperLCD code
⚠️ Risk bricking LCD
⚠️ Complex protocol translation
⚠️ Hard to maintain/update

**Benefit:** Tap buttons instead of typing
**Cost:** Hours of work, risk of bricking LCD

## My Honest Recommendation

### Do This Now:
1. ✅ Use console shortcuts (already working!)
2. ✅ Set up your default_pa in config
3. ✅ Test all features: SHOW_MESH, SHOW_STATUS, etc.
4. ✅ Actually use your printer!

### Do This Later (If You Really Want):
1. Research exact LCD model number
2. Join Neptune 3 Pro community (Reddit/Discord)
3. See if anyone has created Nextion firmware
4. If yes, use theirs
5. If no, decide if it's worth the effort

### Don't Do This:
- ❌ Spend hours reverse engineering DWIN format
- ❌ Risk bricking your working LCD
- ❌ Modify working code for minor convenience

## Test Your Features RIGHT NOW

**SSH to printer:**
```bash
ssh biqu@192.168.0.50
journalctl -u KlipperLCD.service -f
```

**On LCD console:**
```
HELP_LCD
SHOW_STATUS
SHOW_MESH
SHOW_PA
PA_ADJUST 0.001
```

**If these work, you're done! You have all the features!** 🎉

## FAQ

**Q: Can I flash Nextion firmware without bricking?**
A: Usually yes, but small risk. Always keep original .tft backup.

**Q: Will Nextion firmware work on DWIN-compatible hardware?**
A: If board markings say "Nextion compatible", probably yes.

**Q: Should I try it?**
A: Only if:
  - You have backup LCD available
  - You're comfortable with hardware risk
  - You enjoy tinkering
  - You have exact model number

**Q: What if I brick the LCD?**
A: Flash original 20240129.tft back (you have backup!)

**Q: Is there an easier way?**
A: Yes! Use the console shortcuts that work now.

---

## Bottom Line

You already have **fully working enhanced features** via console shortcuts.

TFT modding would give you **pretty buttons** at the cost of:
- Significant time investment
- Hardware risk
- Code modifications
- Maintenance burden

**Unless you really enjoy hardware hacking, just use the console shortcuts!**

They work perfectly, they're safe, and they give you ALL the same functionality. 🚀
