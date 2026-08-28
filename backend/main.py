from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
import numpy as np
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestCentroid
from sentence_transformers import SentenceTransformer
import networkx as nx 
from umap import UMAP
from hdbscan import prediction
import umap
import httpx
import asyncio
from keybert import KeyBERT 

# NEW IMPORTS FOR MONGODB
import motor.motor_asyncio
from bson.json_util import dumps, loads

# ==============================================================
# 🧩 Data Models
# ==============================================================

class NodeData(BaseModel):
    id: str = Field(default_factory=lambda: str(np.random.randint(100000, 999999))) # Generate ID if missing
    title: str
    summary: str
    similar_to: List[str] = []
    embedding: List[float] = [] 
    x: Optional[float] = None 
    y: Optional[float] = None 
    collection_id: Optional[int] = None 

class ClusterData(BaseModel):
    id: int
    name: str
    cx: Optional[float] = None
    cy: Optional[float] = None
    nodes: List[NodeData]

class CollectionData(BaseModel):
    # MongoDB documents use a string ID, but collection ID is kept as int for internal logic
    id: int
    name: str
    clusters: List[ClusterData]
    # For MongoDB: field alias for internal ID
    mongo_id: Optional[Any] = Field(None, alias='_id')


class QueryResult(BaseModel): 
    node: NodeData
    similarity_score: float


# ==============================================================
# 🧠 ML Setup
# ==============================================================


print("Loading embedding model... (this may take a few seconds)")
# Note: You need the 'sentence-transformers' library installed for this to work
#model= SentenceTransformer('all-mpmpnet-base-v2')
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("Model loaded ✅")
# Reuse your sentence-transformer model
kw_model = KeyBERT(model)
print("Keyword extraction model loaded ✅")

# ==============================================================
# 🗄 MongoDB Configuration (Hardcoded)
# ==============================================================

# Hardcoded MongoDB URI and details as requested.
MONGO_URI = "mongodb+srv://muhammadhasan4269_db_user:OvxPkpS8AiZXGEWa@minorcluster.cond7qq.mongodb.net/"
DB_NAME = "infinite_desk_demo"
COLLECTION_NAME = "collections"

# Global references for DB connection
mongo_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
mongo_db = None
mongo_collections = None


# ==============================================================
# 🌐 GEMINI API CONFIGURATION & HELPER
# ==============================================================

# The API key is set as an empty string as per environment requirements.
apiKey = "AIzaSyCFnZY2euplsaO2yFyNJV5TZh60CEcwyKo"
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={apiKey}"

async def call_gemini_api(prompt: str) -> str:
    """
    Performs the asynchronous POST request to the Gemini generateContent endpoint.
    """
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        # Using a system instruction to guide the model's persona and rules
        "systemInstruction": {
            "parts": [{"text": "You are a professional knowledge system assistant. Answer precisely and truthfully based only on the provided context."}]
        }
    }

    try:
        # Use httpx for asynchronous HTTP requests in a FastAPI application
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                API_URL,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload)
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Safely extract the generated text
            llm_answer = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Error: Could not extract text from AI response.')
            
            return llm_answer
    except httpx.HTTPError as e:
        print(f"HTTP error calling Gemini API: {e}")
        return f"Error: Failed to connect to AI model ({GEMINI_MODEL}). Check network or API key. Detail: {e}"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return f"Error: An unexpected error occurred during AI generation: {e}"
    

async def rewrite_query_with_llm(query: str) -> str:
    """
    Uses the LLM to rewrite a complex query into an optimal search string.
    This step improves the quality of the vector search.
    """
    REWRITE_SYSTEM_PROMPT = (
        "You are a sophisticated query rewriter. Your goal is to transform "
        "a user's natural language, potentially conversational or ambiguous, "
        "question into the most effective, concise, and specific standalone "
        "search query possible. Output ONLY the rewritten query text, with no preamble or explanation."
    )
    
    prompt = f"Rewrite the following query for optimal semantic search: '{query}'"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {
            "parts": [{"text": REWRITE_SYSTEM_PROMPT}]
        }
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                API_URL,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload)
            )
            response.raise_for_status()
            result = response.json()
            
            # Safely extract and clean the rewritten query
            rewritten_query = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', query).strip()
            
            # Fallback to original query if LLM response is empty or unexpected
            return rewritten_query if rewritten_query else query

    except Exception as e:
        # If rewriting fails (network error, etc.), fall back to the original query
        print(f"Query rewriting failed, falling back to original query: {e}")
        return query
    


# ==============================================================
# 🗂 MongoDB Data Management (Replaced Mock Data Logic)
# ==============================================================

# The original load_mock_data and CS_MOCK_COLLECTIONS variables were removed.

