#!/usr/bin/env python3
"""
ATO Aquarium Monitor - Main Script
Version: 1.0.0
Author: ATO Aquarium Monitor Project
License: MIT

Complete aquarium Auto Top-Off monitoring system with:
- Float switch monitoring
- Pump control via relay
- Temperature monitoring (DS18B20)
- Auto-calibration
- Seasonal tracking
- MQTT integration for Home Assistant
"""

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
import json
import pickle
import os
import glob

# Import configuration (will be in config.py after user copies config.example.py)
try:
    from config import *
except ImportError:
    print("ERROR: config.py not found!")
    print("Please copy config.example.py to config.py and edit with your settings")
    exit(1)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(FLOAT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PUMP_PIN, GPIO.OUT)
GPIO.output(PUMP_PIN, GPIO.HIGH)  # Start with pump OFF

# Initialize MQTT client
client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    print(f"ERROR: Could not connect to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Error: {e}")
    print("Please check your MQTT configuration in config.py")
    exit(1)

# State variables
daily_usage = 0
activation_count = 0
reservoir_level = RESERVOIR_CAPACITY
last_activation_time = datetime.now()
activation_history = []
last_state = GPIO.input(FLOAT_PIN)
monitoring_enabled = True
disabled_reason = None
filling_start_time = None
filling_duration = 0
stuck_alert_sent = False
pump_running = False

# Calibration data
calibration_data = {
    'activations_since_refill': 0,
    'last_refill_amount': 0,
    'refill_history': [],
    'calibrated_lph': LITERS_PER_ACTIVATION,
    'confidence': 0,
    'last_calibration_date': None
}

# Tracking data
alerts_history = []
pump_performance_history = []
current_temperature = None
temp_history = []
last_temp_alert = None
temp_calibration_offset = 0.0
TEMP_SENSOR_ID = None

# ============================================================================
# SEASONAL TRACKING FUNCTIONS
# ============================================================================

def get_current_season():
    """Determine current season based on date (Northern Hemisphere)"""
    now = datetime.now()
    month = now.month
    
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    elif month in [9, 10, 11]:
        return "Autumn"

def get_season_emoji():
    """Get emoji for current season"""
    season = get_current_season()
    emojis = {
        "Spring": "🌸",
        "Summer": "☀️",
        "Autumn": "🍂",
        "Winter": "❄️"
    }
    return emojis.get(season, "🌍")

def calculate_seasonal_stats():
    """Calculate evaporation statistics by season"""
    seasonal_data = {
        "Spring": {"activations": 0, "liters": 0, "days": 91, "avg_per_day": 0, "lph": 0},
        "Summer": {"activations": 0, "liters": 0, "days": 91, "avg_per_day": 0, "lph": 0},
        "Autumn": {"activations": 0, "liters": 0, "days": 91, "avg_per_day": 0, "lph": 0},
        "Winter": {"activations": 0, "liters": 0, "days": 91, "avg_per_day": 0, "lph": 0}
    }
    
    year_ago = datetime.now() - timedelta(days=365)
    
    for activation_time in activation_history:
        if activation_time >= year_ago:
            month = activation_time.month
            if month in [12, 1, 2]:
                season = "Winter"
            elif month in [3, 4, 5]:
                season = "Spring"
            elif month in [6, 7, 8]:
                season = "Summer"
            else:
                season = "Autumn"
            
            seasonal_data[season]["activations"] += 1
            seasonal_data[season]["liters"] += LITERS_PER_ACTIVATION
    
    for season in seasonal_data:
        days = seasonal_data[season]["days"]
        if days > 0 and seasonal_data[season]["liters"] > 0:
            seasonal_data[season]["avg_per_day"] = round(seasonal_data[season]["liters"] / days, 2)
            seasonal_data[season]["lph"] = round(seasonal_data[season]["avg_per_day"] / 24, 3)
    
    return seasonal_data

# ============================================================================
# FILE I/O FUNCTIONS
# ============================================================================

def load_history():
    """Load activation history from file"""
    global activation_history
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'rb') as f:
                activation_history = pickle.load(f)
            print(f"✅ Loaded {len(activation_history)} historical activations")
        except Exception as e:
            print(f"⚠️  Error loading history: {e}")
            activation_history = []

def save_history():
    """Save activation history to file"""
    try:
        with open(HISTORY_FILE, 'wb') as f:
            pickle.dump(activation_history, f)
    except Exception as e:
        print(f"⚠️  Error saving history: {e}")

