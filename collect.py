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
FLIGHTS = ["AA621", "AA917"]
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
    params = {"flights": ",".join(FLIGHTS)}
    
    print(f"Fetching from: {url} (sandbox={USE_SANDBOX})")

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
        "lat": flight_data.get("latitude"),
        "lon": flight_data.get("longitude"),
        "alt": flight_data.get("altitude"),
        "speed": flight_data.get("ground_speed"),
        "heading": flight_data.get("heading"),
    }


def main():
    data = load_positions()
    api_response = fetch_live_positions()

    flights_in_response = api_response.get("data", [])
    
    if not flights_in_response:
        print("No flights found in API response")
        save_positions(data)
        return

    for flight in flights_in_response:
        callsign = flight.get("callsign", "").strip()
        flight_number = flight.get("flight_number")
        
        if flight_number in FLIGHTS:
            if flight.get("latitude") and flight.get("longitude"):
                position = extract_position(flight)
                data["flights"][flight_number]["positions"].append(position)
                print(f"Added position for {flight_number}: lat={position['lat']}, lon={position['lon']}, alt={position['alt']}")
            else:
                print(f"{flight_number} found but no position data (not airborne yet)")

    data["updated"] = datetime.now(timezone.utc).isoformat()
    save_positions(data)
    print(f"Updated positions.json at {data['updated']}")


if __name__ == "__main__":
    main()