def get_collection_id_from_db_doc(doc: Dict[str, Any]) -> CollectionData:
    """Converts a MongoDB document to a CollectionData Pydantic model."""
    if not doc:
        return None
    # Use loads/dumps to safely handle BSON types (like ObjectId)
    json_data = loads(dumps(doc))
    # Rename _id to mongo_id for Pydantic mapping
    if '_id' in json_data:
        json_data['mongo_id'] = json_data.pop('_id')
    
    return CollectionData(**json_data)


async def get_collection_by_id(collection_id: int) -> CollectionData:
    """Helper to retrieve a collection from MongoDB or raise 404."""
    # FIX: Check for None instead of using boolean context
    global mongo_collections
    if mongo_collections is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    # Search by the 'id' field, which is the unique collection identifier.
    doc = await mongo_collections.find_one({"id": collection_id})
    if not doc:
        raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")
        
    return get_collection_id_from_db_doc(doc)


async def get_all_collections() -> List[CollectionData]:
    """Helper to retrieve all collections from MongoDB."""
    # FIX: Check for None instead of using boolean context
    global mongo_collections
    if mongo_collections is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    cursor = mongo_collections.find({})
    collections = []
    async for doc in cursor:
        collections.append(get_collection_id_from_db_doc(doc))
    return collections


async def update_collection_in_db(updated_collection: CollectionData):
    """Replaces the existing collection in MongoDB with the updated one."""
    # FIX: Check for None instead of using boolean context
    global mongo_collections
    if mongo_collections is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    # Use by_alias=True to correctly map the mongo_id field back to '_id' 
    # and exclude the optional 'mongo_id' if it's None (for new documents)
    update_data = updated_collection.model_dump(by_alias=True, exclude_none=True)
    
    result = await mongo_collections.replace_one(
        {"id": updated_collection.id},
        update_data,
        upsert=True
    )
    
    if result.matched_count == 0 and result.upserted_id is None:
         print(f"WARNING: Collection ID {updated_collection.id} failed to update/upsert.")



# ==============================================================
# 🚀 FastAPI App Setup
# ==============================================================

app = FastAPI(title="Knowledge Galaxy ML API")

# Setup database connection on startup
@app.on_event("startup")
async def startup_db_client():
    global mongo_client, mongo_db, mongo_collections
    try:
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        mongo_db = mongo_client[DB_NAME]
        mongo_collections = mongo_db[COLLECTION_NAME]
        print(f"MongoDB connection initialized for DB: {DB_NAME}")
            
    except Exception as e:
        print(f"FATAL: Could not connect to MongoDB at {MONGO_URI}. Error: {e}")

# Close database connection on shutdown
@app.on_event("shutdown")
async def shutdown_db_client():
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("MongoDB connection closed.")


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

EMBEDDING_CACHE = {}

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


def calculate_pagerank_names(clusters: List[ClusterData]) -> List[ClusterData]:
    """
    Assigns a human-readable name to each cluster using:
    1. PageRank of nodes within the cluster (based on similar_to links)
    2. Keyword extraction from top node or entire cluster text
    """
    for cluster in clusters:
        # Skip empty clusters or outliers
        if not cluster.nodes or cluster.name == "Outliers":
            continue

        # 1️⃣ Build graph for PageRank
        G = nx.DiGraph()
        node_map = {node.id: node for node in cluster.nodes}
        for source_node in cluster.nodes:
            for target_id in source_node.similar_to:
                if target_id in node_map:
                    G.add_edge(source_node.id, target_id)

        # 2️⃣ Compute PageRank (fallback if graph is empty)
        central_node = None
        if G.nodes and G.edges:
            try:
                pr = nx.pagerank(G, alpha=0.85)
                top_node_id = max(pr, key=pr.get)
                central_node = node_map.get(top_node_id)
            except Exception:
                central_node = cluster.nodes[0]
        else:
            central_node = cluster.nodes[0]

        # 3️⃣ Extract keywords from central node or full cluster
        if central_node:
            # Use central node text + cluster text as fallback
            corpus = [n.title + ". " + n.summary for n in cluster.nodes]
            cluster_text = " ".join(corpus)
            try:
                keywords = kw_model.extract_keywords(cluster_text, top_n=1, stop_words='english')
                keyword_name = keywords[0][0] if keywords else central_node.title
            except Exception:
                keyword_name = central_node.title
        else:
            keyword_name = "Unnamed Cluster"

        # 4️⃣ Assign cluster name
        cluster.name = keyword_name

    return clusters
    

# ==============================================================
# 🧭 Get Assigned Cluster ID (Internal Function)
# ==============================================================

