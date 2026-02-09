# Contributing to ATO Aquarium Monitor

First off, thank you for considering contributing to ATO Aquarium Monitor! 🎉

## How Can I Contribute?

### Reporting Bugs 🐛

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the problem
- **Expected behavior** vs actual behavior
- **Screenshots** if applicable
- **System info:**
  - Raspberry Pi model
  - Python version: `python3 --version`
  - Home Assistant version
  - OS version: `uname -a`

### Suggesting Features 💡

Feature requests are welcome! Please include:

- **Clear use case** - Why is this feature useful?
- **Detailed description** - How should it work?
- **Alternatives considered** - What else did you think about?
- **Impact** - Who else would benefit?

### Pull Requests 🔧

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test thoroughly** on actual hardware if possible
5. **Commit**: `git commit -am 'Add some feature'`
6. **Push**: `git push origin feature/your-feature-name`
7. **Open a Pull Request**

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Keep functions focused and small

### Testing

Before submitting:

```bash
# Test the script
python3 ato_monitor.py

# Check for syntax errors
python3 -m py_compile ato_monitor.py

# Verify MQTT messages
mosquitto_sub -h YOUR_HA_IP -t 'aquarium/#' -v
```

### Documentation

- Update README.md if adding features
- Add entries to CHANGELOG.md
- Update relevant documentation in docs/
- Include comments in code

### Commit Messages

Use clear, descriptive commit messages:

```
Good: "Add pH sensor support with calibration"
Bad: "Update code"

Good: "Fix pump timeout not triggering emergency stop"
Bad: "Fix bug"
```

## Project Structure

```
ato-aquarium-monitor/
├── ato_monitor.py          # Main script
├── config.example.py       # Configuration template
├── docs/                   # Documentation
├── home-assistant/         # HA configuration files
└── images/                 # Screenshots and diagrams
```

## Areas Needing Help

- 🐛 Bug fixes and testing
- 📝 Documentation improvements
- 🌐 Translations (if applicable)
- 🎨 Dashboard design enhancements
- 🧪 Testing on different hardware
- 📸 Photos/videos of setups
- 🔧 New sensor integrations

## Questions?

Feel free to open a discussion or issue if you have questions!

Thank you for contributing! 🐠💙