def load_calibration():
    """Load calibration data from file"""
    global calibration_data, LITERS_PER_ACTIVATION
    if os.path.exists(CALIBRATION_FILE):
        try:
            with open(CALIBRATION_FILE, 'rb') as f:
                calibration_data = pickle.load(f)
            if calibration_data['confidence'] >= 50:
                LITERS_PER_ACTIVATION = calibration_data['calibrated_lph']
            print(f"✅ Loaded calibration: {LITERS_PER_ACTIVATION}L/activation (confidence: {calibration_data['confidence']}%)")
        except Exception as e:
            print(f"⚠️  Error loading calibration: {e}")

def save_calibration():
    """Save calibration data to file"""
    try:
        with open(CALIBRATION_FILE, 'wb') as f:
            pickle.dump(calibration_data, f)
    except Exception as e:
        print(f"⚠️  Error saving calibration: {e}")

def load_alerts_history():
    """Load alerts history from file"""
    global alerts_history
    if os.path.exists(ALERTS_HISTORY_FILE):
        try:
            with open(ALERTS_HISTORY_FILE, 'rb') as f:
                alerts_history = pickle.load(f)
            print(f"✅ Loaded {len(alerts_history)} historical alerts")
        except Exception as e:
            print(f"⚠️  Error loading alerts history: {e}")
            alerts_history = []

def save_alerts_history():
    """Save alerts history to file"""
    try:
        with open(ALERTS_HISTORY_FILE, 'wb') as f:
            pickle.dump(alerts_history, f)
    except Exception as e:
        print(f"⚠️  Error saving alerts history: {e}")

def load_pump_performance():
    """Load pump performance history from file"""
    global pump_performance_history
    if os.path.exists(PUMP_PERFORMANCE_FILE):
        try:
            with open(PUMP_PERFORMANCE_FILE, 'rb') as f:
                pump_performance_history = pickle.load(f)
            print(f"✅ Loaded {len(pump_performance_history)} pump performance records")
        except Exception as e:
            print(f"⚠️  Error loading pump performance: {e}")
            pump_performance_history = []

def save_pump_performance():
    """Save pump performance history to file"""
    try:
        with open(PUMP_PERFORMANCE_FILE, 'wb') as f:
            pickle.dump(pump_performance_history, f)
    except Exception as e:
        print(f"⚠️  Error saving pump performance: {e}")

def load_temp_history():
    """Load temperature history from file"""
    global temp_history
    if os.path.exists(TEMP_HISTORY_FILE):
        try:
            with open(TEMP_HISTORY_FILE, 'rb') as f:
                temp_history = pickle.load(f)
            print(f"✅ Loaded {len(temp_history)} temperature readings")
        except Exception as e:
            print(f"⚠️  Error loading temp history: {e}")
            temp_history = []

def save_temp_history():
    """Save temperature history to file"""
    try:
        with open(TEMP_HISTORY_FILE, 'wb') as f:
            pickle.dump(temp_history, f)
    except Exception as e:
        print(f"⚠️  Error saving temp history: {e}")

def load_temp_calibration():
    """Load temperature calibration offset from file"""
    global temp_calibration_offset
    if os.path.exists(TEMP_CALIBRATION_FILE):
        try:
            with open(TEMP_CALIBRATION_FILE, 'rb') as f:
                data = pickle.load(f)
                temp_calibration_offset = data.get('offset', 0.0)
            print(f"✅ Loaded temperature calibration offset: {temp_calibration_offset}°C")
        except Exception as e:
            print(f"⚠️  Error loading temp calibration: {e}")
            temp_calibration_offset = 0.0
    else:
        temp_calibration_offset = 0.0

def save_temp_calibration():
    """Save temperature calibration offset to file"""
    try:
        data = {
            'offset': temp_calibration_offset,
            'last_calibration': datetime.now().isoformat(),
            'calibration_method': 'manual'
        }
        with open(TEMP_CALIBRATION_FILE, 'wb') as f:
            pickle.dump(data, f)
        print(f"✅ Saved temperature calibration offset: {temp_calibration_offset}°C")
    except Exception as e:
        print(f"⚠️  Error saving temp calibration: {e}")

# ============================================================================
# TEMPERATURE SENSOR FUNCTIONS
# ============================================================================

def find_temp_sensor():
    """Auto-detect DS18B20 sensor"""
    global TEMP_SENSOR_ID
    try:
        device_folder = glob.glob('/sys/bus/w1/devices/28*')
        if device_folder:
            TEMP_SENSOR_ID = device_folder[0]
            print(f"✅ Temperature sensor found: {TEMP_SENSOR_ID}")
            return True
        else:
            print("⚠️  No DS18B20 temperature sensor detected")
            return False
    except Exception as e:
        print(f"⚠️  Error finding temperature sensor: {e}")
        return False

