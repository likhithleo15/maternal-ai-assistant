# Sensor Fusion Engine Logic
## Raspberry Pi 4 — Maternal Wearable Belt

---

## Overview

This document defines exactly **what each sensor measures**, **how raw values are processed**, **what thresholds trigger flags**, and **how multiple sensors are fused** into clinical alert flags. This is the "deterministic engine" — all logic here is rule-based, not AI.

The AI agent reads the OUTPUT of this engine (the flags). It never re-derives them.

---

## Sensors on the Belt

| Sensor | Model (Example) | What it Measures | Output Format |
|---|---|---|---|
| Pulse Oximeter | MAX30102 | Maternal SpO2, Maternal HR (PPG signal) | SpO2 (%), HR (bpm) |
| Temperature | DS18B20 or MLX90614 (IR) | Skin/body temperature | Temperature (°C) |
| Accelerometer | MPU6050 (3-axis) | Body movement, position, vibration | X,Y,Z acceleration (g) |
| Microphone | MEMS mic (e.g., INMP441) | Sound vibrations for fetal HR extraction | Raw audio signal (PCM) |
| Buzzer | Passive buzzer | Alarm output | On/Off |

---

## Signal Processing Per Sensor

### 1. Pulse Oximeter (MAX30102)

**Raw signal:** PPG (photoplethysmography) waveform from red and infrared LEDs.

**Processing steps:**
1. Read raw red and IR samples at 100 Hz
2. Apply bandpass filter (0.5–3 Hz) to isolate heartbeat frequencies
3. Peak detection → inter-beat intervals (IBI) → HR in bpm
4. SpO2 = 110 − 25 × (raw_red/raw_ir ratio) — simplified formula
5. Smooth over 5-second window

**Output to SQLite:**
```python
{
    "maternal_hr": 84,          # beats per minute
    "spo2": 97.8,              # percentage
    "hr_variability_rmssd": 45  # ms — root mean square of successive differences
}
```

### 2. Temperature Sensor (DS18B20)

**Raw signal:** Digital temperature reading in °C.

**Processing steps:**
1. Read every 60 seconds (temperature changes slowly)
2. Apply 3-reading moving average to reduce noise
3. Validate: reject readings outside 34°C–41°C (sensor error)

**Output to SQLite:**
```python
{
    "temperature": 36.8  # Celsius
}
```

### 3. Accelerometer (MPU6050)

**Raw signal:** X, Y, Z acceleration at 50 Hz.

**Processing:**

**For fetal movement detection:**
1. Calculate magnitude = sqrt(x² + y² + z²)
2. High-pass filter to remove gravity (DC component)
3. Detect spikes above threshold (0.15g) that last 200ms–2000ms
4. Filter out maternal movement (maternal breathing ~0.3 Hz, walking ~1–3 Hz)
5. Fetal kicks have characteristic frequency of 0.5–1.5 Hz with duration 300–800ms
6. Count fetal movement events per hour

**For activity level:**
1. Calculate mean absolute deviation of magnitude over 30-second windows
2. < 0.05g = Resting/sleeping
3. 0.05–0.15g = Light activity (sitting, light movement)
4. 0.15–0.3g = Moderate activity (walking slowly)
5. > 0.3g = High activity (walking fast, exercising)

**For contraction detection (future feature):**
1. Very low frequency (0.01–0.03 Hz) periodic tightening
2. Duration 30–90 seconds
3. Returns time between contractions

**Output to SQLite:**
```python
{
    "fetal_movement_count_1h": 8,     # counts per hour
    "activity_level": "light",         # resting/light/moderate/high
    "contraction_detected": False,
    "contraction_interval_min": None
}
```

### 4. Microphone (INMP441) — Fetal HR Extraction

**Raw signal:** PCM audio at 16 kHz. Microphone placed over fundus (top of uterus).

