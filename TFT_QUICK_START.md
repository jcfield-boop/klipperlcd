# Quick Start: Custom TFT Firmware

## What You Need
- Windows 7 (or newer) computer
- DGUS Tool (DWIN screen editor)
- Micro SD card (FAT32)
- Original .tft firmware backup

## Fast Track: Add One Feature Screen

### Option 1: Bed Mesh Screen (Easiest to Start)

**1. Extract Original TFT:**
```
- Rename 20240125.tft → 20240125.zip
- Extract to working folder
```

**2. Open in DGUS Tool:**
```
- Launch DGUS Tool
- Open DGUS_SET file from extracted folder
- Note current screen IDs used
```

**3. Add New Screen (ID: 20):**
```
- Click "Add Screen"
- Screen ID: 20
- Size: 480x320
- Create background: 20.bmp
```

**4. Add Text Display:**
```
- Variable Type: Text
- VP Address: 0x3000
- Position: X=10, Y=40
- Size: 40 chars wide, 15 chars tall
- Font: Select existing font
- Mode: Read/Write
```

**5. Add Buttons:**

**Refresh Button:**
```
- Touch Area: X=10, Y=250, W=100, H=40
- Action: Return Key Code
- VP Address: 0x1001
- Key Value: 30
```

**Back Button:**
```
- Touch Area: X=370, Y=250, W=100, H=40
- Action: Jump Screen
- Target: 0 (main screen)
```

**6. Add Navigation from Main Screen:**
```
- Go to main screen in DGUS Tool
- Add "Bed Mesh" button
- Action: Jump Screen → Screen 20
```

**7. Build & Flash:**
```
- Click "Generate" in DGUS Tool
- Zip all files in DWIN_SET
- Rename to klipperlcd_v1.tft
- Copy to FAT32 SD card
- Flash to LCD (power off, insert SD, power on)
```

## Test Immediately with Console

Don't want to build TFT yet? Test features NOW:

```
1. Open console on LCD
2. Type: SHOW_MESH
3. View bed mesh visualization
```

All shortcuts work right away:
- `SHOW_MESH`
- `SHOW_STATUS`
- `SHOW_PA`
- `SHOW_SHAPER`
- `PA_ADJUST 0.001`
- `HELP_LCD`

## Screen IDs to Add

| Screen | ID | Priority | Complexity |
|--------|----|---------|----|
| Bed Mesh | 20 | High | Easy |
| System Status | 21 | High | Easy |
| Pressure Advance | 22 | Medium | Medium |
| Input Shaper | 23 | Low | Easy |
| Tools Menu | 24 | High | Easy |

## VP Address Map

| Feature | VP | Type |
|---------|-----|------|
| Event Code | 0x1001 | Word |
| Mesh Text | 0x3000 | Text |
| Status Text | 0x3100 | Text |
| PA Text | 0x3200 | Text |
| PA Adjust Value | 0x3201 | Float |
| Shaper Text | 0x3300 | Text |

## Common Issues

**"Update Failed"**
- Use FAT32 format
- .tft file in root directory
- Try different SD card

**Buttons Don't Work**
- Check VP 0x1001 is used for events
- Verify event IDs: 30-36
- Check logs: `journalctl -u KlipperLCD.service -f`

**Text Not Showing**
- VP must be Read/Write mode
- Check font files included
- Verify character encoding

## Full Documentation

See `TFT_FIRMWARE_GUIDE.md` for complete step-by-step instructions with screen layouts, button configurations, and troubleshooting.

## Recommendation

**Start Simple:**
1. Use console shortcuts now (immediate)
2. Add Tools Menu screen first (just navigation)
3. Add Bed Mesh screen (most useful)
4. Add others as you learn DGUS Tool

**Share Your Work:**
If you create a working enhanced .tft, consider sharing it with the community!
