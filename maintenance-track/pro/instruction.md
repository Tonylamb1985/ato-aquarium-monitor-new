# 🚀 Enhanced Maintenance Tracker - Complete System

## Overview

**Advanced aquarium management system with:**
- 📊 Historical tracking & charts
- 💰 Cost tracking
- 📦 Supply inventory management
- 🍽️ Feeding schedules
- 💊 Dosing schedules
- 🧪 Water parameter logging
- 📈 Trend analysis
- 🎯 Equipment lifespan tracking

---

## 📦 Part 1: Supply Inventory Management

Track supplies and get alerts when running low!

### Configuration

```yaml
# Add to configuration.yaml

input_number:
  # Salt Mix
  aquarium_salt_stock:
    name: "Salt Mix Stock"
    min: 0
    max: 50
    step: 0.5
    unit_of_measurement: "kg"
    icon: mdi:shaker
  
  aquarium_salt_usage_per_change:
    name: "Salt Usage Per Change"
    min: 0
    max: 5
    step: 0.1
    unit_of_measurement: "kg"
    icon: mdi:shaker-outline
    initial: 1.0
  
  aquarium_salt_low_alert:
    name: "Salt Low Alert Level"
    min: 0
    max: 10
    step: 0.5
    unit_of_measurement: "kg"
    icon: mdi:alert
    initial: 2.0
  
  # Carbon
  aquarium_carbon_stock:
    name: "Activated Carbon Stock"
    min: 0
    max: 5000
    step: 50
    unit_of_measurement: "g"
    icon: mdi:chart-bubble
  
  aquarium_carbon_usage_per_change:
    name: "Carbon Per Change"
    min: 0
    max: 500
    step: 10
    unit_of_measurement: "g"
    icon: mdi:chart-bubble
    initial: 100
  
  # Filter Media
  aquarium_filter_media_stock:
    name: "Filter Media Stock"
    min: 0
    max: 10
    step: 1
    unit_of_measurement: "units"
    icon: mdi:air-filter
  
  # Test Kits Remaining
  aquarium_test_strips_remaining:
    name: "Test Strips Remaining"
    min: 0
    max: 100
    step: 1
    unit_of_measurement: "strips"
    icon: mdi:test-tube
  
  # Food Stock
  aquarium_food_stock:
    name: "Fish Food Stock"
    min: 0
    max: 1000
    step: 10
    unit_of_measurement: "g"
    icon: mdi:food-fish

# Template Sensors for Inventory
template:
  - sensor:
      # Salt - Changes Remaining
      - name: "Salt Changes Remaining"
        unit_of_measurement: "changes"
        state: >
          {% set stock = states('input_number.aquarium_salt_stock') | float %}
          {% set usage = states('input_number.aquarium_salt_usage_per_change') | float %}
          {% if usage > 0 %}
            {{ (stock / usage) | round(0) }}
          {% else %}
            0
          {% endif %}
        icon: >
          {% set changes = (states('input_number.aquarium_salt_stock') | float / states('input_number.aquarium_salt_usage_per_change') | float) | round(0) %}
          {% if changes < 3 %}
            mdi:alert-circle
          {% elif changes < 5 %}
            mdi:alert
          {% else %}
            mdi:check-circle
          {% endif %}
      
      # Carbon - Changes Remaining
      - name: "Carbon Changes Remaining"
        unit_of_measurement: "changes"
        state: >
          {% set stock = states('input_number.aquarium_carbon_stock') | float %}
          {% set usage = states('input_number.aquarium_carbon_usage_per_change') | float %}
          {% if usage > 0 %}
            {{ (stock / usage) | round(0) }}
          {% else %}
            0
          {% endif %}
        icon: mdi:chart-bubble
      
      # Food - Days Remaining
      - name: "Food Days Remaining"
        unit_of_measurement: "days"
        state: >
          {% set stock = states('input_number.aquarium_food_stock') | float %}
          {% set daily = states('input_number.aquarium_food_daily_amount') | float(3) %}
          {% if daily > 0 %}
            {{ (stock / daily) | round(0) }}
          {% else %}
            0
          {% endif %}
        icon: mdi:food-fish

# Inventory Alerts
automation:
  - alias: "Aquarium Salt Stock Low"
    id: aquarium_salt_low
    trigger:
      - platform: numeric_state
        entity_id: input_number.aquarium_salt_stock
        below: input_number.aquarium_salt_low_alert
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "🧂 Salt Stock Low"
          message: "Only {{ states('sensor.salt_changes_remaining') }} water changes remaining. Order more salt!"
          data:
            actions:
              - action: "SALT_ORDERED"
                title: "Ordered"
  
  - alias: "Aquarium Carbon Stock Low"
    id: aquarium_carbon_low
    trigger:
      - platform: numeric_state
        entity_id: sensor.carbon_changes_remaining
        below: 2
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "⚫ Carbon Stock Low"
          message: "Only {{ states('sensor.carbon_changes_remaining') }} changes remaining!"
  
  - alias: "Aquarium Test Strips Low"
    id: aquarium_tests_low
    trigger:
      - platform: numeric_state
        entity_id: input_number.aquarium_test_strips_remaining
        below: 10
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "🧪 Test Strips Running Low"
          message: "Only {{ states('input_number.aquarium_test_strips_remaining') }} strips remaining"
  
  - alias: "Aquarium Food Running Low"
    id: aquarium_food_low
    trigger:
      - platform: numeric_state
        entity_id: sensor.food_days_remaining
        below: 7
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "🐟 Food Running Low"
          message: "Only {{ states('sensor.food_days_remaining') }} days of food remaining"

# Scripts to Update Inventory
script:
  record_salt_usage:
    alias: "Record Salt Usage"
    sequence:
      - service: input_number.set_value
        target:
          entity_id: input_number.aquarium_salt_stock
        data:
          value: >
            {{ states('input_number.aquarium_salt_stock') | float - states('input_number.aquarium_salt_usage_per_change') | float }}
  
  add_salt_stock:
    alias: "Add Salt Stock"
    fields:
      amount:
        description: "Amount to add (kg)"
        example: 10
    sequence:
      - service: input_number.set_value
        target:
          entity_id: input_number.aquarium_salt_stock
        data:
          value: >
            {{ states('input_number.aquarium_salt_stock') | float + amount | float }}
      
      - service: persistent_notification.create
        data:
          title: "✅ Salt Stock Updated"
          message: "Added {{ amount }}kg. Total: {{ states('input_number.aquarium_salt_stock') }}kg"
```

