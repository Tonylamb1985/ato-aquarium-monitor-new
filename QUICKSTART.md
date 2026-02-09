# 🚀 Quick Start Guide

Get your ATO Aquarium Monitor up and running in 30 minutes!

## Prerequisites Checklist

- [ ] Raspberry Pi 3 (or newer) with Raspbian/Raspberry Pi OS
- [ ] MicroSD card (16GB+) with OS installed
- [ ] Home Assistant running with MQTT broker (Mosquitto)
- [ ] Hardware components (see README.md)
- [ ] Basic soldering skills (for connecting sensors)

## Installation Steps

### 1. Prepare Raspberry Pi (5 minutes)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Git
sudo apt install git -y

# Install Python dependencies
pip3 install paho-mqtt --break-system-packages
pip3 install RPi.GPIO --break-system-packages
```

### 2. Enable 1-Wire for Temperature Sensor (2 minutes)

```bash
# Edit boot config
sudo nano /boot/config.txt

# Add this line at the end:
dtoverlay=w1-gpio,gpiopin=4

# Save (Ctrl+X, Y, Enter) and reboot
sudo reboot
```

### 3. Clone Repository (1 minute)

```bash
cd /home/pi
git clone https://github.com/tonylamb1985/ato-aquarium-monitor.git
cd ato-aquarium-monitor
```

### 4. Configure Settings (3 minutes)

```bash
# Copy example config
cp config.example.py config.py

# Edit configuration
nano config.py
```

Update these values:
- `MQTT_BROKER = "192.168.1.XXX"` ← Your Home Assistant IP
- `MQTT_USER = "your_username"`
- `MQTT_PASS = "your_password"`

Save and exit (Ctrl+X, Y, Enter)

### 5. Wire Hardware (10 minutes)

Connect components according to wiring diagram:

```
DS18B20 → GPIO 4 (Pin 7) with 4.7kΩ pull-up
Float Switch → GPIO 17 (Pin 11)
Relay IN1 → GPIO 27 (Pin 13)
```

See [docs/WIRING.md](docs/WIRING.md) for detailed diagram.

### 6. Test Run (2 minutes)

```bash
# Test the script
python3 ato_monitor.py

# You should see:
# "ATO Monitor Started with Temperature Monitoring"
# "Temperature sensor: Found"
# "Monitoring: ENABLED"
```

Press Ctrl+C to stop.

### 7. Install as Service (3 minutes)

```bash
# Copy service file
sudo cp ato-monitor.service /etc/systemd/system/

# Enable service
sudo systemctl enable ato-monitor.service

# Start service
sudo systemctl start ato-monitor.service

# Check status
sudo systemctl status ato-monitor.service
```

### 8. Configure Home Assistant (5 minutes)

1. Open Home Assistant
2. Go to **Settings** → **Devices & Services**
3. Make sure MQTT integration is set up
4. Add configuration from `home-assistant/configuration.yaml` to your `configuration.yaml`
5. Restart Home Assistant
6. Check **Developer Tools** → **States** for `sensor.ato_*` entities

### 9. Add Dashboard (3 minutes)

1. Go to **Settings** → **Dashboards**
2. Create new dashboard: "Aquarium ATO"
3. Add tabs using YAML from `home-assistant/dashboard-*.yaml` files
4. Save and view!

### 10. Calibrate (2 minutes)

1. Go to Settings tab in dashboard
2. Use reference thermometer to calibrate temperature sensor
3. System will auto-calibrate water usage after first few refills

## Verification Checklist

- [ ] Script is running: `sudo systemctl status ato-monitor.service`
- [ ] Temperature reading in Home Assistant
- [ ] Reservoir level showing correctly
- [ ] Float switch triggers pump (test safely!)
- [ ] Alerts working (try disabling monitoring)
- [ ] Dashboard displays all data

## Common Issues

**No temperature sensor detected?**
```bash
ls /sys/bus/w1/devices/
# Should show: 28-xxxxxxxxxxxx
```

**MQTT not connecting?**
- Check IP address in config.py
- Verify MQTT broker is running in Home Assistant
- Test with: `mosquitto_sub -h YOUR_IP -t aquarium/#`

**Service won't start?**
```bash
journalctl -u ato-monitor.service -n 50
# Check logs for errors
```

## Next Steps

1. Monitor for 24 hours to establish baseline
2. Record your first reservoir refill for calibration
3. Adjust alert thresholds for your tank
4. Set up mobile notifications
5. Join the community and share your setup!

## Need Help?

- 📚 Read full docs: [README.md](README.md)
- 🐛 Report issues: [GitHub Issues](https://github.com/tonylamb1985/ato-aquarium-monitor/issues)
- 💬 Ask questions: [Discussions](https://github.com/tonylamb1985/ato-aquarium-monitor/discussions)

---

**Congratulations! Your ATO monitoring system is now running! 🎉🐠**
