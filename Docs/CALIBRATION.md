# 🎯 Calibration Guide

Complete calibration procedures for ATO Aquarium Monitor sensors.

## Two Types of Calibration

1. **Liters Per Activation** - Auto-calibrating (recommended)
2. **Temperature Sensor** - Manual one-time calibration

---

## 1. Liters Per Activation Calibration

### Auto-Calibration (Recommended)

The system automatically calibrates based on your reservoir refills.

#### How It Works

1. **System tracks** activations between refills
2. **You record** exact amount added when refilling
3. **System calculates:** Liters ÷ Activations = L/activation
4. **Rolling average** of last 5 refills for accuracy
5. **Confidence increases** with each refill (20% per refill)

#### Calibration Procedure

**Step 1: Let System Run**
- Don't manually calibrate initially
- Let it use default 1.0L/activation
- Monitor for natural usage

**Step 2: First Refill**
- Wait until reservoir needs refilling
- Use measuring jug to measure EXACTLY how much you add
- Example: Added 18.5L

**Step 3: Record in Home Assistant**
- Go to Settings tab in dashboard
- Find "Record Reservoir Refill" section
- Enter: `18.5` in "Liters Added" field
- Click enter or press "Refill" button

**Step 4: System Calculates**
- System counts activations since last refill (e.g., 15)
- Calculates: 18.5L ÷ 15 = 1.23L per activation
- Updates calibration automatically
- Confidence: 20%

**Step 5: Repeat**
- After 2nd refill: 40% confidence
- After 3rd refill: 60% confidence
- After 4th refill: 80% confidence
- After 5th refill: 100% confidence ✅

#### Monitoring Calibration

**Dashboard Indicators:**
- **Calibrated Value:** Shows current L/activation
- **Confidence Level:** 0-100%
- **Activations Since Refill:** Tracks current cycle

**Confidence Levels:**
- 🔴 0-40%: Need more data (< 2 refills)
- 🟡 40-70%: Learning phase (2-3 refills)
- 🟢 70-100%: Highly accurate (4+ refills)

#### Tips for Accurate Calibration

✅ **DO:**
- Measure refills accurately (use measuring jug)
- Always fill reservoir to same level
- Record every refill consistently
- Wait for natural usage cycles

❌ **DON'T:**
- Estimate refill amounts
- Skip recording refills
- Manually adjust pump runtime
- Change pump speed during calibration

### Manual Calibration (Alternative)

If you want to manually measure:

**Method 1: Single Cycle Measurement**

1. **Mark reservoir level** with tape
2. **Note starting level** (e.g., 20.0L)
3. **Trigger ONE ATO cycle** manually
4. **Let pump run** until float switches off
5. **Measure water used:**
   - Refill to original mark
   - Measure amount added
   - Example: Added 1.2L
6. **Update config.py:**
   ```python
   LITERS_PER_ACTIVATION = 1.2
   ```
7. **Restart service:**
   ```bash
   sudo systemctl restart ato-monitor.service
   ```

**Method 2: Pump Flow Rate**

1. **Disconnect pump** output from tank
2. **Place in measuring container**
3. **Run for exactly 60 seconds:**
   ```bash
   # Use manual pump control in HA
   # Or use test script
   ```
4. **Measure collected water** (e.g., 2.1L)
5. **Calculate flow rate:** 2.1L/min = 126 L/h
6. **Estimate per cycle:**
   - If pump typically runs 30 seconds
   - Volume = (126 L/h ÷ 3600) × 30s = 1.05L
7. **Update config and test**

**Method 3: Multiple Cycles Average**

1. **Empty reservoir** completely
2. **Add exact amount** (e.g., 20.0L)
3. **Let run for 5 cycles** naturally
4. **Measure remaining** (e.g., 14.2L)
5. **Calculate:**
   - Used: 20.0 - 14.2 = 5.8L
   - Average: 5.8L ÷ 5 = 1.16L per cycle
6. **Update config**

---

## 2. Temperature Sensor Calibration

### Why Calibrate?

- DS18B20 accuracy: ±0.5°C (factory)
- After calibration: ±0.1°C possible
- Important for accurate evaporation tracking
- One-time manual calibration

### Method 1: Reference Thermometer (Recommended)

**Equipment Needed:**
- High-quality aquarium thermometer
- Or digital thermometer (±0.1°C accuracy)

**Procedure:**

1. **Place reference thermometer in tank**
   - Submerge fully
   - Keep away from heater/filter
   - Wait 5-10 minutes

2. **Read both thermometers:**
   - Reference: 25.0°C
   - DS18B20 raw: 24.5°C (from Settings tab)

3. **Calculate offset:**
   - Offset = Reference - Raw
   - Offset = 25.0 - 24.5 = +0.5°C

