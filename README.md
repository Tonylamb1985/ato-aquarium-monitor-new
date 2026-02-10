# 🐠 ATO Aquarium Monitor

**Enterprise-grade Auto Top-Off monitoring and control system for aquariums**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%203-red.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-compatible-green.svg)

## 🌟 Features

- ✅ **Auto-Calibration** - Self-calibrates based on refills
- ✅ **Temperature Monitoring** - DS18B20 waterproof sensor with calibration
- ✅ **Pump Control** - Safe relay-based pump activation with timeout
- ✅ **Seasonal Tracking** - Automatic season detection and evaporation analysis
- ✅ **30-Day History** - Persistent data storage across reboots
- ✅ **Multiple Safety Features** - 30s timeout, emergency stop, alerts
- ✅ **6-Tab Dashboard** - Comprehensive Home Assistant interface
- ✅ **MQTT Integration** - Real-time updates and control
- ✅ **Mobile Notifications** - Critical alerts via Home Assistant app

## 📊 System Overview

This system monitors and controls an aquarium Auto Top-Off (ATO) system using:
- **Raspberry Pi 3** as the main controller
- **D-D Float Switch** for water level detection
- **8-Channel Relay Module** for pump control
- **DS18B20 Temperature Sensor** for tank monitoring
- **Home Assistant** for visualization and alerts

### Monitoring Capabilities

| Metric | Timeframes | Features |
|--------|-----------|----------|
| Evaporation Rate | 1h, 6h, 24h, 7d, 30d | Auto-calibrating |
| Temperature | Real-time, 24h, 7d stats | ±0.5°C accuracy |
| Pump Performance | Per-cycle tracking | Degradation detection |
| Seasonal Analysis | Spring/Summer/Autumn/Winter | Historical comparison |
| Alerts | Real-time logging | 500 alert history |

## 🚀 Quick Start

### Prerequisites

- Raspberry Pi 3 (or newer)
- Home Assistant with MQTT broker
- Python 3.7+
- Basic electronics skills

### Hardware Required

| Component | Specification | Qty |
|-----------|--------------|-----|
| Raspberry Pi 3 | Model B | 1 |
| 8-Channel Relay Module | 5V with optocouplers | 1 |
| DS18B20 Temp Sensor | Waterproof, digital | 1 |
| 4.7kΩ Resistor | Pull-up for DS18B20 | 1 |
| Float Switch | D-D ATO or compatible | 1 |
| 12V Power Supply | 500mA+ for pump | 1 |

### Installation

```bash
# 1. Clone this repository
git clone https://github.com/tonylamb1985/ato-aquarium-monitor.git
cd ato-aquarium-monitor

# 2. Install dependencies
pip3 install paho-mqtt --break-system-packages
pip3 install RPi.GPIO --break-system-packages

# 3. Enable 1-Wire for DS18B20
sudo nano /boot/config.txt
# Add: dtoverlay=w1-gpio,gpiopin=4
sudo reboot

# 4. Configure the script
cp config.example.py config.py
nano config.py
# Edit MQTT broker IP, credentials, etc.

# 5. Run the script
python3 ato_monitor.py

# 6. Install as service (optional but recommended)
sudo cp ato-monitor.service /etc/systemd/system/
sudo systemctl enable ato-monitor.service
sudo systemctl start ato-monitor.service
```

## 📁 Repository Structure

```
ato-aquarium-monitor/
├── README.md                          # This file
├── LICENSE                            # MIT License
├── ato_monitor.py                     # Main Python script
├── config.example.py                  # Example configuration
├── requirements.txt                   # Python dependencies
├── ato-monitor.service               # Systemd service file
├── docs/
│   ├── INSTALLATION.md               # Detailed installation guide
│   ├── WIRING.md                     # Wiring diagrams
│   ├── CALIBRATION.md                # Calibration procedures
│   ├── TROUBLESHOOTING.md            # Common issues & solutions
│   └── API.md                        # MQTT API documentation
├── home-assistant/
│   ├── configuration.yaml            # HA MQTT sensors config
│   ├── dashboard-overview.yaml       # Overview tab
│   ├── dashboard-analytics.yaml      # Analytics tab
│   ├── dashboard-settings.yaml       # Settings tab
│   ├── dashboard-calibration.yaml    # Calibration tab
│   ├── dashboard-advanced.yaml       # Advanced analytics tab
│   └── dashboard-temperature.yaml    # Temperature monitoring tab
├── images/
│   ├── wiring-diagram.png           # System wiring diagram
│   ├── dashboard-screenshot.png     # Dashboard preview
│   └── hardware-setup.jpg           # Physical setup photo
└── CHANGELOG.md                      # Version history
```