---

## 💰 Part 2: Cost Tracking

Track maintenance costs over time!

### Configuration

```yaml
input_number:
  # Supply Costs
  aquarium_salt_cost_per_kg:
    name: "Salt Cost per kg"
    min: 0
    max: 100
    step: 0.5
    unit_of_measurement: "$/kg"
    icon: mdi:currency-usd
    initial: 15
  
  aquarium_carbon_cost_per_100g:
    name: "Carbon Cost per 100g"
    min: 0
    max: 50
    step: 0.5
    unit_of_measurement: "$"
    icon: mdi:currency-usd
    initial: 5
  
  aquarium_filter_media_cost:
    name: "Filter Media Cost"
    min: 0
    max: 100
    step: 1
    unit_of_measurement: "$"
    icon: mdi:currency-usd
    initial: 20
  
  aquarium_food_cost_per_100g:
    name: "Food Cost per 100g"
    min: 0
    max: 50
    step: 0.5
    unit_of_measurement: "$"
    icon: mdi:currency-usd
    initial: 8
  
  # Running Costs (auto-calculated)
  aquarium_total_cost_ytd:
    name: "Total Cost Year-to-Date"
    min: 0
    max: 10000
    step: 0.01
    unit_of_measurement: "$"
    icon: mdi:cash-multiple
  
  aquarium_monthly_cost_estimate:
    name: "Estimated Monthly Cost"
    min: 0
    max: 500
    step: 0.01
    unit_of_measurement: "$"
    icon: mdi:calendar-month

template:
  - sensor:
      # Cost Per Water Change
      - name: "Water Change Cost"
        unit_of_measurement: "$"
        state: >
          {% set salt_cost = states('input_number.aquarium_salt_cost_per_kg') | float %}
          {% set salt_usage = states('input_number.aquarium_salt_usage_per_change') | float %}
          {{ (salt_cost * salt_usage) | round(2) }}
        icon: mdi:currency-usd
      
      # Cost Per Carbon Change
      - name: "Carbon Change Cost"
        unit_of_measurement: "$"
        state: >
          {% set cost = states('input_number.aquarium_carbon_cost_per_100g') | float %}
          {% set usage = states('input_number.aquarium_carbon_usage_per_change') | float %}
          {{ (cost * (usage / 100)) | round(2) }}
        icon: mdi:currency-usd
      
      # Estimated Monthly Costs
      - name: "Estimated Monthly Costs"
        unit_of_measurement: "$"
        state: >
          {% set wc_cost = states('sensor.water_change_cost') | float %}
          {% set wc_interval = states('input_number.aquarium_water_change_interval') | float %}
          {% set carbon_cost = states('sensor.carbon_change_cost') | float %}
          {% set carbon_interval = states('input_number.aquarium_carbon_change_interval') | float %}
          {% set wc_monthly = (30 / wc_interval) * wc_cost %}
          {% set carbon_monthly = (30 / carbon_interval) * carbon_cost %}
          {{ (wc_monthly + carbon_monthly) | round(2) }}
        icon: mdi:cash
        attributes:
          water_changes: >
            {% set cost = states('sensor.water_change_cost') | float %}
            {% set interval = states('input_number.aquarium_water_change_interval') | float %}
            {{ ((30 / interval) * cost) | round(2) }}
          carbon: >
            {% set cost = states('sensor.carbon_change_cost') | float %}
            {% set interval = states('input_number.aquarium_carbon_change_interval') | float %}
            {{ ((30 / interval) * cost) | round(2) }}
      
      # Annual Cost Estimate
      - name: "Estimated Annual Cost"
        unit_of_measurement: "$"
        state: >
          {{ (states('sensor.estimated_monthly_costs') | float * 12) | round(2) }}
        icon: mdi:calendar-year

# Track actual spending
automation:
  - alias: "Record Water Change Cost"
    id: record_water_change_cost
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "WATER_CHANGE_DONE"
    action:
      - service: input_number.set_value
        target:
          entity_id: input_number.aquarium_total_cost_ytd
        data:
          value: >
            {{ states('input_number.aquarium_total_cost_ytd') | float + states('sensor.water_change_cost') | float }}
      
      - service: script.record_salt_usage
```