4. **Set calibration in Home Assistant:**
   - Go to Settings tab
   - Find "Temperature Calibration" section
   - Enter: `+0.5` in offset field
   - Click Save

5. **Verify:**
   - Calibrated reading should now show 25.0°C
   - Matches reference thermometer ✅

### Method 2: Ice Water Bath (0°C Reference)

**Equipment Needed:**
- Container with ice water
- Ice cubes
- Stirrer

**Procedure:**

1. **Prepare ice bath:**
   - Fill container with ice and water
   - Stir well for 2-3 minutes
   - Temperature stabilizes at 0°C

2. **Submerge DS18B20:**
   - Place sensor in ice water
   - Wait 2 minutes for stabilization
   - Don't let sensor touch ice directly

3. **Read raw temperature:**
   - Check "Raw Sensor Reading" in HA
   - Example: -0.3°C

4. **Calculate offset:**
   - Target: 0°C
   - Measured: -0.3°C
   - Offset = 0 - (-0.3) = +0.3°C

5. **Apply offset** in Home Assistant

6. **Verify:**
   - Should now read 0.0°C in ice bath

### Method 3: Boiling Water (100°C Reference)

⚠️ **Use only if sensor rated for 100°C!**

**Procedure:**

1. **Boil water** (exactly 100°C at sea level)
2. **Submerge sensor** for 1 minute
3. **Read raw temperature** (e.g., 99.7°C)
4. **Calculate offset:** 100 - 99.7 = +0.3°C
5. **Apply in HA**

**Note:** Adjust for altitude:
- Sea level: 100°C
- 1000m: 96.7°C
- 2000m: 93.5°C

### Calibration Interface

**Home Assistant Settings Tab:**

```
┌─────────────────────────────────────────┐
│  Temperature Sensor Calibration         │
├─────────────────────────────────────────┤
│                                         │
│  Raw Reading:        24.5°C             │
│  Calibration Offset: +0.5°C             │
│  Calibrated Reading: 25.0°C             │
│                                         │
│  [Set Offset: +0.5]  [Reset]           │
│                                         │
│  Quick Adjust:                          │
│  [-0.1°C]  [+0.1°C]                    │
│                                         │
└─────────────────────────────────────────┘
```

### Verification Procedure

After calibration:

1. **Wait 5 minutes** for temperature to stabilize
2. **Compare readings:**
   - Reference thermometer
   - Calibrated DS18B20
   - Should match within ±0.1°C

3. **Test in different conditions:**
   - Morning (cooler)
   - Afternoon (warmer)
   - Heater on/off
   - Verify consistency

4. **Re-calibrate if needed:**
   - If off by >0.2°C
   - Or if conditions change significantly

### Calibration Tips

✅ **Best Practices:**
- Calibrate when tank temperature stable
- Use high-quality reference thermometer
- Allow time for thermal equilibrium
- Verify in ice bath for precision

❌ **Common Mistakes:**
- Not waiting for stabilization
- Using cheap thermometers as reference
- Calibrating during temperature swings
- Touching ice directly with sensor

### When to Re-Calibrate

- **Every 6 months** - Regular maintenance
- **After power outage** - Verify still accurate
- **If readings seem off** - Compare to reference
- **Sensor replacement** - New sensor needs calibration

---

## Calibration Records

### Template

Keep track of calibrations:

```
┌──────────────────────────────────────────────────────┐
│  ATO CALIBRATION LOG                                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│  LITERS PER ACTIVATION                               │
│  Date: ___/___/___                                   │
│  Refill Amount: _______ L                            │
│  Activations: _______                                │
│  Calculated: _______ L/activation                    │
│  Confidence: _______ %                               │
│                                                      │
│  TEMPERATURE SENSOR                                  │
│  Date: ___/___/___                                   │
│  Reference: _______ °C                               │
│  Raw Reading: _______ °C                             │
│  Offset Applied: _______ °C                          │
│  Method: □ Reference  □ Ice Bath  □ Boiling         │
│                                                      │
│  Notes:                                              │
│  _______________________________________________     │
│  _______________________________________________     │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## Calibration Validation

### System Health Check

After calibration, verify:

- [ ] Temperature readings stable
- [ ] Evaporation rates reasonable
- [ ] No alerts triggered
- [ ] Confidence level increasing
- [ ] Dashboard shows correct values

### Expected Values

**Typical Ranges:**
- **L/activation:** 0.5 - 2.5L (depends on float position)
- **Temp offset:** -2.0 to +2.0°C (larger = sensor issue)
- **Confidence:** Should reach 80%+ after 4-5 refills

**Red Flags:**
- Offset > ±2.0°C → Sensor may be faulty
- L/activation varies wildly → Pump issue
- Confidence not improving → Check refill recording

---

**Your system is now calibrated! 🎯✨**

Next: [Troubleshooting Guide](TROUBLESHOOTING.md)
