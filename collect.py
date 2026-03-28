#!/usr/bin/env python3
"""
Fetch live flight positions from FlightRadar24 API using pyfr24 and append to positions.json
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


def fetch_positions(api):
    url = "https://fr24api.flightradar24.com/api/live/flight-positions/full"
    params = {"callsigns": ",".join(CALLSIGNS)}
    response = api._make_request("get", url, headers=api.session.headers, params=params)
    return response.json()


def main():
    if not API_KEY:
        print("ERROR: FLIGHTRADAR_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    api = FR24API(API_KEY)
    data = load_positions()
    response = fetch_positions(api)

    flights_in_response = response.get("data", [])

    if not flights_in_response:
        print("No flights found in API response")
        data["updated"] = datetime.now(timezone.utc).isoformat()
        save_positions(data)
        return

    for flight in flights_in_response:
        callsign = flight.get("callsign", "").strip()

        if callsign in CALLSIGNS:
            display_name = CALLSIGN_MAP[callsign]["name"]
            lat = flight.get("lat")
            lon = flight.get("lon")

            if lat and lon:
                position = {
                    "ts": int(datetime.now(timezone.utc).timestamp()),
                    "lat": lat,
                    "lon": lon,
                    "alt": flight.get("alt"),
                    "speed": flight.get("gspeed"),
                    "heading": flight.get("track"),
                }
                data["flights"][display_name]["positions"].append(position)
                print(f"Added position for {display_name}: lat={lat:.5f}, lon={lon:.5f}, alt={flight.get('alt')} ft")
            else:
                print(f"{display_name} found but no position data (not airborne yet)")

    data["updated"] = datetime.now(timezone.utc).isoformat()
    save_positions(data)
    print(f"Updated positions.json at {data['updated']}")


if __name__ == "__main__":
    main()
