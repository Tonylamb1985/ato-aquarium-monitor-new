# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-09

### Added
- Initial release of ATO Aquarium Monitor
- Float switch monitoring (GPIO 17)
- Relay-controlled pump activation (GPIO 27)
- DS18B20 temperature sensor integration (GPIO 4)
- Auto-calibration based on refill data
- Temperature sensor manual calibration
- 30-day activation history persistence
- Real-time evaporation rate tracking (1h, 6h, 24h, 7d, 30d)
- Seasonal detection and analysis (Spring/Summer/Autumn/Winter)
- Pump performance monitoring and degradation detection
- Comprehensive alert system with logging
- MQTT integration for Home Assistant
- 6-tab Home Assistant dashboard
- Emergency stop functionality (30-second timeout)
- Mobile notifications via Home Assistant
- Complete documentation and troubleshooting guides

### Safety Features
- 30-second pump timeout with emergency stop
- MQTT-controlled monitoring enable/disable
- Multiple alert thresholds (warning & critical)
- Rapid temperature change detection
- Persistent data storage across reboots

### Dashboard Tabs
1. Overview - Real-time monitoring and quick actions
2. Analytics - Historical trends and usage patterns
3. Settings - Configuration and calibration controls
4. Calibration - Auto-calibration status and history
5. Advanced - Seasonal stats, alerts history, pump performance
6. Temperature - Tank temperature monitoring and trends

## [Unreleased]

### Planned for 1.1.0
- Multi-tank support
- Web interface (no Home Assistant required)
- Additional sensor support (pH, TDS, conductivity)
- Automated dosing integration
- Cloud backup option
- Export data to CSV/Excel
- Improved seasonal prediction algorithms

### Planned for 1.2.0
- Machine learning for predictive maintenance
- Camera integration for visual monitoring
- Voice control (Alexa/Google Home)
- Native mobile app
- SMS alert support
- Advanced graphing and reporting

## Version History

### [1.0.0] - 2026-02-09
- First stable release
- Tested on Raspberry Pi 3 Model B
- Compatible with Home Assistant 2024.1+
- Python 3.7+ required

---

## Notes

- All versions are backward compatible with configuration files
- Data files (.pkl) are maintained across updates
- Always backup data files before upgrading
- Check breaking changes section before updating

## Breaking Changes

None yet - this is the first release.

## Security

If you discover a security vulnerability, please email security@example.com instead of opening a public issue.
