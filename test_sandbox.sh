#!/bin/bash
# Test the collection script with sandbox API

export USE_SANDBOX=true
export FLIGHTRADAR_API_KEY="${FLIGHTRADAR_SANDBOX_API_KEY}"

echo "Testing collection script with sandbox API..."
python collect.py

echo ""
echo "Positions collected:"
cat data/positions.json
