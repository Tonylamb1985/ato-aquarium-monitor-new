# 🔧 Aquarium Maintenance Tracker

## Overview

Add automated maintenance reminders and countdowns to your ATO system!

Track:
- 💧 Water changes (weekly/bi-weekly)
- 🧹 Filter cleaning
- 🔄 Media replacement
- 🧪 Testing schedules
- 📊 Equipment maintenance

---

## 🎯 Three Implementation Options

### Option 1: Home Assistant Only ⭐ **Easiest**
Use HA's built-in helpers and automations
- No coding required
- Quick setup (15 min)
- Flexible scheduling

### Option 2: Enhanced Python Script
Add to ATO monitor script
- Integrated tracking
- MQTT-based
- More features

### Option 3: Separate Maintenance Script
Standalone maintenance system
- Independent operation
- Can run separately

**Recommended: Option 1** (simplest and most flexible)

---

## ✅ Option 1: Home Assistant Implementation

### Step 1: Create Input Helpers

Go to **Settings → Devices & Services → Helpers → Create Helper**

Create these **Input Datetime** helpers:

```yaml
# Add to configuration.yaml:

input_datetime:
  # Water Changes
  aquarium_last_water_change:
    name: "Last Water Change"
    has_date: true
    has_time: false
  
  aquarium_next_water_change:
    name: "Next Water Change"
    has_date: true
    has_time: false
  
  # Filter Maintenance
  aquarium_last_filter_clean:
    name: "Last Filter Cleaning"
    has_date: true
    has_time: false
  
  aquarium_next_filter_clean:
    name: "Next Filter Cleaning"
    has_date: true
    has_time: false
  
  # Media Replacement
  aquarium_last_media_change:
    name: "Last Filter Media Change"
    has_date: true
    has_time: false
  
  aquarium_next_media_change:
    name: "Next Filter Media Change"
    has_date: true
    has_time: false
  
  # Carbon Replacement
  aquarium_last_carbon_change:
    name: "Last Carbon Change"
    has_date: true
    has_time: false
  
  aquarium_next_carbon_change:
    name: "Next Carbon Change"
    has_date: true
    has_time: false
  
  # Equipment Check
  aquarium_last_equipment_check:
    name: "Last Equipment Check"
    has_date: true
    has_time: false
  
  # Water Testing
  aquarium_last_water_test:
    name: "Last Water Test"
    has_date: true
    has_time: false

# Maintenance Intervals (in days)
input_number:
  aquarium_water_change_interval:
    name: "Water Change Interval"
    min: 1
    max: 60
    step: 1
    unit_of_measurement: "days"
    icon: mdi:water-sync
    initial: 7  # Weekly
  
  aquarium_filter_clean_interval:
    name: "Filter Cleaning Interval"
    min: 1
    max: 90
    step: 1
    unit_of_measurement: "days"
    icon: mdi:air-filter
    initial: 14  # Every 2 weeks
  
  aquarium_media_change_interval:
    name: "Media Change Interval"
    min: 7
    max: 365
    step: 1
    unit_of_measurement: "days"
    icon: mdi:sync
    initial: 90  # Every 3 months
  
  aquarium_carbon_change_interval:
    name: "Carbon Change Interval"
    min: 7
    max: 180
    step: 1
    unit_of_measurement: "days"
    icon: mdi:chart-bubble
    initial: 30  # Monthly
  
  aquarium_equipment_check_interval:
    name: "Equipment Check Interval"
    min: 1
    max: 365
    step: 1
    unit_of_measurement: "days"
    icon: mdi:wrench-clock
    initial: 30  # Monthly
```

### Step 2: Create Template Sensors

Add countdown sensors:

