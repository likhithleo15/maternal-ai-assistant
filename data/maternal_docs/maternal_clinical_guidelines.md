# Maternal Health Clinical Guidelines
## For Wearable Sensor Belt System — Indian Antenatal Context

---

## 1. Normal Vital Ranges in Pregnancy (Trimester-wise)

### Heart Rate (Maternal)

| Trimester | Normal Range | Mild Tachycardia | Significant Tachycardia |
|---|---|---|---|
| First (0–12 weeks) | 68–88 bpm | 89–100 bpm | >100 bpm |
| Second (13–26 weeks) | 75–92 bpm | 93–105 bpm | >105 bpm |
| Third (27–40 weeks) | 78–95 bpm | 96–110 bpm | >110 bpm |

**Why HR increases in pregnancy:** Blood volume increases by 40–50% during pregnancy, making the heart work harder. A resting HR of 80–90 bpm is common and normal in the third trimester.

### Oxygen Saturation (SpO2)

| SpO2 Value | Interpretation | Action |
|---|---|---|
| 98–100% | Optimal | None required |
| 96–97% | Acceptable | Monitor, ensure good posture |
| 94–95% | Borderline low | Sit upright, avoid lying flat, recheck |
| <94% | Concerning | Seek medical attention promptly |

**Important:** SpO2 can drop momentarily when lying flat on back (supine hypotension syndrome). Always measure while sitting or lying on left side.

### Body Temperature

| Temperature | Interpretation | Action |
|---|---|---|
| 36.5–37.5°C | Normal | None |
| 37.6–37.9°C | Low-grade fever | Rest, fluids, monitor |
| 38.0–38.4°C | Fever — Moderate | Seek medical attention same day |
| ≥38.5°C | High fever | Seek emergency care |

### Fetal Heart Rate (FHR)

| FHR Range | Interpretation |
|---|---|
| 110–160 bpm | Normal |
| 100–109 bpm | Mild bradycardia — requires monitoring |
| <100 bpm | Severe bradycardia — emergency |
| 161–180 bpm | Mild tachycardia — monitor, check mother's temperature |
| >180 bpm | Severe tachycardia — seek emergency care |

**Note:** FHR naturally varies (beat-to-beat variability). Absence of variability (flat trace) is more concerning than mildly elevated/decreased rate.

### Fetal Movement

| Gestational Age | Expected Movements |
|---|---|
| 24–28 weeks | At least 10 movements in 2 hours |
| 28–32 weeks | At least 10 movements in 2 hours |
| 32–36 weeks | At least 10 movements in 2 hours |
| 36–40 weeks | At least 10 in 2 hours (may feel different — baby has less space) |

**Cardiff Count-to-Ten Method:** Start counting at the same time each day. Count the first 10 movements. Normal: 10 movements within 2 hours. If fewer than 10 in 2 hours — contact doctor.

---

## 2. Chorioamnionitis (Intrauterine Infection)

### What is Chorioamnionitis?

Chorioamnionitis is an infection of the membranes (chorion and amnion) surrounding the baby and the amniotic fluid. It is a serious pregnancy complication that requires immediate medical attention.

### How Our Sensor Fusion Detects It

The system detects the **clinical triad** — three signs occurring together:
1. **Maternal fever** (temperature ≥38.0°C)
2. **Maternal tachycardia** (HR >100 bpm)
3. **Fetal tachycardia** (FHR >160 bpm)

Any single sign alone is not specific. All three together are highly suggestive.

### Why These Three Together?

The infection triggers the body's immune response:
- Fever: Body fighting the infection
- Maternal tachycardia: Heart working harder due to fever and infection
- Fetal tachycardia: Baby's heart rate rises when exposed to infection chemicals (cytokines) crossing the placenta

### Additional Supporting Signs (from our sensors)

- Reduced fetal movement (baby becomes less active when stressed)
- Normal SpO2 (helps rule out hypoxia as the cause of tachycardia)

### Risk Factors for Chorioamnionitis in Indian Context

- Premature rupture of membranes (PROM) — waters breaking before labor
- Multiple vaginal examinations
- Untreated urinary tract infections (UTI)
- Poor hygiene, lack of clean water access
- Prolonged labor

### What to Do When Flag is Raised

