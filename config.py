#!/usr/bin/env python3
"""
KlipperLCD Configuration Module

Handles loading, validation, and management of KlipperLCD configuration
from KlipperLCD.cfg file or defaults.
"""

import os
import sys
import logging
from configparser import ConfigParser
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('KlipperLCD.config')


class ConnectionConfig:
    """Serial connection configuration"""
    def __init__(self, config_parser=None):
        if config_parser and config_parser.has_section('connection'):
            self.serial_port = config_parser.get('connection', 'serial_port', fallback='/dev/ttyUSB0')
            self.baud_rate = config_parser.getint('connection', 'baud_rate', fallback=115200)
        else:
            self.serial_port = '/dev/ttyUSB0'
            self.baud_rate = 115200

        self._validate()

    def _validate(self):
        """Validate connection settings"""
        valid_bauds = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        if self.baud_rate not in valid_bauds:
            logger.error(f"Invalid baud rate {self.baud_rate}. Must be one of {valid_bauds}")
            raise ValueError(f"Invalid baud rate: {self.baud_rate}")

        if not os.path.exists(self.serial_port):
            logger.warning(f"Serial port {self.serial_port} does not exist - ensure device is connected")


class KlipperConfig:
    """Klipper/Moonraker configuration"""
    def __init__(self, config_parser=None):
        if config_parser and config_parser.has_section('klipper'):
            self.moonraker_host = config_parser.get('klipper', 'moonraker_host', fallback='127.0.0.1')
            self.moonraker_port = config_parser.getint('klipper', 'moonraker_port', fallback=80)
            self.moonraker_api_key = config_parser.get('klipper', 'moonraker_api_key', fallback='XXXXXX')
            klippy_sock = config_parser.get('klipper', 'klippy_socket',
                                           fallback='~/printer_data/comms/klippy.sock')
            self.klippy_socket = os.path.expanduser(klippy_sock)
        else:
            self.moonraker_host = '127.0.0.1'
            self.moonraker_port = 80
            self.moonraker_api_key = 'XXXXXX'
            self.klippy_socket = os.path.expanduser('~/printer_data/comms/klippy.sock')

        self._validate()

    def _validate(self):
        """Validate Klipper settings"""
        if self.moonraker_port < 1 or self.moonraker_port > 65535:
            logger.error(f"Invalid port {self.moonraker_port}. Must be 1-65535")
            raise ValueError(f"Invalid moonraker port: {self.moonraker_port}")


class PathsConfig:
    """Path configuration"""
    def __init__(self, config_parser=None):
        if config_parser and config_parser.has_section('paths'):
            install_dir = config_parser.get('paths', 'install_dir', fallback='~/KlipperLCD')
            self.install_dir = os.path.expanduser(install_dir)
            log_file = config_parser.get('paths', 'log_file',
                                         fallback='~/printer_data/logs/KlipperLCD.log')
            self.log_file = os.path.expanduser(log_file)
        else:
            self.install_dir = os.path.expanduser('~/KlipperLCD')
            self.log_file = os.path.expanduser('~/printer_data/logs/KlipperLCD.log')


