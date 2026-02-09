# 🔧 Troubleshooting Guide

Common issues and solutions for ATO Aquarium Monitor.

## Quick Diagnostics

Run these commands first:

```bash
# Check service status
sudo systemctl status ato-monitor.service

# View recent logs
journalctl -u ato-monitor.service -n 50

# Check MQTT messages
mosquitto_sub -h YOUR_HA_IP -t 'aquarium/#' -v

# Test GPIO
gpio readall
```

---

## Temperature Sensor Issues

### Problem: No temperature sensor detected

**Symptoms:**
- "Temperature sensor: Not detected" in logs
- No `28-*` folder in `/sys/bus/w1/devices/`
- Temperature shows "unavailable" in HA

**Solutions:**

1. **Check 1-Wire is enabled:**
   ```bash
   cat /boot/config.txt | grep w1-gpio
   # Should show: dtoverlay=w1-gpio,gpiopin=4
   ```

2. **Reload 1-Wire modules:**
   ```bash
   sudo modprobe -r w1-therm
   sudo modprobe -r w1-gpio
   sudo modprobe w1-gpio
   sudo modprobe w1-therm
   ls /sys/bus/w1/devices/
   ```

3. **Check wiring:**
   - Red → 3.3V (Pin 1)
   - Black → GND (Pin 6)
   - Yellow → GPIO 4 (Pin 7)
   - 4.7kΩ resistor between Red and Yellow

4. **Test sensor directly:**
   ```bash
   cat /sys/bus/w1/devices/28-*/w1_slave
   # Should show temperature reading
   ```

5. **Try different GPIO pin:**
   Edit `/boot/config.txt`:
   ```
   dtoverlay=w1-gpio,gpiopin=22  # Try GPIO 22
   ```
   Reconnect sensor to Pin 15 (GPIO 22)
   Reboot

### Problem: Temperature readings unstable

**Symptoms:**
- Temperature jumps around wildly
- Readings freeze then update
- "CRC error" in logs

**Solutions:**

1. **Check pull-up resistor:**
   - Must be 4.7kΩ (not 1kΩ or 10kΩ)
   - Connected between Data and VCC
   - Use multimeter to verify

2. **Check cable length:**
   - Keep DS18B20 cable < 3 meters
   - Use shielded cable for longer runs
   - Add stronger pull-up (2.2kΩ) for long cables

3. **Check for interference:**
   - Keep away from power cables
   - Separate from pump wires
   - Use shielded cable if needed

4. **Verify power:**
   ```bash
   # Measure voltage at sensor
   # Should be 3.3V ±0.1V
   ```

### Problem: Temperature reads incorrectly

**Symptoms:**
- Always shows 85°C or -127°C
- Readings way off from actual
- Constant wrong temperature

**Solutions:**

1. **85°C = Sensor not initialized:**
   - Power cycle the Pi
   - Check sensor is properly connected
   - Try different sensor

2. **-127°C = Communication error:**
   - Check wiring connections
   - Verify pull-up resistor
   - Replace sensor if damaged

3. **Slightly off = Needs calibration:**
   - See [CALIBRATION.md](CALIBRATION.md)
   - Use reference thermometer
   - Set offset in Home Assistant

---

## MQTT Connection Issues

### Problem: Cannot connect to MQTT broker

**Symptoms:**
- "Connection refused" in logs
- Script exits immediately
- No data in Home Assistant

**Solutions:**

1. **Check Mosquitto is running:**
   - Open Home Assistant
   - Settings → Add-ons
   - Mosquitto broker should be "Running"

2. **Verify credentials:**
   Edit `config.py`:
   ```python
   MQTT_BROKER = "192.168.1.100"  # Correct IP?
   MQTT_USER = "username"          # Correct username?
   MQTT_PASS = "password"          # Correct password?
   ```

3. **Test MQTT manually:**
   ```bash
   # Subscribe to test connection
   mosquitto_sub -h 192.168.1.100 -t test -u username -P password
   
   # In another terminal, publish
   mosquitto_pub -h 192.168.1.100 -t test -m "hello" -u username -P password
   
   # Should see "hello" in first terminal
   ```

4. **Check firewall:**
   ```bash
   # On Home Assistant host
   sudo ufw allow 1883
   ```

