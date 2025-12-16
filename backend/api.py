from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json
import time
import sys
import os
from queue import Queue
import threading

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.graph_builder import SourceGraph

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["https://isaacamar.github.io", "http://localhost:8000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Store active analysis sessions
sessions = {}

class ProgressEmitter:
    """Emits progress updates for Server-Sent Events"""
    def __init__(self):
        self.queue = Queue()

    def emit(self, event_type, data):
        """Add event to queue"""
        self.queue.put({
            'event': event_type,
            'data': data
        })

    def stream(self):
        """Generator for SSE stream"""
        while True:
            event = self.queue.get()
            if event is None:  # Sentinel to stop
                break

            yield f"event: {event['event']}\n"
            yield f"data: {json.dumps(event['data'])}\n\n"

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

@app.route('/analyze', methods=['POST'])
def analyze():
    """Start analysis of a URL with real-time updates via SSE"""
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Create progress emitter
    emitter = ProgressEmitter()
    session_id = str(time.time())
    sessions[session_id] = emitter

    def run_analysis():
        """Run analysis in background thread"""
        try:
            emitter.emit('status', {'message': 'Starting analysis...', 'url': url})

            # Monkey-patch NetworkX add_node and add_edge to emit progress
            import networkx as nx

            graph = SourceGraph()
            original_nx_add_node = graph.G.add_node
            original_nx_add_edge = graph.G.add_edge

            def add_node_with_emit(node_id, **attr):
                result = original_nx_add_node(node_id, **attr)
                # Emit new node
                emitter.emit('node', {
                    'id': node_id,
                    'title': attr.get('title', node_id),
                    'url': attr.get('url', node_id),
                    'type': attr.get('type', 'unknown'),
                    'tier': graph.get_tier(attr.get('type', 'unknown'))
                })
                return result

            def add_edge_with_emit(source, target, **attr):
                result = original_nx_add_edge(source, target, **attr)
                # Emit new edge
                emitter.emit('edge', {
                    'source': source,
                    'target': target,
                    'type': attr.get('type', 'unknown'),
                    'confidence': attr.get('confidence', 0.5)
                })
                return result

            # Patch the graph's methods
            graph.G.add_node = add_node_with_emit
            graph.G.add_edge = add_edge_with_emit

            # Build graph
            emitter.emit('status', {'message': f'Scraping {url}...'})
            graph.build_graph(url)

            # Restore original methods
            graph.G.add_node = original_nx_add_node
            graph.G.add_edge = original_nx_add_edge

            # Get final data
            viz_data = graph.export_for_visualization()
            metrics = graph.analyze_structure()

            emitter.emit('complete', {
                'message': 'Analysis complete!',
                'metrics': {
                    'nodes': metrics.get('total_nodes'),
                    'edges': metrics.get('total_edges'),
                    'max_depth': metrics.get('max_depth')
                },
                'graph': viz_data
            })

        except Exception as e:
            emitter.emit('error', {'message': str(e)})
        finally:
            emitter.queue.put(None)  # Stop stream
            # Cleanup session after 5 seconds
            time.sleep(5)
            if session_id in sessions:
                del sessions[session_id]

    # Start background thread
    thread = threading.Thread(target=run_analysis)
    thread.daemon = True
    thread.start()

    # Return SSE stream
    return Response(
        emitter.stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

@app.route('/quick-analyze', methods=['POST'])
def quick_analyze():
    """Quick analysis endpoint - returns result when done (no streaming)"""
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        graph = SourceGraph()
        graph.build_graph(url)
        viz_data = graph.export_for_visualization()
        metrics = graph.analyze_structure()

        return jsonify({
            'success': True,
            'graph': viz_data,
            'metrics': {
                'nodes': metrics.get('total_nodes'),
                'edges': metrics.get('total_edges'),
                'max_depth': metrics.get('max_depth')
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
