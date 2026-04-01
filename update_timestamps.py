#!/usr/bin/env python3
"""Update timestamps in imported flight data to match actual flight date"""
import json
from datetime import datetime, timezone

with open('data/positions.json', 'r') as f:
    data = json.load(f)

with open('data/itinerary.json', 'r') as f:
    itinerary = json.load(f)

lim_cuz_leg = next(l for l in itinerary['legs'] if l['id'] == 'H85721-LIM-CUZ')
actual_depart = datetime.fromisoformat(lim_cuz_leg['depart'].replace('Z', '+00:00'))
actual_depart_ts = int(actual_depart.timestamp())

csv_first_ts = 1773658539
time_offset = actual_depart_ts - csv_first_ts

print(f'CSV flight was: {datetime.fromtimestamp(csv_first_ts, tz=timezone.utc)}')
print(f'Actual flight was: {actual_depart}')
print(f'Time offset: {time_offset} seconds ({time_offset // 86400} days)')

if 'H85721-LIM-CUZ' in data['flights']:
    flight = data['flights']['H85721-LIM-CUZ']
    for pos in flight['positions']:
        pos['ts'] += time_offset
    print(f'Updated {len(flight["positions"])} positions')

with open('data/positions.json', 'w') as f:
    json.dump(data, f, indent=2)

print('Done')