---

## 🍽️ Part 3: Feeding Schedules

Automated feeding reminders and tracking!

### Configuration

```yaml
input_datetime:
  aquarium_morning_feed_time:
    name: "Morning Feed Time"
    has_date: false
    has_time: true
  
  aquarium_evening_feed_time:
    name: "Evening Feed Time"
    has_date: false
    has_time: true

input_number:
  aquarium_food_daily_amount:
    name: "Daily Food Amount"
    min: 0
    max: 50
    step: 0.5
    unit_of_measurement: "g"
    icon: mdi:food-fish
    initial: 3
  
  aquarium_feedings_per_day:
    name: "Feedings Per Day"
    min: 1
    max: 5
    step: 1
    icon: mdi:counter
    initial: 2

input_boolean:
  aquarium_feeding_morning_enabled:
    name: "Morning Feeding Enabled"
    icon: mdi:weather-sunset-up
    initial: true
  
  aquarium_feeding_evening_enabled:
    name: "Evening Feeding Enabled"
    icon: mdi:weather-sunset-down
    initial: true
  
  aquarium_vacation_mode:
    name: "Vacation Mode (Disable Feeding)"
    icon: mdi:beach
    initial: false

# Feeding Counter
counter:
  aquarium_feedings_today:
    name: "Feedings Today"
    icon: mdi:counter
    restore: false

# Feeding Automations
automation:
  - alias: "Aquarium Morning Feeding Reminder"
    id: aquarium_morning_feed
    trigger:
      - platform: time
        at: input_datetime.aquarium_morning_feed_time
    condition:
      - condition: state
        entity_id: input_boolean.aquarium_feeding_morning_enabled
        state: "on"
      - condition: state
        entity_id: input_boolean.aquarium_vacation_mode
        state: "off"
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "🐟 Time to Feed Fish"
          message: "Morning feeding time!"
          data:
            actions:
              - action: "FEEDING_DONE"
                title: "Fed"
  
  - alias: "Aquarium Evening Feeding Reminder"
    id: aquarium_evening_feed
    trigger:
      - platform: time
        at: input_datetime.aquarium_evening_feed_time
    condition:
      - condition: state
        entity_id: input_boolean.aquarium_feeding_evening_enabled
        state: "on"
      - condition: state
        entity_id: input_boolean.aquarium_vacation_mode
        state: "off"
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "🐟 Time to Feed Fish"
          message: "Evening feeding time!"
          data:
            actions:
              - action: "FEEDING_DONE"
                title: "Fed"
  
  - alias: "Record Feeding"
    id: record_feeding
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "FEEDING_DONE"
    action:
      - service: counter.increment
        target:
          entity_id: counter.aquarium_feedings_today
      
      # Deduct from food stock
      - service: input_number.set_value
        target:
          entity_id: input_number.aquarium_food_stock
        data:
          value: >
            {% set current = states('input_number.aquarium_food_stock') | float %}
            {% set daily = states('input_number.aquarium_food_daily_amount') | float %}
            {% set feedings = states('input_number.aquarium_feedings_per_day') | float %}
            {% set per_feeding = daily / feedings %}
            {{ current - per_feeding }}
  
  - alias: "Reset Daily Feeding Counter"
    id: reset_feeding_counter
    trigger:
      - platform: time
        at: "00:00:00"
    action:
      - service: counter.reset
        target:
          entity_id: counter.aquarium_feedings_today
  
  - alias: "Missed Feeding Alert"
    id: missed_feeding_alert
    trigger:
      - platform: time
        at: "22:00:00"
    condition:
      - condition: numeric_state
        entity_id: counter.aquarium_feedings_today
        below: 1
      - condition: state
        entity_id: input_boolean.aquarium_vacation_mode
        state: "off"
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "⚠️ No Feedings Today!"
          message: "Did you forget to feed the fish?"
```

