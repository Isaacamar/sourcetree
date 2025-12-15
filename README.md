# Source Tree: A Visual Genealogy of Digital Knowledge

## Overview
Source Tree is a research tool that visualizes the "genealogy" of knowledge on the web. It goes beyond traditional link scraping by using NLP and LLM analysis to identify *implicit* citations—claims made without links—and finding their likely sources.

The result is a force-directed graph where you can see the flow of information, identify bottlenecks (widely cited sources), and analyze the authority of different domains.

## Features
- **Real-Time Analysis**: Enter any URL and watch the knowledge graph build live
- **Recursive Scraping**: Follows links to build a citation network
- **Semantic Analysis**: Extracts factual claims using SpaCy and LLM analysis
- **Offline Source Detection**: Identifies books, papers, and non-web sources with special visualization
- **Authority Classification**: Color-codes nodes by type (Government, Academic, News, etc.)
- **Interactive D3.js Visualization**: Organic force-directed graph with flow animations

## Quick Start

### Prerequisites
- Python 3.11+
- Anthropic API Key ([get one here](https://console.anthropic.com))

### Local Development

1. **Clone and setup**
   ```bash
   git clone https://github.com/YOUR_USERNAME/sourcetree.git
   cd sourcetree
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

2. **Set API key**
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

3. **Run backend**
   ```bash
   python backend/api.py
   ```

4. **Run frontend** (separate terminal)
   ```bash
   cd frontend
   python -m http.server 8000
   ```

5. **Open in browser**
   Visit `http://localhost:8000/visualization.html`

### Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for full deployment instructions to Railway + GitHub Pages.

## Project Structure
- `backend/`: Flask API and graph analysis engine
- `frontend/`: D3.js real-time visualization
- `DEPLOYMENT.md`: Production deployment guide
- `QUICKSTART.md`: 5-minute setup guide
