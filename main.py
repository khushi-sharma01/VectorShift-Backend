from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import networkx as nx  # Use NetworkX for graph operations
import json

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins for better security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.post('/pipelines/parse')
def parse_pipeline(pipeline: str = Form(...)):
    try:
        # Parse pipeline using JSON
        pipeline_data = json.loads(pipeline)
        if not isinstance(pipeline_data, dict):
            raise ValueError("Pipeline must be a JSON object.")

        # Extract nodes and edges
        nodes = pipeline_data.get('nodes', [])
        edges = pipeline_data.get('edges', [])

        # Validate nodes
        graph = nx.DiGraph()
        graph.add_nodes_from([node['id'] for node in nodes])  # Add only the IDs of the nodes

        # Transform edges into (source, target) format
        transformed_edges = [(edge['source'], edge['target']) for edge in edges]
        graph.add_edges_from(transformed_edges)

        # Check if graph is a DAG
        is_dag = nx.is_directed_acyclic_graph(graph)

        return {
            'status': 'success',
            'nodes': list(graph.nodes),
            'edges': list(graph.edges),
            'is_dag': is_dag,
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
