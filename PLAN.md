# Bantay Baha sprint plan

## User stories and acceptance criteria
1. As a resident, I want to see the current water level so that I can monitor changes near the creek.
   - The current level displays in centimeters with Normal below 100, Alert from 100 to below 150, and Danger from 150.
   - Readings refresh every five seconds without a full reload.
   - The page fits a 375px screen.
2. As a barangay official, I want analytics and bilingual advisory drafts so that I can explain the readings to residents.
   - The API returns average, minimum, maximum and status counts for all readings.
   - Trend compares the newest five readings with the previous five; fewer than ten readings displays insufficient data.
   - Advisory generation produces English and Filipino text; missing or failed AI uses a labeled rule-based fallback.
3. As a developer, I want a gradual sensor simulator so that I can demonstrate the system without hardware.
   - A separate script posts a reading every five seconds, with steps of at most three centimeters.
   - Invalid levels and missing sensor identifiers return HTTP 400; valid readings return 201.
   - The latest-readings endpoint returns at most 50 rows, newest first.

## Sprint backlog
- Done: plan and acceptance criteria
- Done: API and persistent database
- Done: simulator script and dashboard controls
- Done: responsive UI, chart, ten-row table, five-second refresh
- Done: analytics and threshold logic
- Done: server-side AI integration and rule-based fallback
- Done: README and reflection draft
- Doing: cloud deployment and verification
- To Do: supply Gemini key and verify a real AI response
- To Do: public GitHub repository and public submission URL
- To Do: record a demonstration of two minutes or less

## SDLC
This lab follows an Agile iterative model because a single short sprint delivers a working prototype that is tested and refined against acceptance criteria.