---

## 💊 Part 4: Dosing Schedules

Track liquid supplements and dosing!

### Configuration

```yaml
input_number:
  # Dosing Amounts
  aquarium_calcium_dose:
    name: "Calcium Dose"
    min: 0
    max: 50
    step: 0.5
    unit_of_measurement: "ml"
    icon: mdi:bottle-tonic-plus
  
  aquarium_alkalinity_dose:
    name: "Alkalinity Dose"
    min: 0
    max: 50
    step: 0.5
    unit_of_measurement: "ml"
    icon: mdi:bottle-tonic-plus
  
  aquarium_magnesium_dose:
    name: "Magnesium Dose"
    min: 0
    max: 50
    step: 0.5
    unit_of_measurement: "ml"
    icon: mdi:bottle-tonic-plus
  
  # Stock Levels
  aquarium_calcium_stock:
    name: "Calcium Stock"
    min: 0
    max: 5000
    step: 10
    unit_of_measurement: "ml"
    icon: mdi:bottle-tonic
  
  aquarium_alkalinity_stock:
    name: "Alkalinity Stock"
    min: 0
    max: 5000
    step: 10
    unit_of_measurement: "ml"
    icon: mdi:bottle-tonic
  
  aquarium_magnesium_stock:
    name: "Magnesium Stock"
    min: 0
    max: 5000
    step: 10
    unit_of_measurement: "ml"
    icon: mdi:bottle-tonic

input_datetime:
  aquarium_dosing_time:
    name: "Daily Dosing Time"
    has_date: false
    has_time: true

input_boolean:
  aquarium_dosing_enabled:
    name: "Automatic Dosing Enabled"
    icon: mdi:water-plus
    initial: true

template:
  - sensor:
      # Days of Calcium Remaining
      - name: "Calcium Days Remaining"
        unit_of_measurement: "days"
        state: >
          {% set stock = states('input_number.aquarium_calcium_stock') | float %}
          {% set daily = states('input_number.aquarium_calcium_dose') | float %}
          {% if daily > 0 %}
            {{ (stock / daily) | round(0) }}
          {% else %}
            999
          {% endif %}
        icon: >
          {% set days = (states('input_number.aquarium_calcium_stock') | float / states('input_number.aquarium_calcium_dose') | float) | round(0) %}
          {% if days < 7 %}
            mdi:alert-circle
          {% else %}
            mdi:bottle-tonic
          {% endif %}
      
      # Days of Alkalinity Remaining
      - name: "Alkalinity Days Remaining"
        unit_of_measurement: "days"
        state: >
          {% set stock = states('input_number.aquarium_alkalinity_stock') | float %}
          {% set daily = states('input_number.aquarium_alkalinity_dose') | float %}
          {% if daily > 0 %}
            {{ (stock / daily) | round(0) }}
          {% else %}
            999
          {% endif %}
        icon: mdi:bottle-tonic

automation:
  - alias: "Daily Dosing Reminder"
    id: daily_dosing_reminder
    trigger:
      - platform: time
        at: input_datetime.aquarium_dosing_time
    condition:
      - condition: state
        entity_id: input_boolean.aquarium_dosing_enabled
        state: "on"
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "💊 Time to Dose"
          message: >
            Calcium: {{ states('input_number.aquarium_calcium_dose') }}ml
            Alkalinity: {{ states('input_number.aquarium_alkalinity_dose') }}ml
            Magnesium: {{ states('input_number.aquarium_magnesium_dose') }}ml
          data:
            actions:
              - action: "DOSING_DONE"
                title: "Done"
  
  - alias: "Record Dosing"
    id: record_dosing
    trigger:
      - platform: event
        event_type: mobile_app_notification_action
        event_data:
          action: "DOSING_DONE"
    action:
      # Deduct calcium
      - service: input_number.set_value
        target:
          entity_id: input_number.aquarium_calcium_stock
        data:
          value: >
            {{ states('input_number.aquarium_calcium_stock') | float - states('input_number.aquarium_calcium_dose') | float }}
      
      # Deduct alkalinity
      - service: input_number.set_value
        target:
          entity_id: input_number.aquarium_alkalinity_stock
        data:
          value: >
            {{ states('input_number.aquarium_alkalinity_stock') | float - states('input_number.aquarium_alkalinity_dose') | float }}
      
      # Deduct magnesium
      - service: input_number.set_value
        target:
          entity_id: input_number.aquarium_magnesium_stock
        data:
          value: >
            {{ states('input_number.aquarium_magnesium_stock') | float - states('input_number.aquarium_magnesium_dose') | float }}
  
  - alias: "Calcium Stock Low Alert"
    id: calcium_low_alert
    trigger:
      - platform: numeric_state
        entity_id: sensor.calcium_days_remaining
        below: 7
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "💊 Calcium Running Low"
          message: "Only {{ states('sensor.calcium_days_remaining') }} days of calcium remaining"
```

