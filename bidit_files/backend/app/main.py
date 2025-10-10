"""
Infinite Desk - FastAPI Backend - With Authentication
"""
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import json
import os
from pathlib import Path
from datetime import datetime
import hashlib

app = FastAPI(
    title="Infinite Desk API",
    description="Backend API for Infinite Floating Knowledge Map with Authentication",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
COLLECTIONS_FILE = DATA_DIR / "collections.json"
CLUSTERS_FILE = DATA_DIR / "clusters.json"
NODES_FILE = DATA_DIR / "nodes.json"
USERS_FILE = DATA_DIR / "users.json"

DATA_DIR.mkdir(exist_ok=True, parents=True)

for file_path in [COLLECTIONS_FILE, CLUSTERS_FILE, NODES_FILE, USERS_FILE]:
    if not file_path.exists():
        with open(file_path, 'w') as f:
            json.dump([], f)

def read_json_file(file_path: Path) -> List[Dict[str, Any]]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def write_json_file(file_path: Path, data: List[Dict[str, Any]]) -> bool:
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error writing {file_path}: {e}")
        return False

def find_by_id(data: List[Dict], item_id: str, id_field: str = "_id") -> Optional[Dict]:
    for item in data:
        if item.get(id_field) == item_id or item.get("id") == item_id:
            return item
    return None

def generate_id(prefix: str = "item") -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"{prefix}_{timestamp}"

@app.get("/")
async def root():
    return {
        "message": "Infinite Desk API - Floating Knowledge Map with Authentication",
        "version": "2.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    collections = read_json_file(COLLECTIONS_FILE)
    clusters = read_json_file(CLUSTERS_FILE)
    nodes = read_json_file(NODES_FILE)
    users = read_json_file(USERS_FILE)

    return {
        "status": "healthy",
        "data": {
            "collections": len(collections),
            "clusters": len(clusters),
            "nodes": len(nodes),
            "users": len(users)
        }
    }

# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/signup")
async def signup(user_data: Dict = Body(...)):
    users = read_json_file(USERS_FILE)

    email = user_data.get("email")
    password = user_data.get("password")
    name = user_data.get("name")

    if not email or not password or not name:
        raise HTTPException(status_code=400, detail="Email, password, and name are required")

    # Check if user already exists
    existing_user = next((u for u in users if u.get("email") == email), None)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    new_user = {
        "id": generate_id("user"),
        "name": name,
        "email": email,
        "password": password,  # In production, hash this!
        "created_at": datetime.now().isoformat()
    }

    users.append(new_user)
    write_json_file(USERS_FILE, users)

    # Return user without password
    return {
        "success": True,
        "message": "User created successfully",
        "user": {
            "id": new_user["id"],
            "name": new_user["name"],
            "email": new_user["email"]
        }
    }

@app.post("/api/auth/login")
async def login(credentials: Dict = Body(...)):
    users = read_json_file(USERS_FILE)

    email = credentials.get("email")
    password = credentials.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    # Find user
    user = next((u for u in users if u.get("email") == email and u.get("password") == password), None)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Return user without password
    return {
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }

@app.get("/api/auth/check-email/{email}")
async def check_email(email: str):
    users = read_json_file(USERS_FILE)
    exists = any(u.get("email") == email for u in users)
    return {"exists": exists}

# ==================== EXISTING ENDPOINTS ====================

@app.get("/api/collections")
async def get_all_collections():
    return read_json_file(COLLECTIONS_FILE)

@app.get("/api/collections/{collection_id}")
async def get_collection_by_id(collection_id: str):
    collections = read_json_file(COLLECTIONS_FILE)
    collection = find_by_id(collections, collection_id)

    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection not found")

    return collection

@app.get("/api/collections/{collection_id}/clusters")
async def get_collection_clusters(collection_id: str):
    clusters = read_json_file(CLUSTERS_FILE)
    return [c for c in clusters if c.get("sheet_id") == collection_id]

@app.post("/api/clusters")
async def create_cluster(cluster_data: Dict = Body(...)):
    clusters = read_json_file(CLUSTERS_FILE)

    new_cluster = {
        "_id": generate_id("cluster"),
        "id": None,
        "sheet_id": cluster_data.get("sheet_id"),
        "cluster_label": cluster_data.get("cluster_label", len(clusters)),
        "name": cluster_data.get("name", "New Cluster"),
        "user_defined_name": cluster_data.get("user_defined_name", cluster_data.get("name")),
        "color": cluster_data.get("color", "#3498db"),
        "node_count": 0
    }
    new_cluster["id"] = new_cluster["_id"]

    clusters.append(new_cluster)
    write_json_file(CLUSTERS_FILE, clusters)

    return new_cluster

@app.put("/api/clusters/{cluster_id}")
async def update_cluster(cluster_id: str, update_data: Dict = Body(...)):
    clusters = read_json_file(CLUSTERS_FILE)
    cluster = find_by_id(clusters, cluster_id)

    if not cluster:
        raise HTTPException(status_code=404, detail=f"Cluster not found")

    if "name" in update_data:
        cluster["name"] = update_data["name"]
    if "user_defined_name" in update_data:
        cluster["user_defined_name"] = update_data["user_defined_name"]
    if "color" in update_data:
        cluster["color"] = update_data["color"]

    write_json_file(CLUSTERS_FILE, clusters)
    return cluster

@app.delete("/api/clusters/{cluster_id}")
async def delete_cluster(cluster_id: str):
    clusters = read_json_file(CLUSTERS_FILE)
    cluster = find_by_id(clusters, cluster_id)

    if not cluster:
        raise HTTPException(status_code=404, detail=f"Cluster not found")

    clusters = [c for c in clusters if c.get("_id") != cluster_id and c.get("id") != cluster_id]
    write_json_file(CLUSTERS_FILE, clusters)

    return {"message": "Cluster deleted successfully", "cluster_id": cluster_id}

@app.get("/api/clusters/{cluster_id}/nodes")
async def get_cluster_nodes(cluster_id: str):
    nodes = read_json_file(NODES_FILE)
    return [n for n in nodes if n.get("cluster_id") == cluster_id]

@app.post("/api/nodes")
async def create_node(node_data: Dict = Body(...)):
    nodes = read_json_file(NODES_FILE)

    new_node = {
        "_id": generate_id("node"),
        "id": None,
        "cluster_id": node_data.get("cluster_id"),
        "title": node_data.get("title", "Untitled"),
        "content": node_data.get("content", {"text": ""}),
        "summary": node_data.get("summary", ""),
        "position": node_data.get("position", {"x": 100, "y": 100}),
        "color": node_data.get("color", "#3498db"),
        "similar_to": node_data.get("similar_to", []),
        "created_at": datetime.now().isoformat()
    }
    new_node["id"] = new_node["_id"]

    nodes.append(new_node)
    write_json_file(NODES_FILE, nodes)

    return new_node

@app.get("/api/nodes/{node_id}")
async def get_node_by_id(node_id: str):
    nodes = read_json_file(NODES_FILE)
    node = find_by_id(nodes, node_id)

    if not node:
        raise HTTPException(status_code=404, detail=f"Node not found")

    return node

@app.put("/api/nodes/{node_id}")
async def update_node(node_id: str, update_data: Dict = Body(...)):
    nodes = read_json_file(NODES_FILE)
    node = find_by_id(nodes, node_id)

    if not node:
        raise HTTPException(status_code=404, detail=f"Node not found")

    allowed_fields = ["title", "content", "summary", "position", "color"]
    for field in allowed_fields:
        if field in update_data:
            node[field] = update_data[field]

    write_json_file(NODES_FILE, nodes)
    return node

@app.delete("/api/nodes/{node_id}")
async def delete_node(node_id: str):
    nodes = read_json_file(NODES_FILE)
    node = find_by_id(nodes, node_id)

    if not node:
        raise HTTPException(status_code=404, detail=f"Node not found")

    nodes = [n for n in nodes if n.get("_id") != node_id and n.get("id") != node_id]
    write_json_file(NODES_FILE, nodes)

    return {"message": "Node deleted successfully", "node_id": node_id}

if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("🚀 Infinite Desk API Server with Authentication")
    print("=" * 60)
    print(f"📁 Data: {DATA_DIR}")
    print(f"🌐 Server: http://127.0.0.1:8000")
    print(f"📚 Docs: http://127.0.0.1:8000/docs")
    print(f"🔐 Auth: /api/auth/login, /api/auth/signup")
    print("=" * 60)

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
