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
            self.log_file = config_parser.get('paths', 'log_file', fallback='/tmp/KlipperLCD.log')
        else:
            self.install_dir = os.path.expanduser('~/KlipperLCD')
            self.log_file = '/tmp/KlipperLCD.log'


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
        config_content = """# KlipperLCD Configuration File
# This file configures the KlipperLCD service for Elegoo Neptune 3 Pro LCD screens
# Edit this file and restart the KlipperLCD service for changes to take effect

[connection]
# Serial port configuration
serial_port = /dev/ttyUSB0
baud_rate = 115200

[klipper]
# Moonraker configuration
moonraker_host = 127.0.0.1
moonraker_port = 80
moonraker_api_key = XXXXXX

# Klipper socket path
klippy_socket = ~/printer_data/comms/klippy.sock

[paths]
# Installation and data paths
install_dir = ~/KlipperLCD
log_file = /tmp/KlipperLCD.log

[presets]
# Material temperature presets (in Celsius)
# PLA settings
pla_hotend = 200
pla_bed = 60

# ABS settings
abs_hotend = 245
abs_bed = 100

# PETG settings
petg_hotend = 225
petg_bed = 70

# TPU settings
tpu_hotend = 220
tpu_bed = 60

# Probe/mesh bed leveling temperature
probe_hotend = 200
probe_bed = 60

[adjustments]
# Default adjustment increments for UI controls
temp_unit = 10
move_unit = 1
speed_unit = 10
accel_unit = 100

[filament]
# Filament load/unload settings
load_length = 25
feedrate = 300
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