```yaml
template:
  - sensor:
      # Water Change Countdown
      - name: "Water Change Due In"
        unit_of_measurement: "days"
        state: >
          {% set next = states('input_datetime.aquarium_next_water_change') %}
          {% if next %}
            {{ ((as_timestamp(next) - as_timestamp(now())) / 86400) | round(0) }}
          {% else %}
            0
          {% endif %}
        icon: >
          {% set days = ((as_timestamp(states('input_datetime.aquarium_next_water_change')) - as_timestamp(now())) / 86400) | round(0) %}
          {% if days < 0 %}
            mdi:alert-circle
          {% elif days <= 1 %}
            mdi:water-alert
          {% else %}
            mdi:water-sync
          {% endif %}
        attributes:
          status: >
            {% set days = ((as_timestamp(states('input_datetime.aquarium_next_water_change')) - as_timestamp(now())) / 86400) | round(0) %}
            {% if days < 0 %}
              Overdue by {{ days|abs }} day(s)!
            {% elif days == 0 %}
              Due today!
            {% elif days == 1 %}
              Due tomorrow
            {% else %}
              Due in {{ days }} days
            {% endif %}
      
      # Filter Cleaning Countdown
      - name: "Filter Cleaning Due In"
        unit_of_measurement: "days"
        state: >
          {% set next = states('input_datetime.aquarium_next_filter_clean') %}
          {% if next %}
            {{ ((as_timestamp(next) - as_timestamp(now())) / 86400) | round(0) }}
          {% else %}
            0
          {% endif %}
        icon: >
          {% set days = ((as_timestamp(states('input_datetime.aquarium_next_filter_clean')) - as_timestamp(now())) / 86400) | round(0) %}
          {% if days < 0 %}
            mdi:alert-circle
          {% elif days <= 1 %}
            mdi:air-filter
          {% else %}
            mdi:air-filter
          {% endif %}
      
      # Media Change Countdown
      - name: "Media Change Due In"
        unit_of_measurement: "days"
        state: >
          {% set next = states('input_datetime.aquarium_next_media_change') %}
          {% if next %}
            {{ ((as_timestamp(next) - as_timestamp(now())) / 86400) | round(0) }}
          {% else %}
            0
          {% endif %}
        icon: mdi:sync
      
      # Carbon Change Countdown
      - name: "Carbon Change Due In"
        unit_of_measurement: "days"
        state: >
          {% set next = states('input_datetime.aquarium_next_carbon_change') %}
          {% if next %}
            {{ ((as_timestamp(next) - as_timestamp(now())) / 86400) | round(0) }}
          {% else %}
            0
          {% endif %}
        icon: mdi:chart-bubble
      
      # Equipment Check Countdown
      - name: "Equipment Check Due In"
        unit_of_measurement: "days"
        state: >
          {% set next = states('input_datetime.aquarium_last_equipment_check') %}
          {% if next %}
            {% set interval = states('input_number.aquarium_equipment_check_interval') | int %}
            {% set last = as_timestamp(next) %}
            {% set due = last + (interval * 86400) %}
            {{ ((due - as_timestamp(now())) / 86400) | round(0) }}
          {% else %}
            0
          {% endif %}
        icon: mdi:wrench-clock
      
      # Days Since Water Test
      - name: "Days Since Water Test"
        unit_of_measurement: "days"
        state: >
          {% set last = states('input_datetime.aquarium_last_water_test') %}
          {% if last %}
            {{ ((as_timestamp(now()) - as_timestamp(last)) / 86400) | round(0) }}
          {% else %}
            0
          {% endif %}
        icon: >
          {% set days = ((as_timestamp(now()) - as_timestamp(states('input_datetime.aquarium_last_water_test'))) / 86400) | round(0) %}
          {% if days > 7 %}
            mdi:test-tube-off
          {% else %}
            mdi:test-tube
          {% endif %}
```

### Step 3: Create Automations

Add reminder automations:

