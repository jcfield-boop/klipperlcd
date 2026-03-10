import argparse
import logging
import sys
import time
import base64
import os

from threading import Thread
from datetime import timedelta

from config import KlipperLCDConfig
from printer import PrinterData
from lcd import LCD, _printerData
from visualization import (format_bed_mesh_grid, format_klipper_state,
                           format_pressure_advance_info, format_input_shaper_info,
                           format_file_metadata, format_system_stats)

logger = logging.getLogger('KlipperLCD.main')

class KlipperLCD ():
    def __init__(self, config=None):
        self.config = config if config else KlipperLCDConfig()

        logger.info("Initialising LCD on %s at %d baud" % (
            self.config.connection.serial_port, self.config.connection.baud_rate))
        self.lcd = LCD(
            self.config.connection.serial_port,
            baud=self.config.connection.baud_rate,
            callback=self.lcd_callback,
            config=self.config
        )
        self.lcd.start()

        logger.info("Connecting to Moonraker at %s:%d" % (
            self.config.klipper.moonraker_host, self.config.klipper.moonraker_port))
        self.printer = PrinterData(
            self.config.klipper.moonraker_api_key,
            host=self.config.klipper.moonraker_host,
            port=self.config.klipper.moonraker_port,
            klippy_sock=self.config.klipper.klippy_socket,
            callback=self.printer_callback,
            led_name=self.config.features.led_name
        )
        self.running = False
        self.wait_probe = False
        self.thumbnail_inprogress = False

        logger.info("Waiting for Klipper/Moonraker to become ready...")
        progress_bar = 1
        while self.printer.update_variable() is None:
            progress_bar += 5
            self.lcd.boot_progress(progress_bar)
            time.sleep(1)
        logger.info("Klipper ready")

        logger.info("Initialising Moonraker web services")
        self.printer.init_Webservices()

        logger.info("Loading gcode store")
        gcode_store = self.printer.get_gcode_store()
        self.lcd.write_gcode_store(gcode_store)

        logger.info("Loading macros")
        macros = self.printer.get_macros()
        self.lcd.write_macros(macros)

        logger.info("Switching LCD to main page (size=%s, fw=%s)" % (
            self.printer.MACHINE_SIZE, self.printer.SHORT_BUILD_VERSION))
        self.lcd.write("main.va0.val=1")
        self.lcd.write("page main")
        time.sleep(0.2)  # let display process page switch before cross-page writes
        self.lcd.write("information.size.txt=\"%s\"" % self.printer.MACHINE_SIZE)
        self.lcd.write("information.sversion.txt=\"%s\"" % self.printer.SHORT_BUILD_VERSION)
        logger.info("Startup complete")

    def start(self):
        logger.info("KlipperLCD start")
        self.running = True
        #self.lcd.start()
        Thread(target=self.periodic_update).start()

    def periodic_update(self):
        while self.running:
            if self.wait_probe:
                print("Zpos=%f, Zoff=%f" % (self.printer.current_position.z, self.printer.BABY_Z_VAR))
                if self.printer.ishomed():
                        self.wait_probe = False
                        print("IsHomed")
                        self.lcd.probe_mode_start()

            self.printer.update_variable()
            data = _printerData()
            data.hotend_target = self.printer.thermalManager['temp_hotend'][0]['target']
            data.hotend        = self.printer.thermalManager['temp_hotend'][0]['celsius']
            data.bed_target    = self.printer.thermalManager['temp_bed']['target']
            data.bed           = self.printer.thermalManager['temp_bed']['celsius']
            data.state         = self.printer.getState()
            data.percent       = self.printer.getPercent()
            data.duration      = self.printer.duration()
            data.remaining     = self.printer.remain()
            data.feedrate      = self.printer.print_speed
            data.flowrate      = self.printer.flow_percentage
            data.fan           = self.printer.thermalManager['fan_speed'][0]
            data.x_pos         = self.printer.current_position.x
            data.y_pos         = self.printer.current_position.y
            data.z_pos         = self.printer.current_position.z
            data.z_offset      = self.printer.BABY_Z_VAR
            data.file_name     = self.printer.file_name
            data.max_velocity           = self.printer.max_velocity          
            data.max_accel              = self.printer.max_accel             
            data.max_accel_to_decel     = self.printer.max_accel_to_decel    
            data.square_corner_velocity = self.printer.square_corner_velocity

            self.lcd.data_update(data)
                
            time.sleep(2)

    def printer_callback(self, data, data_type):
        msg = self.lcd.format_console_data(data, data_type)
        if msg:
            self.lcd.write_console(msg)

    def show_thumbnail(self):
        if self.printer.file_path and (self.printer.file_name or self.lcd.files[self.lcd.selected_file]):
            file_name = ""
            if self.lcd.files:
                file_name = self.lcd.files[self.lcd.selected_file]
            elif self.printer.file_name:
                file_name = self.printer.file_name
            else:
                print("ERROR: gcode file not known")
            
            file = os.path.expanduser(self.printer.file_path) + "/" + file_name

            # Reading file
            print(file)
            try:
                f = open(file, "r")
                buf = f.readlines()
                f.close()
            except Exception as e:
                print("File could not be read: %s — %s" % (file, e))
                return
            thumbnail_found = False
            b64 = ""

            for line in buf:
                if 'thumbnail begin' in line:
                    thumbnail_found = True
                elif 'thumbnail end' in line:
                    thumbnail_found = False
                    break
                elif thumbnail_found:
                    b64 += line.strip(' \t\n\r;')
        
            if len(b64):
                # Decode Base64
                img = base64.b64decode(b64)        
                
                # Write thumbnail to LCD
                self.lcd.write_thumbnail(img)
            else:
                self.lcd.clear_thumbnail()
                print("Aborting thumbnail, no image found")
        else:
            print("File path or name to gcode-files missing")
        
        self.thumbnail_inprogress = False

    def lcd_callback(self, evt, data=None):
        if evt == self.lcd.evt.HOME:
            self.printer.home(data)
        elif evt == self.lcd.evt.MOVE_X:
            self.printer.moveRelative('X', data, 4000)
        elif evt == self.lcd.evt.MOVE_Y:
            self.printer.moveRelative('Y', data, 4000)
        elif evt == self.lcd.evt.MOVE_Z:
            self.printer.moveRelative('Z', data, 600)
        elif evt == self.lcd.evt.MOVE_E:
            print(data)
            self.printer.moveRelative('E', data[0], data[1])
        elif evt == self.lcd.evt.Z_OFFSET:
            self.printer.setZOffset(data)
        elif evt == self.lcd.evt.NOZZLE:
            self.printer.setExtTemp(data)
        elif evt == self.lcd.evt.BED:
            self.printer.setBedTemp(data)
        elif evt == self.lcd.evt.FILES:
            files = self.printer.GetFiles(True)
            return files
        elif evt == self.lcd.evt.PRINT_START:
            self.printer.openAndPrintFile(data)
            if self.thumbnail_inprogress == False:
                self.thumbnail_inprogress = True
        elif evt == self.lcd.evt.THUMBNAIL:
            if self.thumbnail_inprogress == False:
                self.thumbnail_inprogress = True
                Thread(target=self.show_thumbnail).start()
        elif evt == self.lcd.evt.PRINT_STATUS:
            pass
        elif evt == self.lcd.evt.PRINT_STOP:
            self.printer.cancel_job()
        elif evt == self.lcd.evt.PRINT_PAUSE:
            self.printer.pause_job()
        elif evt == self.lcd.evt.PRINT_RESUME:
            self.printer.resume_job()
        elif evt == self.lcd.evt.PRINT_SPEED:
            self.printer.set_print_speed(data)
        elif evt == self.lcd.evt.FLOW:
            self.printer.set_flow(data)
        elif evt == self.lcd.evt.PROBE:
            if data == None:
                self.printer.probe_calibrate()
                self.wait_probe = True
            else:
                self.printer.probe_adjust(data)
        elif evt == self.lcd.evt.PROBE_COMPLETE:
            self.wait_probe = False
            print("Save settings!")
            self.printer.sendGCode('ACCEPT')
            self.printer.sendGCode('G1 F1000 Z15.0')
            print("Calibrate!")
            self.printer.sendGCode('BED_MESH_CALIBRATE PROFILE=default METHOD=automatic')
        elif evt == self.lcd.evt.PROBE_BACK:
            print("BACK!")
            self.printer.sendGCode('ACCEPT')
            self.printer.sendGCode('G1 F1000 Z15.0')
            self.printer.sendGCode('SAVE_CONFIG')
        elif evt == self.lcd.evt.BED_MESH:
            pass
        elif evt == self.lcd.evt.LIGHT:
            self.printer.set_led(data)
        elif evt == self.lcd.evt.FAN:
            self.printer.set_fan(data)
        elif evt == self.lcd.evt.MOTOR_OFF:
            self.printer.sendGCode('M18')
        elif evt == self.lcd.evt.ACCEL:
            #print("SET_VELOCITY_LIMIT ACCEL=%d" % data)
            self.printer.sendGCode("SET_VELOCITY_LIMIT ACCEL=%d" % data)
        elif evt == self.lcd.evt.ACCEL_TO_DECEL:
            if getattr(self.printer, 'minimum_cruise_ratio', None) is not None:
                ratio = max(0.0, min(1.0, data / max(self.printer.max_accel, 1)))
                self.printer.sendGCode("SET_VELOCITY_LIMIT MINIMUM_CRUISE_RATIO=%.4f" % ratio)
            else:
                self.printer.sendGCode("SET_VELOCITY_LIMIT ACCEL_TO_DECEL=%d" % data)
        elif evt == self.lcd.evt.VELOCITY:
            #print("SET_VELOCITY_LIMIT VELOCITY=%d" % data)
            self.printer.sendGCode("SET_VELOCITY_LIMIT VELOCITY=%d" % data)
        elif evt == self.lcd.evt.SQUARE_CORNER_VELOCITY:
            #print(data)
            print("SET_VELOCITY_LIMIT SQUARE_CORNER_VELOCITY=%.1f" % data)
            self.printer.sendGCode("SET_VELOCITY_LIMIT SQUARE_CORNER_VELOCITY=%.1f" % data)
        elif evt == self.lcd.evt.CONSOLE:
            # Check for console shortcuts first (if enabled)
            if self.config.features.enable_console_shortcuts:
                command = data.strip().upper()

                if command == "SHOW_MESH":
                    mesh_data = self.printer.get_bed_mesh_data()
                    if mesh_data:
                        formatted_mesh = format_bed_mesh_grid(mesh_data)
                        self.lcd.write_console(formatted_mesh)
                    else:
                        self.lcd.write_console("No bed mesh data available.\nRun BED_MESH_CALIBRATE first.")
                elif command == "SHOW_STATUS":
                    state_info = self.printer.get_klipper_state()
                    mcu_stats = self.printer.get_mcu_stats()
                    status_text, color = format_klipper_state(state_info)
                    stats_text = format_system_stats(mcu_stats)
                    output = f"System Status:\n{status_text}\n\n{stats_text}"
                    self.lcd.write_console(output)
                elif command == "SHOW_PA":
                    pa_value = self.printer.get_pressure_advance()
                    if pa_value is not None:
                        formatted_pa = format_pressure_advance_info(pa_value)
                        self.lcd.write_console(formatted_pa)
                    else:
                        self.lcd.write_console("Could not retrieve Pressure Advance value")
                elif command == "SHOW_SHAPER":
                    shaper_config = self.printer.get_input_shaper_config()
                    if shaper_config:
                        formatted_shaper = format_input_shaper_info(shaper_config)
                        self.lcd.write_console(formatted_shaper)
                    else:
                        self.lcd.write_console("Input Shaper not configured")
                elif command.startswith("PA_ADJUST "):
                    try:
                        adjustment = float(command.split()[1])
                        current_pa = self.printer.get_pressure_advance()
                        if current_pa is not None:
                            new_pa = max(0, current_pa + adjustment)
                            self.printer.set_pressure_advance(new_pa)
                            self.lcd.write_console(f"Pressure Advance adjusted to: {new_pa:.4f}")
                        else:
                            self.lcd.write_console("Could not retrieve current PA value")
                    except (IndexError, ValueError):
                        self.lcd.write_console("Usage: PA_ADJUST <value>\nExample: PA_ADJUST 0.001")
                elif command == "PA_RESET":
                    default_pa = self.config.features.default_pa
                    self.printer.set_pressure_advance(default_pa)
                    self.lcd.write_console(f"Pressure Advance reset to: {default_pa:.4f}")
                elif command == "LOAD_FILAMENT":
                    self.printer.sendGCode("FILAMENT_LOAD")
                    self.lcd.write_console("Loading filament...\nFollow prompts on screen.")
                elif command == "UNLOAD_FILAMENT":
                    self.printer.sendGCode("FILAMENT_UNLOAD")
                    self.lcd.write_console("Unloading filament...\nFollow prompts on screen.")
                elif command == "CHANGE_FILAMENT":
                    self.printer.sendGCode("FILAMENT_CHANGE")
                    self.lcd.write_console("Filament change started...\nFollow prompts on screen.")
                elif command == "HELP_LCD":
                    help_text = """KlipperLCD Console Shortcuts:

SHOW_MESH     - View bed mesh
SHOW_STATUS   - System status & MCU temp
SHOW_PA       - Pressure Advance info
SHOW_SHAPER   - Input Shaper config
PA_ADJUST <n> - Adjust PA (±0.001, ±0.01)
PA_RESET      - Reset PA to 0.0

LOAD_FILAMENT   - Load filament
UNLOAD_FILAMENT - Unload filament
CHANGE_FILAMENT - Change filament during print

HELP_LCD      - This help message

All standard Klipper GCode commands also work."""
                    self.lcd.write_console(help_text)
                else:
                    # Not a shortcut, send as regular GCode
                    self.printer.sendGCode(data)
            else:
                # Console shortcuts disabled, send as regular GCode
                self.printer.sendGCode(data)
        # System Status & Visualization Events
        elif evt == self.lcd.evt.VIEW_MESH:
            mesh_data = self.printer.get_bed_mesh_data()
            if mesh_data:
                formatted_mesh = format_bed_mesh_grid(mesh_data)
                print(formatted_mesh)
                # Send to LCD console or display
                self.lcd.write_console(formatted_mesh)
            else:
                self.lcd.write_console("No bed mesh data available.\nRun BED_MESH_CALIBRATE first.")
        elif evt == self.lcd.evt.MESH_PROFILE_SELECT:
            if data:
                self.printer.load_mesh_profile(data)
                print(f"Loaded mesh profile: {data}")
        elif evt == self.lcd.evt.FIRMWARE_RESTART:
            print("Restarting Klipper firmware...")
            self.printer.firmware_restart()
        elif evt == self.lcd.evt.PA_ADJUST:
            current_pa = self.printer.get_pressure_advance()
            new_pa = max(0, current_pa + data)  # data is adjustment amount
            self.printer.set_pressure_advance(new_pa)
            print(f"Pressure Advance adjusted to: {new_pa:.4f}")
        elif evt == self.lcd.evt.PA_RESET:
            # Reset to default from config
            default_pa = self.config.features.default_pa
            self.printer.set_pressure_advance(default_pa)
            print(f"Pressure Advance reset to: {default_pa:.4f}")
        elif evt == self.lcd.evt.VIEW_SYSTEM_STATUS:
            state_info = self.printer.get_klipper_state()
            mcu_stats = self.printer.get_mcu_stats()

            status_text, color = format_klipper_state(state_info)
            stats_text = format_system_stats(mcu_stats)

            output = f"System Status:\n{status_text}\n\n{stats_text}"
            print(output)
            self.lcd.write_console(output)
        elif evt == self.lcd.evt.TOGGLE_INPUT_SHAPER:
            enabled = bool(data)  # data should be 1 for enable, 0 for disable
            self.printer.toggle_input_shaper(enabled)
            print(f"Input Shaper {'enabled' if enabled else 'disabled'}")
        # Filament change events
        elif evt == self.lcd.evt.FILAMENT_LOAD:
            print("Filament load initiated")
            self.printer.sendGCode("FILAMENT_LOAD")
            self.lcd.write_console("Loading filament...\nHeat nozzle and wait for extrusion.")
        elif evt == self.lcd.evt.FILAMENT_UNLOAD:
            print("Filament unload initiated")
            self.printer.sendGCode("FILAMENT_UNLOAD")
            self.lcd.write_console("Unloading filament...\nHeat nozzle and wait for retraction.")
        elif evt == self.lcd.evt.FILAMENT_CHANGE:
            print("Filament change initiated")
            self.printer.sendGCode("FILAMENT_CHANGE")
            self.lcd.write_console("Filament change started.\nWait for instructions...")
        else:
            print("lcd_callback event not recognised %d" % evt)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='KlipperLCD Service')
    parser.add_argument('--config', '-c', type=str, help='Path to KlipperLCD.cfg')
    parser.add_argument('--generate-config', type=str, metavar='PATH',
                       help='Generate a sample configuration file at the specified path')
    args = parser.parse_args()

    if args.generate_config:
        config = KlipperLCDConfig()
        config.generate_sample_config(args.generate_config)
        print("Sample configuration generated at: %s" % args.generate_config)
        sys.exit(0)

    config = KlipperLCDConfig(args.config)

    # Set up file logging so all logger.info() calls go to KlipperLCD.log
    log_handler = logging.FileHandler(config.paths.log_file)
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(log_handler)
    logging.getLogger().setLevel(logging.INFO)

    x = KlipperLCD(config)
    x.start()
