#!/usr/bin/env python3
"""
Fetch live flight positions from FlightRadar24 API and append to positions.json
"""
import json
import os
import sys
from datetime import datetime, timezone
import requests


API_KEY = os.getenv("FLIGHTRADAR_API_KEY")
USE_SANDBOX = os.getenv("USE_SANDBOX", "false").lower() == "true"
BASE_URL = "https://fr24api.flightradar24.com/api"
FLIGHTS = ["AAL0621", "AAL0917"]
FLIGHT_DISPLAY = {
    "AAL0621": {"name": "AA621", "route": "LAX-MIA"},
    "AAL0917": {"name": "AA917", "route": "MIA-LIM"}
}
DATA_FILE = "data/positions.json"


def load_positions():
    """Load existing positions from JSON file"""
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
    """Save positions to JSON file"""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def fetch_live_positions():
    """Fetch live positions for tracked flights from FR24 API"""
    if not API_KEY:
        print("ERROR: FLIGHTRADAR_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    endpoint = "/sandbox/live/flight-positions/full" if USE_SANDBOX else "/live/flight-positions/full"
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept-Version": "v1",
    }
    params = {"callsigns": ",".join(FLIGHTS)}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"ERROR fetching FR24 API: {e}", file=sys.stderr)
        sys.exit(1)


def extract_position(flight_data):
    """Extract position data from FR24 API response"""
    return {
        "ts": int(datetime.now(timezone.utc).timestamp()),
        "lat": flight_data.get("lat"),
        "lon": flight_data.get("lon"),
        "alt": flight_data.get("alt"),
        "speed": flight_data.get("gspeed"),
        "heading": flight_data.get("track"),
    }


def main():
    data = load_positions()
    api_response = fetch_live_positions()

    print(f"API response keys: {list(api_response.keys())}")
    
    flights_in_response = api_response.get("data", [])
    
    if not flights_in_response:
        print("No flights found in API response")
        save_positions(data)
        return
    
    for flight in flights_in_response:
        callsign = flight.get("callsign", "").strip()
        
        if callsign in FLIGHTS:
            display_name = FLIGHT_DISPLAY[callsign]["name"]
            if flight.get("lat") and flight.get("lon"):
                position = extract_position(flight)
                data["flights"][display_name]["positions"].append(position)
                print(f"Added position for {display_name}: lat={position['lat']:.5f}, lon={position['lon']:.5f}, alt={position['alt']} ft")
            else:
                print(f"{display_name} found but no position data (not airborne yet)")

    data["updated"] = datetime.now(timezone.utc).isoformat()
    save_positions(data)
    print(f"Updated positions.json at {data['updated']}")


if __name__ == "__main__":
    main()