async def get_assigned_cluster_id(collection: CollectionData, node: NodeData) -> Optional[int]:
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
    print(f"DEBUG: Node '{node.title}' assigned to cluster {pred_cluster}")
    return int(pred_cluster)


# ==============================================================
# 📡 API Routes (Public)
# ==============================================================
@app.get("/api")
async def root():
    return {"message": "Knowledge Galaxy ML API running with MongoDB backend"}


@app.get("/api/collections", response_model=List[CollectionData])
async def get_collections():
    # Use the new async data retrieval function
    return await get_all_collections()


# ==============================================================
# 🧠 AI/ML Endpoints
# ==============================================================

@app.post("/api/ai/recluster/{collection_id}")
async def recluster(collection_id: int):
    """
    Perform semantic reclustering using HDBSCAN + UMAP + soft reassignment 
    to minimize outliers and improve cluster cohesion.
    """

    # 1️⃣ Fetch the collection (NOW ASYNC)
    original_collection = await get_collection_by_id(collection_id)
    working_collection = original_collection.model_copy(deep=True)

    all_nodes = [n for cl in working_collection.clusters for n in cl.nodes]
    ensure_embeddings(all_nodes)
    embeddings = np.array([n.embedding for n in all_nodes if n.embedding])

    if len(embeddings) < 10:
        return {"message": "Not enough data to recluster"}

     # 2️⃣ Dimensionality reduction (UMAP helps tighten density structure)
    reducer = umap.UMAP(
        n_neighbors=12,
        n_components=8,
        metric="cosine",
        random_state=42,
    )

    X = reducer.fit_transform(embeddings)

    # 3️⃣ Run HDBSCAN (tuned for fewer outliers)
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=3,#max(2, int(np.sqrt(len(X)))),
        min_samples=1,  # auto
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
        clusters=new_cluster_list,
        mongo_id=original_collection.mongo_id # Preserve MongoDB ID
    )
    # 🔟 Save the new collection back to the DB (NOW ASYNC)
    await update_collection_in_db(new_collection)
    return new_collection.model_dump(by_alias=True)


@app.post("/api/ai/query/{collection_id}", response_model=List[QueryResult])
async def semantic_query(collection_id: int, query: Dict[str, str], top_n: int = 5):
    """
    NEW ENDPOINT: Performs a semantic search against all nodes in a collection
    and returns the top N most similar nodes based on embedding similarity.
    """
    query_text = query.get("text")
    if not query_text:
        raise HTTPException(status_code=400, detail="Missing 'text' field in query body.")

    # Fetch collection (NOW ASYNC)
    collection = await get_collection_by_id(collection_id)

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

@app.post("/api/rag/query/{collection_id}")
async def rag_query(collection_id: int, data: Dict[str, Any]):
    """
    RAG-based query endpoint (Gemini compatible).
    1. Embed the query
    2. Retrieve top similar nodes (vector search)
    3. Use them as context for LLM response
    """
    query_text: str = data.get("query", "")
    top_n: int = data.get("k", 5)

    if not query_text:
        raise HTTPException(status_code=400, detail="Missing 'query' field in body.")
    
    # 1. NEW: Rewrite the user's query for better search
    rewritten_query = await rewrite_query_with_llm(query_text)
    print(f"DEBUG: Original Query: '{query_text}' -> Rewritten Query: '{rewritten_query}'")

    # Fetch collection (NOW ASYNC)
    collection = await get_collection_by_id(collection_id)

    # 1. Get all nodes and their embeddings
    # Filter for nodes that actually have an embedding
    all_nodes = [n for cl in collection.clusters for n in cl.nodes if n.embedding]
    if len(all_nodes) < 1 or not all_nodes[0].embedding:
        raise HTTPException(status_code=404, detail="No nodes with embeddings found for RAG.")

    # 2. Embed the query
    query_embedding = model.encode([query_text], normalize_embeddings=True)
    
    # 3. Vector Search (Retrieve top-n nodes)
    node_embeddings = np.array([n.embedding for n in all_nodes])
    similarities = cosine_similarity(query_embedding, node_embeddings)[0]
    top_indices = np.argsort(similarities)[::-1][:top_n]
    top_nodes = [all_nodes[i] for i in top_indices]
    
    # 4. Construct context
    # Format the retrieved nodes into a readable context block for the LLM
    context = "\n\n---\n\n".join([f"**{n.title}**\nSummary: {n.summary}" for n in top_nodes])
    
    # 5. Query the LLM (Gemini API)
    prompt = f'''
                You are an intelligent assistant for a knowledge system.
                Answer the following query based **only** on the provided context. If the context does not contain the answer, state clearly that you cannot answer based on the provided information.
                <CONTEXT>
                {context}
                </CONTEXT>
                <QUERY>
                {query_text}
                </QUERY>
                <ANSWER>
                '''
    
    llm_answer = await call_gemini_api(prompt)

    # 6. Return the RAG result
    return { "response": llm_answer, "context": context }




