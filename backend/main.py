from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import numpy as np
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestCentroid
from sentence_transformers import SentenceTransformer
import networkx as nx # NEW: For PageRank calculation
from umap import UMAP
from hdbscan import prediction
import umap
# ==============================================================
# 🧩 Data Models
# ==============================================================

class NodeData(BaseModel):
    id: str
    title: str
    summary: str
    similar_to: List[str] = []
    embedding: List[float] = [] 
    x: Optional[float] = None # NEW: For layout saving
    y: Optional[float] = None # NEW: For layout saving
    # Explicit link to the collection for efficient lookups
    collection_id: Optional[int] = None 

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

class QueryResult(BaseModel): # NEW: Model for Semantic Query results
    node: NodeData
    similarity_score: float


# ==============================================================
# 🧠 ML Setup
# ==============================================================

print("Loading embedding model... (this may take a few seconds)")
# Note: You need the 'sentence-transformers' library installed for this to work
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("Model loaded ✅")


# ==============================================================
# 🗂 Load Mock Data
# ==============================================================

def load_mock_data(file_path: str) -> List[CollectionData]:
    """Loads mock data and ensures all nodes have collection_id set."""
    try:
        # NOTE: This assumes 'collections.json' exists in the environment.
        with open(file_path, 'r') as f:
            data = json.load(f)
            collections = [CollectionData(**item) for item in data]
            
            # Ensure all nodes have their collection_id set for new logic
            for collection in collections:
                for cluster in collection.clusters:
                    for node in cluster.nodes:
                        node.collection_id = collection.id
            
            print(f"DEBUG: Loaded {len(collections)} collections")
            return collections
    except Exception as e:
        print(f"ERROR loading {file_path}: {e}")
        return []

CS_MOCK_COLLECTIONS: List[CollectionData] = load_mock_data("collections.json")


# ==============================================================
# 🚀 FastAPI App Setup
# ==============================================================

app = FastAPI(title="Knowledge Galaxy ML API")

# Standard CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================
# ⚙️ Utility Functions
# ==============================================================

def ensure_embeddings(nodes: List[NodeData]):
    """Generate embeddings for nodes that lack them."""
    texts = [f"{n.title}. {n.summary}" for n in nodes if not n.embedding]
    if not texts:
        return
    vectors = model.encode(texts, normalize_embeddings=True).tolist()
    j = 0
    for n in nodes:
        if not n.embedding:
            n.embedding = vectors[j]
            j += 1

def get_collection_by_id(collection_id: int) -> CollectionData:
    """Helper to retrieve a collection or raise 404."""
    # NOTE: Returns a reference to the mutable global object for CRUD operations.
    collection = next((c for c in CS_MOCK_COLLECTIONS if c.id == collection_id), None)
    if not collection:
        raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")
    return collection

def update_collection_in_db(updated_collection: CollectionData):
    """Replaces the existing collection in the mock DB with the updated one."""
    global CS_MOCK_COLLECTIONS
    
    # Find and replace the collection by ID
    for i, col in enumerate(CS_MOCK_COLLECTIONS):
        if col.id == updated_collection.id:
            CS_MOCK_COLLECTIONS[i] = updated_collection
            return
    
    # If not found, append it (shouldn't happen in standard flow)
    CS_MOCK_COLLECTIONS.append(updated_collection)
    
def calculate_pagerank_names(clusters: List[ClusterData]):
    """
    Calculates PageRank for nodes within each cluster (based on similar_to links)
    and uses the title of the most central node to name the cluster.
    """
    for cluster in clusters:
        # Skip outliers and empty clusters
        if cluster.name == "Outliers" or not cluster.nodes:
            continue
        
        # 1. Build the graph for this cluster
        G = nx.DiGraph()
        node_map = {node.id: node for node in cluster.nodes}
        
        for source_node in cluster.nodes:
            # Check only similar_to links that point to other nodes within the same cluster
            for target_id in source_node.similar_to:
                if target_id in node_map:
                    # PageRank calculation uses undirected links for simplicity here,
                    # but nx.pagerank works fine with DiGraph.
                    G.add_edge(source_node.id, target_id)

        if not G.nodes or not G.edges:
            # Cannot calculate PR if there are no nodes/edges
            continue

        # 2. Calculate PageRank
        try:
            # Use a high dampening factor (alpha=0.85 is standard)
            pr = nx.pagerank(G, alpha=0.85) 
        except Exception:
             # Skip if calculation fails (e.g., disconnected graph components)
             continue

        # 3. Find the node with the highest PageRank score
        if pr:
            # Find the ID corresponding to the max PageRank value
            most_important_node_id = max(pr, key=pr.get) 
            central_node = node_map.get(most_important_node_id)
            
            if central_node:
                # Use the title of the most central node to name the cluster
                cluster.name = central_node.title

    return clusters