**Processing (simplified Doppler audio analysis):**
1. Apply bandpass filter (100–200 Hz) — fetal heart sounds are 120–180 bpm = 2–3 Hz, but harmonics are detectable
2. Apply autocorrelation to detect periodicity
3. Dominant frequency peak → FHR in bpm
4. Validate: accept only 80–220 bpm range (outside is noise)
5. Smooth over 15-second window
6. Confidence score: how clear the peak is (0.0–1.0)

**Note:** FHR extraction via microphone is approximate (±10–15 bpm). Best accuracy achieved when:
- Mother is lying still
- Belt is correctly positioned
- Environment is quiet

**Output to SQLite:**
```python
{
    "fetal_hr": 142,             # bpm
    "fetal_hr_confidence": 0.78  # 0.0–1.0 (use >0.6 for reliable readings)
}
```

---

## Fusion Thresholds Table

### Individual Sensor Thresholds (Per Priya's Context, 28 weeks)

```python
THRESHOLDS = {
    # Maternal HR
    "maternal_hr_normal_max": 95,
    "maternal_hr_tachycardia": 100,
    "maternal_hr_severe_tachy": 120,
    
    # SpO2
    "spo2_normal_min": 96.0,
    "spo2_borderline_min": 94.0,
    "spo2_critical_min": 92.0,
    
    # Temperature
    "temp_normal_max": 37.5,
    "temp_lowgrade_fever": 37.6,
    "temp_moderate_fever": 38.0,
    "temp_high_fever": 38.5,
    
    # Fetal HR
    "fhr_normal_min": 110,
    "fhr_normal_max": 160,
    "fhr_bradycardia": 100,
    "fhr_tachycardia": 161,
    "fhr_severe_tachy": 180,
    
    # Fetal Movement
    "fetal_movement_min_per_hour": 4,
    "fetal_movement_concern_per_hour": 2,
    
    # Confidence
    "fhr_confidence_min": 0.60,
}
```

---

## Fusion Rules (The Decision Engine)

### Flag 1: CHORIOAMNIONITIS_RISK

```python
def check_chorioamnionitis(vitals):
    """
    Classic clinical triad: maternal fever + maternal tachycardia + fetal tachycardia.
    All three must be present simultaneously.
    """
    has_fever = vitals["temperature"] >= THRESHOLDS["temp_moderate_fever"]  # ≥38.0°C
    has_maternal_tachy = vitals["maternal_hr"] >= THRESHOLDS["maternal_hr_tachycardia"]  # ≥100 bpm
    
    fhr_reliable = vitals["fetal_hr_confidence"] >= THRESHOLDS["fhr_confidence_min"]
    has_fetal_tachy = fhr_reliable and vitals["fetal_hr"] >= THRESHOLDS["fhr_tachycardia"]  # ≥161 bpm
    
    if has_fever and has_maternal_tachy and has_fetal_tachy:
        severity = "CRITICAL" if vitals["temperature"] >= THRESHOLDS["temp_high_fever"] else "WARNING"
        reasoning = (
            f"Maternal fever ({vitals['temperature']}°C) + "
            f"Maternal tachycardia ({vitals['maternal_hr']} bpm) + "
            f"Fetal tachycardia ({vitals['fetal_hr']} bpm)"
        )
        return FusionFlag("CHORIOAMNIONITIS_RISK", severity, reasoning)
    
    return None
```

### Flag 2: FETAL_DISTRESS_POSSIBLE

```python
def check_fetal_distress(vitals):
    """
    Reduced fetal movement + abnormal fetal HR (too high or too low).
    """
    fhr_reliable = vitals["fetal_hr_confidence"] >= THRESHOLDS["fhr_confidence_min"]
    
    fhr_abnormal = fhr_reliable and (
        vitals["fetal_hr"] < THRESHOLDS["fhr_normal_min"] or  # bradycardia
        vitals["fetal_hr"] > THRESHOLDS["fhr_tachycardia"]    # tachycardia
    )
    
    low_movement = vitals["fetal_movement_count_1h"] <= THRESHOLDS["fetal_movement_concern_per_hour"]
    
    # Secondary: SpO2 borderline
    spo2_low = vitals["spo2"] < THRESHOLDS["spo2_normal_min"]
    
    # Temperature normal (not infection)
    no_fever = vitals["temperature"] < THRESHOLDS["temp_lowgrade_fever"]
    
    if fhr_abnormal and low_movement:
        severity = "CRITICAL" if vitals["fetal_hr"] < THRESHOLDS["fhr_bradycardia"] else "WARNING"
        reasoning = (
            f"Fetal HR {vitals['fetal_hr']} bpm (abnormal) + "
            f"Low fetal movement ({vitals['fetal_movement_count_1h']}/hour)"
        )
        if spo2_low:
            reasoning += f" + Borderline SpO2 ({vitals['spo2']}%)"
        return FusionFlag("FETAL_DISTRESS_POSSIBLE", severity, reasoning)
    
    return None
```

