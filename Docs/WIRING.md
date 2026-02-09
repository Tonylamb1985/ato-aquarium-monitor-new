# 🔌 Wiring Guide

Complete wiring diagrams for ATO Aquarium Monitor hardware.

## GPIO Pin Reference (BCM Numbering)

| GPIO | Physical Pin | Component | Purpose |
|------|--------------|-----------|---------|
| GPIO 4 | Pin 7 | DS18B20 Data | Temperature sensor |
| GPIO 17 | Pin 11 | Float Switch | Water level detection |
| GPIO 27 | Pin 13 | Relay IN1 | Pump control |
| 3.3V | Pin 1 | DS18B20 VCC | Sensor power |
| 5V | Pin 2 | Relay VCC | Relay logic power |
| GND | Pins 6, 9, 14, 20 | Ground | Common ground |

## Complete System Diagram

```
                    RASPBERRY PI 3/4
    ┌───────────────────────────────────────────┐
    │  Pin Layout (Top View)                    │
    │                                           │
    │  1  3.3V     ●───┬──── DS18B20 Red (VCC) │
    │  3  GPIO 2   ●   │                        │
    │  5  GPIO 3   ●   4.7kΩ (Pull-up)         │
    │  7  GPIO 4   ●───┴──── DS18B20 Yellow    │
    │  9  GND      ●──────── DS18B20 Black     │
    │ 11  GPIO 17  ●──────── Float Switch 1    │
    │ 13  GPIO 27  ●──────── Relay IN1         │
    │                                           │
    │  2  5V       ●──────── Relay VCC         │
    │  4  5V       ●                            │
    │  6  GND      ●──────── Relay GND         │
    │  8  GPIO 14  ●         Float Switch 2    │
    │ 10  GPIO 15  ●                            │
    │ 12  GPIO 18  ●                            │
    │ 14  GND      ●                            │
    └───────────────────────────────────────────┘
```

## DS18B20 Temperature Sensor Wiring

### Waterproof DS18B20 (3-wire)

```
    DS18B20 Sensor
    ┌────────────┐
    │            │
    │   ▓▓▓▓▓▓   │  Waterproof Probe
    │   ▓▓▓▓▓▓   │
    └─────┬──────┘
          │
          │ 3 wires exit
          ├─── Red (VCC)    → Pi Pin 1 (3.3V)
          ├─── Black (GND)  → Pi Pin 6 (GND)
          └─── Yellow (Data)→ Pi Pin 7 (GPIO 4)

    4.7kΩ Resistor between Red (3.3V) and Yellow (Data)
```

### Pull-up Resistor Connection

```
    3.3V (Pin 1)
         │
         ├────────┐
         │        │
      4.7kΩ    ┌─┴─┐
         │     │ Pi│
         │     │   │ GPIO 4 (Pin 7)
         └─────┤   ├────── DS18B20 Yellow Wire
               │   │
         ┌─────┤   │
         │     └─┬─┘
       GND       │
    (Pin 6)      │
         │       │
         └───────┴────── DS18B20 Black Wire
```

## Float Switch Wiring

### Simple 2-Wire Float Switch

```
    Float Switch
    ┌──────────────┐
    │   ╭─╮  ╭─╮   │  
    │   │ │  │ │   │  Float mechanism
    │   ╰─╯  ╰─╯   │
    └───┬──────┬───┘
        │      │
      Wire 1  Wire 2
        │      │
        │      └────── Pi GND (Pin 6)
        │
        └───────────── Pi GPIO 17 (Pin 11)
```

**Logic:**
- Float DOWN (needs water): GPIO 17 = LOW (0)
- Float UP (tank full): GPIO 17 = HIGH (1)

## Relay Module Wiring

### 8-Channel Relay Module

```
    Relay Module
    ┌──────────────────────────────────────┐
    │  VCC  GND  IN1  IN2 ... IN8          │
    │   ●    ●    ●    ●       ●           │
    │   │    │    │                         │
    │   │    │    └──── Pi GPIO 27 (Pin 13)│
    │   │    └────────── Pi GND (Pin 9)    │
    │   └─────────────── Pi 5V (Pin 2)     │
    │                                       │
    │  [Relay 1] [Relay 2] ... [Relay 8]   │
    │   COM NO NC                           │
    │    ●  ●  ●                            │
    └────┼──┼──┼─────────────────────────── │
         │  │  │
         │  │  └── Normally Closed (unused)
         │  └───── Normally Open → Pump +
         └──────── Common ← 12V PSU +

    Relay Logic (Active-LOW):
    - GPIO 27 = HIGH → Relay OFF
    - GPIO 27 = LOW  → Relay ON
```

## Power Connections

### 12V Pump Circuit

