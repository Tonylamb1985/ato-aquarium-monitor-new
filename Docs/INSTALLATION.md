# 📦 Installation Guide

Complete step-by-step installation guide for ATO Aquarium Monitor.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Hardware Setup](#hardware-setup)
3. [Software Installation](#software-installation)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Service Installation](#service-installation)
7. [Home Assistant Setup](#home-assistant-setup)

---

## Prerequisites

### Hardware Requirements

- **Raspberry Pi 3 or newer** (Raspberry Pi 4 recommended)
- **MicroSD card** (16GB minimum, 32GB recommended, Class 10)
- **Power supply** (5V 2.5A minimum for Pi 3, 3A for Pi 4)
- **8-Channel Relay Module** (5V with optocouplers)
- **DS18B20 Temperature Sensor** (waterproof version)
- **4.7kΩ Resistor** (for DS18B20 pull-up)
- **D-D Float Switch** (or compatible ATO float switch)
- **12V Power Supply** (for ATO pump, 500mA+)
- **Jumper wires** (male-to-female)
- **Breadboard or soldering equipment**

### Software Requirements

- **Raspberry Pi OS** (Bullseye or newer)
- **Home Assistant** (any version with MQTT support)
- **Mosquitto MQTT Broker** (installed in Home Assistant)
- **Python 3.7+** (included in Raspberry Pi OS)

### Skills Required

- Basic command line knowledge
- Basic electronics (connecting wires)
- Soldering (optional but recommended)
- Home Assistant configuration

---

## Hardware Setup

### Step 1: Prepare Raspberry Pi

1. **Install Raspberry Pi OS:**
   - Download [Raspberry Pi Imager](https://www.raspberrypi.org/software/)
   - Flash Raspberry Pi OS to SD card
   - Enable SSH during setup (recommended)
   - Boot Raspberry Pi and connect to network

2. **Update System:**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

3. **Enable Interfaces:**
   ```bash
   sudo raspi-config
   ```
   - Navigate to "Interface Options"
   - Enable: SSH, I2C (optional), SPI (optional)
   - Do NOT enable 1-Wire yet (we'll do this later with GPIO 4)

### Step 2: Wire DS18B20 Temperature Sensor

**Components needed:**
- DS18B20 waterproof sensor (3 wires: Red, Black, Yellow)
- 4.7kΩ resistor

**Wiring:**
```
DS18B20 Red (VCC)    → Raspberry Pi Pin 1 (3.3V)
DS18B20 Black (GND)  → Raspberry Pi Pin 6 (GND)
DS18B20 Yellow (Data)→ Raspberry Pi Pin 7 (GPIO 4)

4.7kΩ Resistor between Yellow (Data) and Red (3.3V)
```

**Important:** The pull-up resistor is critical for reliable readings!

### Step 3: Wire Float Switch

**Components needed:**
- D-D Float switch (2 wires)

**Wiring:**
```
Float Switch Wire 1 → Raspberry Pi Pin 11 (GPIO 17)
Float Switch Wire 2 → Raspberry Pi Pin 6 (GND)
```

**Note:** Float switch should be LOW (0) when water needs filling, HIGH (1) when full.

### Step 4: Wire Relay Module

**Components needed:**
- 8-channel relay module

**Wiring:**
```
Relay VCC  → Raspberry Pi Pin 2 (5V)
Relay GND  → Raspberry Pi Pin 9 (GND)
Relay IN1  → Raspberry Pi Pin 13 (GPIO 27)

Relay COM  → 12V Power Supply (+)
Relay NO   → ATO Pump (+)

12V PSU (-) → ATO Pump (-)
```

**Important:** Most relay modules are active-LOW (LOW = ON, HIGH = OFF)

### Step 5: Complete Wiring Diagram

```
┌─────────────────────────────────────────┐
│         RASPBERRY PI 3/4                │
│                                         │
│  Pin 1  (3.3V)     ●─┬─ DS18B20 Red    │
│                      │                  │
│                   4.7kΩ                 │
│                      │                  │
│  Pin 7  (GPIO 4)   ●─┴─ DS18B20 Yellow │
│  Pin 6  (GND)      ●─── DS18B20 Black  │
│                                         │
│  Pin 11 (GPIO 17)  ●─── Float Wire 1   │
│  Pin 6  (GND)      ●─── Float Wire 2   │
│                                         │
│  Pin 2  (5V)       ●─── Relay VCC      │
│  Pin 9  (GND)      ●─── Relay GND      │
│  Pin 13 (GPIO 27)  ●─── Relay IN1      │
│                                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         RELAY & PUMP                    │
│                                         │
│  Relay COM ← 12V PSU (+)                │
│  Relay NO  → ATO Pump (+)               │
│  12V PSU (-)→ ATO Pump (-)              │
│                                         │
└─────────────────────────────────────────┘
```

### Step 6: Verify Wiring

**Before powering on:**
1. Double-check all connections
2. Ensure no short circuits
3. Verify voltage levels (3.3V for sensor, 5V for relay, 12V for pump)
4. Check polarity of power connections

---

## Software Installation

### Step 1: Install Dependencies

```bash
# Update package lists
sudo apt update

# Install Python dependencies
pip3 install paho-mqtt --break-system-packages
pip3 install RPi.GPIO --break-system-packages

# Install Git (if not already installed)
sudo apt install git -y
```

### Step 2: Clone Repository

```bash
cd /home/pi
git clone https://github.com/tonylamb1985/ato-aquarium-monitor.git
cd ato-aquarium-monitor
```

Replace `tonylamb1985` with the actual GitHub username.

### Step 3: Enable 1-Wire Interface

```bash
# Edit boot configuration
sudo nano /boot/config.txt

# Add this line at the end of the file:
dtoverlay=w1-gpio,gpiopin=4

# Save and exit (Ctrl+X, Y, Enter)

# Reboot to apply changes
sudo reboot
```

### Step 4: Verify Temperature Sensor

After reboot:

```bash
# Load 1-Wire kernel modules
sudo modprobe w1-gpio
sudo modprobe w1-therm

# Check for sensor
ls /sys/bus/w1/devices/

# You should see something like: 28-xxxxxxxxxxxx
# That's your DS18B20 sensor!

# Test reading
cat /sys/bus/w1/devices/28-*/w1_slave

# Output should show temperature in millidegrees Celsius
```

---

## Configuration

### Step 1: Create Configuration File

```bash
cd /home/pi/ato-aquarium-monitor

# Copy example configuration
cp config.example.py config.py

# Edit configuration
nano config.py
```

### Step 2: Update Configuration

**Required changes:**

```python
# MQTT Broker (Your Home Assistant IP)
MQTT_BROKER = "192.168.1.100"  # Change to your HA IP
MQTT_PORT = 1883
MQTT_USER = "your_mqtt_username"  # Your MQTT username
MQTT_PASS = "your_mqtt_password"  # Your MQTT password

# GPIO Pins (usually don't need to change)
FLOAT_PIN = 17
PUMP_PIN = 27

# Tank Configuration
RESERVOIR_CAPACITY = 23.0  # Your reservoir size in liters
LITERS_PER_ACTIVATION = 1.0  # Initial estimate (will auto-calibrate)

# Temperature Thresholds (adjust for your fish)
TEMP_MIN_WARNING = 22.0    # Minimum safe temperature
TEMP_MAX_WARNING = 28.0    # Maximum safe temperature
TEMP_MIN_CRITICAL = 20.0   # Critical low
TEMP_MAX_CRITICAL = 30.0   # Critical high
```

Save and exit (Ctrl+X, Y, Enter).

---

## Testing

### Step 1: Test Run

```bash
cd /home/pi/ato-aquarium-monitor

# Run the script
python3 ato_monitor.py
```

**Expected output:**
```
🚀 Starting ATO Aquarium Monitor...
============================================================
✅ Loaded 0 historical activations
✅ Loaded calibration: 1.0L/activation (confidence: 0%)
✅ Loaded 0 historical alerts
✅ Loaded 0 pump performance records
✅ Loaded 0 temperature readings
✅ Temperature sensor found: /sys/bus/w1/devices/28-xxxxxxxxxxxx

✅ ATO Monitor Started
   Monitoring: ENABLED
   Float switch: GPIO 17
   Pump relay: GPIO 27
   Temperature sensor: Found
   Calibration: 1.0L/activation (confidence: 0%)
   Max fill duration: 30s
   MQTT broker: 192.168.1.100:1883
   Current season: Winter ❄️
============================================================

💚 System running... Press Ctrl+C to stop
```

### Step 2: Test Temperature Sensor

While script is running, you should see temperature in Home Assistant.

Check manually:
```bash
cat /sys/bus/w1/devices/28-*/w1_slave
```

### Step 3: Test Float Switch

**⚠️ CAUTION:** Test safely without water first!

```bash
# In another terminal:
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP); print('Float state:', GPIO.input(17)); GPIO.cleanup()"

# Should print 0 or 1
# 0 = LOW (needs water)
# 1 = HIGH (full)
```

### Step 4: Test Relay

**⚠️ CAUTION:** Disconnect pump before testing!

```bash
# Test relay manually
python3 -c "import RPi.GPIO as GPIO; import time; GPIO.setmode(GPIO.BCM); GPIO.setup(27, GPIO.OUT); print('Relay ON'); GPIO.output(27, GPIO.LOW); time.sleep(2); print('Relay OFF'); GPIO.output(27, GPIO.HIGH); GPIO.cleanup()"

# Should hear relay click ON then OFF
```

### Step 5: Stop Test

Press `Ctrl+C` to stop the script.

---

## Service Installation

### Step 1: Edit Service File

```bash
# Check service file
nano /home/pi/ato-aquarium-monitor/ato-monitor.service

# Verify paths are correct:
# WorkingDirectory=/home/pi/ato-aquarium-monitor
# ExecStart=/usr/bin/python3 /home/pi/ato-aquarium-monitor/ato_monitor.py
```

### Step 2: Install Service

```bash
# Copy service file to systemd
sudo cp /home/pi/ato-aquarium-monitor/ato-monitor.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable ato-monitor.service

# Start service
sudo systemctl start ato-monitor.service
```

### Step 3: Verify Service

```bash
# Check service status
sudo systemctl status ato-monitor.service

# Should show:
# ● ato-monitor.service - ATO Aquarium Monitor Service
#    Loaded: loaded
#    Active: active (running)

# View live logs
journalctl -u ato-monitor.service -f

# Press Ctrl+C to stop viewing logs
```

### Service Management Commands

```bash
# Start service
sudo systemctl start ato-monitor.service

# Stop service
sudo systemctl stop ato-monitor.service

# Restart service
sudo systemctl restart ato-monitor.service

# Check status
sudo systemctl status ato-monitor.service

# View logs (last 50 lines)
journalctl -u ato-monitor.service -n 50

# View live logs
journalctl -u ato-monitor.service -f

# Disable auto-start
sudo systemctl disable ato-monitor.service

# Enable auto-start
sudo systemctl enable ato-monitor.service
```

---

## Home Assistant Setup

### Step 1: Install Mosquitto MQTT Broker

1. Open Home Assistant
2. Go to **Settings** → **Add-ons**
3. Click **Add-on Store**
4. Search for "Mosquitto broker"
5. Click **Install**
6. After installation:
   - Go to **Configuration** tab
   - Add username/password (same as in config.py)
   - Click **Save**
   - Start the add-on
   - Enable "Start on boot"

### Step 2: Configure MQTT Integration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "MQTT"
4. Enter broker details:
   - Broker: `localhost` (or `core-mosquitto`)
   - Port: `1883`
   - Username: (your MQTT username)
   - Password: (your MQTT password)
5. Click **Submit**

### Step 3: Add Configuration

1. Edit your Home Assistant `configuration.yaml`:
   ```bash
   # In Home Assistant
   Configuration → Edit in File Editor → configuration.yaml
   ```

2. Copy contents from:
   `/home/pi/ato-aquarium-monitor/home-assistant/configuration.yaml`

3. Paste into your `configuration.yaml`

4. **Check Configuration:**
   - Go to **Developer Tools** → **YAML**
   - Click **Check Configuration**
   - Should show "Configuration valid!"

5. **Restart Home Assistant:**
   - Go to **Settings** → **System**
   - Click **Restart**

### Step 4: Verify Entities

1. Go to **Developer Tools** → **States**
2. Search for `ato`
3. You should see entities like:
   - `sensor.ato_tank_temperature`
   - `sensor.ato_reservoir_level`
   - `sensor.ato_daily_usage`
   - `switch.ato_monitoring_enable`
   - etc.

### Step 5: Create Dashboard

1. Go to **Settings** → **Dashboards**
2. Click **Add Dashboard**
3. Name it "Aquarium ATO"
4. Click **Save**
5. Open the new dashboard
6. Click **Edit Dashboard** → **3 dots** → **Raw configuration editor**
7. Copy YAML from each dashboard file in:
   - `home-assistant/dashboard-overview.yaml`
   - `home-assistant/dashboard-analytics.yaml`
   - etc.
8. Create tabs and paste YAML for each

---

## Troubleshooting

### No Temperature Readings

```bash
# Check 1-Wire is enabled
ls /sys/bus/w1/devices/

# Should show 28-xxxxxxxxxxxx
# If not, check /boot/config.txt has:
# dtoverlay=w1-gpio,gpiopin=4

# Reload modules
sudo modprobe -r w1-therm
sudo modprobe -r w1-gpio
sudo modprobe w1-gpio
sudo modprobe w1-therm
```

### MQTT Connection Failed

```bash
# Test MQTT from Pi
mosquitto_sub -h YOUR_HA_IP -t aquarium/# -u username -P password

# If fails, check:
# 1. Home Assistant IP is correct
# 2. Mosquitto broker is running
# 3. Username/password are correct
# 4. No firewall blocking port 1883
```

### Service Won't Start

```bash
# Check service logs
journalctl -u ato-monitor.service -n 100

# Common issues:
# - config.py not found (did you copy config.example.py?)
# - Wrong paths in service file
# - Missing Python dependencies
# - GPIO permission issues
```

### GPIO Permission Denied

```bash
# Add user to gpio group
sudo usermod -a -G gpio pi

# Reboot
sudo reboot
```

---

## Next Steps

1. ✅ **Calibrate Temperature Sensor**
   - Use reference thermometer
   - Set calibration offset in Home Assistant

2. ✅ **Monitor for 24 Hours**
   - Verify all sensors working
   - Check for any alerts
   - Ensure pump activates correctly

3. ✅ **Record First Refill**
   - Measure exact amount added
   - Enter in Home Assistant
   - System will auto-calibrate

4. ✅ **Set Up Notifications**
   - Configure mobile app
   - Test critical alerts
   - Adjust thresholds if needed

5. ✅ **Enjoy Peace of Mind!**
   - Your aquarium is now monitored 24/7
   - Auto-calibrating system
   - Complete historical data

---

**Congratulations! Your ATO Monitoring System is now installed! 🎉🐠**
