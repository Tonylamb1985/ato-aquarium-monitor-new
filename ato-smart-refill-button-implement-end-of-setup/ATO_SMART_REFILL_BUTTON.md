# 🎯 Smart ATO Refill Button Enhancement

## Problem
Currently you have to manually enter how many liters you added each time you refill.

## Solution
**Smart refill button that:**
- ✅ Only appears when calibration confidence ≥ 80%
- ✅ Automatically calculates exact refill amount
- ✅ One-tap to mark as refilled to 100%
- ✅ Uses auto-calibration to know the amount

---

## 🚀 How It Works

### Logic:
```
Current Reservoir: 8.5L
Activations Since Refill: 15
Calibrated L/activation: 1.0L

When you press "Full Refill":
→ Calculates: 15 activations × 1.0L = 15.0L added
→ Records refill for calibration
→ Resets reservoir to 23.0L (100%)
→ Resets activation counter to 0
```

### Smart Display:
- **Confidence < 80%:** Show manual input (not accurate enough yet)
- **Confidence ≥ 80%:** Show smart button (accurate!)

---

## 📝 Home Assistant Configuration

### Step 1: Add Conditional Card Logic

Update your dashboard Settings or Calibration tab:

```yaml
# Replace the existing refill section with this:

- type: vertical-stack
  cards:
    # Show this when confidence is LOW (< 80%)
    - type: conditional
      conditions:
        - entity: sensor.ato_calibration_confidence
          state_not: unavailable
          state_below: 80
      card:
        type: entities
        title: 💧 Manual Refill Recording
        entities:
          - entity: number.ato_refill_amount
            name: "Liters Added (Manual)"
          
          - type: button
            name: "Record Refill"
            icon: mdi:water-plus
            tap_action:
              action: call-service
              service: mqtt.publish
              data:
                topic: "aquarium/ato/refill"
                payload: >
                  {{ states('number.ato_refill_amount') }}
        
        card_mod:
          style: |
            ha-card {
              background: #fef3c7;
              border-left: 4px solid #f59e0b;
            }
        
        footer:
          type: markdown
          content: |
            ⚠️ **Low Confidence Mode**
            
            Calibration: {{ states('sensor.ato_calibration_confidence') }}%
            
            Please measure and enter exact refill amount.
            After 4-5 refills, smart refill will be enabled!
    
    # Show this when confidence is HIGH (≥ 80%)
    - type: conditional
      conditions:
        - entity: sensor.ato_calibration_confidence
          state_not: unavailable
          above: 79
      card:
        type: entities
        title: 🎯 Smart Refill (Auto-Calculated)
        entities:
          - type: custom:mushroom-template-card
            primary: "Calculated Refill Amount"
            secondary: >
              {% set activations = states('sensor.ato_activations_since_refill') | int %}
              {% set lph = states('sensor.ato_calibrated_l_activation') | float %}
              {{ (activations * lph) | round(2) }}L
            icon: mdi:calculator
            icon_color: green
          
          - entity: sensor.ato_activations_since_refill
            name: "Activations Since Last Refill"
          
          - entity: sensor.ato_calibrated_l_activation
            name: "Calibrated Amount"
          
          - type: divider
          
          - type: button
            name: "✅ Full Refill (Auto)"
            icon: mdi:water-check
            tap_action:
              action: call-service
              service: button.ato_smart_refill
            action_name: "REFILL"
        
        card_mod:
          style: |
            ha-card {
              background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
              border-left: 4px solid #10b981;
            }
        
        footer:
          type: markdown
          content: |
            ✅ **Smart Refill Enabled**
            
            Confidence: {{ states('sensor.ato_calibration_confidence') }}%
            
            Amount is automatically calculated based on usage!
            Just press the button when you've refilled to full.
```

### Step 2: Add Smart Refill Button Entity

Add to `configuration.yaml`:

```yaml
mqtt:
  button:
    - name: "ATO Smart Refill"
      command_topic: "aquarium/ato/smart_refill"
      payload_press: "1"
      icon: mdi:water-check
      availability:
        - topic: "aquarium/ato/calibration_confidence"
          value_template: "{{ value | int >= 80 }}"
```

