# Deployment checklist

Follow these steps to deploy the flight tracker to GitHub Pages.

## Pre-deployment

1. **Test locally with sandbox key** (optional but recommended)

```bash
export FLIGHTRADAR_API_KEY="your_sandbox_key"
export USE_SANDBOX=true
python collect.py
```

Open `index.html` in a browser to verify the map works.

2. **Replace Mapbox token in index.html**

Open `index.html` and find this line:

```javascript
const MAPBOX_TOKEN = 'PERSONAL_MAPBOX_ACCESS_TOKEN';
```

Replace `PERSONAL_MAPBOX_ACCESS_TOKEN` with your actual Mapbox token.

## GitHub setup

1. **Create GitHub repository**

Go to github.com and create a new public repository named `live-flight-tracker`.

2. **Push code to GitHub**

```bash
git add .
git commit -m "Initial flight tracker setup"
git remote add origin https://github.com/YOUR_USERNAME/live-flight-tracker.git
git branch -M main
git push -u origin main
```

3. **Add API key as secret**

- Go to repository Settings > Secrets and variables > Actions
- Click "New repository secret"
- Name: `FLIGHTRADAR_API_KEY`
- Value: paste your FlightRadar24 production API key
- Click "Add secret"

4. **Enable GitHub Pages**

- Go to Settings > Pages
- Source: "Deploy from a branch"
- Branch: `main`
- Folder: `/ (root)`
- Click "Save"

Wait 1-2 minutes for the initial deployment.

5. **Test the workflow**

- Go to the Actions tab
- Click "Collect flight positions"
- Click "Run workflow" > "Run workflow"
- Wait for it to complete (should take ~30 seconds)
- Check that `data/positions.json` was updated in the repo

6. **Access your tracker**

Your tracker will be live at:
`https://YOUR_USERNAME.github.io/live-flight-tracker/`

## Monitoring

- The workflow runs every 3 minutes automatically
- Check the Actions tab to see workflow runs
- View `data/positions.json` in the repo to see collected data
- Each API call costs 6 credits per flight (12 credits total per run)

## Share with families

Send them the GitHub Pages URL. The map updates automatically every 60 seconds.

## After the trip

Consider disabling the workflow to stop using API credits:
- Go to Actions > "Collect flight positions" > click the "..." menu > "Disable workflow"