---

## 🧪 Part 5: Water Parameter Logging

Track water parameters over time!

### Configuration

```yaml
input_number:
  # Current Parameters
  aquarium_ammonia:
    name: "Ammonia (NH3)"
    min: 0
    max: 5
    step: 0.01
    unit_of_measurement: "ppm"
    icon: mdi:flask
  
  aquarium_nitrite:
    name: "Nitrite (NO2)"
    min: 0
    max: 5
    step: 0.01
    unit_of_measurement: "ppm"
    icon: mdi:flask
  
  aquarium_nitrate:
    name: "Nitrate (NO3)"
    min: 0
    max: 100
    step: 1
    unit_of_measurement: "ppm"
    icon: mdi:flask
  
  aquarium_ph:
    name: "pH"
    min: 6.0
    max: 9.0
    step: 0.1
    icon: mdi:ph
  
  aquarium_kh:
    name: "KH (Alkalinity)"
    min: 0
    max: 20
    step: 0.5
    unit_of_measurement: "dKH"
    icon: mdi:water-check
  
  aquarium_gh:
    name: "GH (Hardness)"
    min: 0
    max: 30
    step: 0.5
    unit_of_measurement: "dGH"
    icon: mdi:water-check
  
  aquarium_calcium:
    name: "Calcium"
    min: 0
    max: 600
    step: 5
    unit_of_measurement: "ppm"
    icon: mdi:calcium
  
  aquarium_salinity:
    name: "Salinity"
    min: 1.000
    max: 1.040
    step: 0.001
    unit_of_measurement: "SG"
    icon: mdi:shaker

input_button:
  aquarium_save_parameters:
    name: "Save Current Parameters"
    icon: mdi:content-save

# Parameter Status
template:
  - binary_sensor:
      # Ammonia Status
      - name: "Ammonia Status"
        state: >
          {{ states('input_number.aquarium_ammonia') | float <= 0.02 }}
        device_class: safety
        icon: >
          {% if states('input_number.aquarium_ammonia') | float <= 0.02 %}
            mdi:check-circle
          {% else %}
            mdi:alert-circle
          {% endif %}
        attributes:
          level: "{{ states('input_number.aquarium_ammonia') }}"
          status: >
            {% set val = states('input_number.aquarium_ammonia') | float %}
            {% if val == 0 %}
              Perfect
            {% elif val <= 0.02 %}
              Safe
            {% elif val <= 0.25 %}
              Caution
            {% else %}
              Danger!
            {% endif %}
      
      # Nitrite Status
      - name: "Nitrite Status"
        state: >
          {{ states('input_number.aquarium_nitrite') | float == 0 }}
        device_class: safety
        icon: >
          {% if states('input_number.aquarium_nitrite') | float == 0 %}
            mdi:check-circle
          {% else %}
            mdi:alert-circle
          {% endif %}
      
      # pH Status  
      - name: "pH Status"
        state: >
          {% set ph = states('input_number.aquarium_ph') | float %}
          {{ ph >= 7.8 and ph <= 8.4 }}
        device_class: safety
        icon: >
          {% set ph = states('input_number.aquarium_ph') | float %}
          {% if ph >= 7.8 and ph <= 8.4 %}
            mdi:check-circle
          {% elif ph >= 7.5 and ph <= 8.6 %}
            mdi:alert
          {% else %}
            mdi:alert-circle
          {% endif %}

automation:
  - alias: "Water Parameter Alert - Ammonia"
    id: parameter_alert_ammonia
    trigger:
      - platform: numeric_state
        entity_id: input_number.aquarium_ammonia
        above: 0.25
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "🚨 High Ammonia!"
          message: "Ammonia level: {{ states('input_number.aquarium_ammonia') }}ppm - Do water change!"
          data:
            priority: high
  
  - alias: "Water Parameter Alert - Nitrite"
    id: parameter_alert_nitrite
    trigger:
      - platform: numeric_state
        entity_id: input_number.aquarium_nitrite
        above: 0.1
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "⚠️ Nitrite Detected"
          message: "Nitrite level: {{ states('input_number.aquarium_nitrite') }}ppm"
  
  - alias: "Water Parameter Alert - pH"
    id: parameter_alert_ph
    trigger:
      - platform: numeric_state
        entity_id: input_number.aquarium_ph
        below: 7.5
      - platform: numeric_state
        entity_id: input_number.aquarium_ph
        above: 8.6
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "⚠️ pH Out of Range"
          message: "pH: {{ states('input_number.aquarium_ph') }} (ideal: 7.8-8.4)"
```