## 🎛️ Dashboard Preview

The system includes 6 comprehensive dashboard tabs:

1. **Overview** - Real-time status, charts, quick actions
2. **Analytics** - Historical trends, usage patterns
3. **Settings** - Configuration, calibration, controls
4. **Calibration** - Auto-calibration status and history
5. **Advanced** - Seasonal stats, alerts history, pump performance
6. **Temperature** - Tank temperature monitoring and trends

## 📈 Auto-Calibration

The system automatically calibrates itself based on your refills:

1. Refill your reservoir and enter the exact amount added
2. System tracks activations between refills
3. Calculates: `Liters per activation = Total liters / Activations`
4. Uses rolling average of last 5 refills for accuracy
5. Confidence increases with each refill (20% per refill)

**Typical Results:**
- After 2 refills: 40% confidence
- After 4 refills: 80% confidence
- After 5 refills: 100% confidence

## 🌡️ Temperature Monitoring

- **Sensor:** DS18B20 waterproof digital temperature sensor
- **Accuracy:** ±0.5°C factory, ±0.1°C after calibration
- **Reading Interval:** Every 30 seconds
- **Calibration:** Manual offset adjustment via Home Assistant
- **Alerts:** Configurable warning and critical thresholds

## 🔔 Alerts & Notifications

The system monitors for:

| Alert Type | Trigger | Action |
|------------|---------|--------|
| Critical Low Temp | <20°C | Immediate notification |
| Critical High Temp | >30°C | Immediate notification |
| Pump Timeout | >30s runtime | Emergency stop + disable |
| Rapid Activations | >3 per hour | Leak warning |
| Reservoir Low | <5L remaining | Refill reminder |
| No Activity | >36 hours | Check pump/float |

## 🛡️ Safety Features

1. **30-Second Timeout** - Pump automatically stops if running too long
2. **Emergency Stop** - MQTT-controlled monitoring disable
3. **Float Switch Independence** - Monitors existing D-D ATO system
4. **Persistent Data** - Survives power outages and reboots
5. **Alert Logging** - Complete history of all alerts
6. **Multiple Thresholds** - Warning and critical levels

## 📊 Seasonal Intelligence

The system automatically detects the current season and tracks:

- Seasonal evaporation patterns
- Temperature variations by season
- Pump performance across seasons
- Year-over-year comparisons

**Supported Seasons:** Spring 🌸, Summer ☀️, Autumn 🍂, Winter ❄️

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Tank Configuration
RESERVOIR_CAPACITY = 23.0      # Liters
LITERS_PER_ACTIVATION = 1.0    # Initial estimate (auto-calibrates)

# Alert Thresholds
MAX_ACTIVATIONS_PER_HOUR = 3
MAX_DAILY_USAGE = 6.0          # Liters
MAX_FILL_DURATION = 30         # Seconds

