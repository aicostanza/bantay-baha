# Security, ethics and emerging technology

Draft responses for review and personalization before submission.

## 1. Security risks
The readings API does not authenticate individual sensors, so a user with access could submit fabricated levels. A production version should verify a per-device credential or signed payload, enforce rate limits and detect replayed timestamps. The advisory endpoint could also be called repeatedly to exhaust the AI budget; role checks, per-user limits and cached advisories would reduce this risk.

## 2. Accountability and safeguards
The developer and deploying barangay share responsibility for validating the system and deciding how an advisory reaches residents; an AI provider does not replace local accountability. This prototype labels all readings as simulated, distinguishes fallback guidance from AI drafts, and avoids claiming to be an official warning service. A production release should require an authorized official to review advisories and cross-check calibrated sensors before public distribution.

## 3. AR extension
Augmented reality could overlay measured flood-depth markers on a camera view to help trained barangay personnel understand levels at known reference points. It would need reliable positioning and surveyed reference heights because a misplaced overlay could mislead users. The extra development, calibration and device requirements may cost more than a clear conventional map and dashboard.

## 4. Two hundred sensors
At a five-second interval, 200 sensors would produce 40 readings per second, or about 3.46 million readings per day. Queries would need per-sensor and time-window indexes, retention policies and precomputed aggregates instead of reading the entire database for every summary. Stream processing could identify rising levels across neighboring areas while accounting for calibration, delayed messages and missing data. Access controls and monitoring would also need to distinguish individual devices and flag unreliable readings.
