#!/usr/bin/env python3
"""Import a CSV flight track and merge it into positions.json"""
import csv
import json
import sys

if len(sys.argv) < 3:
    print("Usage: python3 import_csv_flight.py <csv_path> <leg_id>")
    sys.exit(1)

csv_path = sys.argv[1]
leg_id = sys.argv[2]

with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    positions = []
    last_ts = None
    for row in reader:
        ts = int(row['Timestamp'])
        if last_ts and ts - last_ts < 30:
            continue
        lat, lon = row['Position'].split(',')
        positions.append({
            'ts': ts,
            'lat': float(lat),
            'lon': float(lon),
            'alt': int(row['Altitude']),
            'speed': int(row['Speed']),
            'heading': int(row['Direction'])
        })
        last_ts = ts

with open('data/positions.json', 'r') as f:
    data = json.load(f)

if leg_id not in data['flights']:
    print(f"Creating new entry for {leg_id}")
    data['flights'][leg_id] = {
        'route': leg_id,
        'positions': [],
        'status': 'scheduled'
    }

data['flights'][leg_id]['positions'] = positions
data['flights'][leg_id]['status'] = 'landed'
data['flights'][leg_id]['approximated'] = True

with open('data/positions.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Imported {len(positions)} points for {leg_id}")