class PresetsConfig:
    """Material preset temperatures configuration"""
    def __init__(self, config_parser=None):
        if config_parser and config_parser.has_section('presets'):
            self.pla_hotend = config_parser.getint('presets', 'pla_hotend', fallback=200)
            self.pla_bed = config_parser.getint('presets', 'pla_bed', fallback=60)
            self.abs_hotend = config_parser.getint('presets', 'abs_hotend', fallback=245)
            self.abs_bed = config_parser.getint('presets', 'abs_bed', fallback=100)
            self.petg_hotend = config_parser.getint('presets', 'petg_hotend', fallback=225)
            self.petg_bed = config_parser.getint('presets', 'petg_bed', fallback=70)
            self.tpu_hotend = config_parser.getint('presets', 'tpu_hotend', fallback=220)
            self.tpu_bed = config_parser.getint('presets', 'tpu_bed', fallback=60)
            self.probe_hotend = config_parser.getint('presets', 'probe_hotend', fallback=200)
            self.probe_bed = config_parser.getint('presets', 'probe_bed', fallback=60)
        else:
            self.pla_hotend = 200
            self.pla_bed = 60
            self.abs_hotend = 245
            self.abs_bed = 100
            self.petg_hotend = 225
            self.petg_bed = 70
            self.tpu_hotend = 220
            self.tpu_bed = 60
            self.probe_hotend = 200
            self.probe_bed = 60

        self._validate()

    def _validate(self):
        """Validate temperature ranges"""
        hotend_temps = [self.pla_hotend, self.abs_hotend, self.petg_hotend,
                       self.tpu_hotend, self.probe_hotend]
        bed_temps = [self.pla_bed, self.abs_bed, self.petg_bed,
                    self.tpu_bed, self.probe_bed]

        for temp in hotend_temps:
            if not (0 <= temp <= 300):
                logger.warning(f"Hotend temperature {temp}°C out of range [0-300], clamping")

        for temp in bed_temps:
            if not (0 <= temp <= 150):
                logger.warning(f"Bed temperature {temp}°C out of range [0-150], clamping")

    def get_hotend_temps(self):
        """Get hotend temperatures as ordered list [PLA, ABS, PETG, TPU, PROBE]"""
        return [self.pla_hotend, self.abs_hotend, self.petg_hotend,
                self.tpu_hotend, self.probe_hotend]

    def get_bed_temps(self):
        """Get bed temperatures as ordered list [PLA, ABS, PETG, TPU, PROBE]"""
        return [self.pla_bed, self.abs_bed, self.petg_bed,
                self.tpu_bed, self.probe_bed]


class AdjustmentsConfig:
    """UI adjustment increments configuration"""
    def __init__(self, config_parser=None):
        if config_parser and config_parser.has_section('adjustments'):
            self.temp_unit = config_parser.getint('adjustments', 'temp_unit', fallback=10)
            self.move_unit = config_parser.getint('adjustments', 'move_unit', fallback=1)
            self.speed_unit = config_parser.getint('adjustments', 'speed_unit', fallback=10)
            self.accel_unit = config_parser.getint('adjustments', 'accel_unit', fallback=100)
        else:
            self.temp_unit = 10
            self.move_unit = 1
            self.speed_unit = 10
            self.accel_unit = 100

        self._validate()

    def _validate(self):
        """Validate adjustment values are positive"""
        if self.temp_unit <= 0 or self.move_unit <= 0 or \
           self.speed_unit <= 0 or self.accel_unit <= 0:
            logger.error("All adjustment units must be positive")
            raise ValueError("Adjustment units must be positive")


class FilamentConfig:
    """Filament load/unload configuration"""
    def __init__(self, config_parser=None):
        if config_parser and config_parser.has_section('filament'):
            self.load_length = config_parser.getint('filament', 'load_length', fallback=25)
            self.feedrate = config_parser.getint('filament', 'feedrate', fallback=300)
        else:
            self.load_length = 25
            self.feedrate = 300

        self._validate()

    def _validate(self):
        """Validate filament settings"""
        if self.load_length <= 0 or self.load_length > 1000:
            logger.warning(f"Load length {self.load_length}mm seems unusual, using anyway")
        if self.feedrate <= 0 or self.feedrate > 3000:
            logger.warning(f"Feedrate {self.feedrate}mm/min seems unusual, using anyway")


class FeaturesConfig:
    """Enhanced features configuration"""
    def __init__(self, config_parser=None):
        if config_parser and config_parser.has_section('features'):
            self.default_pa = config_parser.getfloat('features', 'default_pa', fallback=0.0)
            self.enable_console_shortcuts = config_parser.getboolean('features', 'enable_console_shortcuts', fallback=True)
            self.led_name = config_parser.get('features', 'led_name', fallback='top_LEDs')
        else:
            self.default_pa = 0.0
            self.enable_console_shortcuts = True
            self.led_name = 'top_LEDs'

        self._validate()

    def _validate(self):
        """Validate feature settings"""
        if self.default_pa < 0 or self.default_pa > 2.0:
            logger.warning(f"Default PA value {self.default_pa} seems unusual (typical: 0.0-0.7)")