# ==============================================================
# 🧭 Get Assigned Cluster ID (Internal Function)
# ==============================================================

def get_assigned_cluster_id(collection: CollectionData, node: NodeData) -> Optional[int]:
    """Assigns new node to the most suitable cluster using NearestCentroid, returns ID."""
    
    X, y = [], []
    for cl in collection.clusters:
        # Skip empty or outlier clusters for centroid calculation stability
        if cl.nodes and cl.id != -1: 
            for n in cl.nodes:
                if n.embedding:
                    X.append(n.embedding)
                    y.append(cl.id)

    if len(X) < 2 or not node.embedding:
        # Insufficient data to train model or missing node embedding
        return None

    X = np.array(X)
    y = np.array(y)

    # Use NearestCentroid for fast assignment to the closest cluster center
    knn = NearestCentroid()
    knn.fit(X, y)
    
    # Predict the cluster ID
    pred_cluster = knn.predict([node.embedding])[0]
    return int(pred_cluster)


# ==============================================================
# 📡 API Routes (Public)
# ==============================================================

@app.get("/api")
async def root():
    return {"message": "Knowledge Galaxy ML API running"}


@app.get("/api/collections", response_model=List[CollectionData])
async def get_collections():
    return CS_MOCK_COLLECTIONS


# ==============================================================
# 🧠 AI/ML Endpoints
# ==============================================================

@app.post("/api/ai/recluster/{collection_id}")
async def recluster(collection_id: int):
    """
    Perform semantic reclustering using HDBSCAN + UMAP + soft reassignment 
    to minimize outliers and improve cluster cohesion.
    """

    # 1️⃣ Fetch the collection
    original_collection = get_collection_by_id(collection_id)
    working_collection = original_collection.model_copy(deep=True)

    all_nodes = [n for cl in working_collection.clusters for n in cl.nodes]
    ensure_embeddings(all_nodes)
    embeddings = np.array([n.embedding for n in all_nodes if n.embedding])

    if len(embeddings) < 10:
        return {"message": "Not enough data to recluster"}

    # 2️⃣ Dimensionality reduction (UMAP helps tighten density structure)
    reducer = umap.UMAP(
        n_neighbors=15,
        n_components=8,
        metric="cosine",
        random_state=42,
    )
    X = reducer.fit_transform(embeddings)

    # 3️⃣ Run HDBSCAN (tuned for fewer outliers)
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=2,#max(1, int(np.sqrt(len(X)))),
        min_samples=None,  # auto
        metric="euclidean",
        cluster_selection_epsilon=0.05,  # merge nearby clusters
        cluster_selection_method="eom",
        prediction_data=True,
    )
    labels = clusterer.fit_predict(X)
    probs = clusterer.probabilities_

    # 4️⃣ Soft reassignment: use approximate_predict for low-confidence outliers
    outlier_idx = np.where(labels == -1)[0]
    if len(outlier_idx) > 0:
        pred_labels, strengths = prediction.approximate_predict(clusterer, X[outlier_idx])
        for idx, new_label, strength in zip(outlier_idx, pred_labels, strengths):
            if new_label != -1 and strength > 0.6:
                labels[idx] = int(new_label)

    # 5️⃣ Fallback reassignment using NearestCentroid for remaining outliers
    remaining_outliers = np.where(labels == -1)[0]
    if len(remaining_outliers) > 0 and np.any(labels != -1):
        clf = NearestCentroid()
        clf.fit(X[labels != -1], labels[labels != -1])
        new_assignments = clf.predict(X[remaining_outliers])
        for i, idx in enumerate(remaining_outliers):
            labels[idx] = int(new_assignments[i])

    # 6️⃣ Rebuild clusters
    new_clusters_map: Dict[int, List[NodeData]] = {}
    for node, label in zip(all_nodes, labels):
        node.similar_to = []
        new_clusters_map.setdefault(label, []).append(node)

    # 7️⃣ Build ClusterData list
    new_cluster_list: List[ClusterData] = []
    for idx, (label, nodes) in enumerate(new_clusters_map.items()):
        name = "Outliers" if label == -1 else f"Galaxy {idx + 1}"
        new_cluster_list.append(ClusterData(id=idx, name=name, nodes=nodes, cx=None, cy=None))

    # 8️⃣ Compute similarity links + PageRank-based naming
    sim = cosine_similarity(embeddings)
    for i, node in enumerate(all_nodes):
        similar_indices = np.argsort(sim[i])[::-1][1:4]
        node.similar_to = [all_nodes[j].id for j in similar_indices if sim[i][j] > 0.5 and i != j]
    new_cluster_list = calculate_pagerank_names(new_cluster_list)

    # 9️⃣ Return updated collection
    new_collection = CollectionData(
        id=original_collection.id,
        name=f"Reclustered: {original_collection.name}",
        clusters=new_cluster_list
    )
    return new_collection.model_dump()


