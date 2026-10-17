"""A real IoT setup replaces this with a microcontroller and ultrasonic sensor over Wi-Fi/MQTT."""
import argparse
import json
import random
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description='Send gradual simulated readings every five seconds')
    parser.add_argument('url', nargs='?', default='http://127.0.0.1:5000')
    parser.add_argument('--level', type=float, default=84.5)
    args = parser.parse_args()
    level = max(0, min(500, args.level))
    try:
        while True:
            started = time.monotonic()
            level = max(0, min(500, level + random.uniform(-3, 3)))
            reading = dict(sensorId='CREEK-01', waterLevelCm=round(level, 1), timestamp=datetime.now(timezone.utc).isoformat())
            req = Request(args.url.rstrip('/') + '/api/readings', data=json.dumps(reading).encode(), headers={'Content-Type':'application/json'}, method='POST')
            try:
                with urlopen(req, timeout=4) as response:
                    print(response.status, reading, flush=True)
            except Exception as exc:
                print('Reading failed:', exc, flush=True)
            time.sleep(max(0, 5 - (time.monotonic() - started)))
    except KeyboardInterrupt:
        print('\nSimulator stopped.')


if __name__ == '__main__':
    main()
