# TJC4827 Display - Quick Start Guide

## Your Display: TJC4827

**Manufacturer:** TJC (Nextion clone)
**Size:** 4.3 inch
**Resolution:** 480 x 272 pixels (NOT 480x320!)
**Protocol:** Nextion-compatible
**Baud:** 115200

## Step 1: Download Editor

**Best Option: Nextion Editor**
1. Go to: https://nextion.tech/nextion-editor/
2. Download Windows version
3. Install on Windows 7 laptop

**Alternative: TJC Editor**
- Search "TJC HMI Editor" if Nextion doesn't work
- Nearly identical interface

## Step 2: Create Test Project

### In Nextion Editor:

1. **File → New**

2. **Device Selection:**
   - Model: Select closest to "4.3 inch Basic"
   - Resolution: **480 x 272** ← IMPORTANT!
   - If asked for exact model: NX4827T043 or NX4827K043

3. **Project Created**

### Add Simple Test Screen:

**Page 0 (Main):**

1. **Add Text Component:**
   - Drag "Text" from toolbox
   - Name: `t0`
   - Text: "KlipperLCD Test"
   - Position: X=100, Y=50
   - Font: 32pt
   - Color: White

2. **Add Button:**
   - Drag "Button" from toolbox
   - Name: `b0`
   - Text: "Test Button"
   - Position: X=150, Y=150
   - Size: W=180, H=60

3. **Add Button Code:**
   - Double-click button
   - Touch Release Event:
   ```c
   t0.txt="Button Pressed!"
   ```

### Compile and Test:

1. **File → Compile** (F5)
2. Save as: `nextion_test.tft`
3. Copy to FAT32 SD card
4. Flash to LCD (power off, insert SD, power on)
5. Test: Press button, text should change!

## Step 3: Understand Nextion Protocol

**Key Differences from DWIN:**

### DWIN (current firmware):
```
Binary: 0x5A 0xA5 0x04 0x01 0x10 ...
```

### Nextion (new firmware):
```
ASCII: t0.txt="Hello"ÿÿÿ
Commands end with 3x 0xFF bytes
```

### Example Commands:

**Set text:**
```c
t0.txt="System Ready"ÿÿÿ
```

**Read value:**
```c
get t0.txt
```

**Change page:**
```c
page 1
```

**Send data to serial:**
```c
print "EVENT:35"  // Custom protocol
```

## Step 4: Create System Status Screen

### Page 1: SystemStatus

**Components:**

1. **Title Text (t_title):**
   ```
   Position: X=10, Y=10
   Text: "System Status"
   Font: 24pt Bold
   Color: White
   ```

2. **Status Text Area (t_status):**
   ```
   Position: X=10, Y=40
   Size: W=460, H=180
   Font: 16pt
   Color: White
   Background: Black
   Type: Text (multi-line if available)
   ```

3. **View Status Button (b_view):**
   ```
   Position: X=10, Y=225
   Size: W=210, H=40
   Text: "View Status"
   ```

4. **Back Button (b_back):**
   ```
   Position: X=260, Y=225
   Size: W=210, H=40
   Text: "Back"
   ```

### Button Code:

**b_view Touch Release:**
```c
// Send event to KlipperLCD
// We'll use print to send ASCII
print "EVT:35"
```

**b_back Touch Release:**
```c
page 0  // Go to main page
```

## Step 5: Modify KlipperLCD for Nextion

**The Problem:** Current KlipperLCD expects DWIN binary protocol.

**The Solution:** Modify lcd.py to support Nextion ASCII protocol.

### Quick Hack (Test First):

**In lcd.py, modify write_console:**

```python
def write_console(self, msg):
    # Nextion ASCII format
    # Assuming you named text component t_status
    cmd = f't_status.txt="{msg}"'
    # Add Nextion terminators
    cmd_bytes = cmd.encode('ascii') + b'\xff\xff\xff'
    self.ser.write(cmd_bytes)
```

**Parse incoming events:**

```python
def _listen_serial(self):
    while self.running:
        if self.ser.in_waiting:
            # Read until we get terminators or newline
            data = self.ser.read_until(b'\n')

            # Parse Nextion events
            if data.startswith(b'EVT:'):
                event_code = int(data[4:].strip())
                # Call callback with event
                if self.callback:
                    self.callback(event_code)
```

### Better Solution: Add Nextion Mode

**Create nextion_lcd.py:**