# Temperature Thresholds (°C)
TEMP_MIN_WARNING = 22.0
TEMP_MAX_WARNING = 28.0
TEMP_MIN_CRITICAL = 20.0
TEMP_MAX_CRITICAL = 30.0
```

## 📡 MQTT API

The system publishes to these MQTT topics:

### Status Topics
- `aquarium/ato/state` - Current state (filling/idle/disabled)
- `aquarium/ato/pump_state` - Pump status (ON/OFF)
- `aquarium/ato/monitoring_enabled` - Monitoring status
- `aquarium/ato/temperature` - Current tank temperature

### Data Topics
- `aquarium/ato/daily_usage` - Water used today (L)
- `aquarium/ato/reservoir_level` - Remaining water (L)
- `aquarium/ato/lph_24h` - 24-hour evaporation rate (L/h)
- `aquarium/ato/calibrated_lph` - Current calibration value

### Control Topics
- `aquarium/ato/enable` - Enable/disable monitoring (ON/OFF)
- `aquarium/ato/refill` - Record reservoir refill (liters)
- `aquarium/ato/temp_calibration_set` - Set temp offset (°C)

See [docs/API.md](docs/API.md) for complete API documentation.

## 🐛 Troubleshooting

Common issues and solutions:

**No temperature readings?**
```bash
ls /sys/bus/w1/devices/
# Should show: 28-xxxxxxxxxxxx
```

**Pump not activating?**
```bash
sudo systemctl status ato-monitor.service
journalctl -u ato-monitor.service -n 50
```

**Script keeps crashing?**
```bash
# Check permissions
sudo usermod -a -G gpio pi
```

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed solutions.

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md) - Step-by-step setup
- [Wiring Diagrams](docs/WIRING.md) - Hardware connections
- [Calibration Guide](docs/CALIBRATION.md) - How to calibrate sensors
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues
- [MQTT API](docs/API.md) - Integration reference

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report Bugs** - Open an issue with details
2. **Suggest Features** - Share your ideas in discussions
3. **Submit PRs** - Fork, make changes, submit pull request
4. **Improve Docs** - Help make documentation clearer
5. **Share Your Setup** - Post photos/videos of your system

### Development Setup

```bash
git clone https://github.com/tonylamb1985/ato-aquarium-monitor.git
cd ato-aquarium-monitor
# Make your changes
git checkout -b feature/your-feature-name
git commit -am "Add your feature"
git push origin feature/your-feature-name
# Open a Pull Request
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Raspberry Pi Foundation** - Raspberry Pi hardware
- **Home Assistant** - Open source home automation
- **Mosquitto** - MQTT broker
- **D-D** - ATO system inspiration
- **Community** - All contributors and users

## 📞 Support

- 🐛 **Bug Reports:** [Open an Issue](https://github.com/tonylamb1985/ato-aquarium-monitor/issues)
- 💡 **Feature Requests:** [Start a Discussion](https://github.com/tonylamb1985/ato-aquarium-monitor/discussions)
- 📧 **Email:** your.email@example.com
- 💬 **Discord:** [Join our server](#)

## 🗺️ Roadmap

### Version 1.1 (Planned)
- [ ] Multi-tank support
- [ ] Web interface (no HA required)
- [ ] Additional sensor support (pH, TDS)
- [ ] Automated dosing integration
- [ ] Cloud backup option

### Version 1.2 (Future)
- [ ] Machine learning predictions
- [ ] Camera integration
- [ ] Voice control (Alexa/Google)
- [ ] Mobile app
- [ ] SMS alerts

## 📊 Stats

- **Lines of Code:** ~1,500
- **Files Created:** 6 data files
- **Storage Used:** ~1MB
- **Update Frequency:** 0.5s (float switch), 30s (temperature)
- **Data Retention:** 30 days (activations), 10,000 readings (temp)

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=tonylamb1985/ato-aquarium-monitor&type=Date)](https://star-history.com/#tonylamb1985/ato-aquarium-monitor&Date)

## 📸 Gallery

### Hardware Setup
![Hardware Setup](images/hardware-setup.jpg)

### Dashboard
![Dashboard Screenshot](images/dashboard-screenshot.png)

### Wiring Diagram
![Wiring Diagram](images/wiring-diagram.png)

---

**Made with ❤️ for the aquarium community**

*Keep your fish happy and your tank topped off!* 🐠💧

≈==============================
## 🌡️ 3-Sensor Temperature Monitoring

**NEW:** Upgraded to support 3 DS18B20 temperature sensors!

Monitor:
- 🐠 **Display Tank** - Main aquarium
- 💧 **Sump** - Filtration area
- 🪣 **ATO Reservoir** - Top-off water

### Features:
- Individual calibration per sensor
- Temperature difference alerts
- Circulation monitoring
- New "All Temps" dashboard tab

See [QUICK_3SENSOR_SETUP.md](QUICK_3SENSOR_SETUP.md) for installation!