def read_temp_raw():
    """Read raw data from temperature sensor"""
    if not TEMP_SENSOR_ID:
        return None
    try:
        with open(TEMP_SENSOR_ID + '/w1_slave', 'r') as f:
            return f.readlines()
    except Exception as e:
        return None

def read_temperature():
    """Read temperature from DS18B20 sensor with calibration"""
    global current_temperature
    
    lines = read_temp_raw()
    if not lines:
        return None
    
    if lines[0].strip()[-3:] != 'YES':
        return None
    
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        calibrated_temp = temp_c + temp_calibration_offset
        current_temperature = round(calibrated_temp, 2)
        return current_temperature
    
    return None

def read_temperature_raw():
    """Read raw (uncalibrated) temperature for calibration purposes"""
    lines = read_temp_raw()
    if not lines:
        return None
    
    if lines[0].strip()[-3:] != 'YES':
        return None
    
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return round(temp_c, 2)
    
    return None

def set_temp_calibration_offset(offset):
    """Set temperature calibration offset"""
    global temp_calibration_offset
    temp_calibration_offset = round(float(offset), 2)
    save_temp_calibration()
    client.publish("aquarium/ato/temp_calibration_offset", temp_calibration_offset)
    print(f"🌡️  Temperature calibration offset set to: {temp_calibration_offset}°C")

def record_temperature(temp):
    """Record a temperature reading"""
    global temp_history
    
    temp_record = {
        'timestamp': datetime.now().isoformat(),
        'temperature': temp,
        'season': get_current_season()
    }
    
    temp_history.append(temp_record)
    
    if len(temp_history) > 10000:
        temp_history.pop(0)
    
    save_temp_history()

def calculate_temp_stats():
    """Calculate temperature statistics"""
    if not temp_history:
        return {
            'avg_24h': None,
            'min_24h': None,
            'max_24h': None,
            'avg_7d': None,
            'min_7d': None,
            'max_7d': None
        }
    
    now = datetime.now()
    day_ago = now - timedelta(hours=24)
    week_ago = now - timedelta(days=7)
    
    temps_24h = [r['temperature'] for r in temp_history 
                 if datetime.fromisoformat(r['timestamp']) >= day_ago]
    
    temps_7d = [r['temperature'] for r in temp_history 
                if datetime.fromisoformat(r['timestamp']) >= week_ago]
    
    return {
        'avg_24h': round(sum(temps_24h) / len(temps_24h), 2) if temps_24h else None,
        'min_24h': round(min(temps_24h), 2) if temps_24h else None,
        'max_24h': round(max(temps_24h), 2) if temps_24h else None,
        'avg_7d': round(sum(temps_7d) / len(temps_7d), 2) if temps_7d else None,
        'min_7d': round(min(temps_7d), 2) if temps_7d else None,
        'max_7d': round(max(temps_7d), 2) if temps_7d else None
    }

# ============================================================================
# PUMP CONTROL FUNCTIONS
# ============================================================================

def start_pump():
    """Start the ATO pump"""
    global pump_running, filling_start_time, stuck_alert_sent
    GPIO.output(PUMP_PIN, GPIO.LOW)
    pump_running = True
    filling_start_time = datetime.now()
    stuck_alert_sent = False
    client.publish("aquarium/ato/pump_state", "ON")
    print("🔵 Pump STARTED")

def stop_pump():
    """Stop the ATO pump"""
    global pump_running, filling_start_time, filling_duration
    GPIO.output(PUMP_PIN, GPIO.HIGH)
    pump_running = False
    if filling_start_time is not None:
        filling_duration = (datetime.now() - filling_start_time).total_seconds()
        
        # Record pump performance
        record_pump_cycle(filling_duration, LITERS_PER_ACTIVATION)
        
        print(f"🔴 Pump STOPPED - ran for {filling_duration:.1f}s")
        filling_start_time = None
    client.publish("aquarium/ato/pump_state", "OFF")

def emergency_stop_pump():
    """Emergency stop with alert"""
    global monitoring_enabled, disabled_reason
    stop_pump()
    monitoring_enabled = False
    disabled_reason = "Emergency stop - stuck float/pump timeout"
    client.publish("aquarium/ato/state", "emergency_stopped")
    client.publish("aquarium/ato/monitoring_enabled", "OFF")
    print("🚨 EMERGENCY STOP - monitoring disabled for safety")