```yaml
automation:
  # Water Change Reminder (3 days before)
  - alias: "Aquarium Water Change Reminder - 3 Days"
    id: aquarium_water_change_3days
    trigger:
      - platform: numeric_state
        entity_id: sensor.water_change_due_in
        below: 4
        above: 2
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "💧 Water Change Due Soon"
          message: "Water change due in {{ states('sensor.water_change_due_in') }} days"
          data:
            actions:
              - action: "WATER_CHANGE_DONE"
                title: "Mark as Done"
  
  # Water Change Due Today
  - alias: "Aquarium Water Change Due Today"
    id: aquarium_water_change_today
    trigger:
      - platform: numeric_state
        entity_id: sensor.water_change_due_in
        below: 1
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "💧 Water Change DUE TODAY"
          message: "Time for your scheduled water change!"
          data:
            priority: high
            actions:
              - action: "WATER_CHANGE_DONE"
                title: "Mark as Done"
  
  # Water Change Overdue
  - alias: "Aquarium Water Change OVERDUE"
    id: aquarium_water_change_overdue
    trigger:
      - platform: numeric_state
        entity_id: sensor.water_change_due_in
        below: 0
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "🚨 Water Change OVERDUE!"
          message: "Water change is {{ states('sensor.water_change_due_in')|abs }} day(s) overdue!"
          data:
            priority: high
            ttl: 0
  
  # Filter Cleaning Reminder
  - alias: "Aquarium Filter Cleaning Reminder"
    id: aquarium_filter_reminder
    trigger:
      - platform: numeric_state
        entity_id: sensor.filter_cleaning_due_in
        below: 2
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "🧹 Filter Cleaning Due"
          message: "Filter cleaning due in {{ states('sensor.filter_cleaning_due_in') }} day(s)"
          data:
            actions:
              - action: "FILTER_CLEAN_DONE"
                title: "Mark as Done"
  
  # Media Change Reminder
  - alias: "Aquarium Media Change Reminder"
    id: aquarium_media_reminder
    trigger:
      - platform: numeric_state
        entity_id: sensor.media_change_due_in
        below: 7
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "🔄 Media Change Due Soon"
          message: "Filter media change due in {{ states('sensor.media_change_due_in') }} days"
  
  # Carbon Change Reminder
  - alias: "Aquarium Carbon Change Reminder"
    id: aquarium_carbon_reminder
    trigger:
      - platform: numeric_state
        entity_id: sensor.carbon_change_due_in
        below: 3
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "⚫ Carbon Change Due"
          message: "Carbon change due in {{ states('sensor.carbon_change_due_in') }} days"
  
  # Water Test Reminder (Weekly)
  - alias: "Aquarium Water Test Reminder"
    id: aquarium_test_reminder
    trigger:
      - platform: numeric_state
        entity_id: sensor.days_since_water_test
        above: 7
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "🧪 Time to Test Water"
          message: "It's been {{ states('sensor.days_since_water_test') }} days since last test"

  # Handle "Mark as Done" Actions
  - alias: "Handle Water Change Done"
    id: handle_water_change_done
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "WATER_CHANGE_DONE"
    action:
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.aquarium_last_water_change
        data:
          date: "{{ now().date() }}"
      
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.aquarium_next_water_change
        data:
          date: "{{ (now() + timedelta(days=states('input_number.aquarium_water_change_interval')|int)).date() }}"
      
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "✅ Water Change Recorded"
          message: "Next change scheduled for {{ states('input_datetime.aquarium_next_water_change') }}"
  
  - alias: "Handle Filter Clean Done"
    id: handle_filter_clean_done
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "FILTER_CLEAN_DONE"
    action:
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.aquarium_last_filter_clean
        data:
          date: "{{ now().date() }}"
      
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.aquarium_next_filter_clean
        data:
          date: "{{ (now() + timedelta(days=states('input_number.aquarium_filter_clean_interval')|int)).date() }}"
      
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "✅ Filter Cleaning Recorded"
          message: "Next cleaning scheduled"
```

### Step 4: Create Maintenance Dashboard Tab

Add this as a new tab:

```yaml
- title: Maintenance
  path: maintenance
  icon: mdi:wrench-clock
  cards:
    # Header
    - type: markdown
      content: |
        # 🔧 Maintenance Schedule & Tracking
      card_mod:
        style: |
          ha-card {
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            color: white;
            text-align: center;
          }
    
    # Countdown Cards
    - type: horizontal-stack
      cards:
        - type: custom:mushroom-template-card
          primary: "Water Change"
          secondary: >
            {% set days = states('sensor.water_change_due_in') | int %}
            {% if days < 0 %}
            🚨 {{ days|abs }} days overdue!
            {% elif days == 0 %}
            ⚠️ Due today!
            {% elif days == 1 %}
            Due tomorrow
            {% else %}
            In {{ days }} days
            {% endif %}
          icon: mdi:water-sync
          icon_color: >
            {% set days = states('sensor.water_change_due_in') | int %}
            {% if days < 0 %}
            red
            {% elif days <= 1 %}
            orange
            {% elif days <= 3 %}
            yellow
            {% else %}
            green
            {% endif %}
          tap_action:
            action: call-service
            service: script.record_water_change
        
        - type: custom:mushroom-template-card
          primary: "Filter Clean"
          secondary: >
            {% set days = states('sensor.filter_cleaning_due_in') | int %}
            {% if days < 0 %}
            🚨 {{ days|abs }} days overdue!
            {% elif days == 0 %}
            Due today!
            {% else %}
            In {{ days }} days
            {% endif %}
          icon: mdi:air-filter
          icon_color: >
            {% set days = states('sensor.filter_cleaning_due_in') | int %}
            {% if days < 0 %}
            red
            {% elif days <= 1 %}
            orange
            {% else %}
            green
            {% endif %}
          tap_action:
            action: call-service
            service: script.record_filter_clean
    
    # Maintenance Schedule
    - type: entities
      title: 📅 Next Maintenance Due
      show_header_toggle: false
      entities:
        - entity: input_datetime.aquarium_next_water_change
          name: Water Change
          icon: mdi:water-sync
        
        - entity: sensor.water_change_due_in
          name: Due In
        
        - type: divider
        
        - entity: input_datetime.aquarium_next_filter_clean
          name: Filter Cleaning
          icon: mdi:air-filter
        
        - entity: sensor.filter_cleaning_due_in
          name: Due In
        
        - type: divider
        
        - entity: input_datetime.aquarium_next_media_change
          name: Media Change
          icon: mdi:sync
        
        - entity: sensor.media_change_due_in
          name: Due In
        
        - type: divider
        
        - entity: input_datetime.aquarium_next_carbon_change
          name: Carbon Change
          icon: mdi:chart-bubble
        
        - entity: sensor.carbon_change_due_in
          name: Due In
    
    # Quick Actions
    - type: entities
      title: ✅ Mark as Complete
      show_header_toggle: false
      entities:
        - type: button
          name: "Water Change Done"
          icon: mdi:check-circle
          action_name: "Mark Done"
          tap_action:
            action: call-service
            service: script.record_water_change
        
        - type: button
          name: "Filter Clean Done"
          icon: mdi:check-circle
          action_name: "Mark Done"
          tap_action:
            action: call-service
            service: script.record_filter_clean
        
        - type: button
          name: "Media Change Done"
          icon: mdi:check-circle
          action_name: "Mark Done"
          tap_action:
            action: call-service
            service: script.record_media_change
        
        - type: button
          name: "Carbon Change Done"
          icon: mdi:check-circle
          action_name: "Mark Done"
          tap_action:
            action: call-service
            service: script.record_carbon_change
        
        - type: button
          name: "Water Test Done"
          icon: mdi:test-tube
          action_name: "Mark Done"
          tap_action:
            action: call-service
            service: script.record_water_test
    
    # Maintenance Intervals
    - type: entities
      title: ⚙️ Maintenance Intervals
      entities:
        - entity: input_number.aquarium_water_change_interval
          name: Water Change Interval
        
        - entity: input_number.aquarium_filter_clean_interval
          name: Filter Cleaning Interval
        
        - entity: input_number.aquarium_media_change_interval
          name: Media Change Interval
        
        - entity: input_number.aquarium_carbon_change_interval
          name: Carbon Change Interval
        
        - entity: input_number.aquarium_equipment_check_interval
          name: Equipment Check Interval
    
    # Last Completed
    - type: entities
      title: 📊 Last Completed
      entities:
        - entity: input_datetime.aquarium_last_water_change
          name: Last Water Change
        
        - entity: input_datetime.aquarium_last_filter_clean
          name: Last Filter Clean
        
        - entity: input_datetime.aquarium_last_media_change
          name: Last Media Change
        
        - entity: input_datetime.aquarium_last_carbon_change
          name: Last Carbon Change
        
        - entity: input_datetime.aquarium_last_water_test
          name: Last Water Test
        
        - entity: sensor.days_since_water_test
          name: Days Since Test
```