@app.post("/api/ai/query/{collection_id}", response_model=List[QueryResult])
async def semantic_query(collection_id: int, query: Dict[str, str], top_n: int = 5):
    """
    NEW ENDPOINT: Performs a semantic search against all nodes in a collection
    and returns the top N most similar nodes based on embedding similarity.
    """
    query_text = query.get("text")
    if not query_text:
        raise HTTPException(status_code=400, detail="Missing 'text' field in query body.")

    collection = get_collection_by_id(collection_id)

    # 1. Get all nodes and their embeddings
    # Filter for nodes that actually have an embedding
    all_nodes = [n for cl in collection.clusters for n in cl.nodes if n.embedding]
    if len(all_nodes) < 1 or not all_nodes[0].embedding:
        raise HTTPException(status_code=404, detail="No nodes with embeddings found for search.")

    # 2. Embed the query
    query_embedding = model.encode([query_text], normalize_embeddings=True)
    
    # 3. Create matrix of node embeddings
    node_embeddings = np.array([n.embedding for n in all_nodes])
    
    # 4. Calculate cosine similarity
    similarities = cosine_similarity(query_embedding, node_embeddings)[0]
    
    # 5. Get top N indices
    top_indices = np.argsort(similarities)[::-1][:top_n]
    
    # 6. Build the result list
    results = []
    for i in top_indices:
        results.append(QueryResult(
            node=all_nodes[i],
            similarity_score=float(similarities[i])
        ))
        
    return results


# ==============================================================
# 🧩 Functional API Endpoints (CRUD)
# ==============================================================

@app.post("/api/nodes", response_model=NodeData)
async def add_node(data: Dict[str, Any]):
    """Adds a new node to the collection and assigns it to a cluster, or creates a new one."""
    collection_id = data.get("collection_id")
    # Get a mutable reference to the collection
    collection = get_collection_by_id(collection_id) 

    # 1. Create NodeData and generate embedding
    new_node = NodeData(
        id=str(np.random.randint(100000, 999999)), 
        title=data.get("title", "New Star"),
        summary=data.get("summary", "A new star added by the user."),
        collection_id=collection_id
    )
    # Initialize coordinates if not provided (optional, but good for new nodes)
    new_node.x = data.get("x", 0.0)
    new_node.y = data.get("y", 0.0)
    
    ensure_embeddings([new_node])

    # 2. Assign to Cluster using internal utility
    assigned_cluster_id = get_assigned_cluster_id(collection, new_node)
    
    # 3. Find cluster reference
    # Note: Clusters with id -1 (outliers) might not be present if the user hasn't reclustered yet.
    assigned_cluster = next((c for c in collection.clusters if c.id == assigned_cluster_id), None)
    
    if assigned_cluster:
        # Case 1: Successfully assigned to an existing cluster
        assigned_cluster.nodes.append(new_node)
    else:
        # Case 2: New cluster fallback (default to creating a new cluster)
        # Find the max cluster ID to assign a new unique ID
        max_id = max([c.id for c in collection.clusters]) if collection.clusters else 0
        # Use a large ID to avoid collision with temporary HDBSCAN IDs if clustering is next
        new_cluster_id = max_id + 1 
        
        new_cluster = ClusterData(
            id=new_cluster_id,
            name=f"User Cluster {new_cluster_id}",
            nodes=[new_node]
        )
        collection.clusters.append(new_cluster)

    # 4. Save the modified collection back to the mock DB (updates global list)
    update_collection_in_db(collection)
    
    return new_node


