from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json

# --- API Data Models ---
# Define the structure the frontend expects
class NodeData(BaseModel):
    id: str
    title: str
    summary: str
    similar_to: List[str]
    # Added 'embedding' field to support vector storage for HDBSCAN clustering input
    embedding: List[float] = [] 

class ClusterData(BaseModel):
    id: int
    name: str
    cx: Optional[float] = None
    cy: Optional[float] = None
    nodes: List[NodeData]

class CollectionData(BaseModel):
    id: int
    name: str
    clusters: List[ClusterData]

# --- LOAD DATA FROM EXTERNAL JSON FILE ---
def load_mock_data(file_path: str) -> List[CollectionData]:
    """Loads mock data from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Validate structure against CollectionData models
            
            collections = [CollectionData(**item) for item in data]
             # --- DEBUG PRINT ---
            loaded_ids = [c.id for c in collections]
            print(f"DEBUG: Successfully loaded {len(collections)} collections. IDs: {loaded_ids}")
            # -------------------
            return collections
    except FileNotFoundError:
        print(f"ERROR: Mock data file not found at {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to decode JSON from {file_path}: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while loading data: {e}")
        return []

# Assuming the JSON file is in the same directory
CS_MOCK_COLLECTIONS: List[CollectionData] = load_mock_data("collections.json")

# --- FASTAPI SETUP ---
app = FastAPI(title="Knowledge Galaxy Mock API")

# Add CORS middleware to allow the HTML file (running locally) to fetch data
origins = ["*"] # Allow all origins for local testing

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/collections", response_model=List[CollectionData], tags=["Data"])
async def get_collections():
    """Returns the list of collections (Knowledge Bases)."""
    return CS_MOCK_COLLECTIONS

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Knowledge Galaxy Mock API is running. Access /api/collections to see data."}

# Placeholder endpoints for future development (to match frontend buttons)
@app.post("/api/ai/recluster/{collection_id}", tags=["AI"])
async def recluster(collection_id: int):
    return {"message": f"AI re-clustering initiated for collection {collection_id}"}

@app.post("/api/nodes", tags=["Nodes"])
async def add_node(node: Dict[str, Any]):
    # Note: In a real implementation, you would need to add this node to one of the collections' clusters.
    return {"message": "Node addition simulated successfully", "node_data": node}

@app.delete("/api/nodes/{node_id}", tags=["Nodes"])
async def delete_node(node_id: str):
    return {"message": f"Node {node_id} deletion simulated successfully"}

@app.post("/api/clusters/merge", tags=["Clusters"])
async def merge_clusters(data: Dict[str, int]):
    return {"message": f"Clusters {data.get('cluster1')} and {data.get('cluster2')} merge simulated"}

@app.post("/api/collections/{collection_id}/save", tags=["Data"])
async def save_layout(collection_id: int, data: Dict[str, Any]):
    return {"message": f"Layout for collection {collection_id} saved successfully (simulated)"}