# Patient Case Profile: Priya Sharma
## Maternal Health Monitoring — Wearable Belt System

---

## Patient Overview

**Name:** Priya Sharma  
**Age:** 26 years  
**Gestational Age:** 28 weeks (7 months pregnant)  
**Location:** Bengaluru, Karnataka, India  
**Language:** Kannada (primary), Hindi, English  
**Gravida/Para:** G2P1 (second pregnancy, one previous delivery)  
**Previous Delivery:** Normal vaginal delivery, healthy baby girl, 3 years ago  
**Current Pregnancy:** Singleton, cephalic presentation  
**ANC Visits:** 4 completed as per schedule  
**BMI (pre-pregnancy):** 22.4 kg/m²  
**Blood Group:** B+  
**Known Allergies:** None  
**Known Conditions:** Mild iron-deficiency anemia (on supplementation since Week 12)

---

## Baseline Vitals (Established at Week 20 ANC Visit)

| Vital Sign | Priya's Baseline | Normal Range (28 weeks) |
|---|---|---|
| Maternal Heart Rate | 78–85 bpm | 70–90 bpm |
| SpO2 (oxygen saturation) | 98–99% | 97–100% |
| Body Temperature | 36.6–37.1°C | 36.5–37.5°C |
| Fetal Heart Rate (FHR) | 138–148 bpm | 120–160 bpm |
| Fetal Movement (per hour) | 8–12 counts | 4–10 counts per hour |
| Activity Level (accelerometer) | Moderate | Variable |

---

## Week 28 — Normal Day Sensor Readings (Reference)

**Morning (08:00–09:00):**
- Maternal HR: 82 bpm
- SpO2: 98.5%
- Temperature: 36.7°C
- Fetal HR (mic-extracted): 142 bpm
- Fetal movement (1 hour): 9 counts
- Activity: Low (resting/sitting)
- Fusion flags: NONE — all normal

**Afternoon (14:00–15:00):**
- Maternal HR: 88 bpm (slightly higher, post-meal + walking)
- SpO2: 97.8%
- Temperature: 37.0°C
- Fetal HR: 146 bpm
- Fetal movement: 7 counts
- Activity: Moderate (household activity)
- Fusion flags: NONE

**Night (22:00–23:00):**
- Maternal HR: 76 bpm
- SpO2: 99.1%
- Temperature: 36.6°C
- Fetal HR: 139 bpm
- Fetal movement: 3 counts (normal — fetal sleep cycle)
- Activity: Low (lying down)
- Fusion flags: NONE

---

## Scenario 1: Chorioamnionitis Risk Alert (Week 29)

**What happened:** Priya developed a low-grade fever after a urinary tract infection that went untreated for 3 days.

**Sensor readings at time of alert:**

| Sensor | Value | Status |
|---|---|---|
| Maternal HR | 108 bpm | ⚠ Elevated (tachycardia) |
| SpO2 | 97.1% | Normal |
| Temperature | 38.3°C | ⚠ Fever (>38°C) |
| Fetal HR | 168 bpm | ⚠ Elevated (fetal tachycardia >160) |
| Fetal movement | 2 counts/hour | ⚠ Reduced |
| Activity | Low | Priya is resting in bed |

**Fusion engine reasoning:**  
Maternal fever (38.3°C) + Maternal tachycardia (108 bpm) + Fetal tachycardia (168 bpm) = Classic triad for chorioamnionitis.

**Flag raised:** `CHORIOAMNIONITIS_RISK` — severity: CRITICAL

**What Priya felt:** "I feel hot and uncomfortable. My belly feels tight and I haven't felt the baby move much since morning."

**What the AI agent told Priya (in Kannada, translated):**  
"Priya, your wearable shows your temperature is 38.3°C, which is a fever, and both your heart rate and the baby's heart rate are higher than usual. This combination can sometimes indicate an infection inside the womb. Please go to the hospital or contact your doctor right away. Do not wait. This needs immediate medical attention."

**Medical outcome (for realism):** Doctor confirmed UTI ascending to chorioamnionitis. IV antibiotics started. Baby delivered healthy at 30 weeks after signs of improvement.

---

## Scenario 2: Fetal Distress / Possible Hypoxia (Week 31)

**What happened:** Priya was walking uphill. The baby showed reduced movement and fetal HR dropped irregularly.

**Sensor readings:**

