
def convert_to_tree(flat_data):
    """
    Convert flat nodes/links to hierarchical tree structure for D3.
    """
    nodes = {n['id']: n for n in flat_data['nodes']}
    links = flat_data['links']
    
    # 1. Identify the root (node with no incoming explicit links, or most cited if circular)
    # Actually, main.py knows the root URL. But here we work with JSON.
    # Simple heuristic: The first node in list is usually the root because we added it first.
    root_id = flat_data['nodes'][0]['id']
    
    # 2. Build adjacency list
    children_map = {}
    for link in links:
        src = link['source']
        target = link['target']
        # if link['type'] == 'explicit': # Follow explicit paths for tree structure
        if src not in children_map: children_map[src] = []
        children_map[src].append(target)
            
    # 3. Recursive builder
    visited = set()
    
    def build_node(node_id):
        if node_id in visited:
            return {"name": nodes[node_id]['domain'], "type": "cycle", "url": node_id}
        visited.add(node_id)
        
        node_data = nodes.get(node_id, {"domain": "Unknown", "type": "unknown"})
        
        tree_node = {
            "name": node_data.get('domain', 'Unknown'),
            "url": node_id,
            "type": node_data.get('type', 'unknown'),
            "title": node_data.get('title', ''),
            "citations": node_data.get('citations', 0)
        }
        
        children_ids = children_map.get(node_id, [])
        if children_ids:
            tree_node["children"] = [build_node(child_id) for child_id in children_ids]
            
        return tree_node

    return build_node(root_id)
