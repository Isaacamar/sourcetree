# Railway Deployment Guide

## Deploy Backend to Railway (via GitHub)

### 1. Push to GitHub

```bash
# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit"

# Create GitHub repo at: https://github.com/new
# Name it: sourcetree

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/sourcetree.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Railway

1. **Go to Railway:** https://railway.app/new

2. **Click "Deploy from GitHub repo"**

3. **Select your `sourcetree` repository**

4. **Configure the service:**
   - Railway will auto-detect Python and use `railway.json` config
   - Wait for initial build (~2 minutes)

5. **Add Environment Variable:**
   - Click on your service
   - Go to "Variables" tab
   - Add:
     - Name: `ANTHROPIC_API_KEY`
     - Value: `your-api-key-here`
   - Save (auto-redeploys)

6. **Generate Domain:**
   - Go to "Settings" tab
   - Scroll to "Networking"
   - Click "Generate Domain"
   - Copy the URL (e.g., `https://sourcetree-production.up.railway.app`)

### 3. Update Frontend

Edit `frontend/visualization.html` line ~63:

```javascript
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5001'
    : 'https://YOUR-RAILWAY-URL.up.railway.app';  // Replace with your Railway URL
```

Commit and push:
```bash
git add frontend/visualization.html
git commit -m "Update API URL"
git push
```

### 4. Deploy Frontend to GitHub Pages

1. **Go to your GitHub repo → Settings → Pages**

2. **Configure:**
   - Source: "Deploy from a branch"
   - Branch: `main`
   - Folder: `/frontend`
   - Save

3. **Wait ~2 minutes**

4. **Your site will be live at:**
   ```
   https://YOUR_USERNAME.github.io/sourcetree/visualization.html
   ```

---

## Troubleshooting

### Backend not starting
- Check Railway logs in the dashboard
- Ensure `ANTHROPIC_API_KEY` is set
- Verify `railway.json` and `Procfile` are in the root

### Frontend can't connect
- Check the API URL in `visualization.html`
- Ensure Railway service has a public domain
- Check browser console for CORS errors

### "Module not found" errors
- Ensure all dependencies are in `requirements.txt`
- Railway should auto-install SpaCy model via `railway.json`

---

## Updates

When you make changes:

```bash
git add .
git commit -m "Description of changes"
git push
```

Railway auto-deploys on push to `main`.

---

## Cost

- **Railway**: Free tier (500 hours/month)
- **GitHub Pages**: Free unlimited
- **Anthropic API**: ~$0.01-0.10 per analysis

**Total: <$5/month for typical usage**