### Step 5: Create Scripts for Quick Actions

```yaml
script:
  record_water_change:
    alias: "Record Water Change"
    sequence:
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.aquarium_last_water_change
        data:
          date: "{{ now().date() }}"
      
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.aquarium_next_water_change
        data:
          date: "{{ (now() + timedelta(days=states('input_number.aquarium_water_change_interval')|int)).date() }}"
      
      - service: persistent_notification.create
        data:
          title: "✅ Water Change Recorded"
          message: "Next change scheduled for {{ (now() + timedelta(days=states('input_number.aquarium_water_change_interval')|int)).date() }}"
  
  record_filter_clean:
    alias: "Record Filter Cleaning"
    sequence:
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.aquarium_last_filter_clean
        data:
          date: "{{ now().date() }}"
      
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.aquarium_next_filter_clean
        data:
          date: "{{ (now() + timedelta(days=states('input_number.aquarium_filter_clean_interval')|int)).date() }}"
      
      - service: persistent_notification.create
        data:
          title: "✅ Filter Cleaning Recorded"
          message: "Next cleaning scheduled"
  
  record_media_change:
    alias: "Record Media Change"
    sequence:
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.aquarium_last_media_change
        data:
          date: "{{ now().date() }}"
      
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.aquarium_next_media_change
        data:
          date: "{{ (now() + timedelta(days=states('input_number.aquarium_media_change_interval')|int)).date() }}"
  
  record_carbon_change:
    alias: "Record Carbon Change"
    sequence:
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.aquarium_last_carbon_change
        data:
          date: "{{ now().date() }}"
      
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.aquarium_next_carbon_change
        data:
          date: "{{ (now() + timedelta(days=states('input_number.aquarium_carbon_change_interval')|int)).date() }}"
  
  record_water_test:
    alias: "Record Water Test"
    sequence:
      - service: input_datetime.set_datetime
        target:
          entity_id: input_datetime.aquarium_last_water_test
        data:
          date: "{{ now().date() }}"
```

---

## 🎯 Features You Get

### Automated Reminders
- ✅ 3-day advance warning (water changes)
- ✅ Due today notifications
- ✅ Overdue alerts
- ✅ "Mark as Done" quick actions

### Visual Countdown
- ✅ Days remaining indicators
- ✅ Color-coded status (green/yellow/red)
- ✅ Overdue warnings

### Flexible Scheduling
- ✅ Adjustable intervals for each task
- ✅ Individual schedules
- ✅ Easy rescheduling

### Quick Actions
- ✅ One-tap "Mark as Done" buttons
- ✅ Notification action buttons
- ✅ Automatic next-date calculation

---

## 📱 Mobile Notifications

You'll receive notifications like:

**3 Days Before:**
```
💧 Water Change Due Soon
Water change due in 3 days
[Mark as Done]
```

**Due Today:**
```
💧 Water Change DUE TODAY
Time for your scheduled water change!
[Mark as Done]
```

**Overdue:**
```
🚨 Water Change OVERDUE!
Water change is 2 day(s) overdue!
```

---

## ⚙️ Customization

### Change Intervals

Dashboard → Maintenance → Adjust sliders:
- Water Change: 7 days (weekly)
- Filter Clean: 14 days (bi-weekly)
- Media Change: 90 days (quarterly)
- Carbon: 30 days (monthly)

### Add More Tasks

Just duplicate the pattern for any task:
1. Add input_datetime (last/next)
2. Add input_number (interval)
3. Add template sensor (countdown)
4. Add automation (reminder)
5. Add to dashboard

---

## 🚀 Installation Time

- **Setup:** 20 minutes
- **Configuration:** 5 minutes
- **Testing:** 5 minutes
- **Total:** 30 minutes

---

## ✅ Quick Start Checklist

- [ ] Add input helpers to configuration.yaml
- [ ] Add template sensors
- [ ] Add automations
- [ ] Add scripts
- [ ] Restart Home Assistant
- [ ] Create maintenance dashboard tab
- [ ] Set initial dates and intervals
- [ ] Test notifications

---

**Never forget maintenance again! Full automation! 🔧✨**