---

## 📊 Part 6: Equipment Lifespan Tracking

Track when equipment needs replacement!

### Configuration

```yaml
input_datetime:
  # Installation Dates
  aquarium_heater_installed:
    name: "Heater Installed Date"
    has_date: true
    has_time: false
  
  aquarium_pump_installed:
    name: "Pump Installed Date"
    has_date: true
    has_time: false
  
  aquarium_uv_bulb_installed:
    name: "UV Bulb Installed Date"
    has_date: true
    has_time: false
  
  aquarium_light_installed:
    name: "LED Light Installed Date"
    has_date: true
    has_time: false

input_number:
  # Expected Lifespan (months)
  aquarium_heater_lifespan:
    name: "Heater Expected Lifespan"
    min: 6
    max: 60
    step: 1
    unit_of_measurement: "months"
    icon: mdi:radiator
    initial: 24
  
  aquarium_pump_lifespan:
    name: "Pump Expected Lifespan"
    min: 6
    max: 60
    step: 1
    unit_of_measurement: "months"
    icon: mdi:pump
    initial: 36
  
  aquarium_uv_lifespan:
    name: "UV Bulb Expected Lifespan"
    min: 3
    max: 18
    step: 1
    unit_of_measurement: "months"
    icon: mdi:lightbulb
    initial: 6
  
  aquarium_light_lifespan:
    name: "LED Light Expected Lifespan"
    min: 12
    max: 120
    step: 1
    unit_of_measurement: "months"
    icon: mdi:ceiling-light
    initial: 60

template:
  - sensor:
      # Heater Age
      - name: "Heater Age"
        unit_of_measurement: "months"
        state: >
          {% set installed = states('input_datetime.aquarium_heater_installed') %}
          {% if installed %}
            {{ ((as_timestamp(now()) - as_timestamp(installed)) / 2592000) | round(1) }}
          {% else %}
            0
          {% endif %}
        icon: >
          {% set age = ((as_timestamp(now()) - as_timestamp(states('input_datetime.aquarium_heater_installed'))) / 2592000) | round(1) %}
          {% set lifespan = states('input_number.aquarium_heater_lifespan') | float %}
          {% if age >= lifespan %}
            mdi:alert-circle
          {% elif age >= lifespan * 0.8 %}
            mdi:alert
          {% else %}
            mdi:radiator
          {% endif %}
        attributes:
          percent_used: >
            {% set age = ((as_timestamp(now()) - as_timestamp(states('input_datetime.aquarium_heater_installed'))) / 2592000) | round(1) %}
            {% set lifespan = states('input_number.aquarium_heater_lifespan') | float %}
            {{ ((age / lifespan) * 100) | round(0) }}
          months_remaining: >
            {% set age = ((as_timestamp(now()) - as_timestamp(states('input_datetime.aquarium_heater_installed'))) / 2592000) | round(1) %}
            {% set lifespan = states('input_number.aquarium_heater_lifespan') | float %}
            {{ (lifespan - age) | round(1) }}
      
      # UV Bulb Age
      - name: "UV Bulb Age"
        unit_of_measurement: "months"
        state: >
          {% set installed = states('input_datetime.aquarium_uv_bulb_installed') %}
          {% if installed %}
            {{ ((as_timestamp(now()) - as_timestamp(installed)) / 2592000) | round(1) }}
          {% else %}
            0
          {% endif %}
        icon: >
          {% set age = ((as_timestamp(now()) - as_timestamp(states('input_datetime.aquarium_uv_bulb_installed'))) / 2592000) | round(1) %}
          {% set lifespan = states('input_number.aquarium_uv_lifespan') | float %}
          {% if age >= lifespan %}
            mdi:lightbulb-off
          {% else %}
            mdi:lightbulb-on
          {% endif %}

automation:
  - alias: "Equipment Replacement Alert - Heater"
    id: equipment_heater_alert
    trigger:
      - platform: template
        value_template: >
          {% set age = ((as_timestamp(now()) - as_timestamp(states('input_datetime.aquarium_heater_installed'))) / 2592000) | round(1) %}
          {% set lifespan = states('input_number.aquarium_heater_lifespan') | float %}
          {{ age >= lifespan * 0.9 }}
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "🔧 Heater Needs Replacement"
          message: "Heater is {{ states('sensor.heater_age') }} months old (lifespan: {{ states('input_number.aquarium_heater_lifespan') }} months)"
  
  - alias: "Equipment Replacement Alert - UV Bulb"
    id: equipment_uv_alert
    trigger:
      - platform: template
        value_template: >
          {% set age = ((as_timestamp(now()) - as_timestamp(states('input_datetime.aquarium_uv_bulb_installed'))) / 2592000) | round(1) %}
          {% set lifespan = states('input_number.aquarium_uv_lifespan') | float %}
          {{ age >= lifespan }}
    action:
      - service: notify.mobile_app_YOUR_PHONE
        data:
          title: "💡 UV Bulb Needs Replacement"
          message: "UV effectiveness decreases after {{ states('input_number.aquarium_uv_lifespan') }} months. Replace now!"
```