| Sensor | Value | Status |
|---|---|---|
| Maternal HR | 94 bpm | Slightly elevated (exertion) |
| SpO2 | 96.4% | Borderline low |
| Temperature | 36.9°C | Normal |
| Fetal HR | 108 bpm (was 144) | ⚠ Sudden drop — bradycardia |
| Fetal movement | 1 count/hour | ⚠ Very low |
| Activity | High | Walking fast |

**Fusion engine reasoning:**  
Reduced fetal movement + reduced FHR variability + borderline SpO2 = Possible fetal distress.

**Flag raised:** `FETAL_DISTRESS_POSSIBLE` — severity: WARNING

**What the AI agent told Priya:**  
"Priya, the baby's heart rate has dropped and movement is low. Please stop what you are doing, sit down, rest, and lie on your left side. If this does not improve in 20 minutes or you feel something is wrong, go to the hospital immediately."

---

## Scenario 3: Dehydration / Maternal Exhaustion (Week 30, Summer)

**What happened:** Priya forgot to drink water during a hot day. She felt dizzy and weak.

**Sensor readings:**

| Sensor | Value | Status |
|---|---|---|
| Maternal HR | 102 bpm | ⚠ Elevated |
| SpO2 | 98.0% | Normal |
| Temperature | 37.2°C | Normal |
| Fetal HR | 151 bpm | Normal |
| Fetal movement | 6 counts/hour | Normal |
| Activity | Very low | Barely moving, lying down |

**Fusion engine reasoning:**  
Elevated HR + Normal SpO2 + Normal temperature + Very low activity = Rules out infection and hypoxia. Points to dehydration or exhaustion.

**Flag raised:** `MATERNAL_DEHYDRATION_EXHAUSTION` — severity: INFO

**What the AI agent told Priya:**  
"Priya, your heart rate is a bit high but your oxygen and temperature are normal — this can happen when you are dehydrated or tired. Please drink water or oral rehydration solution (ORS) right now. Rest on your left side. If your heart rate does not come down in 30 minutes, call your doctor."

---

## Scenario 4: Placental Insufficiency / IUGR Watch (Week 32 — Trend Alert)

**What happened:** Priya's fetal movement gradually decreased over 10 days. No single day was alarming, but the trend was significant.

**Movement trend (movements per day):**

| Day | Movement Count | Status |
|---|---|---|
| Day 1 | 48 | Normal |
| Day 3 | 42 | Normal |
| Day 5 | 35 | Slightly low |
| Day 7 | 28 | ⚠ Low |
| Day 9 | 22 | ⚠ Low |
| Day 10 | 18 | ⚠ Very low |

**Fusion engine reasoning:**  
Gradual decline in fetal movement over >7 days = IUGR risk flag (not a single-reading alert).

**Flag raised:** `IUGR_RISK_WATCH` — severity: INFO (trend-based, not real-time)

**What the AI agent told Priya:**  
"Priya, over the last 10 days, we have noticed the baby is moving less and less each day. This slow change over time can sometimes mean the baby is not getting enough nutrition from the placenta. This is not an emergency right now, but you need to schedule an ultrasound with your doctor soon — ideally within 48 hours — to check the baby's growth."

---

## Priya's Common Questions to the AI Agent

1. "ನನ್ನ ಹೃದಯ ಬಡಿತ ಹೆಚ್ಚಾಗಿದೆ, ಏನಾದರೂ ತಪ್ಪಾಗಿದೆಯೇ?" (My heart rate is high, is something wrong?)
2. "Baby is not moving much since this morning. Should I be worried?"
3. "I have mild fever since last night. The app showed a warning. What does it mean?"
4. "How many times should my baby move per hour at 28 weeks?"
5. "Can I walk in the evening? Is it safe for the baby?"
6. "My belt is showing oxygen 96%. Is that okay for the baby?"

**Agent responses are always:**
- In the language the question was asked (Kannada, Hindi, or English)
- Conservative — always recommending professional consultation when in doubt
- Based on the RAG corpus and active sensor flags, never on individual raw sensor values
- Never diagnosing — only narrating what the sensor flags say and pointing to guidelines

---

## Emergency Contact Information (Template for Indian Context)

- **Emergency:** 108 (Ambulance — India)
- **ASHA Worker Number:** (stored by app)
- **Doctor/Clinic:** (stored by app)
- **Nearest Government Hospital:** (GPS-based)
