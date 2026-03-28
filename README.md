# Live Flight Tracker

Track AA621 (LAX→MIA) and AA917 (MIA→LIM) in real-time.

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

The tracker will update every 3 minutes via GitHub Actions. Share your Pages URL with the families.

## Data storage

Flight positions are stored in `data/positions.json`. Per FR24 API terms, data must be deleted after 30 days.

## Cost

The FR24 API charges 6 credits per flight per call. With 2 flights collected every 3 minutes:
- ~20 calls per hour = 240 credits/hour
- ~480 calls per day = ~5,760 credits/day

The Explorer plan includes 100,000 credits/month.