### Flag 3: MATERNAL_DEHYDRATION_EXHAUSTION

```python
def check_dehydration_exhaustion(vitals):
    """
    Elevated HR + normal SpO2 + normal temperature + low activity.
    Elimination logic: rules out infection and hypoxia.
    """
    hr_elevated = vitals["maternal_hr"] >= THRESHOLDS["maternal_hr_tachycardia"]  # ≥100 bpm
    spo2_normal = vitals["spo2"] >= THRESHOLDS["spo2_normal_min"]                 # ≥96%
    temp_normal = vitals["temperature"] < THRESHOLDS["temp_lowgrade_fever"]       # <37.6°C
    low_activity = vitals["activity_level"] in ["resting", "light"]
    
    # Fetal HR and movement should be normal too
    fhr_reliable = vitals["fetal_hr_confidence"] >= THRESHOLDS["fhr_confidence_min"]
    fhr_normal = not fhr_reliable or (
        THRESHOLDS["fhr_normal_min"] <= vitals["fetal_hr"] <= THRESHOLDS["fhr_normal_max"]
    )
    
    if hr_elevated and spo2_normal and temp_normal and low_activity and fhr_normal:
        reasoning = (
            f"Elevated maternal HR ({vitals['maternal_hr']} bpm) "
            f"with normal SpO2 ({vitals['spo2']}%), "
            f"normal temp ({vitals['temperature']}°C), "
            f"and low activity — suggests dehydration or exhaustion"
        )
        return FusionFlag("MATERNAL_DEHYDRATION_EXHAUSTION", "INFO", reasoning)
    
    return None
```

### Flag 4: PREECLAMPSIA_ANCILLARY_RISK

```python
def check_preeclampsia_ancillary(vitals, trend_data):
    """
    Indirect risk flag only. No BP sensor available.
    Uses HR variability trend + declining fetal movement + normal temperature.
    """
    # Need trend data — cannot detect from single reading
    movement_declining = trend_data.get("movement_7day_trend") == "declining"
    temp_normal = vitals["temperature"] < THRESHOLDS["temp_lowgrade_fever"]
    
    # HR variability decreasing (RMSSD dropping over time)
    hr_variability_low = trend_data.get("avg_rmssd_7day", 50) < 30  # ms
    
    if movement_declining and temp_normal and hr_variability_low:
        reasoning = (
            "Declining fetal movement trend over 7 days + "
            "reduced HR variability + normal temperature — "
            "indirect signs consistent with preeclampsia risk. "
            "BP CHECK REQUIRED — this is not a diagnosis."
        )
        return FusionFlag("PREECLAMPSIA_ANCILLARY_RISK", "WARNING", reasoning)
    
    return None
```

### Flag 5: IUGR_RISK_WATCH

