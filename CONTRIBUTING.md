# Contributing to Source Tree

## Development Setup

1. **Fork and clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/sourcetree.git
   cd sourcetree
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Set environment variables**
   ```bash
   export ANTHROPIC_API_KEY='your-key-here'
   ```

## Architecture

### Backend (`backend/`)
- **`api.py`**: Flask server with Server-Sent Events for real-time updates
- **`graph_builder.py`**: Core graph construction and analysis
- **`scraper.py`**: Web scraping and link extraction
- **`llm_analyzer.py`**: LLM-based semantic analysis
- **`source_hunter.py`**: Implicit source discovery

### Frontend (`frontend/`)
- **`visualization.html`**: Main D3.js visualization with real-time updates
- **`lombardi.css`**: Styling (inspired by Mark Lombardi's network diagrams)

## Key Features

### Offline Source Detection
The system identifies non-web sources (books, papers, etc.) and visualizes them with:
- Sandy orange color (#f4a460)
- Book emoji (📖)
- Dashed borders
- Special tooltip styling

### Real-Time Streaming
The backend uses Server-Sent Events to stream:
- Individual node discoveries
- Link creation
- Progress updates
- Final metrics

### Visual Design
- Organic force-directed layout with radial clustering
- Animated flow particles along links
- Pulsing halos for important nodes
- Color-coded by tier and source type

## Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow existing code style
   - Add comments for complex logic
   - Test locally before committing

3. **Test thoroughly**
   ```bash
   # Terminal 1
   python backend/api.py

   # Terminal 2
   cd frontend && python -m http.server 8000
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request**

## Code Style

- Python: Follow PEP 8
- JavaScript: Use ES6+ features
- Comments: Explain *why*, not *what*
- Variable names: Descriptive and clear

## Testing URLs

Good test cases:
- `https://en.wikipedia.org/wiki/Philosophy`
- `https://plato.stanford.edu/entries/epistemology/`
- `https://www.bbc.com/news`

## Questions?

Open an issue or reach out to the maintainers.
