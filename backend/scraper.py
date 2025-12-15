import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def fetch_page(url):
    """Fetch HTML content from URL"""
    headers = {'User-Agent': 'Mozilla/5.0 (Educational Research Bot)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_metadata(soup, url):
    """Extract page metadata for graph node"""
    return {
        'url': url,
        'title': soup.find('title').text.strip() if soup.find('title') else url,
        'domain': urlparse(url).netloc,
        # 'type' will be classified later by graph_builder
    }

def extract_links(soup, base_url):
    """Extract all outbound links from page"""
    links = []
    
    # Hyperlinks
    for a_tag in soup.find_all('a', href=True):
        href = urljoin(base_url, a_tag['href'])
        # Filter internal navigation, social media, ads
        if is_valid_source(href):
            # Get Context: The text of the parent element (likely the sentence/paragraph)
            # This helps the LLM decide if the link is a "source" or just "related"
            parent = a_tag.find_parent(['p', 'li', 'div', 'span'])
            context_text = parent.get_text(strip=True)[:300] if parent else a_tag.get_text(strip=True)
            
            links.append({
                'url': href,
                'context': context_text, # Expanding context for significance analysis
                'anchor_text': a_tag.get_text(strip=True),
                'type': 'hyperlink'
            })
    
    return links

def is_valid_source(url):
    """Filter out navigation/social/ads"""
    parsed = urlparse(url)
    
    # Exclude
    excluded_domains = ['facebook.com', 'twitter.com', 'instagram.com', 
                       'linkedin.com', 'youtube.com', 'ads.', 'google.com']
    excluded_paths = ['/login', '/signup', '/share', '/subscribe']
    
    if any(ex in parsed.netloc for ex in excluded_domains):
        return False
    if any(ex in parsed.path for ex in excluded_paths):
        return False
        
    return True