```
    12V Power Supply         ATO Pump
    ┌──────────────┐        ┌─────────┐
    │              │        │         │
    │     (+)      ●────┐   │   (+)   │
    │              │    │   │         │
    │              │    │   │  Motor  │
    │              │    │   │         │
    │     (-)      ●────┼───┤   (-)   │
    │              │    │   │         │
    └──────────────┘    │   └─────────┘
                        │
                   Relay COM ───┘
                   Relay NO  ────┘

    When Relay ON:
    12V(+) → COM → NO → Pump(+)
    12V(-) → Pump(-)
    Circuit Complete → Pump Runs
```

## Safety Considerations

### ⚠️ IMPORTANT WARNINGS

1. **Never mix voltages:**
   - 3.3V for DS18B20
   - 5V for Relay logic
   - 12V for Pump (ISOLATED from Pi)

2. **Use optocoupler relay:**
   - Electrically isolates Pi from pump
   - Protects against voltage spikes
   - Required for safety

3. **Double-check polarity:**
   - Wrong polarity can damage components
   - DS18B20 is polarity-sensitive
   - Verify before powering on

4. **Waterproofing:**
   - Keep Pi and electronics DRY
   - Only submerge waterproof sensor
   - Use IP67+ enclosures near water

5. **Fusing:**
   - Add inline fuse to 12V circuit
   - Protects against short circuits
   - Use 1A fuse for typical ATO pump

## Testing Procedure

### 1. Visual Inspection
- [ ] All connections tight
- [ ] No exposed wires
- [ ] Correct pins used
- [ ] Pull-up resistor installed
- [ ] No short circuits

### 2. Multimeter Testing
```bash
# Power OFF testing:
- Continuity test all GND connections
- Check no short between VCC and GND
- Verify resistor is 4.7kΩ

# Power ON testing:
- Measure 3.3V at DS18B20 VCC
- Measure 5V at Relay VCC
- Measure 12V at pump terminals (relay OFF)
```

### 3. Component Testing
```bash
# Test DS18B20:
cat /sys/bus/w1/devices/28-*/w1_slave

# Test Float Switch:
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP); print(GPIO.input(17))"

# Test Relay (DISCONNECT PUMP FIRST):
python3 -c "import RPi.GPIO as GPIO; import time; GPIO.setmode(GPIO.BCM); GPIO.setup(27, GPIO.OUT); GPIO.output(27, GPIO.LOW); time.sleep(1); GPIO.output(27, GPIO.HIGH); GPIO.cleanup()"
```

## Troubleshooting

### Temperature Sensor Not Detected

**Check:**
1. Wiring connections (especially data wire to GPIO 4)
2. 4.7kΩ pull-up resistor present
3. 1-Wire enabled in /boot/config.txt
4. Sensor is not damaged

**Test:**
```bash
ls /sys/bus/w1/devices/
# Should show: 28-xxxxxxxxxxxx
```

### Float Switch Not Working

**Check:**
1. Connections secure
2. Float moves freely
3. Internal switch contacts clean
4. Pull-up resistor (internal to Pi) enabled in code

**Test:**
```bash
# Read state
gpio -g read 17
# Should be 0 or 1
```

### Relay Not Clicking

**Check:**
1. 5V power to relay module
2. GPIO 27 signal wire connected to IN1
3. Common ground between Pi and relay
4. Relay LEDs lighting up

**Test:**
```bash
# Toggle relay
gpio -g write 27 0  # Should click ON
gpio -g write 27 1  # Should click OFF
```

## Alternative Configurations

### Using Different GPIO Pins

Edit `config.py`:
```python
FLOAT_PIN = 17   # Change to your pin
PUMP_PIN = 27    # Change to your pin
```

For temperature sensor, edit `/boot/config.txt`:
```
dtoverlay=w1-gpio,gpiopin=4  # Change 4 to your pin
```

### Using 3.3V Relay

Some relay modules work with 3.3V:
```python
# Connect relay VCC to 3.3V instead of 5V
# Everything else same
```

### Multiple Temperature Sensors

```
# Add more DS18B20 sensors on same data line
# All sensors share GPIO 4, each needs own address
# System will auto-detect all sensors
```

## Bill of Materials

| Item | Specification | Qty | Est. Cost |
|------|--------------|-----|-----------|
| Raspberry Pi 3 | Model B | 1 | $35 |
| MicroSD Card | 32GB Class 10 | 1 | $10 |
| Power Supply | 5V 2.5A | 1 | $8 |
| DS18B20 | Waterproof | 1 | $5 |
| 4.7kΩ Resistor | 1/4W | 1 | $0.10 |
| Relay Module | 8-ch 5V | 1 | $8 |
| Float Switch | D-D or compatible | 1 | $15 |
| 12V PSU | 1A | 1 | $8 |
| Jumper Wires | M-F | 10 | $5 |
| **TOTAL** | | | **~$95** |

---

**Your hardware is now properly wired! 🔌✨**

Next: [Software Installation](INSTALLATION.md)
