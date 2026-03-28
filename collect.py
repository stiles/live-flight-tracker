#!/usr/bin/env python3
"""
Fetch full flight tracks from FlightRadar24 API using pyfr24 and write to positions.json.
Pulls the complete track history each run so gaps in cron scheduling don't matter.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pyfr24 import FR24API


API_KEY = os.getenv("FLIGHTRADAR_API_KEY")
CALLSIGNS = ["AAL0621", "AAL0917"]
CALLSIGN_MAP = {
    "AAL0621": {"name": "AA621", "route": "LAX-MIA"},
    "AAL0917": {"name": "AA917", "route": "MIA-LIM"},
}
DATA_FILE = "data/positions.json"
SAMPLE_INTERVAL = 30  # seconds between sampled points


def load_positions():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "flights": {
            "AA621": {"route": "LAX-MIA", "positions": []},
            "AA917": {"route": "MIA-LIM", "positions": []},
        },
        "updated": None,
    }


def save_positions(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_live_fr24_ids(api):
    """Get FR24 flight IDs for any currently airborne tracked flights."""
    url = "https://fr24api.flightradar24.com/api/live/flight-positions/full"
    params = {"callsigns": ",".join(CALLSIGNS)}
    response = api._make_request("get", url, headers=api.session.headers, params=params)
    result = response.json()

    ids = {}
    for flight in result.get("data", []):
        callsign = flight.get("callsign", "").strip()
        fr24_id = flight.get("fr24_id")
        if callsign in CALLSIGNS and fr24_id:
            display_name = CALLSIGN_MAP[callsign]["name"]
            ids[display_name] = fr24_id
    return ids


def fetch_full_track(api, fr24_id):
    """Pull the full ADS-B track for a flight and sample it down."""
    tracks_response = api.get_flight_tracks(fr24_id)
    if not tracks_response or not tracks_response[0].get("tracks"):
        return []

    raw_tracks = tracks_response[0]["tracks"]
    sampled = []
    last_ts = None

    for t in raw_tracks:
        ts = datetime.fromisoformat(t["timestamp"].replace("Z", "+00:00"))
        if last_ts is None or (ts - last_ts).total_seconds() >= SAMPLE_INTERVAL:
            sampled.append({
                "ts": int(ts.timestamp()),
                "lat": t["lat"],
                "lon": t["lon"],
                "alt": t["alt"],
                "speed": t["gspeed"],
                "heading": t["track"],
            })
            last_ts = ts

    return sampled


def main():
    if not API_KEY:
        print("ERROR: FLIGHTRADAR_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    api = FR24API(API_KEY)
    data = load_positions()

    live_ids = get_live_fr24_ids(api)

    if not live_ids:
        print("No tracked flights currently airborne")
        data["updated"] = datetime.now(timezone.utc).isoformat()
        save_positions(data)
        return

    for display_name, fr24_id in live_ids.items():
        print(f"Fetching full track for {display_name} (fr24_id={fr24_id})")
        positions = fetch_full_track(api, fr24_id)
        if positions:
            data["flights"][display_name]["positions"] = positions
            print(f"  {len(positions)} positions, latest: lat={positions[-1]['lat']:.5f}, lon={positions[-1]['lon']:.5f}")
        else:
            print(f"  No track data available")

    data["updated"] = datetime.now(timezone.utc).isoformat()
    save_positions(data)
    print(f"Updated positions.json at {data['updated']}")


if __name__ == "__main__":
    main()
