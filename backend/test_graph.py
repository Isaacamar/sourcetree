from backend.graph_builder import SourceGraph
import networkx as nx

def test():
    print("Testing SourceGraph analysis fix...")
    g = SourceGraph()
    g.add_page_node("http://a.com", {})
    g.add_page_node("http://b.com", {})
    g.add_citation_edge("http://a.com", "http://b.com", {})
    
    try:
        metrics = g.analyze_structure()
        print("Success! Metrics computed:")
        print(metrics)
    except Exception as e:
        print(f"FAILED: {e}")
        raise

if __name__ == "__main__":
    test()