# ==============================================================
# 🧩 Functional API Endpoints (CRUD)
# ==============================================================

@app.post("/api/nodes", response_model=NodeData)
async def add_node(data: Dict[str, Any]):
    """Adds a new node to the collection and assigns it to a cluster, or creates a new one."""
    collection_id = data.get("collection_id")
    # Get a mutable reference to the collection (NOW ASYNC)
    collection = await get_collection_by_id(collection_id) 

    # 1. Create NodeData and generate embedding
    new_node = NodeData(
        # ID is generated by Pydantic default_factory now
        title=data.get("title", "New Star"),
        summary=data.get("summary", "A new star added by the user."),
        collection_id=collection_id
    )
    # Initialize coordinates if not provided (optional, but good for new nodes)
    new_node.x = data.get("x", 0.0)
    new_node.y = data.get("y", 0.0)
    
    ensure_embeddings([new_node])

    # 2. Assign to Cluster using internal utility (NOW ASYNC)
    assigned_cluster_id = await get_assigned_cluster_id(collection, new_node)
    print(f"DEBUG: New node '{new_node.title}' assigned to cluster ID {assigned_cluster_id}")
    
    # 3. Find cluster reference
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

    # 4. Save the modified collection back to the DB (NOW ASYNC)
    await update_collection_in_db(collection)
    
    return new_node


@app.delete("/api/collections/{collection_id}/nodes/{node_id}")
async def delete_node(collection_id: int, node_id: str):
    """Deletes a node only from the specified collection."""
    
    # Get a mutable reference to the collection (NOW ASYNC)
    collection = await get_collection_by_id(collection_id)
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
        
    # Save the modified collection back to the DB (NOW ASYNC)
    await update_collection_in_db(collection)
        
    return {"message": f"Node {node_id} deleted successfully from Collection {collection_id}"}


@app.post("/api/clusters/merge")
async def merge_clusters(data: Dict[str, Any]):
    """Merges two clusters (cluster2 into cluster1) and deletes cluster2."""
    collection_id = data.get("collection_id")
    cluster1_id = data.get("cluster1_id")
    cluster2_id = data.get("cluster2_id")

    if not all([collection_id, cluster1_id, cluster2_id]):
        raise HTTPException(status_code=400, detail="Missing required IDs (collection_id, cluster1_id, cluster2_id)")

    # Get a mutable reference to the collection (NOW ASYNC)
    collection = await get_collection_by_id(collection_id)
    
    try:
        # FastAPI path parameters are usually strings, but the body might be int/str.
        # Ensure conversion from body data, but for safety, ensure type consistency.
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
        
    # Save the modified collection back to the DB (NOW ASYNC)
    await update_collection_in_db(collection)
        
    return {"message": f"Clusters merged successfully. New cluster count: {len(collection.clusters)}"}


@app.post("/api/clusters/rename")
async def rename_cluster(data: Dict[str, Any]):
    """Allows manual renaming of a cluster and persists the change to the DB."""
    collection_id = data.get("collection_id")
    cluster_id = data.get("cluster_id")
    new_name = data.get("new_name")

    if not all([collection_id, cluster_id, new_name]):
        raise HTTPException(status_code=400, detail="Missing required fields: collection_id, cluster_id, or new_name")

    # Get a mutable reference to the collection (NOW ASYNC)
    collection = await get_collection_by_id(collection_id)

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

    # Save the modified collection back to the DB (NOW ASYNC)
    await update_collection_in_db(collection)

    return {"message": f"Cluster {cluster_id} in Collection {collection_id} successfully renamed to '{new_name}'"}


@app.post("/api/collections/{collection_id}/save")
async def save_layout(collection_id: int, data: List[NodeData]):
    """Saves the node positions (x, y) after dragging."""
    # Fetch collection (NOW ASYNC)
    collection = await get_collection_by_id(collection_id)
    
    # Create a map for fast lookup of new positions
    node_updates = {n.id: (n.x, n.y) for n in data}

    # Iterate through all clusters and nodes in the collection and update coordinates
    for cluster in collection.clusters:
        for node in cluster.nodes:
            if node.id in node_updates:
                node.x, node.y = node_updates[node.id]
                
    # Save the modified collection back to the DB (NOW ASYNC)
    await update_collection_in_db(collection)
    
    return {"message": f"Layout for collection {collection_id} saved successfully. {len(data)} nodes updated."}