**IMMEDIATE action required:**
1. Do NOT wait to see if it improves
2. Call your doctor or 108 (ambulance)
3. Go to the nearest hospital with obstetric emergency services
4. Treatment: IV antibiotics (ampicillin + gentamicin, or as prescribed)
5. Baby may need to be delivered, even if premature

### What the AI Agent Will Say

The agent will explain the flag in simple language and urge immediate hospital visit. It will NOT prescribe medicines or say definitively that chorioamnionitis is present — only that the sensor flags match the pattern and a doctor must evaluate immediately.

---

## 3. Fetal Distress / Possible Hypoxia

### What is Fetal Distress?

Fetal distress means the baby is not getting enough oxygen (hypoxia) or is under stress. It is detected by abnormal heart rate patterns and reduced movement.

### How Our Sensor Fusion Detects It

The system looks for:
1. **Abnormal FHR** — either very low (<110 bpm, bradycardia) or high (>160 bpm, tachycardia) OR sudden change
2. **Reduced fetal movement** — less than 4 counts in 2 hours when previously normal
3. **These two occurring together**

### FHR Patterns That Suggest Distress

| Pattern | What It Means | Sensor Detection |
|---|---|---|
| Late decelerations | FHR drops AFTER a contraction (or movement) | FHR dip 15–30 sec after movement spike |
| Prolonged bradycardia | FHR stays below 110 for >3 minutes | Sustained low FHR reading |
| Absent variability + tachycardia | No beat-to-beat variation + high rate | Flat FHR trend + rate >160 |

### Why Movement Matters

When a baby is distressed, it conserves energy and moves less. Combined with abnormal FHR, reduced movement strongly suggests a problem.

### The Accelerometer Role

The wearable belt's accelerometer helps by:
- Distinguishing maternal movement from fetal movement
- Confirming that reduced fetal movement is real (not just Priya sitting still)
- Detecting contractions (rhythmic tightening pattern)

### Causes in Indian Context

- Umbilical cord compression (cord around neck)
- Placental insufficiency (placenta not working well)
- Prolonged lying on back (supine position) — very common
- Severe maternal dehydration
- Severe maternal anemia (common in India — affects oxygen delivery)
- Preeclampsia

### Immediate Actions When Flag Raised

1. **Stop any activity immediately**
2. **Lie on left side** (increases blood flow to placenta)
3. **Drink water**
4. **Count movements for 30 minutes**
5. If no improvement or fewer than 4 movements in 1 hour → go to hospital immediately

---

## 4. Preeclampsia — Ancillary Risk Flag Only

### Important Limitation

**Our wearable belt has NO blood pressure sensor.** Blood pressure measurement is the primary diagnostic criterion for preeclampsia. Therefore, our system can ONLY raise an **indirect risk flag** — it cannot diagnose preeclampsia.

### What We CAN Detect (Indirect Signs)

| Sensor | Finding | Significance |
|---|---|---|
| HR | Elevated variability changes | Autonomic nervous system changes in preeclampsia |
| Fetal movement | Reduced | Placental insufficiency common in preeclampsia |
| Temperature | Normal | Rules out infection as cause |
| SpO2 | May be mildly low | In severe preeclampsia with pulmonary edema |

### When the Flag is Raised

The system raises `PREECLAMPSIA_ANCILLARY_RISK` when:
- HR variability trend shows changes over multiple days
- Fetal movement has been declining
- Temperature is normal (ruling out infection)
- SpO2 is in normal range but trending downward

### What the Flag Means

This flag means: "Something is changing that is consistent with preeclampsia risk. **Please measure your blood pressure and see a doctor.** This is NOT a diagnosis."

### Risk Factors for Preeclampsia

- First pregnancy
- Age >35 years or <20 years
- Obesity (BMI >30)
- Pre-existing hypertension or kidney disease
- Multiple pregnancy (twins or more)
- Previous preeclampsia
- Family history

### Warning Symptoms (What Priya Should Report Immediately)

- Severe headache that does not go away
- Blurred vision or seeing "lights"
- Sudden swelling of face, hands, or feet
- Upper abdominal pain (right side)
- Vomiting with headache

---

## 5. Placental Insufficiency / IUGR Risk

### What is Placental Insufficiency?

The placenta is the baby's lifeline — it delivers oxygen and nutrition. When the placenta does not work well (insufficiency), the baby may grow slowly (IUGR — Intrauterine Growth Restriction).