---

## 📊 Part 7: Enhanced Dashboard Tab

Complete maintenance dashboard with all features!

```yaml
- title: Maintenance Pro
  path: maintenance_pro
  icon: mdi:chart-timeline-variant
  cards:
    # Header
    - type: markdown
      content: |
        # 🚀 Enhanced Maintenance System
      card_mod:
        style: |
          ha-card {
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            color: white;
            text-align: center;
          }
    
    # Quick Status Overview
    - type: horizontal-stack
      cards:
        - type: custom:mushroom-template-card
          primary: "💧 Water"
          secondary: "{{ states('sensor.water_change_due_in') }} days"
          icon: mdi:water-sync
          icon_color: >
            {% set days = states('sensor.water_change_due_in') | int %}
            {% if days < 0 %}red
            {% elif days <= 1 %}orange
            {% else %}green{% endif %}
        
        - type: custom:mushroom-template-card
          primary: "🧂 Salt"
          secondary: "{{ states('sensor.salt_changes_remaining') }} changes"
          icon: mdi:shaker
          icon_color: >
            {% set changes = states('sensor.salt_changes_remaining') | int %}
            {% if changes < 3 %}red
            {% elif changes < 5 %}orange
            {% else %}green{% endif %}
        
        - type: custom:mushroom-template-card
          primary: "🐟 Food"
          secondary: "{{ states('sensor.food_days_remaining') }} days"
          icon: mdi:food-fish
          icon_color: >
            {% set days = states('sensor.food_days_remaining') | int %}
            {% if days < 7 %}red
            {% elif days < 14 %}orange
            {% else %}green{% endif %}
    
    # Cost Tracking
    - type: entities
      title: 💰 Cost Tracking
      entities:
        - entity: sensor.estimated_monthly_costs
          name: Estimated Monthly
        - entity: sensor.estimated_annual_cost
          name: Estimated Annual
        - entity: sensor.water_change_cost
          name: Per Water Change
        - entity: sensor.carbon_change_cost
          name: Per Carbon Change
        - entity: input_number.aquarium_total_cost_ytd
          name: Total This Year
    
    # Supply Inventory
    - type: entities
      title: 📦 Supply Inventory
      entities:
        - type: section
          label: Stock Levels
        - entity: input_number.aquarium_salt_stock
          name: Salt Mix
        - entity: sensor.salt_changes_remaining
          name: Changes Remaining
        - type: divider
        - entity: input_number.aquarium_carbon_stock
          name: Activated Carbon
        - entity: sensor.carbon_changes_remaining
          name: Changes Remaining
        - type: divider
        - entity: input_number.aquarium_food_stock
          name: Fish Food
        - entity: sensor.food_days_remaining
          name: Days Remaining
        - type: divider
        - entity: input_number.aquarium_test_strips_remaining
          name: Test Strips
    
    # Feeding Schedule
    - type: entities
      title: 🍽️ Feeding Schedule
      entities:
        - entity: input_datetime.aquarium_morning_feed_time
          name: Morning Feed Time
        - entity: input_boolean.aquarium_feeding_morning_enabled
          name: Morning Enabled
        - entity: input_datetime.aquarium_evening_feed_time
          name: Evening Feed Time
        - entity: input_boolean.aquarium_feeding_evening_enabled
          name: Evening Enabled
        - type: divider
        - entity: counter.aquarium_feedings_today
          name: Feedings Today
        - entity: input_boolean.aquarium_vacation_mode
          name: Vacation Mode
    
    # Dosing Schedule
    - type: entities
      title: 💊 Dosing Schedule
      entities:
        - entity: input_datetime.aquarium_dosing_time
          name: Daily Dosing Time
        - entity: input_boolean.aquarium_dosing_enabled
          name: Dosing Enabled
        - type: divider
        - entity: input_number.aquarium_calcium_dose
          name: Calcium Dose
        - entity: sensor.calcium_days_remaining
          name: Days Remaining
        - type: divider
        - entity: input_number.aquarium_alkalinity_dose
          name: Alkalinity Dose
    
    # Water Parameters
    - type: entities
      title: 🧪 Water Parameters
      entities:
        - entity: input_number.aquarium_ammonia
          name: Ammonia (NH3)
        - entity: binary_sensor.ammonia_status
          name: Status
        - type: divider
        - entity: input_number.aquarium_nitrite
          name: Nitrite (NO2)
        - entity: binary_sensor.nitrite_status
          name: Status
        - type: divider
        - entity: input_number.aquarium_nitrate
          name: Nitrate (NO3)
        - type: divider
        - entity: input_number.aquarium_ph
          name: pH
        - entity: binary_sensor.ph_status
          name: Status
        - type: divider
        - entity: input_number.aquarium_salinity
          name: Salinity
    
    # Equipment Lifespan
    - type: entities
      title: 🔧 Equipment Lifespan
      entities:
        - type: section
          label: Heater
        - entity: input_datetime.aquarium_heater_installed
          name: Installed Date
        - entity: sensor.heater_age
          name: Current Age
        - entity: input_number.aquarium_heater_lifespan
          name: Expected Lifespan
        
        - type: section
          label: UV Sterilizer
        - entity: input_datetime.aquarium_uv_bulb_installed
          name: Bulb Installed
        - entity: sensor.uv_bulb_age
          name: Current Age
        - entity: input_number.aquarium_uv_lifespan
          name: Expected Lifespan
    
    # Parameter Charts (if ApexCharts available)
    - type: custom:apexcharts-card
      header:
        show: true
        title: 📈 Parameter Trends
      graph_span: 30d
      series:
        - entity: input_number.aquarium_nitrate
          name: Nitrate
          color: '#f59e0b'
        - entity: input_number.aquarium_ph
          name: pH (x10)
          color: '#3b82f6'
          transform: "return x * 10;"
```

