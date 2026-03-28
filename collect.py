#!/usr/bin/env python3
"""
Fetch full flight tracks from FlightRadar24 API using pyfr24.
Reads itinerary.json to determine which flights are active today,
pulls complete track history for each, and writes to positions.json.
"""
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pyfr24 import FR24API


API_KEY = os.getenv("FLIGHTRADAR_API_KEY")
DATA_FILE = "data/positions.json"
ITINERARY_FILE = "data/itinerary.json"
SAMPLE_INTERVAL = 30


def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


def save_positions(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_active_legs(itinerary):
    """Return itinerary legs that are active today (flight date is today or yesterday for red-eyes)."""
    now = datetime.now(timezone.utc)
    today = now.date()
    yesterday = today - timedelta(days=1)

    active = []
    for leg in itinerary.get("legs", []):
        if not leg.get("callsign"):
            continue
        flight_date = datetime.fromisoformat(leg["date"]).date()
        if flight_date in (today, yesterday):
            active.append(leg)
    return active


def get_live_fr24_ids(api, callsigns):
    """Query live feed for tracked callsigns, return {callsign: fr24_id}."""
    if not callsigns:
        return {}
    url = "https://fr24api.flightradar24.com/api/live/flight-positions/full"
    params = {"callsigns": ",".join(callsigns)}
    response = api._make_request("get", url, headers=api.session.headers, params=params)
    result = response.json()

    ids = {}
    for flight in result.get("data", []):
        cs = flight.get("callsign", "").strip()
        fid = flight.get("fr24_id")
        if cs and fid:
            ids[cs] = fid
    return ids


def fetch_full_track(api, fr24_id):
    """Pull the full ADS-B track for a flight and sample it down."""
    tracks_response = api.get_flight_tracks(fr24_id)
    if not tracks_response or not tracks_response[0].get("tracks"):
        return []

    raw = tracks_response[0]["tracks"]
    sampled = []
    last_ts = None

    for t in raw:
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

    itinerary = load_json(ITINERARY_FILE)
    if not itinerary:
        print("ERROR: itinerary.json not found", file=sys.stderr)
        sys.exit(1)

    positions = load_json(DATA_FILE) or {"flights": {}, "updated": None}
    api = FR24API(API_KEY)
    active_legs = get_active_legs(itinerary)

    if not active_legs:
        print("No flights scheduled for today")
        positions["updated"] = datetime.now(timezone.utc).isoformat()
        save_positions(positions)
        return

    callsigns = [leg["callsign"] for leg in active_legs]
    live_ids = get_live_fr24_ids(api, callsigns)
    print(f"Active legs: {[l['id'] for l in active_legs]}, live: {list(live_ids.keys())}")

    for leg in active_legs:
        leg_id = leg["id"]
        callsign = leg["callsign"]
        flight = positions["flights"].setdefault(leg_id, {
            "route": leg["route"],
            "positions": [],
            "status": "scheduled",
        })
        flight["route"] = leg["route"]

        live_id = live_ids.get(callsign)
        if live_id:
            flight["fr24_id"] = live_id

        fr24_id = flight.get("fr24_id")
        if not fr24_id:
            if not flight.get("positions"):
                flight["status"] = "scheduled"
            print(f"{leg_id}: not yet on live feed")
            continue

        track = fetch_full_track(api, fr24_id)
        if track:
            flight["positions"] = track
            print(f"{leg_id}: {len(track)} points, latest lat={track[-1]['lat']:.4f}")
        else:
            print(f"{leg_id}: no track data for fr24_id={fr24_id}")

        if live_id:
            flight["status"] = "en_route"
        elif flight.get("positions"):
            flight["status"] = "landed"

    positions["updated"] = datetime.now(timezone.utc).isoformat()
    save_positions(positions)
    print(f"Updated at {positions['updated']}")


if __name__ == "__main__":
    main()
