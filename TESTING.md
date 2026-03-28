# Instructions for testing

## Test with sandbox (before going live)

The sandbox returns static test data and doesn't use credits.

```bash
export FLIGHTRADAR_API_KEY="your_sandbox_key_here"
export USE_SANDBOX=true
python collect.py
```

Or use the test script:

```bash
./test_sandbox.sh
```

Then open `index.html` in a browser to verify the map displays correctly.

## Test with production API

```bash
export FLIGHTRADAR_API_KEY="your_production_key_here"
python collect.py
```

## Troubleshooting

### No flights found

The flights may not be airborne yet. The script will add positions only when the aircraft is actively transmitting position data.

### API errors

- Check that your API key is valid
- Verify you have sufficient credits (check fr24api.flightradar24.com)
- For sandbox testing, make sure `USE_SANDBOX=true` is set

### Map not loading

- Verify you replaced `PERSONAL_MAPBOX_ACCESS_TOKEN` in `index.html` with your actual token
- Check browser console for errors
- Make sure `data/positions.json` exists and is valid JSON
