# Quick Start - 5 Minute Deploy

Get your real-time Source Tree visualization online in 5 minutes!

## 1. Install Railway CLI

```bash
npm install -g @railway/cli
# or
brew install railway
```

## 2. Deploy Backend

```bash
# Run the automated deploy script
./deploy.sh
```

Or manually:
```bash
railway login
railway init
railway variables set ANTHROPIC_API_KEY=your-key-here
railway up
railway domain
```

Save the URL you get (e.g., `https://sourcetree-api-production.up.railway.app`)

## 3. Update Frontend

Edit `frontend/visualization.html` line 63:
```javascript
// Change this:
: 'YOUR_RAILWAY_URL_HERE';

// To this (use your Railway URL):
: 'https://sourcetree-api-production.up.railway.app';
```

## 4. Deploy to GitHub Pages

```bash
# Create repo and push
git init
git add .
git commit -m "Deploy source tree"
git remote add origin https://github.com/YOUR_USERNAME/sourcetree.git
git push -u origin main
```

Then:
- Go to GitHub repo → Settings → Pages
- Source: `main` branch, `/frontend` folder
- Save

## 5. Done!

Your site will be live at:
```
https://YOUR_USERNAME.github.io/sourcetree/visualization.html
```

---

## Test Locally First?

**Terminal 1 - Backend:**
```bash
export ANTHROPIC_API_KEY='your-key'
python backend/api.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python -m http.server 8000
```

Visit: `http://localhost:8000/visualization.html`

---

## Try These URLs:

- `https://en.wikipedia.org/wiki/Philosophy`
- `https://www.bbc.com/news`
- `https://plato.stanford.edu/entries/epistemology/`

---

**Full docs:** See [DEPLOYMENT.md](DEPLOYMENT.md)
