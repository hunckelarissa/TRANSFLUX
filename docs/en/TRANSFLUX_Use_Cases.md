> **Language:** English · [Русский](../ru/TRANSFLUX_Use_Cases.md)

# TRANSFLUX: Use cases

> Four worked examples showing
> how the three TRANSFLUX axes work together on concrete problems.

The scenarios below are problem statements. As of October 2026 the library already has, from them: an honest `NoisyFloat` and `gradient_of_truth`, the `FluxVar` channel, panic and fallback, a backup sensor (`degraded`), a mean with weight `1/σ²`, the distinction between a lone jump and a shared one (`classify_jump`), several masks, and erasure of a hash inside one book. The library does not do these by itself: a branch on `scope`, erasure of a hash outside the book, an automatic drop of confidence on a lone jump, a link-loss timer. The synthetic check is `tests/synthetic/`.

---

## 1. Patient monitoring in intensive care

### The pain of the classical approach

The system reads temperature, pulse, and pressure. Each reading is compared with a threshold: temperature > 38.0°C → alarm. Simple. But:

- **Noise is ignored.** The sensor returns 38.1°C with a real error of ±2°C. A classical system fires on a value that cannot be trusted.
- **History is not taken into account.** 38.1°C after a stable 36.6 is one thing. 38.1°C after a smooth rise from 37.0 over four hours is another. A classical system does not tell them apart.
- **False alarms.** Up to 90% of alarms in intensive care are false. The consequence is alarm fatigue: staff start ignoring signals, including the real ones.

### How TRANSFLUX answers

**Value Model (NoisyFloat).**
Each sensor reading is not a number but a distribution: `NoisyFloat(38.1, uncertainty=2.0, confidence=0.4)`. The system knows that trust in this value is 40%. The gradient of truth for the condition "fever" is about 0.35. That is not enough for a full alarm. The decision: request a repeat measurement, or switch to a backup sensor, rather than raise a false alarm.

**State Model (FluxVar).**
The patient's temperature is a `FluxVar` with history. Velocity = 0.32°C/hour is a normal fluctuation (below `trauma_threshold`). But if velocity jumps to 2°C/hour, that is an anomaly the system records independently of the absolute value. The trend matters more than the point.

**Survival Model (SurvivalState).**
If the confidence of three readings in a row falls below 0.3, `threat_level` grows. When it crosses the threshold, the system enters "degraded mode": it switches to the backup sensor, notifies a technician, and marks all current data as unreliable. This is not a failure. It is a managed degradation.

### The result

| Metric | Classical | TRANSFLUX |
|---|---|---|
| False alarms | ~90% | They fall: the alarm is proportional to confidence |
| Detecting trends | None | Velocity / acceleration reveal the dynamics |
| Reaction to a sensor fault | No data → silence or a crash | Managed degradation through SurvivalState |

---

## 2. An autonomous drone in a zone with unstable links

### The pain of the classical approach

The drone flies a GPS route. The controller follows waypoints. If the link is lost, it hovers or returns to base. But:

- **GPS lies silently.** In an urban canyon, accuracy falls from ±1 m to ±15 m. The controller does not know the coordinates are unreliable — and it maneuvers on false data.
- **Gusts of wind.** A sharp gust → the position "jumps" → the controller answers with a sharp correction → oscillation. A classical filter (Kalman) softens this, but it does not recognize a "trauma".
- **Mission data.** If the drone is captured, the route points, the base coordinates, and the link keys are all available.

### How TRANSFLUX answers

**Value Model (NoisyFloat).**
A GPS coordinate = `NoisyFloat(lat, uncertainty=σ_gps, confidence=f(satellite_count))`. In an urban canyon: 3 satellites → confidence = 0.3, uncertainty = 15 m. The drone automatically widens its safety margins (altitude, distance to obstacles) in proportion to uncertainty — without changing the controller's code.

**State Model (FluxVar).**
Position is a `FluxVar` with velocity and acceleration. A gust → a jump in velocity → `trauma_threshold` is crossed → for N seconds the controller switches to inertial navigation and ignores GPS readings until things settle. This is anomaly filtering through the physics of state.

**Survival Model (SurvivalState).**
Loss of the link to base: every 5 seconds without a ping → `threat_delta += 0.1`. After 10 seconds, threat ≥ threshold → panic: destruction of the route points, rotation of the link keys, transition to an autonomous safe mode. A physical impact (the accelerometer shows > 50 g) → `scope="system"` → a full wipe of the data.

### The result

| Metric | Classical | TRANSFLUX |
|---|---|---|
| Navigation with bad GPS | False maneuvers | Margins widen ∝ uncertainty |
| Reaction to a gust | Oscillation / Kalman | Trauma → inertial fallback |
| Data on capture | Available | Destroyed through panic |

