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
        print(f"No flights found in API response. Full response: {json.dumps(api_response, indent=2)}")
        save_positions(data)
        return

    print(f"Found {len(flights_in_response)} flight(s) in response")
    
    for flight in flights_in_response:
        callsign = flight.get("callsign", "").strip()
        flight_number = flight.get("flight_number", "").strip()
        
        print(f"Flight: callsign={callsign}, flight_number={flight_number}")
        print(f"Position data: lat={flight.get('lat')}, lon={flight.get('lon')}, alt={flight.get('alt')}")
        
        if callsign in FLIGHTS:
            display_name = FLIGHT_DISPLAY[callsign]["name"]
            if flight.get("lat") and flight.get("lon"):
                position = extract_position(flight)
                data["flights"][display_name]["positions"].append(position)
                print(f"Added position for {display_name} ({callsign}): lat={position['lat']}, lon={position['lon']}, alt={position['alt']}")
            else:
                print(f"{display_name} ({callsign}) found but no position data")

    data["updated"] = datetime.now(timezone.utc).isoformat()
    save_positions(data)
    print(f"Updated positions.json at {data['updated']}")


if __name__ == "__main__":
    main()