```python
from lcd import LCD, _printerData
import serial

class NextionLCD(LCD):
    """Nextion protocol variant of LCD class"""

    def write(self, data):
        """Override to use Nextion format"""
        cmd = data.encode('ascii') + b'\xff\xff\xff'
        self.ser.write(cmd)

    def write_console(self, msg):
        """Write to Nextion text component"""
        # Escape quotes in message
        msg = msg.replace('"', '\\"')
        self.write(f't_status.txt="{msg}"')

    def _parse_event(self, data):
        """Parse Nextion touch events"""
        if data.startswith(b'EVT:'):
            return int(data[4:].strip())
        return None
```

**In main.py:**
```python
from nextion_lcd import NextionLCD

# Replace:
# self.lcd = LCD(...)
# With:
self.lcd = NextionLCD(
    self.config.connection.serial_port,
    baud=self.config.connection.baud_rate,
    callback=self.lcd_callback,
    config=self.config
)
```

## Step 6: Test Integration

### Test Procedure:

1. **Flash Nextion firmware to LCD**
2. **Modify KlipperLCD to use Nextion protocol**
3. **Restart KlipperLCD service**
4. **Test:**
   - Press "View Status" button on LCD
   - Check logs: `journalctl -u KlipperLCD.service -f`
   - Should see: "Event 35 received"
   - Text should appear in t_status component

### Debug:

**If button doesn't work:**
- Check serial monitor in Nextion Editor
- Verify print "EVT:35" sends data
- Check KlipperLCD receives it (add debug prints)

**If text doesn't display:**
- Verify component name is t_status
- Check for quote escaping issues
- Test with simple text first: t_status.txt="TEST"

## Step 7: Add All Screens

Once basic test works, add remaining screens:

**Page 0:** Main (existing)
**Page 1:** System Status (just created)
**Page 2:** Bed Mesh
**Page 3:** Pressure Advance
**Page 4:** Input Shaper
**Page 5:** Tools Menu

Use coordinates from SCREEN_LAYOUTS.txt, adjusted for 480x272 resolution!

## Important: Resolution Difference

**Your display: 480x272**
**Original guides: 480x320**

**Adjustment needed:**
- Y coordinates scaled by 272/320 = 0.85
- Example: Y=265 → Y=225 (265 × 0.85)

**Quick conversion:**
```
Original Y=10  → Your Y=8.5  ≈ 10 (keep)
Original Y=50  → Your Y=42.5 ≈ 40
Original Y=265 → Your Y=225
Original Y=320 → Your Y=272 (max)
```

## Easiest Test Path

### Test 1: Flash Basic Nextion (No Code Changes)

1. Create simple Nextion project with button
2. Flash to LCD
3. See if LCD accepts it and displays

**Success:** LCD shows Nextion interface
**Failure:** LCD stays blank or shows error

### Test 2: Serial Communication

1. On Nextion screen, add button that does: `print "HELLO"`
2. Monitor serial on printer: `screen /dev/ttyUSB0 115200`
3. Press button
4. Should see: `HELLO` in serial output

**Success:** Nextion can send data
**Failure:** Check baud rate, wiring

### Test 3: Receive Data

1. From SSH, send to LCD: `echo -e 't0.txt="TEST"\xff\xff\xff' > /dev/ttyUSB0`
2. LCD text should change to "TEST"

**Success:** Can control Nextion from printer
**Failure:** Check protocol, syntax

### Test 4: Full Integration

1. Modify KlipperLCD for Nextion
2. Press LCD button
3. Check logs, verify event received
4. Check LCD, verify text displays

## Fallback: Keep Using Console

**If Nextion modding is too complex:**

Your console shortcuts work perfectly! Use them:
```
SHOW_STATUS
SHOW_MESH
SHOW_PA
```

No shame in using what works! 🎯

## Resources

**Nextion Instruction Set:**
- https://nextion.tech/instruction-set/

**TJC Documentation:**
- Search "TJC HMI" for manuals

**Nextion Tutorial:**
- YouTube: "Nextion display tutorial"
- Tons of beginner guides available

---

## My Recommendation

**Try this order:**

1. ✅ **Download Nextion Editor** (5 min)
2. ✅ **Create test project** (10 min)
3. ✅ **Flash test.tft to LCD** (5 min)
4. **See if it works!**

If step 4 works → You can create custom screens!
If step 4 fails → Stick with console shortcuts

**Either way, you have working features!** 🚀
