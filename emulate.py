#!/usr/bin/env python3
"""
LCD Emulator — drive the Neptune 3 Pro LCD from Mac without Klipper.

Usage:
    python3 emulate.py [--port /dev/cu.usbserial-XXXX] [--baud 115200]

Port defaults to the value in KlipperLCD.cfg if --port is not given.
Find your port: ls /dev/cu.*
"""

import argparse
import sys
import time
from threading import Thread

from config import KlipperLCDConfig
from lcd import LCD, _printerData, LCDEvents


# ---------------------------------------------------------------------------
# Mock printer state
# ---------------------------------------------------------------------------

class MockPrinter:
    def __init__(self):
        # Temperatures — ramp toward targets each tick
        self.hotend        = 25.0
        self.hotend_target = 200.0
        self.bed           = 25.0
        self.bed_target    = 60.0

        # Print state
        self.state   = "standby"   # standby / printing / paused / complete
        self.percent = 0
        self.duration  = 0          # seconds elapsed
        self.remaining = 0          # seconds remaining (rough)

        # Motion / speeds
        self.feedrate  = 100
        self.flowrate  = 100
        self.fan       = 0
        self.x_pos     = 0.0
        self.y_pos     = 0.0
        self.z_pos     = 0.0
        self.z_offset  = 0.0

        # Machine info shown on information page
        self.machine_size          = "235x235x280"
        self.short_build_version   = "v0.11.0-emulator"

        # Velocity limits
        self.max_velocity           = 500
        self.max_accel              = 3000
        self.max_accel_to_decel     = 1500
        self.square_corner_velocity = 5.0

        # File list & current file
        self.files     = ["test_cube.gcode", "benchy.gcode", "calibration.gcode"]
        self.file_name = ""

    def tick(self):
        """Advance simulated state by one update cycle."""
        # Ramp temps
        self.hotend = _ramp(self.hotend, self.hotend_target, step=8.0)
        self.bed    = _ramp(self.bed,    self.bed_target,    step=3.0)

        # Advance print progress
        if self.state == "printing":
            self.percent   = min(100, self.percent + 1)
            self.duration += 2
            if self.percent >= 100:
                self.state = "complete"
                print("[emulator] Print complete!")


def _ramp(current, target, step):
    if abs(current - target) <= step:
        return target
    return current + step if current < target else current - step


# ---------------------------------------------------------------------------
# Emulator
# ---------------------------------------------------------------------------