5. **Check network:**
   ```bash
   ping 192.168.1.100  # Can reach HA?
   telnet 192.168.1.100 1883  # Port open?
   ```

### Problem: MQTT connects but no data appears

**Symptoms:**
- Script runs without errors
- MQTT connection successful
- But no sensors in Home Assistant

**Solutions:**

1. **Check MQTT integration in HA:**
   - Settings → Devices & Services
   - MQTT should be configured
   - Click "Configure" → "Listen to a topic"
   - Enter: `aquarium/#`
   - Should see messages

2. **Verify configuration.yaml:**
   - Check sensors are defined
   - Correct topics used
   - No YAML syntax errors

3. **Restart Home Assistant:**
   - Developer Tools → YAML → Restart

4. **Check entity naming:**
   - Developer Tools → States
   - Search for "ato"
   - Entities should appear

---

## Float Switch Issues

### Problem: Float switch not triggering

**Symptoms:**
- No pump activation
- GPIO always shows same state
- No response to water level

**Solutions:**

1. **Test GPIO directly:**
   ```bash
   python3 << 'PYEOF'
   import RPi.GPIO as GPIO
   import time
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
   
   for i in range(10):
       print(f"Float state: {GPIO.input(17)}")
       time.sleep(1)
   
   GPIO.cleanup()
   PYEOF
   ```
   Manually move float up/down - should see 0 and 1

2. **Check wiring:**
   - One wire to GPIO 17 (Pin 11)
   - Other wire to GND (Pin 6)
   - Connections tight

3. **Test float switch separately:**
   - Disconnect from Pi
   - Use multimeter in continuity mode
   - Move float up/down
   - Should beep/show continuity changes

4. **Verify switch logic:**
   - Some switches are NO (Normally Open)
   - Some are NC (Normally Closed)
   - Code expects LOW when needs water

### Problem: False triggers

**Symptoms:**
- Pump activates randomly
- Multiple triggers in short time
- No actual water level change

**Solutions:**

1. **Check float for debris:**
   - Clean float switch
   - Remove algae/buildup
   - Ensure float moves freely

2. **Add debouncing in code:**
   (Already implemented, but verify)

3. **Check for electrical noise:**
   - Keep float wire away from pump power
   - Use shielded cable if needed
   - Add 0.1µF capacitor across switch

4. **Verify pull-up:**
   Code should have:
   ```python
   GPIO.setup(FLOAT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
   ```

---

## Relay / Pump Issues

### Problem: Relay not clicking

**Symptoms:**
- No relay click sound
- Pump doesn't run
- Relay LED not lighting

**Solutions:**

1. **Check relay power:**
   ```bash
   # Measure voltage at relay VCC
   # Should be 5V
   ```

2. **Test GPIO output:**
   ```bash
   python3 << 'PYEOF'
   import RPi.GPIO as GPIO
   import time
   
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(27, GPIO.OUT)
   
   print("Relay ON")
   GPIO.output(27, GPIO.LOW)
   time.sleep(2)
   
   print("Relay OFF")
   GPIO.output(27, GPIO.HIGH)
   time.sleep(2)
   
   GPIO.cleanup()
   PYEOF
   ```
   Should hear click twice

3. **Check wiring:**
   - VCC to 5V
   - GND to GND
   - IN1 to GPIO 27
   - All connections secure

4. **Verify relay logic:**
   - Most relays are active-LOW
   - GPIO LOW = Relay ON
   - GPIO HIGH = Relay OFF

### Problem: Pump doesn't run despite relay clicking

**Symptoms:**
- Relay clicks
- LED lights up
- But pump doesn't start

**Solutions:**

1. **Check pump power:**
   - Measure 12V at COM terminal
   - Measure 12V at NO terminal (when relay ON)
   - Check pump itself gets 12V

2. **Test pump directly:**
   - Disconnect from relay
   - Connect directly to 12V PSU
   - If runs → Relay wiring issue
   - If doesn't run → Pump faulty

3. **Check relay contacts:**
   - Use multimeter continuity test
   - COM to NO should be closed when relay ON
   - Contacts may be worn/dirty

4. **Verify wiring:**
   ```
   12V+ → Relay COM
   Relay NO → Pump +
   12V- → Pump -
   ```

