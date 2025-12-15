# Deployment Guide - Real-Time Source Tree

This guide will help you deploy your Source Tree application with **Railway** (backend) + **GitHub Pages** (frontend).

## Architecture Overview

```
GitHub Pages (Static Frontend)
         ↓ API calls
Railway (Flask Backend with SSE)
         ↓ Uses
Anthropic Claude API
```

---

## Prerequisites

1. **GitHub Account** - for hosting frontend
2. **Railway Account** - sign up at [railway.app](https://railway.app) (free tier available)
3. **Anthropic API Key** - get one at [console.anthropic.com](https://console.anthropic.com)

---

## Step 1: Deploy Backend to Railway

### Using Railway CLI (Easiest)

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   # or with brew:
   brew install railway
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   # From your project root
   railway init
   ```
   - Choose "Create new project"
   - Name it something like "sourcetree-api"

4. **Add Anthropic API Key**
   ```bash
   railway variables set ANTHROPIC_API_KEY=your-api-key-here
   ```

5. **Deploy**
   ```bash
   railway up
   ```

   This will:
   - Upload your code
   - Install dependencies
   - Download SpaCy model
   - Start the Flask server

6. **Get Your URL**
   ```bash
   railway domain
   ```

   This generates a public URL like: `https://sourcetree-api-production.up.railway.app`

   **Save this URL!** You'll need it for the frontend.

### Alternative: Deploy via GitHub

1. Go to [railway.app/new](https://railway.app/new)
2. Click "Deploy from GitHub repo"
3. Select your repository
4. Add environment variable: `ANTHROPIC_API_KEY`
5. Deploy!

---

## Step 2: Update Frontend with Railway URL

1. **Edit `frontend/visualization.html`**

   Find this line (around line 63):
   ```javascript
   const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
       ? 'http://localhost:5001'
       : 'YOUR_RAILWAY_URL_HERE';
   ```

2. **Replace `YOUR_RAILWAY_URL_HERE`** with your Railway URL (without trailing slash):
   ```javascript
   const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
       ? 'http://localhost:5001'
       : 'https://sourcetree-api-production.up.railway.app';
   ```

---

## Step 3: Deploy Frontend to GitHub Pages

1. **Create/Update GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Add real-time source tree visualization"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/sourcetree.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**
   - Go to your repo on GitHub
   - Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` / folder: `/frontend`
   - Save

3. **Wait 1-2 minutes** for deployment

4. **Your site will be live at:**
   ```
   https://YOUR_USERNAME.github.io/sourcetree/visualization.html
   ```

---

## Step 4: Test It!

1. Open your GitHub Pages URL
2. Enter a URL like: `https://en.wikipedia.org/wiki/Philosophy`
3. Click "Analyze"
4. Watch the graph build in real-time!

---

## Local Development Setup

Want to test locally before deploying?

### Terminal 1 - Backend
```bash
# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Set API key
export ANTHROPIC_API_KEY='your-key-here'

# Run Flask server
python backend/api.py
```

### Terminal 2 - Frontend
```bash
cd frontend
python -m http.server 8000
```

Visit: `http://localhost:8000/visualization.html`

---

## Environment Variables

### Railway (Backend)
- `ANTHROPIC_API_KEY` - Your Anthropic API key (required)
- `PORT` - Auto-set by Railway

### GitHub Pages (Frontend)
- No environment variables needed - the API URL is hardcoded in the HTML

---

## Troubleshooting

### "Failed to connect to server"
- Check that your Railway app is running: `railway status`
- Verify the API URL in `visualization.html` matches your Railway domain
- Check Railway logs: `railway logs`

### "CORS Error"
- The backend has CORS enabled for all origins
- If issues persist, check Railway logs for errors

### SpaCy Model Not Found
- Railway should auto-download it via `railway.json`
- If not, manually trigger: `railway run python -m spacy download en_core_web_sm`

### Slow Analysis
- The analysis can take 30-60 seconds for complex pages
- Railway free tier has limited resources
- Consider upgrading to Railway Pro for better performance

---

## Cost Breakdown

- **Railway**: Free tier includes 500 hours/month (enough for demos)
- **GitHub Pages**: Free unlimited
- **Anthropic API**: Pay per use (~$0.01-0.10 per analysis depending on page complexity)

**Estimated cost for demos/testing: <$5/month**

---

## Advanced: Custom Domain

### Backend (Railway)
```bash
railway domain add yourdomain.com
```

### Frontend (GitHub Pages)
- Settings → Pages → Custom domain
- Add your domain
- Update DNS records as instructed

---

## Monitoring

### Railway Dashboard
- View logs: `railway logs`
- Monitor usage: https://railway.app/dashboard
- Check deployments: `railway status`

### API Health Check
```bash
curl https://your-railway-url.up.railway.app/health
```

Should return: `{"status": "ok"}`

---

## Next Steps

- Add rate limiting to prevent abuse
- Implement caching to reduce API costs
- Add authentication for private use
- Customize the visualization styling

---

## Need Help?

- Railway Docs: https://docs.railway.app
- GitHub Pages Docs: https://docs.github.com/pages
- Open an issue in your repo for project-specific questions
