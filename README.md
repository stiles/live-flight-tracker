# Live Flight Tracker

Track and mapping flights in real-time using the Flightradar24 API and Mapbox. 

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set environment variables

```bash
export FLIGHTRADAR_API_KEY="your_production_key"
# or for testing:
export FLIGHTRADAR_API_KEY="your_sandbox_key"
```

### 3. Update Mapbox token

Edit `index.html` and replace `PERSONAL_MAPBOX_ACCESS_TOKEN` with your actual Mapbox token.

### 4. Test locally

Run the collection script:

```bash
python collect.py
```

Open `index.html` in a browser to view the map.

### 5. Deploy to GitHub

```bash
git add .
git commit -m "Initial flight tracker setup"
git remote add origin https://github.com/YOUR_USERNAME/live-flight-tracker.git
git push -u origin main
```

### 6. Configure GitHub

1. Add `FLIGHTRADAR_API_KEY` as a repository secret:
   - Go to Settings > Secrets and variables > Actions
   - Click "New repository secret"
   - Name: `FLIGHTRADAR_API_KEY`
   - Value: your FlightRadar24 API key

2. Enable GitHub Pages:
   - Go to Settings > Pages
   - Source: Deploy from a branch
   - Branch: `main`, folder: `/ (root)`
   - Save

3. Run the workflow manually:
   - Go to Actions tab
   - Select "Collect flight positions"
   - Click "Run workflow"

The tracker will update every 5 minutes via GitHub Actions. Share your Pages URL with the families.

## Data storage

Flight positions are stored in `data/positions.json`.

## Test locally

Run `python3 -m http.server 8000`