class LCDEmulator:
    def __init__(self, port, baud):
        self.mock = MockPrinter()
        self.running = False

        self.lcd = LCD(
            port,
            baud=baud,
            callback=self.lcd_callback,
            config=None          # uses LCD defaults; good enough for emulation
        )

    def boot(self):
        """Mirror KlipperLCD.__init__ boot sequence."""
        # macOS + CP2102: timeout=None causes read() to return 0 bytes immediately.
        # A finite timeout lets the run() loop handle empty reads gracefully.
        self.lcd.ser.timeout = 0.5
        print("[emulator] Opening serial port and sending boot sequence...")
        self.lcd.start()

        # Simulate Klipper connect wait (~3 s, 3 progress increments)
        progress = 1
        for _ in range(3):
            progress += 30
            self.lcd.boot_progress(min(progress, 99))
            time.sleep(1)

        # Fake gcode store (a few lines of history)
        fake_gcode_store = [
            {"message": "KlipperLCD emulator started",  "type": "response"},
            {"message": "Printer ready",                 "type": "response"},
        ]
        self.lcd.write_gcode_store(fake_gcode_store)

        # Fake macros
        fake_macros = ["START_PRINT", "END_PRINT", "CANCEL_PRINT", "BED_MESH_CALIBRATE"]
        self.lcd.write_macros(fake_macros)

        # Machine info
        self.lcd.write("information.size.txt=\"%s\""        % self.mock.machine_size)
        self.lcd.write("information.sversion.txt=\"%s\""    % self.mock.short_build_version)

        # Transition to main page (matches production sequence)
        time.sleep(2)
        self.lcd.write("main.va0.val=1")
        self.lcd.write("page main")
        time.sleep(0.5)
        self.lcd.write("page main")

        print("[emulator] Boot complete — LCD should now show main page.")

    def start(self):
        """Start the periodic update loop."""
        self.running = True
        Thread(target=self._update_loop, daemon=True).start()
        print("[emulator] Update loop running (2 s interval). Press Ctrl+C to quit.")

    def _update_loop(self):
        while self.running:
            self.mock.tick()
            self._send_data_update()
            time.sleep(2)

    def _send_data_update(self):
        data = _printerData()
        data.hotend_target = int(self.mock.hotend_target)
        data.hotend        = int(self.mock.hotend)
        data.bed_target    = int(self.mock.bed_target)
        data.bed           = int(self.mock.bed)
        data.state         = self.mock.state
        data.percent       = self.mock.percent
        data.duration      = self.mock.duration
        data.remaining     = self.mock.remaining
        data.feedrate      = self.mock.feedrate
        data.flowrate      = self.mock.flowrate
        data.fan           = self.mock.fan
        data.x_pos         = self.mock.x_pos
        data.y_pos         = self.mock.y_pos
        data.z_pos         = self.mock.z_pos
        data.z_offset      = self.mock.z_offset
        data.file_name     = self.mock.file_name
        data.max_velocity           = self.mock.max_velocity
        data.max_accel              = self.mock.max_accel
        data.max_accel_to_decel     = self.mock.max_accel_to_decel
        data.square_corner_velocity = self.mock.square_corner_velocity

        self.lcd.data_update(data)

    # -----------------------------------------------------------------------
    # LCD event callback
    # -----------------------------------------------------------------------

    def lcd_callback(self, evt, data=None):
        e = self.lcd.evt

        if evt == e.FILES:
            print("[emulator] FILES requested — returning %d fake files" % len(self.mock.files))
            return self.mock.files

        elif evt == e.HOME:
            print("[emulator] HOME: homing X Y Z (axes=%s)" % data)
            self.mock.x_pos = 0.0
            self.mock.y_pos = 0.0
            self.mock.z_pos = 0.0
            self.lcd.write_console("Homing X Y Z...")

        elif evt == e.MOVE_X:
            self.mock.x_pos = round(self.mock.x_pos + (data or 0), 2)
            print("[emulator] MOVE_X  delta=%s  x_pos=%.2f" % (data, self.mock.x_pos))

        elif evt == e.MOVE_Y:
            self.mock.y_pos = round(self.mock.y_pos + (data or 0), 2)
            print("[emulator] MOVE_Y  delta=%s  y_pos=%.2f" % (data, self.mock.y_pos))

        elif evt == e.MOVE_Z:
            self.mock.z_pos = round(self.mock.z_pos + (data or 0), 2)
            print("[emulator] MOVE_Z  delta=%s  z_pos=%.2f" % (data, self.mock.z_pos))

        elif evt == e.MOVE_E:
            print("[emulator] MOVE_E  data=%s" % str(data))

        elif evt == e.NOZZLE:
            self.mock.hotend_target = float(data or 0)
            print("[emulator] NOZZLE target -> %.0f°C" % self.mock.hotend_target)
            self.lcd.write_console("Nozzle target: %.0f°C" % self.mock.hotend_target)

        elif evt == e.BED:
            self.mock.bed_target = float(data or 0)
            print("[emulator] BED target -> %.0f°C" % self.mock.bed_target)
            self.lcd.write_console("Bed target: %.0f°C" % self.mock.bed_target)

        elif evt == e.PRINT_START:
            file = data or "unknown.gcode"
            self.mock.state    = "printing"
            self.mock.percent  = 0
            self.mock.duration = 0
            self.mock.file_name = file
            print("[emulator] PRINT_START: %s" % file)
            self.lcd.write_console("Starting print: %s" % file)

        elif evt == e.PRINT_STOP:
            self.mock.state   = "standby"
            self.mock.percent = 0
            self.mock.file_name = ""
            print("[emulator] PRINT_STOP")
            self.lcd.write_console("Print cancelled.")

        elif evt == e.PRINT_PAUSE:
            self.mock.state = "paused"
            print("[emulator] PRINT_PAUSE")
            self.lcd.write_console("Print paused.")

        elif evt == e.PRINT_RESUME:
            self.mock.state = "printing"
            print("[emulator] PRINT_RESUME")
            self.lcd.write_console("Print resumed.")

        elif evt == e.PRINT_SPEED:
            self.mock.feedrate = int(data or 100)
            print("[emulator] PRINT_SPEED -> %d%%" % self.mock.feedrate)

        elif evt == e.FLOW:
            self.mock.flowrate = int(data or 100)
            print("[emulator] FLOW -> %d%%" % self.mock.flowrate)

        elif evt == e.FAN:
            self.mock.fan = int(data or 0)
            print("[emulator] FAN -> %d%%" % self.mock.fan)
            self.lcd.write_console("Fan: %d%%" % self.mock.fan)

        elif evt == e.LIGHT:
            print("[emulator] LIGHT -> %s" % str(data))
            self.lcd.write_console("Light: %s" % str(data))

        elif evt == e.MOTOR_OFF:
            print("[emulator] MOTOR_OFF")
            self.lcd.write_console("Motors disabled.")

        elif evt == e.Z_OFFSET:
            self.mock.z_offset = round(float(data or 0), 3)
            print("[emulator] Z_OFFSET -> %.3f" % self.mock.z_offset)
            self.lcd.write_console("Z offset: %.3f" % self.mock.z_offset)

        elif evt == e.CONSOLE:
            cmd = (data or "").strip()
            print("[emulator] CONSOLE: %s" % cmd)
            self.lcd.write_console("> %s\nOK" % cmd)

        elif evt == e.THUMBNAIL:
            # No real files — skip silently
            pass

        elif evt == e.PROBE:
            print("[emulator] PROBE data=%s" % str(data))

        elif evt == e.PROBE_COMPLETE:
            print("[emulator] PROBE_COMPLETE")

        elif evt == e.PROBE_BACK:
            print("[emulator] PROBE_BACK")

        elif evt == e.BED_MESH:
            print("[emulator] BED_MESH")

        elif evt == e.ACCEL:
            self.mock.max_accel = int(data or 3000)
            print("[emulator] ACCEL -> %d" % self.mock.max_accel)

        elif evt == e.ACCEL_TO_DECEL:
            self.mock.max_accel_to_decel = int(data or 1500)
            print("[emulator] ACCEL_TO_DECEL -> %d" % self.mock.max_accel_to_decel)

        elif evt == e.VELOCITY:
            self.mock.max_velocity = int(data or 500)
            print("[emulator] VELOCITY -> %d" % self.mock.max_velocity)

        elif evt == e.SQUARE_CORNER_VELOCITY:
            self.mock.square_corner_velocity = float(data or 5.0)
            print("[emulator] SQUARE_CORNER_VELOCITY -> %.1f" % self.mock.square_corner_velocity)

        else:
            print("[emulator] Unhandled event %d  data=%s" % (evt, str(data)))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="LCD Emulator — drive the Neptune 3 Pro LCD from Mac without Klipper"
    )
    parser.add_argument("--port", "-p", type=str,
                        help="Serial port (e.g. /dev/cu.usbserial-XXXX). "
                             "Defaults to value from KlipperLCD.cfg.")
    parser.add_argument("--baud", "-b", type=int, default=None,
                        help="Baud rate (default 115200).")
    args = parser.parse_args()

    # Resolve port/baud: CLI args take priority, then config file
    port = args.port
    baud = args.baud

    if port is None or baud is None:
        try:
            cfg = KlipperLCDConfig()
            if port is None:
                port = cfg.connection.serial_port
                print("[emulator] Using port from config: %s" % port)
            if baud is None:
                baud = cfg.connection.baud_rate
        except Exception:
            if port is None:
                print("[emulator] ERROR: no --port given and config not found.")
                print("           Run:  ls /dev/cu.*   to find your adapter.")
                sys.exit(1)
            if baud is None:
                baud = 115200

    if baud is None:
        baud = 115200

    print("[emulator] Port: %s  Baud: %d" % (port, baud))

    emulator = LCDEmulator(port, baud)

    try:
        emulator.boot()
        emulator.start()

        # Keep main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[emulator] Shutting down.")
        emulator.running = False
        sys.exit(0)


if __name__ == "__main__":
    main()