@app.delete("/api/collections/{collection_id}/nodes/{node_id}")
async def delete_node(collection_id: int, node_id: str):
    """Deletes a node only from the specified collection."""
    
    # Get a mutable reference to the collection
    collection = get_collection_by_id(collection_id)
    node_found = False
    
    # Iterate only through clusters in the target collection
    for cluster in collection.clusters:
        initial_count = len(cluster.nodes)
        # Filter the node out of the list
        cluster.nodes = [n for n in cluster.nodes if n.id != node_id]
        if len(cluster.nodes) < initial_count:
            node_found = True
            break # Node deleted, stop searching

    if not node_found:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found in Collection {collection_id}.")
        
    # Save the modified collection back to the mock DB
    update_collection_in_db(collection)
        
    return {"message": f"Node {node_id} deleted successfully from Collection {collection_id}"}


@app.post("/api/clusters/merge")
async def merge_clusters(data: Dict[str, Any]):
    """Merges two clusters (cluster2 into cluster1) and deletes cluster2."""
    collection_id = data.get("collection_id")
    cluster1_id = data.get("cluster1_id")
    cluster2_id = data.get("cluster2_id")

    if not all([collection_id, cluster1_id, cluster2_id]):
        raise HTTPException(status_code=400, detail="Missing required IDs (collection_id, cluster1_id, cluster2_id)")

    # Get a mutable reference to the collection
    collection = get_collection_by_id(collection_id)
    
    try:
        cluster1_id = int(cluster1_id)
        cluster2_id = int(cluster2_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Cluster IDs must be integers")


    cluster1 = next((c for c in collection.clusters if c.id == cluster1_id), None)
    cluster2 = next((c for c in collection.clusters if c.id == cluster2_id), None)

    if not cluster1 or not cluster2:
        raise HTTPException(status_code=404, detail="One or both clusters not found")
        
    if cluster1_id == cluster2_id:
        raise HTTPException(status_code=400, detail="Cannot merge a cluster with itself.")


    # 1. Move all nodes from cluster2 to cluster1
    cluster1.nodes.extend(cluster2.nodes)
    
    # 2. Update cluster1's name (optional)
    cluster1.name = f"Merged: {cluster1.name} & {cluster2.name}"

    # 3. Remove cluster2 from the collection
    collection.clusters = [c for c in collection.clusters if c.id != cluster2_id]
    
    # Reassign new unique IDs to the remaining clusters to keep IDs clean after merge/delete
    # This ensures cluster IDs remain sequential and gap-free
    for i, cluster in enumerate(collection.clusters):
        cluster.id = i
        
    # Save the modified collection back to the mock DB
    update_collection_in_db(collection)
        
    return {"message": f"Clusters merged successfully. New cluster count: {len(collection.clusters)}"}


@app.post("/api/clusters/rename")
async def rename_cluster(data: Dict[str, Any]):
    """Allows manual renaming of a cluster and persists the change to the DB."""
    collection_id = data.get("collection_id")
    cluster_id = data.get("cluster_id")
    new_name = data.get("new_name")

    if not all([collection_id, cluster_id, new_name]):
        raise HTTPException(status_code=400, detail="Missing required fields: collection_id, cluster_id, or new_name")

    # Get a mutable reference to the collection
    collection = get_collection_by_id(collection_id)

    try:
        cluster_id = int(cluster_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Cluster ID must be an integer")
    
    # Find the cluster
    target_cluster = next((c for c in collection.clusters if c.id == cluster_id), None)

    if not target_cluster:
        raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} not found in Collection {collection_id}")

    # Rename the cluster
    target_cluster.name = new_name

    # Save the modified collection back to the mock DB
    update_collection_in_db(collection)

    return {"message": f"Cluster {cluster_id} in Collection {collection_id} successfully renamed to '{new_name}'"}


@app.post("/api/collections/{collection_id}/save")
async def save_layout(collection_id: int, data: List[NodeData]):
    """Saves the node positions (x, y) after dragging."""
    collection = get_collection_by_id(collection_id)
    
    # Create a map for fast lookup of new positions
    node_updates = {n.id: (n.x, n.y) for n in data}

    # Iterate through all clusters and nodes in the collection and update coordinates
    for cluster in collection.clusters:
        for node in cluster.nodes:
            if node.id in node_updates:
                node.x, node.y = node_updates[node.id]
                
    # Save the modified collection back to the mock DB
    update_collection_in_db(collection)
    
    return {"message": f"Layout for collection {collection_id} saved successfully. {len(data)} nodes updated."}