---

## 🎯 Summary of Enhancements

### ✅ What You Get:

1. **📦 Supply Inventory**
   - Track stock levels
   - Auto-calculate remaining
   - Low stock alerts
   - Usage tracking

2. **💰 Cost Tracking**
   - Per-task costs
   - Monthly estimates
   - Annual projections
   - Year-to-date totals

3. **🍽️ Feeding Schedules**
   - Multiple daily feeds
   - Automated reminders
   - Vacation mode
   - Food stock tracking
   - Missed feeding alerts

4. **💊 Dosing Schedules**
   - Daily supplement dosing
   - Stock level tracking
   - Low supply alerts
   - Automatic deduction

5. **🧪 Water Parameters**
   - Log test results
   - Track trends
   - Automatic alerts
   - Status indicators

6. **🔧 Equipment Lifespan**
   - Track installation dates
   - Calculate age
   - Replacement reminders
   - Percent used indicators

---

## 📱 Total Notifications You'll Get:

- Water change reminders (3-day, today, overdue)
- Salt stock low
- Carbon stock low
- Test strips low
- Food running low
- Morning feeding reminder
- Evening feeding reminder
- Missed feeding alert
- Daily dosing reminder
- Calcium stock low
- Ammonia/nitrite/pH alerts
- Equipment replacement alerts

**That's enterprise-level aquarium management! 🚀**

---

## ⏱️ Installation Time

- **Initial Setup:** 45-60 minutes
- **Configuration:** 15 minutes
- **Testing:** 10 minutes
- **Total:** ~90 minutes

**But worth it for complete automation! 🎯**