class KlipperLCDConfig:
    """Main configuration container for KlipperLCD"""

    def __init__(self, config_path=None):
        """
        Initialize configuration

        Args:
            config_path: Optional path to config file. If None, will search
                        default locations
        """
        self.config_path = None
        config_parser = None

        # Determine config file path
        if config_path:
            # User specified path
            if os.path.exists(config_path):
                self.config_path = config_path
                logger.info(f"Using config file: {config_path}")
            else:
                logger.error(f"Specified config file not found: {config_path}")
                sys.exit(1)
        else:
            # Search default locations
            self.config_path = self._find_config_file()

        # Load config if found, otherwise auto-generate
        if self.config_path and os.path.exists(self.config_path):
            config_parser = ConfigParser()
            config_parser.read(self.config_path)
            logger.info(f"Loaded configuration from: {self.config_path}")
        else:
            logger.info("No config file found, auto-generating with defaults")
            self._generate_default_config()
            if self.config_path and os.path.exists(self.config_path):
                config_parser = ConfigParser()
                config_parser.read(self.config_path)

        # Initialize all config sections
        self.connection = ConnectionConfig(config_parser)
        self.klipper = KlipperConfig(config_parser)
        self.paths = PathsConfig(config_parser)
        self.presets = PresetsConfig(config_parser)
        self.adjustments = AdjustmentsConfig(config_parser)
        self.filament = FilamentConfig(config_parser)
        self.features = FeaturesConfig(config_parser)

    def _find_config_file(self):
        """Search for config file in default locations"""
        # Priority order:
        # 1. ~/printer_data/config/KlipperLCD.cfg (Mainsail location)
        # 2. <script_dir>/KlipperLCD.cfg (alongside main.py)

        search_paths = [
            os.path.expanduser('~/printer_data/config/KlipperLCD.cfg'),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'KlipperLCD.cfg')
        ]

        for path in search_paths:
            if os.path.exists(path):
                return path

        # Return preferred location for auto-generation
        return os.path.expanduser('~/printer_data/config/KlipperLCD.cfg')

    def _generate_default_config(self):
        """Generate default configuration file"""
        if not self.config_path:
            logger.error("Cannot generate config: no path specified")
            return

        # Ensure directory exists
        config_dir = os.path.dirname(self.config_path)
        os.makedirs(config_dir, exist_ok=True)

        # Generate config content
        config_content = """# ============================================================================
# KlipperLCD Configuration File
# ============================================================================
# This file configures the KlipperLCD service for Elegoo Neptune 3 Pro LCD
#
# IMPORTANT NOTES FOR BEGINNERS:
# - Lines starting with # are comments (ignored by the program)
# - Edit values after the = sign to customize your settings
# - After making changes, restart the service:
#   sudo systemctl restart KlipperLCD.service
# - This file is visible in Mainsail (Machine tab) for easy web editing
# - Backup this file before making major changes!
#
# ============================================================================

# ============================================================================
# [connection] - LCD Hardware Connection Settings
# ============================================================================
[connection]

# Serial port where your LCD is connected
# CHANGE THIS if your LCD doesn't work!
#
# How to find your serial port:
#   Run: ls /dev/tty* | grep -E "(USB|ACM|AMA)"
#
# Common values:
#   /dev/ttyUSB0  - USB to UART converter (MOST COMMON for Neptune 3 Pro)
#   /dev/ttyAMA0  - Direct Raspberry Pi GPIO UART connection
#   /dev/ttyACM0  - Some USB serial devices
#
# If you're not sure, try /dev/ttyUSB0 first (most common)
serial_port = /dev/ttyUSB0

# Communication speed with LCD (bits per second)
# DO NOT CHANGE unless you know what you're doing!
# The Neptune 3 Pro LCD uses 115200 baud
baud_rate = 115200

# ============================================================================
# [klipper] - Klipper/Moonraker Connection Settings
# ============================================================================
[klipper]

# Moonraker server address
# USUALLY LEAVE AS 127.0.0.1 (localhost)
# Only change if Moonraker is on a different machine
moonraker_host = 127.0.0.1

# Moonraker server port
# USUALLY LEAVE AS 80 (default)
# Only change if you've customized Moonraker's port
moonraker_port = 80

# Moonraker API Key (for authentication)
# USUALLY LEAVE AS XXXXXX (most installations don't need this)
#
# When you need to change this:
#   - If you get "401 Unauthorized" errors in logs
#   - If your Moonraker has force_logins enabled
#
# How to find your API key (if needed):
#   cat ~/.moonraker_api_key
#   OR check Mainsail Settings → General → API Key
#
# For 99% of users: LEAVE THIS AS XXXXXX
moonraker_api_key = XXXXXX

# Path to Klipper's communication socket
# USUALLY LEAVE AS-IS unless you have a custom Klipper install
# The ~ means "your home directory"
klippy_socket = ~/printer_data/comms/klippy.sock

# ============================================================================
# [paths] - File Locations (Advanced - Usually Don't Need to Change)
# ============================================================================
[paths]

# KlipperLCD installation directory
# Only change if you installed KlipperLCD in a non-standard location
install_dir = ~/KlipperLCD

# Log file location (for troubleshooting)
# View logs with: tail -f /tmp/KlipperLCD.log
# Or: journalctl -u KlipperLCD.service -f
log_file = /tmp/KlipperLCD.log

# ============================================================================
# [presets] - Material Temperature Presets
# ============================================================================
# These are the temperatures used when you select a material on the LCD
# CUSTOMIZE THESE for your specific filament brands and printer!
#
# Tips:
#   - These are starting points - adjust based on your filament
#   - Check your filament spool for manufacturer recommendations
#   - Lower temps = better overhangs, more stringing
#   - Higher temps = stronger parts, worse overhangs
#
[presets]

# PLA (Polylactic Acid) - Most common beginner filament
# Default: 200°C hotend, 60°C bed
# Adjust if: Your PLA needs different temps (check spool label)
pla_hotend = 200
pla_bed = 60

# ABS (Acrylonitrile Butadiene Styrene) - Strong, requires enclosure
# Default: 245°C hotend, 100°C bed
# Warning: ABS needs good ventilation and ideally an enclosure
# Adjust if: Your ABS prints warp or don't stick
abs_hotend = 245
abs_bed = 100

# PETG (Polyethylene Terephthalate Glycol) - Strong & flexible
# Default: 225°C hotend, 70°C bed
# Tip: PETG sticks VERY well - use glue stick or painter's tape
# Adjust if: Parts don't stick or you get stringing
petg_hotend = 225
petg_bed = 70

# TPU (Thermoplastic Polyurethane) - Flexible filament
# Default: 220°C hotend, 60°C bed
# Tip: Print SLOW with TPU (20-30mm/s) to avoid jams
# Adjust if: Filament buckles or won't extrude smoothly
tpu_hotend = 220
tpu_bed = 60

# Probe/Bed Leveling Temperature
# Temperature to heat bed during mesh bed leveling
# Why: Bed expands when hot, so level at printing temperature
# Tip: Match this to your most-used filament's bed temp
probe_hotend = 200
probe_bed = 60

# ============================================================================
# [adjustments] - UI Control Increments
# ============================================================================
# How much each +/- button press changes values on the LCD
# BEGINNERS: You can leave these at defaults
# Advanced users: Adjust for your preferred control precision
#
[adjustments]

# Temperature adjustment step (in degrees Celsius)
# When you press +/- on temperature, it changes by this amount
# Default: 10°C steps
# Smaller = more precise, more button presses needed
# Larger = faster adjustment, less precise
temp_unit = 10

# Movement step size (in millimeters)
# When you press +/- to move X/Y/Z, it moves this distance
# Default: 1mm steps
# Common alternatives: 0.1mm (precise), 10mm (fast)
move_unit = 1

# Print speed adjustment step (in percent)
# When adjusting print speed, it changes by this amount
# Default: 10% steps (so 100% → 110% → 120%)
# Tip: Smaller steps (5%) give more control
speed_unit = 10

# Acceleration adjustment step (in mm/s²)
# When adjusting acceleration, it changes by this amount
# Default: 100 mm/s² steps
# Beginners: Leave as-is unless tuning for speed/quality
accel_unit = 100

# ============================================================================
# [filament] - Filament Loading/Unloading Settings
# ============================================================================
# Controls how much filament moves during load/unload operations
# BEGINNERS: These defaults work for most setups
#
[filament]

# Filament load/unload length (in millimeters)
# How much filament to push/pull when loading/unloading
# Default: 25mm
#
# Adjust if:
#   - Filament doesn't reach hotend: INCREASE (try 50mm)
#   - Too much oozing during unload: DECREASE (try 15mm)
#   - Bowden tube setup: May need 100mm+ to feed through tube
#
# Tip: For Neptune 3 Pro (direct drive), 25mm is usually perfect
load_length = 25

# Filament extrusion speed (in mm/min)
# How fast to push filament during load/unload
# Default: 300 mm/min (5mm/s)
#
# Adjust if:
#   - Extruder grinds filament: DECREASE (try 200)
#   - Loading is too slow: INCREASE (try 400)
#   - Getting filament jams: DECREASE
#
# WARNING: Too fast can grind filament or cause jams!
feedrate = 300

# ============================================================================
# [features] - Enhanced Features Configuration
# ============================================================================
# Settings for the enhanced KlipperLCD features (bed mesh, PA, input shaper)
# BEGINNERS: You can leave these at defaults
#
[features]

# Default Pressure Advance value
# This is the value PA_RESET will return to
# Default: 0.0 (disabled)
#
# How to set this:
#   1. Run pressure advance calibration test
#   2. Find your ideal PA value (usually 0.02-0.1 for direct drive)
#   3. Set that value here
#   4. Now PA_RESET will return to YOUR tuned value, not 0.0
#
# Typical values:
#   Direct Drive: 0.02 - 0.1
#   Bowden: 0.3 - 0.7
#
# Leave as 0.0 until you've calibrated your printer
default_pa = 0.0

# Enable console shortcuts (SHOW_MESH, SHOW_PA, etc.)
# Default: true (enabled)
#
# Set to false if you want to disable the shortcut commands
# and only allow standard GCode commands in console
#
# Most users should leave this enabled!
enable_console_shortcuts = true

# ============================================================================
# TROUBLESHOOTING TIPS
# ============================================================================
#
# LCD not working?
#   1. Check serial_port is correct (ls /dev/tty*)
#   2. Check LCD cable is plugged in
#   3. Check logs: journalctl -u KlipperLCD.service -f
#
# Temperatures wrong?
#   1. Verify presets match your filament
#   2. Check first layer with paper test
#   3. Adjust bed temp ±5°C for adhesion
#
# Can't connect to Moonraker?
#   1. Check moonraker_host (usually 127.0.0.1)
#   2. Check Moonraker is running: systemctl status moonraker
#   3. Only set API key if you see "401 Unauthorized" errors
#
# Made a mistake?
#   Delete this file and run: python3 ~/KlipperLCD/main.py --generate-config
#   This will regenerate with all defaults
#
# ============================================================================
# AFTER EDITING THIS FILE
# ============================================================================
# Always restart the service for changes to take effect:
#
#   sudo systemctl restart KlipperLCD.service
#
# Check if it worked:
#
#   sudo systemctl status KlipperLCD.service
#   journalctl -u KlipperLCD.service -f
#
# Edit via Mainsail:
#   Open Mainsail → Machine tab → Find KlipperLCD.cfg → Click to edit
#
# ============================================================================
"""

        try:
            with open(self.config_path, 'w') as f:
                f.write(config_content)
            logger.info(f"Generated default config file: {self.config_path}")
            logger.info("Please edit this file to customize your settings")
        except Exception as e:
            logger.error(f"Failed to generate config file: {e}")
            logger.info("Continuing with hardcoded defaults")

    def generate_sample_config(self, output_path):
        """
        Generate a sample configuration file

        Args:
            output_path: Where to write the sample config
        """
        # Just use the same generation method
        original_path = self.config_path
        self.config_path = output_path
        self._generate_default_config()
        self.config_path = original_path


if __name__ == '__main__':
    # Test config loading
    import argparse
    parser = argparse.ArgumentParser(description='Test KlipperLCD configuration')
    parser.add_argument('--config', type=str, help='Config file path')
    parser.add_argument('--generate', type=str, help='Generate sample config at path')
    args = parser.parse_args()

    if args.generate:
        config = KlipperLCDConfig()
        config.generate_sample_config(args.generate)
        print(f"Sample config generated at: {args.generate}")
    else:
        config = KlipperLCDConfig(args.config)
        print("\nConfiguration loaded successfully:")
        print(f"  Serial port: {config.connection.serial_port}")
        print(f"  Baud rate: {config.connection.baud_rate}")
        print(f"  Moonraker: {config.klipper.moonraker_host}:{config.klipper.moonraker_port}")
        print(f"  Klippy socket: {config.klipper.klippy_socket}")
        print(f"  PLA temps: {config.presets.pla_hotend}°C / {config.presets.pla_bed}°C")