### How Our System Detects It (Trend-Based)

Unlike other flags that are real-time, this is a **longitudinal trend detection**:
- Looking at fetal movement counts over the past 7–14 days
- A gradual, consistent decline = concern
- A single low day = NOT concerning (baby has sleep cycles, active and quiet periods)

### The Math

If fetal movement per day drops by >30% over 7+ days compared to the established baseline, the system raises a trend alert.

**Example (Priya's IUGR watch scenario):**
- Baseline: 45 movements/day (Week 28)
- Week 30: 38 movements/day (–15%)
- Week 31: 30 movements/day (–33%)
- Week 32: 22 movements/day (–51%) → IUGR_RISK_WATCH raised

### Why Not Real-Time Alerting?

A single quiet hour or day is normal — babies have sleep-wake cycles of 20–40 minutes. Daily total movement over 7+ days is what matters. Real-time alerting would cause unnecessary panic.

### What to Do

- Schedule a Doppler ultrasound to assess umbilical artery blood flow
- Schedule a growth scan (biometry) to measure baby's size
- These should happen within 48–72 hours of flag being raised, not as an emergency

---

## 6. Maternal Dehydration and Exhaustion

### Why Dehydration is Common in Indian Pregnancies

- Hot climate (especially summer, 35–45°C in South India)
- Cultural practices (fasting, restricted fluids)
- Nausea and vomiting making it hard to drink
- Heavy physical work (many pregnant women in India work until late in pregnancy)
- Lack of awareness

### How the Belt Detects Dehydration (By Elimination)

The system identifies dehydration/exhaustion using an **elimination logic**:
1. Heart rate is elevated (>100 bpm for Priya's context)
2. SpO2 is normal (rules out hypoxia)
3. Temperature is normal (rules out infection/fever)
4. Activity is very low (rules out exertion as the cause)
5. Fetal HR and movement are normal (rules out fetal distress)

When all infection and hypoxia causes are ruled out and HR remains elevated → likely dehydration or exhaustion.

### Signs and Management

**What Priya should do when this flag is raised:**
1. Drink at least 500 ml of water or ORS (Oral Rehydration Salt solution) immediately
2. Rest in a cool place, lying on left side
3. Avoid going outside in peak heat (11am–4pm)
4. Eat small, frequent meals if nauseated
5. Recheck HR after 30 minutes

**Daily hydration target in pregnancy:** At least 2.5–3 litres of fluid per day in Indian climate (more in summer).

**ORS Recipe (if packaged ORS unavailable):**
- 1 litre clean water
- 6 teaspoons of sugar
- 1/2 teaspoon of salt
- Stir and drink slowly

### When to Escalate

If HR does not come down after hydration and rest, or if Priya feels chest pain, severe dizziness, or cannot stand → seek medical attention.

---

## 7. Sensor Limitations and Safe Use

### What the Belt Can Do

- ✅ Continuous monitoring of maternal HR, SpO2, temperature, activity
- ✅ Extraction of fetal heart rate patterns from microphone (Doppler principle)
- ✅ Counting fetal movements via accelerometer
- ✅ Trend analysis over days and weeks
- ✅ Raise fusion flags based on combination of signals

### What the Belt Cannot Do

- ❌ Measure blood pressure (no BP sensor)
- ❌ Diagnose any condition (it is a monitoring and alerting tool)
- ❌ Replace antenatal care visits (ANC)
- ❌ Guarantee detection of all complications
- ❌ Work reliably in very noisy environments (for fetal HR extraction via mic)

### Data Accuracy Notes

| Sensor | Accuracy | Notes |
|---|---|---|
| SpO2 (pulse-ox) | ±2% | Affected by nail polish, movement artifact |
| HR | ±5 bpm | Movement artifact during exercise |
| Temperature | ±0.2°C | Must be worn correctly on skin |
| FHR (mic) | ±10 bpm | Best accuracy when still, adequate gel/contact |
| Movement (accel) | Qualitative | Counts proxy movements, not perfectly precise |

### Important Disclaimer

This system is a **monitoring and alert tool** for use alongside regular medical care. All flags must be evaluated by a qualified healthcare provider. Do not make medical decisions based solely on sensor readings. When in doubt, always seek medical attention.
