# Python Code Addition for Smart Refill Button

## Add to ato_monitor.py

Add this code to the `on_message` function in your `ato_monitor.py` script:

```python
# Add this elif block to the on_message function (around line 1100-1200)

elif msg.topic == "aquarium/ato/smart_refill":
    """
    Smart refill button pressed
    Automatically calculates refill amount based on activations since last refill
    Only works when calibration confidence >= 80%
    """
    activations = calibration_data['activations_since_refill']
    calculated_amount = activations * LITERS_PER_ACTIVATION
    confidence = calibration_data['confidence']
    
    # Validate confidence level
    if confidence >= 80:
        print(f"🎯 Smart Refill Activated:")
        print(f"   Activations: {activations}")
        print(f"   Calibration: {LITERS_PER_ACTIVATION}L per activation")
        print(f"   Calculated: {calculated_amount}L")
        print(f"   Confidence: {confidence}%")
        
        # Record the refill for calibration
        record_refill(calculated_amount)
        
        # Reset reservoir to full capacity
        reservoir_level = RESERVOIR_CAPACITY
        
        # Clear any low reservoir warnings
        client.publish("aquarium/ato/alert_warning", "")
        
        # Publish updated stats
        publish_stats()
        
        # Success message
        success_msg = f"✅ Smart refill: {calculated_amount:.1f}L added, reservoir at {RESERVOIR_CAPACITY}L"
        print(success_msg)
        
        # Optional: Send notification (if you have notifications set up)
        # You can uncomment this if you want a confirmation notification
        # client.publish("aquarium/ato/notification", success_msg)
    
    else:
        # Confidence too low for smart refill
        error_msg = f"⚠️ Smart refill requires 80%+ confidence. Current: {confidence}%"
        print(error_msg)
        
        # Publish warning to user
        client.publish("aquarium/ato/alert_warning", error_msg)
        
        print("   Please use manual refill entry until calibration improves")
```

## Where to Add It

Find this section in `ato_monitor.py`:

```python
def on_message(client, userdata, msg):
    """Handle incoming MQTT messages"""
    global daily_usage, activation_count, reservoir_level, monitoring_enabled, disabled_reason
    
    if msg.topic == "aquarium/ato/reset":
        # ... existing code ...
    
    elif msg.topic == "aquarium/ato/refill":
        # ... existing code ...
    
    elif msg.topic == "aquarium/ato/enable":
        # ... existing code ...
    
    # ADD THE NEW BLOCK HERE ↓
    elif msg.topic == "aquarium/ato/smart_refill":
        # Paste the smart refill code here
```

## Testing

After adding the code:

1. **Restart the ATO service:**
   ```bash
   sudo systemctl restart ato-monitor.service
   ```

2. **Check it's working:**
   ```bash
   journalctl -u ato-monitor.service -f
   ```

3. **Test with MQTT (optional):**
   ```bash
   mosquitto_pub -h YOUR_HA_IP -t "aquarium/ato/smart_refill" -m "1" -u username -P password
   ```

4. **Test in Home Assistant:**
   - Go to Calibration tab
   - If confidence < 80%: Only manual mode shows
   - If confidence ≥ 80%: Smart button appears!

## Expected Behavior

### When Confidence < 80%:
```
⚠️ Smart refill requires 80%+ confidence. Current: 60%
   Please use manual refill entry until calibration improves
```

### When Confidence ≥ 80%:
```
🎯 Smart Refill Activated:
   Activations: 15
   Calibration: 1.22L per activation
   Calculated: 18.3L
   Confidence: 95%
✅ Smart refill: 18.3L added, reservoir at 23.0L
```

---

**That's it! The smart refill button is now functional! 🎯✨**