```python
def check_iugr_trend(mother_id, db_connection):
    """
    Longitudinal trend alert only. Computed daily, not in real-time.
    Requires 7+ days of data.
    """
    # Query 14 days of movement data
    movement_data = db_connection.execute("""
        SELECT date, daily_movement_count 
        FROM movement_trend 
        WHERE mother_id = ? AND date >= date('now', '-14 days')
        ORDER BY date ASC
    """, (mother_id,)).fetchall()
    
    if len(movement_data) < 7:
        return None  # Not enough data yet
    
    # Calculate trend using linear regression slope
    counts = [row["daily_movement_count"] for row in movement_data]
    baseline_avg = sum(counts[:3]) / 3  # Average of first 3 days
    recent_avg = sum(counts[-3:]) / 3   # Average of last 3 days
    
    pct_decline = (baseline_avg - recent_avg) / baseline_avg * 100
    
    if pct_decline >= 30:  # 30% or more decline
        reasoning = (
            f"Fetal movement declined {pct_decline:.0f}% over "
            f"{len(movement_data)} days "
            f"(from ~{baseline_avg:.0f} to ~{recent_avg:.0f} movements/day). "
            "Gradual decline pattern consistent with IUGR risk watch."
        )
        severity = "WARNING" if pct_decline >= 50 else "INFO"
        return FusionFlag("IUGR_RISK_WATCH", severity, reasoning)
    
    return None
```

---

## Data Write Schedule (Raspberry Pi → SQLite)

| Data Type | Write Frequency | Table |
|---|---|---|
| Vitals (HR, SpO2, Temp) | Every 30 seconds | `vitals` |
| Fetal HR + confidence | Every 30 seconds | `vitals` |
| Fetal movement count | Every 5 minutes (rolling 1-hour count) | `vitals` |
| Activity level | Every 30 seconds | `vitals` |
| Fusion flags (real-time) | When flag state changes | `fusion_flags` |
| Daily movement total | Once per day (midnight) | `movement_trend` |

---

## SQLite Write Example (Pi Python Code)

```python
import sqlite3
from datetime import datetime

def write_vitals(mother_id, sensor_data, db_path="./data/sensor_data.db"):
    conn = sqlite3.connect(db_path)
    conn.execute("""
        INSERT INTO vitals (
            mother_id, timestamp,
            maternal_hr, spo2, temperature,
            fetal_hr, fetal_hr_confidence,
            fetal_movement_count_1h, activity_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        mother_id,
        datetime.now().isoformat(),
        sensor_data["maternal_hr"],
        sensor_data["spo2"],
        sensor_data["temperature"],
        sensor_data["fetal_hr"],
        sensor_data["fetal_hr_confidence"],
        sensor_data["fetal_movement_count_1h"],
        sensor_data["activity_level"]
    ))
    conn.commit()
    conn.close()

def write_flag(mother_id, flag, db_path="./data/sensor_data.db"):
    conn = sqlite3.connect(db_path)
    # First resolve any previously active same-type flag
    conn.execute("""
        UPDATE fusion_flags 
        SET is_active = 0, resolved_at = ?
        WHERE mother_id = ? AND flag_name = ? AND is_active = 1
    """, (datetime.now().isoformat(), mother_id, flag.name))
    
    # Insert new flag
    conn.execute("""
        INSERT INTO fusion_flags (mother_id, timestamp, flag_name, severity, reasoning, is_active)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (mother_id, datetime.now().isoformat(), flag.name, flag.severity, flag.reasoning))
    conn.commit()
    conn.close()
```

---

## The AI Agent's Read Contract

The AI agent's `SensorReader` class ONLY uses these SQL queries:

```sql
-- Latest vitals (last 2 minutes)
SELECT * FROM vitals 
WHERE mother_id = ? AND timestamp > datetime('now', '-2 minutes')
ORDER BY timestamp DESC LIMIT 1;

-- Active flags
SELECT * FROM fusion_flags 
WHERE mother_id = ? AND is_active = 1
ORDER BY timestamp DESC;

-- 7-day movement trend
SELECT date, daily_movement_count 
FROM movement_trend 
WHERE mother_id = ? AND date >= date('now', '-7 days')
ORDER BY date ASC;

-- Recent flag history (for context)
SELECT flag_name, severity, reasoning, timestamp
FROM fusion_flags 
WHERE mother_id = ? AND timestamp > datetime('now', '-24 hours')
ORDER BY timestamp DESC;
```

**The AI agent NEVER:**
- Reads raw sensor values and computes thresholds
- Writes to any table
- Decides if a flag should exist
- Changes flag severity
