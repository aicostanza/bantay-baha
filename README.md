# Bantay Baha — Python edition

A Python **Flask + SQLite** flood-monitoring application with the existing dark dashboard, live chart, analytics, simulated sensor and bilingual advisories. The browser interface uses React/TypeScript and CSS; the backend, database logic and standalone simulator are Python. The built browser assets are committed, so **Node.js is not required to run the app**.

## Run locally
Install Python 3.10 or later, then:

```sh
python -m venv .venv
```

Windows PowerShell: `.venv\Scripts\Activate.ps1`

macOS/Linux: `source .venv/bin/activate`

```sh
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. In another terminal:

```sh
python simulator.py http://127.0.0.1:5000
```

Alternatively, click **Start simulator** on the dashboard. Use one simulator at a time. The browser simulator runs only while the page is open; the Python script continues while its terminal process runs. Stop it with Ctrl+C. Use `--level 170` to start the Python simulator in the Danger range.

SQLite is created automatically at `instance/readings.sqlite3`. Set `DATABASE_PATH` to change its location. Database files are not committed.

## API and analytics
- `POST /api/readings`: JSON `sensorId`, `waterLevelCm`, optional timezone-aware ISO `timestamp`. Returns 201; invalid input returns 400.
- `GET /api/readings`: newest 50 readings ordered by timestamp and ID.
- `GET /api/summary`: average, minimum, maximum, status counts and trend across all stored readings.
- `POST /api/advisory`: English and Filipino advisory with its source and timestamp.
- `GET /health`: health check.

Normal: below 100 cm. Alert: 100 to below 150 cm. Danger: 150 cm or above. Trend compares the newest five readings with the preceding five; a difference under 1 cm is steady. Fewer than ten readings reports insufficient data. The table shows ten readings; chart and CSV use up to 50.

## Gemini setup
Set `GEMINI_API_KEY` in the server environment before starting the app. Optionally set `GEMINI_MODEL` (default `gemini-2.5-flash`). Never put keys in browser code or Git. No key, an unavailable provider or malformed output produces a clearly labeled rule-based fallback. Real Gemini output requires your key and has not been verified with a live key.

### Exact prompt
Using ONLY this JSON summary, write a public flood advisory in English and Filipino, at most 3 sentences per language. Never invent weather, forecasts, locations, evacuation orders, or numbers. All readings are simulated educational data, not a real emergency feed. Thresholds: Normal below 100 cm, Alert 100 to below 150 cm, Danger 150 cm or above. Give proportionate precautions, refer to official barangay guidance, and do not declare safety. Return JSON with english and filipino strings. Summary: [the server appends actual summary JSON]

## Deployment
This commit publishes the Python source to GitHub; it does not replace the existing ChatGPT Sites deployment. Deploy this version to a Python-capable host such as Render using the included `render.yaml`, or configure:

- Build: `pip install -r requirements.txt`
- Start: `waitress-serve --host=0.0.0.0 --port=$PORT --call app:create_app`
- Health check: `/health`
- Secret environment variable: `GEMINI_API_KEY`

For durable hosted readings, attach persistent storage and set `DATABASE_PATH` to a file on that disk. Ephemeral hosting filesystems lose SQLite data on redeploy/restart. Run `python simulator.py https://YOUR-DEPLOYED-URL` to feed the live app. GitHub Pages cannot run the Python backend.

## Edit the dashboard (optional)
`frontend/Dashboard.tsx` preserves the original dashboard. CSS is in `static/style.css`. After changing frontend code, install Node.js and run `npm install` then `npm run build`; commit the updated `static/app.js` with its bundled license notices. Python-only changes do not require this step.

## Tests
Run `python -m unittest discover -s tests -v`. Tests cover validation, persistence, ordering and the 50-row cap, threshold boundaries, trend, and AI fallback/provider response handling.

## Lab submission
`PLAN.md` contains stories and acceptance criteria. `REFLECTION.md` is a draft to personalize. Record a demonstration under two minutes: start the simulator, show live updates and analytics, generate an advisory and switch languages. Python hosting and a real Gemini-key verification remain to be completed.

## Limits
Educational simulated data only; never treat the dashboard as an official flood warning. Sensor authentication, rate limits, production-grade storage and human approval of public AI advisories are future work. All-history analytics are designed for a small lab dataset. The original TypeScript server version remains in Git history.
