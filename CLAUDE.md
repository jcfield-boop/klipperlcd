# KlipperLCD — Project Notes

## Hardware
- BTT Pi v1.2 (Allwinner H616, user `biqu`)
- TJC4B25C12785 LCD display
- CP2102 USB-to-UART adapter
- Neptune 3 Pro build volume: 235x235x280
- Klipper fw: v0.13.0-572

## Current Status (2026-03-10)
- Service starts cleanly and LCD switches to main page on startup ✅
- Print preview thumbnail displays correctly ✅
- Boot page ("Waiting for Klipper...") no longer sticks ✅
- LED control working (default name corrected to `LED_Light`) ✅

## Key Fixes Landed
- `com_star` must be re-sent before `page main` in the startup sequence — without it the display ignores the page switch and stays on the boot page
- `page main` must be sent before writing cross-page components (`information.size.txt`, `information.sversion.txt`) — matches pattern used throughout `lcd.py`
- 200ms sleep after `page main` before cross-page writes lets the display process the switch
- 1s delay after serial port open required for CP2102 adapter to initialise before first commands
- `~` must be expanded in file paths before opening gcode files for thumbnails

## TODO
- [x] LED fix: default `led_name` changed from `top_LEDs` to `LED_Light` in `config.py` — matches `[led LED_Light]` in printer.cfg

## Architecture Notes
- `lcd.py` pattern: always `page X` first, then write components on that page
- `com_star` is a TJC-specific command that enables communication mode; required after `page boot` and again before `page main`
- Logs go to `~/printer_data/logs/KlipperLCD.log`
- Config at `~/printer_data/config/KlipperLCD.cfg`
- Service: `sudo systemctl restart KlipperLCD.service`