### Problem: Pump timeout / emergency stop

**Symptoms:**
- Pump runs for 30 seconds then stops
- "PUMP TIMEOUT" alert
- Monitoring disabled

**Solutions:**

1. **Check float switch:**
   - May be stuck LOW
   - Clean float mechanism
   - Verify switch works properly

2. **Check for actual leak:**
   - Water draining faster than pump fills
   - Massive evaporation
   - Siphon or overflow issue

3. **Adjust timeout if needed:**
   Edit `config.py`:
   ```python
   MAX_FILL_DURATION = 45  # Increase if pump is slow
   ```

4. **Check pump flow rate:**
   - May be too slow
   - Clogged intake
   - Weak pump needs replacement

---

## Service / System Issues

### Problem: Service won't start

**Symptoms:**
- `systemctl status` shows "failed"
- Script doesn't run on boot
- Manual run works fine

**Solutions:**

1. **Check service file:**
   ```bash
   cat /etc/systemd/system/ato-monitor.service
   ```
   Verify paths are correct

2. **Check permissions:**
   ```bash
   ls -l /home/pi/ato-aquarium-monitor/ato_monitor.py
   # Should be readable by pi user
   
   # Add pi to gpio group if needed
   sudo usermod -a -G gpio pi
   ```

3. **Check for errors:**
   ```bash
   journalctl -u ato-monitor.service -n 100
   ```

4. **Run manually to see errors:**
   ```bash
   cd /home/pi/ato-aquarium-monitor
   python3 ato_monitor.py
   ```

5. **Reload systemd:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart ato-monitor.service
   ```

### Problem: Config file not found

**Symptoms:**
- "config.py not found" error
- Script exits immediately
- ImportError

**Solutions:**

1. **Copy example config:**
   ```bash
   cd /home/pi/ato-aquarium-monitor
   cp config.example.py config.py
   nano config.py  # Edit with your settings
   ```

2. **Check file exists:**
   ```bash
   ls -l config.py
   # Should exist in project directory
   ```

3. **Verify Python path:**
   Script should be run from project directory

### Problem: GPIO permission denied

**Symptoms:**
- "Permission denied" when accessing GPIO
- Script fails on GPIO setup
- Works with sudo but not as service

**Solutions:**

1. **Add user to gpio group:**
   ```bash
   sudo usermod -a -G gpio pi
   sudo reboot
   ```

2. **Check GPIO permissions:**
   ```bash
   ls -l /dev/gpiomem
   # Should be accessible by gpio group
   ```

3. **Use gpio group in service:**
   Service file should have:
   ```ini
   [Service]
   User=pi
   Group=pi
   ```

---

## Data / Calibration Issues

### Problem: Calibration not improving

**Symptoms:**
- Confidence stays at 0-20%
- Auto-calibration not working
- Values don't change

**Solutions:**

1. **Record refills properly:**
   - Must enter exact amount added
   - Use "Record Refill" in HA
   - Don't skip refills

2. **Check refill recording:**
   ```bash
   # View calibration data
   python3 << 'PYEOF'
   import pickle
   with open('/home/pi/ato_calibration.pkl', 'rb') as f:
       data = pickle.load(f)
   print(f"Refills: {len(data['refill_history'])}")
   print(f"Confidence: {data['confidence']}%")
   PYEOF
   ```

3. **Wait for more data:**
   - Need at least 2 refills
   - 5 refills for 100% confidence
   - Be patient!

4. **Verify activations tracked:**
   Check `activations_since_refill` increases

### Problem: Data files corrupted

**Symptoms:**
- Pickle load errors
- History lost
- Script crashes on startup

**Solutions:**

1. **Backup and reset:**
   ```bash
   cd /home/pi
   cp ato_*.pkl ato_backup/  # Backup
   rm ato_*.pkl  # Delete corrupted files
   # Script will create new ones
   ```

2. **Check disk space:**
   ```bash
   df -h
   # Ensure SD card not full
   ```

3. **Check file permissions:**
   ```bash
   ls -l /home/pi/ato_*.pkl
   # Should be owned by pi user
   ```

---

## Home Assistant Issues

### Problem: Entities not appearing

**Symptoms:**
- No `sensor.ato_*` entities
- Developer Tools → States shows nothing
- Dashboard empty

**Solutions:**

1. **Check MQTT integration:**
   - Settings → Devices & Services
   - MQTT must be configured

2. **Verify configuration:**
   ```yaml
   # Check configuration.yaml has mqtt: section
   mqtt:
     sensor:
       - name: "ATO Daily Usage"
         # ... etc
   ```

3. **Check configuration validity:**
   - Developer Tools → YAML
   - Click "Check Configuration"
   - Fix any errors

4. **Restart HA:**
   - Settings → System → Restart

5. **Check MQTT topics:**
   - Developer Tools → MQTT
   - Listen to: `aquarium/#`
   - Should see messages