def record_pump_cycle(runtime_seconds, volume_liters):
    """Record a pump cycle for performance tracking"""
    global pump_performance_history
    
    performance_record = {
        'timestamp': datetime.now().isoformat(),
        'runtime_seconds': round(runtime_seconds, 1),
        'volume_liters': round(volume_liters, 3),
        'flow_rate_lph': round((volume_liters / runtime_seconds) * 3600, 1) if runtime_seconds > 0 else 0,
        'season': get_current_season(),
        'reservoir_level_before': round(reservoir_level + volume_liters, 1),
        'reservoir_level_after': round(reservoir_level, 1)
    }
    
    pump_performance_history.append(performance_record)
    
    if len(pump_performance_history) > 1000:
        pump_performance_history.pop(0)
    
    save_pump_performance()

# ============================================================================
# CALIBRATION FUNCTIONS
# ============================================================================

def calculate_calibration():
    """Calculate liters per activation based on refill history"""
    global LITERS_PER_ACTIVATION
    
    if len(calibration_data['refill_history']) < 2:
        calibration_data['confidence'] = 0
        return
    
    recent_refills = calibration_data['refill_history'][-5:]
    
    total_liters = sum(r['liters'] for r in recent_refills)
    total_activations = sum(r['activations'] for r in recent_refills)
    
    if total_activations == 0:
        return
    
    new_calibration = total_liters / total_activations
    
    if calibration_data['calibrated_lph'] > 0:
        LITERS_PER_ACTIVATION = (new_calibration * 0.7) + (calibration_data['calibrated_lph'] * 0.3)
    else:
        LITERS_PER_ACTIVATION = new_calibration
    
    calibration_data['calibrated_lph'] = round(LITERS_PER_ACTIVATION, 3)
    calibration_data['last_calibration_date'] = datetime.now().isoformat()
    
    num_refills = len(recent_refills)
    calibration_data['confidence'] = min(100, num_refills * 20)
    
    if num_refills >= 3:
        values = [r['liters'] / r['activations'] for r in recent_refills if r['activations'] > 0]
        avg = sum(values) / len(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        if std_dev > (avg * 0.2):
            calibration_data['confidence'] = max(50, calibration_data['confidence'] - 20)
    
    save_calibration()
    
    print(f"🎯 Auto-calibration updated: {LITERS_PER_ACTIVATION:.3f}L/activation (confidence: {calibration_data['confidence']}%)")
    print(f"   Based on {num_refills} refills: {total_liters}L / {total_activations} activations")
    
    client.publish("aquarium/ato/calibrated_lph", round(LITERS_PER_ACTIVATION, 3))
    client.publish("aquarium/ato/calibration_confidence", calibration_data['confidence'])

def record_refill(liters_added):
    """Record a reservoir refill for calibration"""
    global LITERS_PER_ACTIVATION
    
    activations = calibration_data['activations_since_refill']
    
    if activations > 0 and liters_added > 0:
        refill_record = {
            'activations': activations,
            'liters': liters_added,
            'lph_calculated': liters_added / activations,
            'date': datetime.now().isoformat()
        }
        
        calibration_data['refill_history'].append(refill_record)
        
        if len(calibration_data['refill_history']) > 20:
            calibration_data['refill_history'].pop(0)
        
        print(f"📊 Refill recorded: {liters_added}L over {activations} activations = {refill_record['lph_calculated']:.3f}L/activation")
        
        calculate_calibration()
    
    calibration_data['activations_since_refill'] = 0
    calibration_data['last_refill_amount'] = liters_added
    save_calibration()

# ============================================================================
# ALERT FUNCTIONS
# ============================================================================

def record_alert(alert):
    """Record an alert in history"""
    global alerts_history
    
    alert_record = {
        'timestamp': datetime.now().isoformat(),
        'severity': alert['severity'],
        'message': alert['message'],
        'season': get_current_season(),
        'reservoir_level': reservoir_level,
        'activations_today': activation_count
    }
    
    alerts_history.append(alert_record)
    
    if len(alerts_history) > 500:
        alerts_history.pop(0)
    
    save_alerts_history()

def check_alerts():
    """Check all alert conditions"""
    global stuck_alert_sent, last_temp_alert
    alerts = []
    now = datetime.now()
    
    if not monitoring_enabled:
        alerts.append({
            "severity": "warning",
            "message": f"⚠️ ATO monitoring is DISABLED{' - ' + disabled_reason if disabled_reason else ''}. Pump will not activate automatically."
        })
    
    if filling_start_time is not None and monitoring_enabled:
        elapsed = (now - filling_start_time).total_seconds()
        if elapsed > MAX_FILL_DURATION:
            alerts.append({
                "severity": "critical",
                "message": f"🚨 PUMP TIMEOUT! Running for {int(elapsed)}s (max: {MAX_FILL_DURATION}s). EMERGENCY STOP ACTIVATED!"
            })
            if not stuck_alert_sent:
                stuck_alert_sent = True
                emergency_stop_pump()
    
    # Temperature alerts
    if current_temperature is not None:
        if current_temperature <= TEMP_MIN_CRITICAL:
            alerts.append({
                "severity": "critical",
                "message": f"🥶 CRITICAL LOW TEMPERATURE! Tank at {current_temperature}°C (min: {TEMP_MIN_CRITICAL}°C). Check heater immediately!"
            })
        elif current_temperature >= TEMP_MAX_CRITICAL:
            alerts.append({
                "severity": "critical",
                "message": f"🔥 CRITICAL HIGH TEMPERATURE! Tank at {current_temperature}°C (max: {TEMP_MAX_CRITICAL}°C). Check chiller/cooling!"
            })
        elif current_temperature <= TEMP_MIN_WARNING:
            alerts.append({
                "severity": "warning",
                "message": f"❄️ Low temperature warning: {current_temperature}°C (target: >{TEMP_MIN_WARNING}°C)"
            })
        elif current_temperature >= TEMP_MAX_WARNING:
            alerts.append({
                "severity": "warning",
                "message": f"🌡️ High temperature warning: {current_temperature}°C (target: <{TEMP_MAX_WARNING}°C)"
            })
        
        if len(temp_history) >= 2:
            last_temp = temp_history[-2]['temperature']
            temp_change = abs(current_temperature - last_temp)
            
            if temp_change > 2.0:
                alerts.append({
                    "severity": "warning",
                    "message": f"⚠️ Rapid temperature change: {temp_change:.1f}°C change detected!"
                })
    
    rates = calculate_lph()
    
    if monitoring_enabled:
        if rates["lph_30d"] > 0 and rates["lph_1h"] > rates["lph_30d"] * 4:
            alerts.append({
                "severity": "critical",
                "message": f"Major evaporation spike! {rates['lph_1h']}L/h (baseline: {rates['lph_30d']}L/h)"
            })
        
        if rates["lph_30d"] > 0 and rates["lph_24h"] > rates["lph_30d"] * 1.5:
            alerts.append({
                "severity": "warning",
                "message": f"Higher than normal evaporation: {rates['lph_24h']}L/h (baseline: {rates['lph_30d']}L/h)"
            })
        
        hour_ago = now - timedelta(hours=1)
        recent = [a for a in activation_history if a >= hour_ago]
        if len(recent) > MAX_ACTIVATIONS_PER_HOUR:
            alerts.append({
                "severity": "critical",
                "message": f"Too many ATO activations: {len(recent)} in last hour. Possible leak!"
            })
        
        hours_since = (now - last_activation_time).total_seconds() / 3600
        if hours_since < MIN_HOURS_BETWEEN and activation_count > 1:
            alerts.append({
                "severity": "warning",
                "message": f"ATO activating too frequently: {hours_since:.1f} hours since last fill"
            })
        
        if hours_since > MAX_HOURS_BETWEEN:
            alerts.append({
                "severity": "warning",
                "message": f"No ATO activity for {hours_since:.1f} hours. Check pump/float switch"
            })
        
        if daily_usage > MAX_DAILY_USAGE:
            alerts.append({
                "severity": "warning",
                "message": f"High water usage today: {daily_usage:.1f}L"
            })
    
    if reservoir_level <= LOW_RESERVOIR_WARNING:
        alerts.append({
            "severity": "warning",
            "message": f"ATO reservoir low: {reservoir_level:.1f}L remaining. Refill soon!"
        })
    
    if reservoir_level <= 0:
        alerts.append({
            "severity": "critical",
            "message": "ATO reservoir empty! Refill immediately!"
        })
    
    if alerts:
        client.publish("aquarium/ato/alerts", json.dumps(alerts))
        for alert in alerts:
            client.publish(f"aquarium/ato/alert_{alert['severity']}", alert['message'])
            record_alert(alert)
    else:
        client.publish("aquarium/ato/alerts", json.dumps([]))
        client.publish("aquarium/ato/alert_critical", "")
        client.publish("aquarium/ato/alert_warning", "")

# ============================================================================
# RATE CALCULATION FUNCTIONS
# ============================================================================

def calculate_lph():
    """Calculate liters per hour based on activation history"""
    now = datetime.now()
    
    if not activation_history:
        return {
            "lph_1h": 0,
            "lph_6h": 0,
            "lph_24h": 0,
            "lph_7d": 0,
            "lph_30d": 0
        }
    
    hour_ago = now - timedelta(hours=1)
    recent_activations = [a for a in activation_history if a >= hour_ago]
    lph_1h = len(recent_activations) * LITERS_PER_ACTIVATION
    
    six_hours_ago = now - timedelta(hours=6)
    six_hour_activations = [a for a in activation_history if a >= six_hours_ago]
    hours_elapsed_6h = min(6, (now - activation_history[0]).total_seconds() / 3600)
    lph_6h = (len(six_hour_activations) * LITERS_PER_ACTIVATION) / hours_elapsed_6h if hours_elapsed_6h > 0 else 0
    
    day_ago = now - timedelta(hours=24)
    day_activations = [a for a in activation_history if a >= day_ago]
    hours_elapsed_24h = min(24, (now - activation_history[0]).total_seconds() / 3600)
    lph_24h = (len(day_activations) * LITERS_PER_ACTIVATION) / hours_elapsed_24h if hours_elapsed_24h > 0 else 0
    
    week_ago = now - timedelta(days=7)
    week_activations = [a for a in activation_history if a >= week_ago]
    hours_elapsed_7d = min(168, (now - activation_history[0]).total_seconds() / 3600)
    lph_7d = (len(week_activations) * LITERS_PER_ACTIVATION) / hours_elapsed_7d if hours_elapsed_7d > 0 else 0
    
    month_ago = now - timedelta(days=30)
    month_activations = [a for a in activation_history if a >= month_ago]
    hours_elapsed_30d = min(720, (now - activation_history[0]).total_seconds() / 3600)
    lph_30d = (len(month_activations) * LITERS_PER_ACTIVATION) / hours_elapsed_30d if hours_elapsed_30d > 0 else 0
    
    return {
        "lph_1h": round(lph_1h, 3),
        "lph_6h": round(lph_6h, 3),
        "lph_24h": round(lph_24h, 3),
        "lph_7d": round(lph_7d, 3),
        "lph_30d": round(lph_30d, 3)
    }

# ============================================================================
# MQTT PUBLISHING FUNCTIONS
# ============================================================================

def publish_stats():
    """Publish all statistics to MQTT"""
    now = datetime.now()
    rates = calculate_lph()
    seasonal_stats = calculate_seasonal_stats()
    temp_stats = calculate_temp_stats()
    
    hours_until_empty = reservoir_level / rates["lph_30d"] if rates["lph_30d"] > 0 else 999
    days_until_empty = hours_until_empty / 24
    
    month_ago = now - timedelta(days=30)
    month_activations = [a for a in activation_history if a >= month_ago]
    total_30d = len(month_activations) * LITERS_PER_ACTIVATION
    
    stats = {
        "daily_usage": round(daily_usage, 2),
        "activation_count": activation_count,
        "total_activations_30d": len(month_activations),
        "total_liters_30d": round(total_30d, 1),
        "last_activation": last_activation_time.isoformat(),
        "hours_since_last": round((now - last_activation_time).total_seconds() / 3600, 1),
        "reservoir_level": round(reservoir_level, 1),
        "reservoir_percent": round((reservoir_level / RESERVOIR_CAPACITY) * 100, 0),
        "days_until_empty": round(days_until_empty, 1),
        "history_count": len(activation_history),
        "monitoring_enabled": monitoring_enabled,
        "disabled_reason": disabled_reason if disabled_reason else "N/A",
        "filling_duration": round(filling_duration, 1),
        "pump_running": pump_running,
        "calibrated_lph": round(calibration_data['calibrated_lph'], 3),
        "calibration_confidence": calibration_data['confidence'],
        "activations_since_refill": calibration_data['activations_since_refill'],
        "refill_history": calibration_data['refill_history'],
        "current_season": get_current_season(),
        "season_emoji": get_season_emoji(),
        "seasonal_stats": seasonal_stats,
        "alerts_count": len(alerts_history),
        "pump_cycles_count": len(pump_performance_history),
        "temperature": current_temperature,
        "temp_stats": temp_stats,
        "temp_sensor_available": temp_sensor_available,
        "temp_calibration_offset": temp_calibration_offset,
        "temp_raw": read_temperature_raw() if temp_sensor_available else None,
        **rates
    }
    
    client.publish("aquarium/ato/stats", json.dumps(stats))
    client.publish("aquarium/ato/daily_usage", round(daily_usage, 2))
    client.publish("aquarium/ato/activations", activation_count)
    client.publish("aquarium/ato/hours_since", stats["hours_since_last"])
    client.publish("aquarium/ato/reservoir_level", stats["reservoir_level"])
    client.publish("aquarium/ato/reservoir_percent", stats["reservoir_percent"])
    client.publish("aquarium/ato/days_until_empty", stats["days_until_empty"])
    client.publish("aquarium/ato/total_30d", stats["total_liters_30d"])
    client.publish("aquarium/ato/monitoring_enabled", "ON" if monitoring_enabled else "OFF")
    client.publish("aquarium/ato/filling_duration", stats["filling_duration"])
    client.publish("aquarium/ato/pump_running", "ON" if pump_running else "OFF")
    client.publish("aquarium/ato/calibrated_lph", stats["calibrated_lph"])
    client.publish("aquarium/ato/calibration_confidence", stats["calibration_confidence"])
    client.publish("aquarium/ato/activations_since_refill", stats["activations_since_refill"])
    client.publish("aquarium/ato/current_season", get_current_season())
    client.publish("aquarium/ato/seasonal_stats", json.dumps(seasonal_stats))
    client.publish("aquarium/ato/alerts_history", json.dumps(alerts_history[-50:]))
    client.publish("aquarium/ato/pump_performance", json.dumps(pump_performance_history[-100:]))
    
    if current_temperature is not None:
        client.publish("aquarium/ato/temperature", current_temperature)
        client.publish("aquarium/ato/temp_stats", json.dumps(temp_stats))
        client.publish("aquarium/ato/temp_calibration_offset", temp_calibration_offset)
        
        raw_temp = read_temperature_raw()
        if raw_temp is not None:
            client.publish("aquarium/ato/temperature_raw", raw_temp)
    
    client.publish("aquarium/ato/lph_1h", rates["lph_1h"])
    client.publish("aquarium/ato/lph_6h", rates["lph_6h"])
    client.publish("aquarium/ato/lph_24h", rates["lph_24h"])
    client.publish("aquarium/ato/lph_7d", rates["lph_7d"])
    client.publish("aquarium/ato/lph_30d", rates["lph_30d"])

# ============================================================================
# MQTT MESSAGE HANDLER
# ============================================================================

def on_message(client, userdata, msg):
    """Handle incoming MQTT messages"""
    global daily_usage, activation_count, reservoir_level, monitoring_enabled, disabled_reason
    
    if msg.topic == "aquarium/ato/reset":
        daily_usage = 0
        activation_count = 0
        publish_stats()
        print("📊 Daily counters reset")
    
    elif msg.topic == "aquarium/ato/refill":
        try:
            payload = msg.payload.decode().strip()
            liters_added = float(payload) if payload else RESERVOIR_CAPACITY
        except:
            liters_added = RESERVOIR_CAPACITY
        
        record_refill(liters_added)
        
        reservoir_level = RESERVOIR_CAPACITY
        client.publish("aquarium/ato/alert_warning", "")
        publish_stats()
        print(f"💧 Reservoir marked as refilled: {liters_added}L (used for calibration)")
    
    elif msg.topic == "aquarium/ato/enable":
        payload = msg.payload.decode().strip().lower()
        
        if payload == "on" or payload == "true":
            if not monitoring_enabled:
                monitoring_enabled = True
                disabled_reason = None
                client.publish("aquarium/ato/state", "enabled")
                client.publish("aquarium/ato/monitoring_enabled", "ON")
                print("✅ ATO monitoring ENABLED")
        
        elif payload == "off" or payload == "false":
            if monitoring_enabled:
                stop_pump()
                monitoring_enabled = False
                disabled_reason = "Manual disable"
                client.publish("aquarium/ato/state", "disabled")
                client.publish("aquarium/ato/monitoring_enabled", "OFF")
                print("🛑 ATO monitoring DISABLED - Manual")
        
        publish_stats()
        check_alerts()
    
    elif msg.topic == "aquarium/ato/pump_manual":
        payload = msg.payload.decode().strip().lower()
        if payload == "on" and not pump_running:
            start_pump()
            client.publish("aquarium/ato/state", "manual_fill")
        elif payload == "off" and pump_running:
            stop_pump()
            client.publish("aquarium/ato/state", "idle")
    
    elif msg.topic == "aquarium/ato/temp_calibration_set":
        try:
            offset = float(msg.payload.decode().strip())
            if -5.0 <= offset <= 5.0:
                set_temp_calibration_offset(offset)
                publish_stats()
            else:
                print(f"⚠️  Temperature calibration offset out of range: {offset}°C (limit: ±5°C)")
        except ValueError:
            print("⚠️  Invalid temperature calibration offset")

# ============================================================================
# MAIN PROGRAM
# ============================================================================

def main():
    """Main program loop"""
    global loop_counter
    
    # Load all historical data
    print("\n🚀 Starting ATO Aquarium Monitor...")
    print("=" * 60)
    load_history()
    load_calibration()
    load_alerts_history()
    load_pump_performance()
    load_temp_history()
    load_temp_calibration()
    
    # Find temperature sensor
    global temp_sensor_available
    temp_sensor_available = find_temp_sensor()
    
    # Setup MQTT
    client.on_message = on_message
    client.subscribe("aquarium/ato/reset")
    client.subscribe("aquarium/ato/refill")
    client.subscribe("aquarium/ato/enable")
    client.subscribe("aquarium/ato/pump_manual")
    client.subscribe("aquarium/ato/temp_calibration_set")
    client.loop_start()
    
    # Publish initial state
    client.publish("aquarium/ato/monitoring_enabled", "ON" if monitoring_enabled else "OFF")
    client.publish("aquarium/ato/pump_state", "OFF")
    client.publish("aquarium/ato/state", "startup")
    time.sleep(1)
    
    print("\n✅ ATO Monitor Started")
    print(f"   Monitoring: {'ENABLED' if monitoring_enabled else 'DISABLED'}")
    print(f"   Float switch: GPIO {FLOAT_PIN}")
    print(f"   Pump relay: GPIO {PUMP_PIN}")
    print(f"   Temperature sensor: {'Found' if temp_sensor_available else 'Not detected'}")
    print(f"   Calibration: {LITERS_PER_ACTIVATION}L/activation (confidence: {calibration_data['confidence']}%)")
    print(f"   Max fill duration: {MAX_FILL_DURATION}s")
    print(f"   MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"   Current season: {get_current_season()} {get_season_emoji()}")
    print("=" * 60)
    print("\n💚 System running... Press Ctrl+C to stop\n")
    
    loop_counter = 0
    
    try:
        while True:
            if monitoring_enabled:
                current_state = GPIO.input(FLOAT_PIN)
                
                if current_state != last_state:
                    if current_state == 0:
                        if not pump_running:
                            activation_count += 1
                            daily_usage += LITERS_PER_ACTIVATION
                            reservoir_level -= LITERS_PER_ACTIVATION
                            last_activation_time = datetime.now()
                            
                            calibration_data['activations_since_refill'] += 1
                            save_calibration()
                            
                            activation_history.append(last_activation_time)
                            
                            month_ago = datetime.now() - timedelta(days=30)
                            activation_history = [a for a in activation_history if a >= month_ago]
                            
                            save_history()
                            
                            start_pump()
                            client.publish("aquarium/ato/state", "filling")
                            publish_stats()
                            check_alerts()
                            
                            print(f"💧 ATO activation #{activation_count} (#{calibration_data['activations_since_refill']} since refill)")
                    
                    else:
                        if pump_running:
                            stop_pump()
                            client.publish("aquarium/ato/state", "idle")
                            publish_stats()
                
                if filling_start_time is not None:
                    elapsed = (datetime.now() - filling_start_time).total_seconds()
                    filling_duration = elapsed
                    
                    if elapsed > MAX_FILL_DURATION:
                        check_alerts()
                        client.publish("aquarium/ato/filling_duration", round(elapsed, 1))
                
                last_state = current_state
            else:
                if pump_running:
                    stop_pump()
                client.publish("aquarium/ato/state", "monitoring_disabled")
                filling_start_time = None
                filling_duration = 0
            
            # Read temperature every 30 seconds
            if temp_sensor_available and loop_counter % 60 == 0:
                temp = read_temperature()
                if temp is not None:
                    record_temperature(temp)
                    client.publish("aquarium/ato/temperature", temp)
            
            # Periodic update every 5 minutes
            if int(time.time()) % 300 == 0:
                check_alerts()
                publish_stats()
            
            loop_counter += 1
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        stop_pump()
        save_history()
        save_calibration()
        save_alerts_history()
        save_pump_performance()
        save_temp_history()
        GPIO.cleanup()
        print("✅ Goodbye!")

if __name__ == "__main__":
    main()