---

## 3. A protected messenger for journalists

### The pain of the classical approach

End-to-end encryption (the Signal protocol) protects message content in transit. But:

- **Metadata is open.** Who talks to whom, when, and how often is visible to the operator and to security services. Encrypting content does not protect identity.
- **Seizure of the device.** Under coercion a password can be opened. The local database is evidence. Even with full-disk encryption there is a window of vulnerability while the device is unlocked.
- **There is no emergency protocol.** The user must manually delete chats, sign out of accounts, and change a number. There is no time for that in a threat.

### How TRANSFLUX answers

**Survival Model (SurvivalState).**
Three panic triggers:

- *A panic button* — one press;
- *A dead man's switch* — no status confirmation for N minutes;
- *A duress code* — a special password that looks ordinary but activates panic.

On panic (`scope="system"`):

- rotation of every identifier on every linked device;
- destruction of the local message database;
- a change of the device fingerprint;
- a transition into a "clean" mode with an empty interface.

**Polyphonic identity (derived from Survival).**
A journalist has three layers of identity:

- a public persona (visible to everyone);
- a journalistic handle (visible to the newsroom);
- an alias for working with a source (visible only to the source).

Each layer is a separate `identity_hash`. Proof of membership in the group "accredited journalists" — without revealing which journalist.

**Value Model (NoisyFloat).**
Message delivery status: `NoisyFloat(delivered=1.0, uncertainty=0.2, confidence=0.7)`. Instead of a deceptive "delivered" checkmark — an honest status: "probably delivered, confirmation is not guaranteed". The user decides on the basis of real knowledge, not an illusion.

### The result

| Metric | Classical (Signal) | TRANSFLUX |
|---|---|---|
| Emergency protection | Manual | One trigger → a full rotation |
| Identity protection | Phone number = identifier | Polyphonic: layers without outing |
| Honesty of statuses | "Delivered" (binary) | Delivered, with confidence |

---

## 4. A network of environmental air-quality sensors

### The pain of the classical approach

Two hundred PM2.5 sensors across a city. Each sends a reading once a minute. A central server averages them and publishes an air-quality index. But:

- **Every sensor is treated as equal.** A newly calibrated sensor and a five-year-old one with a dying battery have the same weight in the mean. A mean PM2.5 of 47 µg/m³ can be a meaningless number.
- **A spike is panic.** One sensor next to a factory shows PM2.5 = 300. A real emission? Or a sensor fault? A classical system does not know.
- **A blind spot.** If 30% of the sensors go offline (night, batteries, vandalism), the system still publishes "index 47" with the same confidence. The user does not know the picture is incomplete.

### How TRANSFLUX answers

**Value Model (NoisyFloat).**
Each sensor returns `NoisyFloat(pm25, uncertainty=f(age, calibration, battery), confidence=f(self_test))`.

Aggregation is not a plain mean. It is a weighted combination:

- each sensor's weight ∝ 1/uncertainty²;
- well-calibrated sensors dominate automatically;
- the final result carries its own uncertainty and confidence.

**State Model (FluxVar).**
Each sensor's readings are a `FluxVar` with velocity. A PM2.5 spike of 300 → velocity crosses `trauma_threshold`. The system compares with neighbors:

- neighboring FluxVars also show a rise in velocity → a real emission is likely, escalate;
- only one sensor "jumped" → a fault is likely, lower its confidence.

This is spatial correlation through the physics of state, not through a separate anomaly-detection algorithm.

**Survival Model (SurvivalState).**
A SurvivalState for the whole network: the aggregated confidence of every sensor. If mean confidence falls below the threshold (too many sensors offline or unreliable), the system publishes an honest status:

```
Air quality index: 47
Trustworthiness: LOW
Coverage: 68% of sensors
```

This is not a failure. It is managed honesty.

### The result

| Metric | Classical | TRANSFLUX |
|---|---|---|
| Accounting for sensor quality | All equal | Weight ∝ 1/uncertainty² |
| Detecting anomalies | A separate algorithm | Velocity + spatial correlation |
| Honesty with incomplete data | "Index 47" (in silence) | "Index 47, confidence: LOW" |

---

## The shared pattern

All four scenarios repeat the same structure:

1. The **classical approach** pretends that data is exact, state is stable, and there is no threat.
2. **TRANSFLUX** makes uncertainty, the history of change, and threat **explicit and computable**.
3. **Emergent behavior** arises from the interaction of the axes: uncertainty produces threat, velocity produces threat, panic reloads state.

These are not three separate features. This is a closed system that is smarter than the sum of its parts.
