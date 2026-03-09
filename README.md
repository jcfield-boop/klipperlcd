# KlipperLCD (for Elegoo Neptune 3 Pro LCD screen)
Want to run Klipper on your Neptune 3 Pro? And still want to be able to use your Neptune 3 Pro LCD touch screen?

Take a look at this python service for the Elegoo Neptune 3 Pro LCD! Running together with Klipper3d and Moonraker!

This fork creates a separate KlipperLCD.cfg file that abstracts your user and serial method to make it more maintainable.

## Look and feel
<p float="left">
    <img src="img/boot_screen.PNG" height="400">
    <img src="img/main_screen.PNG" height="400">
    <img src="img/about_screen.PNG" height="400">
</p>

## Whats needed?
* A Elegoo Neptune 3 Pro with LCD screen.
* A Raspberry Pi or similar SBC to run Klipper. I suggest using the [Klipper Installation And Update Helper (KIAUH)](https://github.com/dw-0/kiauh) to setup and install Klipper, Moonraker and the web user interface of choice ([Fluidd](https://docs.fluidd.xyz/)/[Mainsail](https://docs.mainsail.xyz/)).
* Some re-wiring of the LCD screen to connect it to one of the UARTs availible on your Raspberry Pi / SBC or through a USB to UART converter.
* Then you can follow this guide to enable your Neptune 3 Pro touch screen!

## Wire the LCD
When wiring your screen, you can either wire it directly to one of your Raspberry Pi / SBC availible UARTs or you can wire it through a USB to UART converter. Both options are described below, pick the option that suits your needs.

### To a Raspberry Pi UART
1. Remove the back-cover of the LCD by unscrewing the four screws.

2. Connect the LCD to the Raspberry Pi UART according to the table below:

    | Raspberry Pi  | LCD               |
    | ------------- | ----------------- |
    | Pin 4 (5V)    | 5V  (Black wire)  |
    | Pin 6 (GND)   | GND (Red wire)    |
    | GPIO 14 (TXD) | RX  (Green wire)  |
    | GPIO 15 (RXD) | TX (Yellow wire)  |

    <p float="left">
        <img src="img/rpi_conn.png" height="400">
        <img src="img/LCD_conn.png" height="400">
    </p>

### USB to UART Converter
Quite simple, just remember to cross RX and TX on the LCD and the USB/UART HW.
| USB <-> UART HW | LCD               |
| --------------- | ----------------- |
| 5V              | 5V  (Black wire)  |
| GND             | GND (Red wire)    |
| TXD             | RX  (Green wire)  |
| RXD             | TX (Yellow wire)  |

<p float="left">
    <img src="img/USB_conn.png" height="400">
    <img src="img/LCD_conn.png" height="400">
</p>

## Update the LCD screen firmware
1. Copy the LCD screen firmware `LCD/20240129.tft` to the root of a FAT32 formatted micro-SD card.

   > **⚠️ Verify file size:** The `.tft` file should be approximately **6.6 MB** after downloading. If it is only a few KB, it was downloaded incorrectly (GitHub served an HTML page instead of the binary). In that case, download it using the raw URL: `https://raw.githubusercontent.com/jcfield-boop/klipperlcd/main/LCD/20240129.tft`
2. Make sure the LCD screen is powered off.
3. Insert the micro-SD card into the LCD screens SD card holder. Back-cover needs to be removed.
4. Power on the LCD screen and wait for screen to say `Update Successed!`

A more detailed guide on LCD screen firmware update can be found on the [Elegoo web-pages](https://www.elegoo.com/blogs/3d-printing/elegoo-neptune-3-pro-plus-max-fdm-3d-printer-support-files).


## Enable the UART
> **_Note_**: You can safely skip this section if you wired the display through a USB to UART converter
### [Disable Linux serial console](https://www.raspberrypi.org/documentation/configuration/uart.md)
  By default, the primary UART is assigned to the Linux console. If you wish to use the primary UART for other purposes, you must reconfigure Raspberry Pi OS. This can be done by using raspi-config:

  * Start raspi-config: `sudo raspi-config.`
  * Select option 3 - Interface Options.
  * Select option P6 - Serial Port.
  * At the prompt Would you like a login shell to be accessible over serial? answer 'No'
  * At the prompt Would you like the serial port hardware to be enabled? answer 'Yes'
  * Exit raspi-config and reboot the Pi for changes to take effect.
  
  For full instructions on how to use Device Tree overlays see [this page](https://www.raspberrypi.org/documentation/configuration/device-tree.md). 
  
  In brief, add a line to the `/boot/config.txt` file to apply a Device Tree overlay.
    
    dtoverlay=disable-bt

## Run the KlipperLCD service
* SSH into your Raspberry Pi

### Klipper socket API
* Make sure Klipper's API socket is enabled by reading the Klipper arguments.

    Command:

        cat ~/printer_data/systemd/klipper.env

    Response:

        KLIPPER_ARGS="/home/pi/klipper/klippy/klippy.py /home/pi/printer_data/config/printer.cfg -I /home/pi/printer_data/comms/klippy.serial -l /home/pi/printer_data/logs/klippy.log -a /home/pi/printer_data/comms/klippy.sock"
    
    The KLIPPER_ARGS should include `-a /home/pi/printer_data/comms/klippy.sock`. If not add it to the klipper.env file!

### Get the code
    git clone https://github.com/joakimtoe/KlipperLCD
    cd KlipperLCD

### Installation (Automated - Recommended)
The easiest way to install and configure KlipperLCD is using the automated installation script:

    chmod +x install.sh
    ./install.sh

The installation script will:
* Automatically check for and install required Python dependencies (python3-serial, python3-requests, python3-pil)
* Automatically detect your username and home directory
* Generate a configuration file at `~/printer_data/config/KlipperLCD.cfg`
* Install the systemd service with correct paths
* Optionally enable and start the service

After installation, you can customize your settings by editing `~/printer_data/config/KlipperLCD.cfg`. This file will be visible in Mainsail's configuration editor for easy access through the web interface.

### Configuration
All KlipperLCD settings are now managed through the `KlipperLCD.cfg` configuration file located at `~/printer_data/config/KlipperLCD.cfg`.

**Important settings to review:**
* `serial_port` - Set this to your LCD's serial port (e.g., `/dev/ttyUSB0`, `/dev/ttyAMA0`)
* `moonraker_api_key` - Set if your Moonraker requires authentication
* `klippy_socket` - Path to Klipper's socket (default is usually correct)
* Material temperature presets (PLA, ABS, PETG, TPU)

> **_Note_**: If using a USB to UART converter, the port is typically `/dev/ttyUSB0`. For direct Raspberry Pi UART connection, use `/dev/ttyAMA0`.

You can generate a sample configuration file manually:

    python3 main.py --generate-config ~/printer_data/config/KlipperLCD.cfg

For a complete configuration reference, see `KlipperLCD.cfg.example` which includes detailed documentation for all settings.

### Manual Installation (Advanced)
If you prefer manual installation or need custom configuration:

1. Edit `KlipperLCD.cfg` to match your setup
2. Manually create and install the service file with your paths
3. See the automated `install.sh` script for reference

### Testing Your Configuration
Before enabling the service, test that everything works:

    python3 main.py

If you see no errors and your LCD screen initializes, the configuration is correct!

### Managing the Service
After installation, use these commands to manage KlipperLCD:

**Start the service:**

    sudo systemctl start KlipperLCD.service

**Stop the service:**

    sudo systemctl stop KlipperLCD.service

**Restart after config changes:**

    sudo systemctl restart KlipperLCD.service

**Check service status:**

    sudo systemctl status KlipperLCD.service

**View logs:**

    journalctl -u KlipperLCD.service -f

### Editing Configuration Through Mainsail
The configuration file is located in `~/printer_data/config/`, making it accessible through Mainsail's web interface:

1. Open Mainsail in your browser
2. Navigate to the "Machine" tab
3. Find `KlipperLCD.cfg` in the configuration files list
4. Edit the file through the web interface
5. Save changes and restart the service: `sudo systemctl restart KlipperLCD.service`

## Troubleshooting

### LCD stuck on "Waiting for KlipperLCD.service..."
If the display never leaves the waiting screen even though the service starts without errors, this is a TJC firmware handshake issue. The TJC TFT firmware (used on the Neptune 3 Pro) requires the host to set `main.va0.val=1` after the `com_star` command before it will accept any page-switch or variable commands. This is included in the boot sequence as of the current version. If you are on an older version, update to the latest and restart the service:

    git pull
    sudo systemctl restart KlipperLCD.service

## Console
The console is enabled by default and can be accessed by clicking center top of the main screen or by clicking the thumbnail area while printing.

The console enables sending commands and will display all gcode responses and information from Klipper normally found in the console tab in Mainsail or Fluidd.

### Enhanced Console Shortcuts
KlipperLCD includes convenient shortcuts for advanced features:

**Calibration & Tuning:**
- `SHOW_MESH` - View bed mesh visualization
- `SHOW_STATUS` - System status & MCU temperature
- `SHOW_PA` - Pressure Advance info and tuning
- `SHOW_SHAPER` - Input Shaper configuration
- `PA_ADJUST <value>` - Fine-tune Pressure Advance (e.g., `PA_ADJUST 0.001`)

**Filament Management:**
- `LOAD_FILAMENT` - Heat nozzle and load filament
- `UNLOAD_FILAMENT` - Heat nozzle and unload filament
- `CHANGE_FILAMENT` - Pause print, swap filament, resume

**Help:**
- `HELP_LCD` - Show all available shortcuts

See `FEATURES.md` for calibration features and `FILAMENT_CHANGE_GUIDE.md` for filament operations.

<p float="left">
    <img src="img/console.PNG" height="400">
    <img src="img/console_key.PNG" height="400">
    <img src="img/console_num.PNG" height="400">
</p>

## Thumbnails
KlipperLCD also supports thumbnails!

Follow this guide to enable thumbnails in your slicer: https://klipperscreen.readthedocs.io/en/latest/Thumbnails/

<p float="left">
    <img src="img/thumb1.png" height="400">
    <img src="img/thumb2.png" height="400">
</p>
