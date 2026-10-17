"""Bantay Baha: Python/Flask API and SQLite-backed flood monitoring."""
import json
import math
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote

from flask import Flask, jsonify, request

PROMPT = ('Using ONLY this JSON summary, write a public flood advisory in English and Filipino, '
          'at most 3 sentences per language. Never invent weather, forecasts, locations, evacuation '
          'orders, or numbers. All readings are simulated educational data, not a real emergency '
          'feed. Thresholds: Normal below 100 cm, Alert 100 to below 150 cm, Danger 150 cm or above. '
          'Give proportionate precautions, refer to official barangay guidance, and do not declare '
          'safety. Return JSON with english and filipino strings. Summary: ')


def now():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def status(level):
    return 'Normal' if level < 100 else 'Alert' if level < 150 else 'Danger'


def summarize(rows):
    rows = sorted(rows, key=lambda r: (r['timestamp'], r.get('id', 0)))
    values = [r['waterLevelCm'] for r in rows]
    delta = (sum(values[-5:]) - sum(values[-10:-5])) / 5 if len(values) >= 10 else None
    return dict(count=len(values), average=sum(values)/len(values) if values else None,
                minimum=min(values) if values else None, maximum=max(values) if values else None,
                normal=sum(v < 100 for v in values), alert=sum(100 <= v < 150 for v in values),
                danger=sum(v >= 150 for v in values), delta=delta,
                trend='insufficient data' if delta is None else 'steady' if abs(delta) < 1 else 'rising' if delta > 0 else 'falling',
                current=rows[-1] if rows else None)


def fallback(summary):
    if not summary['current']:
        return dict(english='No readings available. Check official barangay updates.',
                    filipino='Wala pang datos. Tingnan ang opisyal na abiso ng barangay.')
    level = summary['current']['waterLevelCm']
    state = status(level)
    en = {'Normal': 'Continue monitoring and follow official barangay updates.',
          'Alert': 'Prepare essential supplies and monitor official barangay updates.',
          'Danger': 'Avoid floodwater and prepare to move to a safer area following official instructions.'}
    fil = {'Normal': 'Patuloy na magmonitor at sundin ang opisyal na abiso ng barangay.',
           'Alert': 'Ihanda ang mahahalagang gamit at subaybayan ang opisyal na abiso ng barangay.',
           'Danger': 'Iwasan ang baha at maghandang pumunta sa mas ligtas na lugar ayon sa opisyal na tagubilin.'}
    return dict(english=f'Simulated water level is {level:.1f} cm ({state}). {en[state]} This is a training advisory, not an official warning.',
                filipino=f'Ang simuladong antas ng tubig ay {level:.1f} cm ({state}). {fil[state]} Para sa pagsasanay lamang ang abisong ito.')


def create_app(database_path=None):
    app = Flask(__name__, static_folder='static')
    app.config['MAX_CONTENT_LENGTH'] = 16384
    database_path = database_path or os.environ.get('DATABASE_PATH', 'instance/readings.sqlite3')
    Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    def connect():
        db = sqlite3.connect(database_path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    db = connect()
    db.execute('CREATE TABLE IF NOT EXISTS readings (id INTEGER PRIMARY KEY AUTOINCREMENT, sensorId TEXT NOT NULL, waterLevelCm REAL NOT NULL, timestamp TEXT NOT NULL)')
    db.execute('CREATE INDEX IF NOT EXISTS readings_time ON readings(timestamp DESC, id DESC)')
    db.commit()
    db.close()

    def read_rows(limit=None):
        db = connect()
        try:
            sql = 'SELECT * FROM readings ORDER BY timestamp DESC, id DESC'
            return [dict(r) for r in db.execute(sql + (' LIMIT ?' if limit else ''), (limit,) if limit else ())]
        finally:
            db.close()

    @app.get('/')
    def index():
        return app.send_static_file('index.html')

    @app.get('/health')
    def health():
        return jsonify(status='ok')

    @app.get('/api/readings')
    def get_readings():
        return jsonify(read_rows(50))

    @app.post('/api/readings')
    def post_reading():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error='Expected a JSON object'), 400
        sensor = data.get('sensorId')
        level = data.get('waterLevelCm')
        if not isinstance(sensor, str) or not sensor.strip() or len(sensor) > 64:
            return jsonify(error='sensorId is required (1–64 characters)'), 400
        if isinstance(level, bool) or not isinstance(level, (int, float)) or not math.isfinite(level) or not 0 <= level <= 500:
            return jsonify(error='waterLevelCm must be a number from 0 to 500'), 400
        timestamp = now()
        if 'timestamp' in data:
            try:
                parsed = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                if parsed.tzinfo is None:
                    raise ValueError('Timezone required')
                timestamp = parsed.astimezone(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            except (ValueError, TypeError, AttributeError):
                return jsonify(error='timestamp must be an ISO date with timezone'), 400
        record = dict(sensorId=sensor.strip(), waterLevelCm=level, timestamp=timestamp)
        db = connect()
        try:
            db.execute('INSERT INTO readings(sensorId, waterLevelCm, timestamp) VALUES (?, ?, ?)', tuple(record.values()))
            db.commit()
        finally:
            db.close()
        return jsonify(record), 201

    @app.get('/api/summary')
    def summary():
        return jsonify(summarize(read_rows()))

    @app.post('/api/advisory')
    def advisory():
        summary = summarize(read_rows())
        result = fallback(summary)
        source = 'Rule-based fallback'
        key = os.environ.get('GEMINI_API_KEY')
        if key and summary['current']:
            try:
                model = quote(os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash'), safe='')
                body = dict(contents=[dict(parts=[dict(text=PROMPT + json.dumps(summary))])],
                            generationConfig=dict(responseMimeType='application/json'))
                req = Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',
                              data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': key}, method='POST')
                with urlopen(req, timeout=15) as response:
                    data = json.load(response)
                generated = json.loads(data['candidates'][0]['content']['parts'][0]['text'])
                if not all(isinstance(generated.get(k), str) and generated[k].strip() for k in ('english', 'filipino')):
                    raise ValueError('Invalid advisory')
                result = {k: generated[k] for k in ('english', 'filipino')}
                source = 'Gemini AI · unreviewed draft'
            except Exception:
                app.logger.warning('AI advisory unavailable; using rule-based fallback')
        return jsonify(**result, source=source, timestamp=now())

    return app


if __name__ == '__main__':
    create_app().run(host='127.0.0.1', port=int(os.environ.get('PORT', 5000)), debug=False)
