# Bantay Baha
A responsive flood-monitoring lab with a real REST API, D1 persistence, simulated IoT input, analytics and bilingual advisories. All water levels are educational simulation data, not official warnings.

## Stack and hosting
React/TypeScript frontend with Vinext route handlers on Cloudflare Workers and D1 SQLite. This hosting-compatible stack differs from the lab's suggested Express/Flask/PHP options; confirm instructor acceptance. Sites source is Git-backed. Hosting initially uses owner-private access, not a public submission URL.

## Run locally
Requirements: Node.js 22.13+ and npm.
1. `npm install`
2. `npm run db:generate` if the schema changed.
3. Run the local D1 migrations using the generated Wrangler configuration (see scripts and hosting setup).
4. `npm run dev`
5. Open the URL printed by the dev server.
6. `node simulator.mjs http://localhost:3000` (substitute the actual server port).
Use one simulator at a time. The dashboard's Start simulator button is an alternative and runs only while the page is open.

## API
- POST /api/readings: JSON sensorId, waterLevelCm, optional ISO timestamp; 201 success, 400 validation errors.
- GET /api/readings: latest 50 readings, newest first.
- GET /api/summary: average, minimum, maximum, total/status counts, current reading and trend from all stored readings.
- POST /api/advisory: English and Filipino advisory plus source and timestamp.
Normal: <100 cm; Alert: 100–<150 cm; Danger: >=150 cm. Trend compares averages of last five vs prior five readings in chronological order. Absolute difference below 1 cm means steady. Fewer than ten readings means insufficient data.
CSV exports up to the latest 50 returned readings. Table shows ten. The chart can show 20 or 50 readings, not a full hour (the lab's specified API cap is 50).

## AI configuration
Set GEMINI_API_KEY in server-side host environment variables. Optionally set GEMINI_MODEL (default gemini-2.5-flash). Never commit keys or include them in browser JavaScript. AI calls have a 15-second timeout; absent credentials, failed requests or invalid responses use labeled deterministic fallback text. AI output is an unreviewed draft, not an automatic official publication.

## Exact AI prompt
Using ONLY this JSON summary, write a public flood advisory in English and Filipino, at most 3 sentences per language. Never invent weather, forecasts, locations, evacuation orders, or numbers. All readings are simulated educational data, not a real emergency feed. Thresholds: Normal below 100 cm, Alert 100 to below 150 cm, Danger 150 cm or above. Give proportionate precautions, refer to official barangay guidance, and do not declare safety. Return JSON with english and filipino strings. Summary: [server appends the actual summary JSON]

## Demonstration (under two minutes)
Show the simulator terminal or start the browser simulator. Show changing readings and chart, wait for ten readings to display the trend, then generate an advisory and switch languages. Explain whether the returned text is Gemini or the fallback. Export a CSV. Use Simulator settings to demonstrate a different starting level.

## Remaining submission steps and limits
Supply a Gemini API key and test the real provider. Create the required public GitHub repository named bantay-baha, publish an accessible submission URL, and record the demonstration. A private Sites URL may require authentication and the standalone simulator may be unable to POST to it without an authenticated session; use the in-page simulator for that deployment. The dataset is shared across authorized visitors. No sensor authentication or AI rate limiter is implemented. All-history analytics are appropriate only for the small lab dataset. No real-world sensor or official emergency integration is connected.