### Problem: Dashboard not working

**Symptoms:**
- YAML errors
- Cards not displaying
- ApexCharts not rendering

**Solutions:**

1. **Install required components:**
   - HACS → Frontend
   - Install: ApexCharts Card
   - Install: Card Mod
   - Install: Layout Card

2. **Check YAML syntax:**
   - Use YAML validator
   - Check indentation
   - Verify all brackets/quotes

3. **Clear browser cache:**
   - Ctrl+Shift+R (hard refresh)
   - Clear cache completely
   - Restart browser

4. **Check console errors:**
   - F12 → Console tab
   - Look for JavaScript errors
   - Fix component issues

---

## Alert Issues

### Problem: No alerts triggered

**Symptoms:**
- Critical conditions but no notification
- Alerts not in history
- No messages on phone

**Solutions:**

1. **Check monitoring enabled:**
   - Switch in HA should be ON
   - Service should be running

2. **Verify alert thresholds:**
   Edit `config.py`:
   ```python
   TEMP_MAX_WARNING = 28.0  # Set appropriately
   MAX_ACTIVATIONS_PER_HOUR = 3
   ```

3. **Check automation:**
   ```yaml
   # In automations.yaml
   - alias: "ATO Critical Alert"
     trigger:
       platform: mqtt
       topic: "aquarium/ato/alert_critical"
     # ... action to notify
   ```

4. **Test notifications:**
   - Send test notification
   - Verify phone/device receives
   - Check notification settings

### Problem: Too many false alerts

**Symptoms:**
- Constant warnings
- Normal operation triggers alerts
- Alert fatigue

**Solutions:**

1. **Adjust thresholds:**
   ```python
   MAX_ACTIVATIONS_PER_HOUR = 5  # Increase
   TEMP_MAX_WARNING = 30.0        # Widen range
   ```

2. **Wait for calibration:**
   - Alerts more accurate after calibration
   - Need baseline data (1-2 weeks)

3. **Check seasonal variations:**
   - Summer = higher evaporation
   - Adjust MAX_DAILY_USAGE seasonally

---

## Emergency Procedures

### System Not Responding

1. **Restart service:**
   ```bash
   sudo systemctl restart ato-monitor.service
   ```

2. **Reboot Pi:**
   ```bash
   sudo reboot
   ```

3. **Manual mode:**
   - Disable monitoring in HA
   - Control pump manually
   - Investigate issue

### Water Emergency

1. **Disable ATO immediately:**
   - Home Assistant → Switch OFF
   - Or unplug pump power

2. **Check for leaks:**
   - Inspect all connections
   - Check tank glass
   - Verify no siphons

3. **Manual water top-off:**
   - Add water manually
   - Don't rely on ATO

4. **Fix then re-enable:**
   - Only after issue resolved
   - Monitor closely

---

## Getting Help

### Information to Provide

When asking for help, include:

1. **System info:**
   ```bash
   uname -a
   python3 --version
   cat /etc/os-release
   ```

2. **Service logs:**
   ```bash
   journalctl -u ato-monitor.service -n 100
   ```

3. **Configuration** (remove passwords!):
   ```bash
   cat config.py | grep -v PASS
   ```

4. **Wiring photo**
5. **Error messages**
6. **What you've tried**

### Support Channels

- 🐛 **GitHub Issues**: For bugs
- 💬 **Discussions**: For questions
- 📧 **Email**: For private issues
- 🏠 **Home Assistant Forum**: For HA-specific issues

---

**Most issues can be resolved with these steps! 🔧✨**

Still stuck? Open an issue on GitHub with details!