### Step 3: Update Python Script

Add this function to `ato_monitor.py`:

```python
# Add to MQTT message handler (on_message function)

elif msg.topic == "aquarium/ato/smart_refill":
    # Calculate refill amount based on activations
    activations = calibration_data['activations_since_refill']
    calculated_amount = activations * LITERS_PER_ACTIVATION
    
    # Only allow if confidence is high enough
    if calibration_data['confidence'] >= 80:
        print(f"🎯 Smart Refill: {activations} activations × {LITERS_PER_ACTIVATION}L = {calculated_amount}L")
        
        # Record the refill
        record_refill(calculated_amount)
        
        # Reset reservoir to full
        reservoir_level = RESERVOIR_CAPACITY
        
        # Publish confirmation
        client.publish("aquarium/ato/alert_warning", "")
        publish_stats()
        
        print(f"✅ Smart refill recorded: {calculated_amount}L added, reservoir now at {RESERVOIR_CAPACITY}L")
    else:
        print(f"⚠️  Smart refill denied: confidence only {calibration_data['confidence']}% (need 80%)")
        client.publish("aquarium/ato/alert_warning", 
            f"Smart refill requires 80%+ confidence. Current: {calibration_data['confidence']}%")
```

---

## 🎨 Alternative: Simplified Version

If you want it even simpler, here's a minimal version:

```yaml
# Single card that changes based on confidence

- type: entities
  title: 💧 Reservoir Refill
  entities:
    # Always show current status
    - entity: sensor.ato_reservoir_level
      name: Current Level
    
    - entity: sensor.ato_activations_since_refill
      name: Activations Since Refill
    
    - type: conditional
      conditions:
        - entity: sensor.ato_calibration_confidence
          above: 79
      row:
        type: section
        label: "Smart Refill Available"
    
    # Manual input (always available)
    - entity: number.ato_refill_amount
      name: Manual Entry
    
    - type: button
      name: "Manual Refill"
      icon: mdi:water-plus
      tap_action:
        action: call-service
        service: mqtt.publish
        data:
          topic: "aquarium/ato/refill"
          payload: "{{ states('number.ato_refill_amount') }}"
    
    # Smart button (only when confidence high)
    - type: conditional
      conditions:
        - entity: sensor.ato_calibration_confidence
          above: 79
      row:
        type: button
        name: "🎯 Smart Refill ({{ (states('sensor.ato_activations_since_refill')|int * states('sensor.ato_calibrated_l_activation')|float)|round(1) }}L)"
        icon: mdi:water-check
        tap_action:
          action: call-service
          service: mqtt.publish
          data:
            topic: "aquarium/ato/smart_refill"
            payload: "1"
  
  footer:
    type: markdown
    content: |
      {% if states('sensor.ato_calibration_confidence')|int >= 80 %}
      ✅ **Smart Refill Active** ({{ states('sensor.ato_calibration_confidence') }}% confidence)
      {% else %}
      ⚠️ **Manual Mode** ({{ states('sensor.ato_calibration_confidence') }}% confidence - need 80%+)
      {% endif %}
```

---

## 🎯 Even Simpler: Always Calculate, Let User Confirm

This version shows the calculated amount and lets you adjust if needed:

```yaml
- type: entities
  title: 💧 Refill Reservoir
  entities:
    - type: custom:mushroom-template-card
      primary: "Calculated Refill Amount"
      secondary: >
        {% set act = states('sensor.ato_activations_since_refill')|int %}
        {% set lph = states('sensor.ato_calibrated_l_activation')|float %}
        {% set conf = states('sensor.ato_calibration_confidence')|int %}
        {{ (act * lph)|round(1) }}L
        ({{ conf }}% confidence)
      icon: >
        {% if states('sensor.ato_calibration_confidence')|int >= 80 %}
        mdi:check-circle
        {% else %}
        mdi:alert-circle
        {% endif %}
      icon_color: >
        {% if states('sensor.ato_calibration_confidence')|int >= 80 %}
        green
        {% else %}
        orange
        {% endif %}
    
    - type: divider
    
    # Always show calculated amount in input
    - entity: number.ato_refill_amount
      name: "Refill Amount"
    
    - type: button
      name: "Record Refill"
      icon: mdi:water-plus
      tap_action:
        action: call-service
        service: mqtt.publish
        data:
          topic: "aquarium/ato/refill"
          payload: "{{ states('number.ato_refill_amount') }}"

# Script to auto-populate the calculated amount
script:
  ato_auto_populate_refill:
    alias: "Auto-Populate Refill Amount"
    sequence:
      - service: input_number.set_value
        target:
          entity_id: number.ato_refill_amount
        data:
          value: >
            {% set act = states('sensor.ato_activations_since_refill')|int %}
            {% set lph = states('sensor.ato_calibrated_l_activation')|float %}
            {{ (act * lph)|round(1) }}

# Auto-populate when opening dashboard
automation:
  - alias: "ATO Auto-Populate Refill Amount"
    trigger:
      - platform: state
        entity_id: sensor.ato_activations_since_refill
    action:
      - service: script.ato_auto_populate_refill
```

---

## 💡 Best Approach (Recommended)

**Use conditional display:**
1. **First 4 refills:** Manual entry (building confidence)
2. **After 80% confidence:** Smart button appears
3. **Both options always available** (for flexibility)

### Why?
- ✅ Encourages accurate manual entry during calibration
- ✅ Rewards you with automation once calibrated
- ✅ Clear visual feedback on calibration progress
- ✅ Still allows manual override if needed

---

## 📱 What You'll See

### During Calibration (< 80%):
```
┌──────────────────────────────────┐
│  💧 Manual Refill Recording      │
├──────────────────────────────────┤
│  ⚠️ Low Confidence Mode          │
│  Calibration: 60%                │
│                                  │
│  Liters Added: [18.5] L          │
│  [Record Refill]                 │
│                                  │
│  Need 4-5 refills for smart mode │
└──────────────────────────────────┘
```

### After Calibration (≥ 80%):
```
┌──────────────────────────────────┐
│  🎯 Smart Refill (Auto)          │
├──────────────────────────────────┤
│  ✅ Smart Refill Enabled         │
│  Confidence: 95%                 │
│                                  │
│  Calculated: 18.3L               │
│  (15 activations × 1.22L)        │
│                                  │
│  [✅ Full Refill (Auto)]         │
│                                  │
│  Amount auto-calculated!         │
└──────────────────────────────────┘
```

---

## 🎛️ Configuration Options

You can adjust the confidence threshold:

```python
# In Python script
SMART_REFILL_CONFIDENCE_MIN = 80  # Change to 70, 90, etc.

# Or in dashboard
above: 79  # Change to 69, 89, etc.
```

---

## ✅ Benefits

**Before:**
1. Refill reservoir
2. Measure amount added
3. Enter in HA
4. Click button

**After (with smart button):**
1. Refill reservoir
2. Click button
3. Done! ✨

**Saves:** ~30 seconds per refill, zero mental effort!

---

## 🔧 Installation

1. **Add conditional card** to dashboard
2. **Add button entity** to configuration.yaml
3. **Update Python script** with smart_refill handler
4. **Restart HA & ATO service**
5. **Test with low confidence** (should show manual)
6. **Wait for 80%+ confidence** (smart button appears!)

---

## 💾 Summary

You get:
- ✅ **Smart button** when confidence ≥ 80%
- ✅ **Auto-calculated** refill amount
- ✅ **One-tap** operation
- ✅ **Manual fallback** always available
- ✅ **Visual feedback** on confidence
- ✅ **Calibration progress** tracking

**This makes refilling almost effortless! 🎯✨**

Would you like me to:
1. Add this to your existing dashboard files?
2. Create a complete updated dashboard with this feature?
3. Add to the Python script modifications?

Let me know! 🚀
