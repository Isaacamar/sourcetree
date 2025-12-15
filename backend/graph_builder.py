import networkx as nx
from datetime import datetime
import time
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import traceback

# Import our modules
# Assuming they are in the same package or path is set up correctly
try:
    from backend.scraper import fetch_page, extract_links, extract_metadata
    from backend.llm_analyzer import llm_extract_implicit_sources
    from backend.source_hunter import find_implicit_sources
except ImportError:
    # Fallback for when running directly
    from scraper import fetch_page, extract_links, extract_metadata
    from llm_analyzer import llm_extract_implicit_sources
    from source_hunter import find_implicit_sources

class SourceGraph:
    def __init__(self):
        self.G = nx.DiGraph()
        self.visited = set()
        self.max_depth = 2  # Don't go too deep
        
    def add_page_node(self, url, metadata):
        """Add a page as a node"""
        # Ensure metadata has 'type'
        metadata['type'] = metadata.get('type') or self.classify_domain(url)
        self.G.add_node(url, **metadata)
    
    def add_citation_edge(self, from_url, to_url, edge_data):
        """
        Add directed edge: from_url cites to_url
        """
        self.G.add_edge(from_url, to_url, **edge_data)
    
    def classify_domain(self, url):
        """
        Classify webpage by authority type for color-coding
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Government/Official
        if domain.endswith('.gov') or 'government' in domain:
            return 'government'
        
        # Academic
        if domain.endswith('.edu') or any(x in domain for x in ['university', 'college', 'academic']):
            return 'academic'
        
        # Research/Scientific
        if any(x in domain for x in ['nature.com', 'science.org', 'arxiv', 'pubmed', 'jstor']):
            return 'research'
        
        # News (attempt to distinguish quality)
        news_quality = {
            'high': ['reuters.com', 'apnews.com', 'bbc.', 'npr.org', 'pbs.org'],
            'mainstream': ['nytimes.com', 'washingtonpost.com', 'wsj.com', 'theguardian.com'],
            'other': ['cnn.com', 'foxnews.com', 'msnbc.com']
        }
        
        for quality, outlets in news_quality.items():
            if any(outlet in domain for outlet in outlets):
                return f'news_{quality}'
        
        # NGO/Org
        if domain.endswith('.org'):
            return 'organization'
        
        # Social/User-generated
        if any(x in domain for x in ['reddit', 'medium', 'substack', 'blog']):
            return 'social'
        
        # Commercial
        return 'commercial'
    
    def get_tier(self, node_type):
        """
        Assign a vertical tier (1-5) based on node type for Lombardi-style layout.
        Tier 1 (Top): Government / Official / Abstract Concepts
        Tier 2: Academic / Research
        Tier 3: News / Media
        Tier 4: NGOs / Organizations / Commercial
        Tier 5 (Bottom): Social / Blogs / Unverified
        """
        mapping = {
            'government': 1,
            'virtual': 1, # Abstract/Offline concepts often high-level
            'academic': 2,
            'research': 2,
            'news_high': 3,
            'news_mainstream': 3,
            'news_other': 3,
            'organization': 4,
            'commercial': 4,
            'social': 5,
            'unknown': 5
        }
        return mapping.get(node_type, 5)

    def build_graph(self, root_url, current_depth=0):
        """
        Recursively build citation graph
        """
        if current_depth >= self.max_depth or root_url in self.visited:
            return
        
        self.visited.add(root_url)
        print(f"Analyzing: {root_url} (depth {current_depth})")
        
        # Fetch and parse page
        html = fetch_page(root_url)
        if not html:
            return
            
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        
        # Extract metadata
        metadata = extract_metadata(soup, root_url)
        self.add_page_node(root_url, metadata)
        
        # TRADITIONAL SCRAPING: Explicit links
        explicit_links = extract_links(soup, root_url)
        
        # PRIORITIZATION STRATEGY:
        # Separate internal vs external links using STRICT base domain comparison
        # This handles edition.cnn.com vs cnn.com
        
        def get_base_domain(netloc):
            """
            Heuristic to get base domain (e.g. 'cnn.com' from 'edition.cnn.com')
            Assumes 'example.com' or 'example.co.uk' structure
            """
            parts = netloc.split('.')
            if len(parts) > 2:
                # Very rough heuristic: if last part is 2 chars (uk, jp), might be co.uk
                if len(parts[-1]) == 2 and len(parts[-2]) <= 3:
                     return '.'.join(parts[-3:])
                return '.'.join(parts[-2:])
            return netloc

        root_netloc = urlparse(root_url).netloc
        root_base = get_base_domain(root_netloc)
        
        external_links = []
        internal_links = []
        
        for link in explicit_links:
            # Skip self-loops
            if link['url'] == root_url: continue
            
            link_netloc = urlparse(link['url']).netloc
            link_base = get_base_domain(link_netloc)
            
            # STRICT CHECK: If base domains match, it's internal!
            if link_base != root_base and link_base not in root_base and root_base not in link_base:
                external_links.append(link)
            else:
                internal_links.append(link)
        
        # Prioritize external links significantly
        # Take up to 8 external links, and only 2 internal links (for structure)
        selected_links = external_links[:10] + internal_links[:3]
        
        print(f"   Found {len(explicit_links)} links. Filtered to {len(external_links)} truly external.")
        print(f"   Selected {len(selected_links)} candidate links for Deep Analysis.")

        for link in selected_links:
            # DEEP SEMANTIC ANALYSIS (The "Truth Seeker" Step)
            # We ask the LLM: Is this link actually a source?
            # print(f"   Analyzing significance of: {link['url']}...")
            
            # Use cached context from scraper
            context = link.get('context', '')
            anchor = link.get('anchor_text', '')
            
            # This function is imported from llm_analyzer
            from backend.llm_analyzer import verify_link_significance
            
            analysis = verify_link_significance(context, link['url'], anchor)
            score = analysis['score']
            link_type = analysis['type']
            
            # SIGNIFICANCE THRESHOLD
            # Only graph links that are fairly significant (>40) to reduce noise
            if score < 40:
                # print(f"   Skipping low significance link ({score}): {link['url']}")
                continue
                
            print(f"   [+] Added Source (Score {score}, Type {link_type}): {link['url']}")

            self.add_citation_edge(
                root_url, 
                link['url'],
                {
                    'type': 'explicit',
                    'context': link['context'],
                    'confidence': score / 100.0, # Use score as confidence
                    'significance': score,
                    'relation_type': link_type,
                    'reason': analysis.get('reason', '')
                }
            )
            
            # Add node if not exists
            if link['url'] not in self.G:
                 self.add_page_node(link['url'], {
                     'url': link['url'],
                     'type': 'source' if score > 75 else 'related'
                 })

            # Recurse only for High Significance links (True Sources)
            # time.sleep(1)  # Be polite
            if score > 60 and current_depth + 1 < self.max_depth:
                self.build_graph(link['url'], current_depth + 1)
        
        # SEMANTIC ANALYSIS: Implicit sources
        # Only run LLM on the root or interesting pages to save tokens/time
        if current_depth == 0: 
            claims = llm_extract_implicit_sources(text[:5000], root_url)
            
            for claim in claims:
                if not claim.get('has_explicit_link'):
                    # Try to discover the source
                    discovered_sources = find_implicit_sources(claim)
                    
                    if discovered_sources:
                        for source in discovered_sources:
                            self.add_citation_edge(
                                root_url,
                                source['url'],
                                {
                                    'type': 'discovered',
                                    'claim': claim.get('claim'),
                                    'confidence': source.get('confidence'),
                                    'search_query': source.get('search_query')
                                }
                            )
                            # Add node
                            if source['url'] not in self.G:
                                self.add_page_node(source['url'], {'url': source['url']})
                            
                            # Recurse on discovered sources
                            if current_depth + 1 < self.max_depth:
                                self.build_graph(source['url'], current_depth + 1)
                    else:
                        # VIRTUAL NODE LOGIC (For offline/missing sources)
                        source_name = claim.get('mentioned_source') or claim.get('needs_source_type')
                        if source_name:
                             virtual_id = f"[Offline] {source_name}"
                             print(f"   [!] Creating Virtual Node: {virtual_id}")
                             
                             self.G.add_node(virtual_id, type='virtual', domain='Offline Source')
                             self.add_citation_edge(
                                 root_url,
                                 virtual_id,
                                 {
                                     'type': 'virtual',
                                     'claim': claim.get('claim'),
                                     'confidence': 0.8,
                                     'reason': 'Cited but not linked'
                                 }
                             )
    
    def analyze_structure(self):
        """
        Compute epistemological metrics
        """
        try:
             # Calculate cycles if possible (might be expensive on large graphs, but ok here)
            cycles = list(nx.simple_cycles(self.G))
        except:
             cycles = []

        return {
            'total_nodes': self.G.number_of_nodes(),
            'total_edges': self.G.number_of_edges(),
            
            # Centralization: Do many nodes cite one source?
            'bottlenecks': self.find_bottlenecks(),
            
            # Independence: Are sources truly separate?
            # Truncate cycles to avoid massive output
            'circular_citations_count': len(cycles),
            'circular_citations_sample': cycles[:5],
            
            # Depth: How far to "bedrock"?
            'max_depth': nx.dag_longest_path_length(self.G) if nx.is_directed_acyclic_graph(self.G) else "Contains Cycles",
            
            # Authority: Which nodes are most cited?
            'most_cited': sorted(
                [(node, self.G.in_degree(node)) for node in self.G.nodes()],
                key=lambda x: x[1],
                reverse=True
            )[:10],
            
            # Orphans: Claims with no sources
            'unsourced_nodes': [n for n in self.G.nodes() if self.G.out_degree(n) == 0]
        }
    
    def find_bottlenecks(self, threshold=3):
        """
        Find nodes that are cited by many others
        (potential single points of failure)
        """
        bottlenecks = []
        for node in self.G.nodes():
            in_degree = self.G.in_degree(node)
            if in_degree >= threshold:
                bottlenecks.append({
                    'url': node,
                    'citations': in_degree,
                    'citing_pages': list(self.G.predecessors(node))
                })
        return bottlenecks
    
    def export_for_visualization(self):
        """
        Export graph as JSON for D3.js
        """
        nodes = []
        links = []
        
        for node in self.G.nodes(data=True):
            try:
                domain_val = node[1].get('domain')
                if not domain_val:
                    if node[0].startswith('[Offline]'):
                        domain_val = node[0] # The name is the domain for virtual nodes
                    else:
                        domain_val = urlparse(node[0]).netloc
                
                node_type = node[1].get('type', 'unknown')
                
                nodes.append({
                    'id': node[0],
                    'title': node[1].get('title', node[0]),
                    'domain': domain_val,
                    'type': node_type,
                    'tier': self.get_tier(node_type),
                    'citations': self.G.in_degree(node[0])
                })
            except Exception as e:
                print(f"Error exporting node {node[0]}: {e}")
        
        for edge in self.G.edges(data=True):
            links.append({
                'source': edge[0],
                'target': edge[1],
                'type': edge[2].get('type', 'unknown'),
                'confidence': edge[2].get('confidence', 0.5),
                'context': edge[2].get('context', '')
            })
        
        return {'nodes': nodes, 'links': links}
