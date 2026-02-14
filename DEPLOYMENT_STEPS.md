# KlipperLCD Deployment Steps for 192.168.0.50

## Quick Deployment (Copy & Paste These Commands)

### Step 1: SSH into your printer
```bash
ssh biqu@192.168.0.50
```
Password: `biqu`

---

### Step 2: Stop the existing service
```bash
sudo systemctl stop KlipperLCD.service
```

---

### Step 3: Navigate to KlipperLCD and update git remote
```bash
cd ~/KlipperLCD
git remote set-url origin https://github.com/jcfield-boop/klipperlcd.git
git remote -v
```

You should see:
```
origin  https://github.com/jcfield-boop/klipperlcd.git (fetch)
origin  https://github.com/jcfield-boop/klipperlcd.git (push)
```

---

### Step 4: Pull the latest changes
```bash
git fetch origin
git pull origin main
```

You should see the new files:
- `config.py`
- `install.sh`
- `KlipperLCD.cfg.example`
- `.gitignore`
- Updated `main.py`, `lcd.py`, `printer.py`, etc.

---

### Step 5: Run the installation script
```bash
chmod +x install.sh
./install.sh
```

The script will:
1. Auto-detect your username (`biqu`) and home directory
2. Create `~/printer_data/config/KlipperLCD.cfg` with defaults
3. Install the systemd service with correct paths
4. Ask if you want to enable and start the service

**Answer "Yes" to both questions to enable and start the service.**

---

### Step 6: Verify the service is running
```bash
sudo systemctl status KlipperLCD.service
```

You should see `Active: active (running)` in green.

---

### Step 7: Check the logs
```bash
journalctl -u KlipperLCD.service -f
```

Look for:
- "Loaded configuration from: /home/biqu/printer_data/config/KlipperLCD.cfg"
- "KlipperLCD start"
- No errors about serial port (if LCD is connected)

Press `Ctrl+C` to exit the log viewer.

---

## Edit Configuration

### Option 1: Via Mainsail Web Interface (Easiest)
1. Open http://192.168.0.50 in your browser
2. Go to **Machine** tab
3. Find **KlipperLCD.cfg** in the configuration files list
4. Click to edit
5. Update your settings:
   - `serial_port` - Verify this matches your LCD connection
   - `moonraker_api_key` - Update if needed
   - Temperature presets for your materials
6. Save the file
7. Restart the service: `sudo systemctl restart KlipperLCD.service`

### Option 2: Via SSH
```bash
nano ~/printer_data/config/KlipperLCD.cfg
```

Edit your settings, then:
```bash
# Save: Ctrl+O, Enter
# Exit: Ctrl+X

# Restart service
sudo systemctl restart KlipperLCD.service
```

---

## Verify Config File Location

```bash
ls -la ~/printer_data/config/KlipperLCD.cfg
cat ~/printer_data/config/KlipperLCD.cfg | head -20
```

---

## Troubleshooting

### Service won't start
```bash
# Check detailed status
sudo systemctl status KlipperLCD.service

# View full logs
journalctl -u KlipperLCD.service -n 100

# Test manually
python3 ~/KlipperLCD/main.py
```

### Serial port issues
```bash
# List available serial ports
ls /dev/tty* | grep -E "(USB|ACM|AMA)"

# Check current config
grep serial_port ~/printer_data/config/KlipperLCD.cfg

# Update if needed
nano ~/printer_data/config/KlipperLCD.cfg
# Change serial_port to the correct device
# Save and restart service
```

### Revert to original if needed
```bash
cd ~/KlipperLCD
git remote set-url origin https://github.com/joakimtoe/KlipperLCD.git
git fetch origin
git reset --hard origin/main
sudo systemctl restart KlipperLCD.service
```

---

## After Deployment

Your KlipperLCD is now fully configured and no longer requires editing code!

**All configuration is now in:**
`~/printer_data/config/KlipperLCD.cfg`

**Manage the service:**
- Start: `sudo systemctl start KlipperLCD.service`
- Stop: `sudo systemctl stop KlipperLCD.service`
- Restart: `sudo systemctl restart KlipperLCD.service`
- Status: `sudo systemctl status KlipperLCD.service`
- Logs: `journalctl -u KlipperLCD.service -f`

**Edit config:**
- Mainsail: Machine tab → KlipperLCD.cfg
- SSH: `nano ~/printer_data/config/KlipperLCD.cfg`
- Always restart after editing: `sudo systemctl restart KlipperLCD.service`
