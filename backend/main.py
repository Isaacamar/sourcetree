from backend.graph_builder import SourceGraph
import json
import os
import sys

# Ensure frontend dir exists
os.makedirs('frontend', exist_ok=True)

def main():
    # Test URLs
    test_urls = [
         # A good starting point - Wikipedia usually has many citations
        "https://en.wikipedia.org/wiki/Epistemology",
        # Example news article (might be behind paywall or complex, but let's try)
        # "https://www.nytimes.com/2024/11/15/climate/climate-change-report.html", 
        # "https://www.reddit.com/r/science/top/"
    ]
    
    # Allow passing URL from command line
    if len(sys.argv) > 1:
        test_urls = [sys.argv[1]]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Analyzing: {url}")
        print('='*60)
        
        # Build graph
        graph = SourceGraph()
        graph.build_graph(url)
        
        # Analyze
        metrics = graph.analyze_structure()
        print("\nAnalysis Metrics:")
        print(f"Nodes: {metrics.get('total_nodes')}")
        print(f"Edges: {metrics.get('total_edges')}")
        print(f"Max Depth: {metrics.get('max_depth')}")
        print(f"Cycles found: {metrics.get('circular_citations_count')}")
        # print(json.dumps(metrics, indent=2, default=str)) # Too verbose
        
        # Export for visualization
        viz_data = graph.export_for_visualization()
        
        # Create a safe filename
        safe_name = url.replace('https://', '').replace('http://', '').replace('/', '_')[:50]
        filename = f"frontend/graph_data_{safe_name}.json"
        
        # Also save as 'graph_data.json' for the default visualization to pick up easily
        with open('frontend/graph_data.json', 'w') as f:
            json.dump(viz_data, f, indent=2)
            
        with open(filename, 'w') as f:
            json.dump(viz_data, f, indent=2)
        
        print(f"\nSaved to: {filename} and frontend/graph_data.json")

if __name__ == '__main__':
    # Add project root to path so we can import packages if run directly
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
