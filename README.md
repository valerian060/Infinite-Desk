# Infinite Desk 🌌

**A Semantic Knowledge Platform with Interactive D3.js Knowledge Graph Visualization**

Infinite Desk is a full-stack web application that helps you organize, visualize, and discover knowledge using semantic embeddings (Sentence Transformers), UMAP dimensionality reduction, and HDBSCAN clustering. Explore your notes as an interactive, navigable knowledge universe with AI-powered search and retrieval.

**[Live Demo](https://infinitedesk.onrender.com)** • [GitHub](https://github.com/valerian060/Infinite-Desk) • [Demo Branch](https://github.com/valerian060/Infinite-Desk/tree/demo) • [Test Branch (Latest)](https://github.com/valerian060/Infinite-Desk/tree/test)

---

## ✨ Features

### 🎯 Core Knowledge Management
- **Interactive Knowledge Graph** — Visualize all your notes as nodes in a D3.js force-directed graph
- **Semantic Clustering** — Automatic topic discovery using HDBSCAN clustering on dense embeddings
- **Smart Search** — Find related notes based on semantic similarity (cosine distance)
- **Drag-to-Merge** — Merge related clusters by dragging nodes to the merge zone
- **Drag-to-Delete** — Remove nodes by dragging them to the delete zone
- **Zoom & Pan** — Explore large knowledge bases with smooth D3 zoom/pan controls

### 🧠 ML-Powered Intelligence
- **Dense Embeddings** — Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`) encode all notes into 384-D vectors
- **Dimensionality Reduction** — UMAP projects embeddings to optimized lower dimensions for fast clustering
- **HDBSCAN Clustering** — Density-based clustering discovers natural topic groupings with minimal outliers
- **Soft Reassignment** — Outliers intelligently reassigned to nearest clusters using `approximate_predict` and `NearestCentroid`
- **KeyBERT Naming** — Cluster names automatically extracted from most relevant keywords in the cluster text
- **Semantic Query** — Search entire knowledge base by meaning, not just keywords

### 🤖 RAG (Retrieval-Augmented Generation)
- **LLM-Powered Answers** — Integrates with Gemini API for intelligent responses
- **Context Retrieval** — Vector search retrieves top-N most relevant nodes for context
- **Query Rewriting** — LLM rewrites user queries for optimal semantic search
- **Grounded Responses** — Answers based only on retrieved knowledge base content

### 💾 Production-Ready Backend
- **MongoDB Integration** — Fully async persistent storage with Motor
- **Async/Await Architecture** — Non-blocking I/O throughout the stack
- **Scalable Design** — Ready for production deployment
- **API-First** — Clean REST API for all operations

### 📊 Collection & Layout Management
- **Multiple Collections** — Organize multiple independent knowledge bases
- **Persistent Layout** — Save node positions after manual arrangement
- **Session Persistence** — Data persisted in MongoDB
- **One-Click Jump** — Navigate directly to context within the knowledge graph

---

## 🏗️ Architecture

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, D3.js v7, JavaScript (ES6+), Tailwind CSS |
| **Backend** | FastAPI, Python, Pydantic, Async/Await |
| **Database** | MongoDB (Motor async driver) |
| **ML/NLP** | Sentence Transformers, UMAP, HDBSCAN, scikit-learn, NetworkX, KeyBERT |
| **LLM Integration** | Gemini API, async HTTP (httpx) |
| **Visualization** | D3.js force simulation, SVG rendering |
| **Hosting** | Hugging Face Spaces (backend), Render/GitHub Pages (frontend) |

### System Design

```
┌─────────────────────────────────────────────┐
│      Frontend (D3.js + JavaScript)          │
│  - Interactive Graph Visualization          │
│  - Auth UI (Login/Signup)                   │
│  - Collection Management                    │
└──────────────┬──────────────────────────────┘
               │ HTTP/REST API (CORS enabled)
┌──────────────▼──────────────────────────────┐
│  FastAPI Backend (Hosted on Hugging Face)   │
│  - Fully Async/Await Architecture           │
│  - Collections & CRUD API                   │
│  - Semantic Embeddings (Sentence Trans.)    │
│  - UMAP Dimensionality Reduction            │
│  - HDBSCAN Clustering with Outlier Handling │
│  - Semantic Query Endpoint                  │
│  - RAG Query with Gemini Integration        │
│  - KeyBERT-based Auto Naming                │
└──────────────┬──────────────────────────────┘
               │ Async Read/Write + ML Compute
┌──────────────▼──────────────────────────────┐
│    MongoDB Atlas                            │
│  - Collections & Persistent Storage         │
│  - Async Operations via Motor               │
│  - Scalable Cloud Database                  │
└─────────────────────────────────────────────┘
```

### ML Pipeline Flow

```
Raw Notes (Text)
    ↓
Sentence Transformers (Encode to 384-D embeddings, cached)
    ↓
UMAP (Project to 8D, n_neighbors=12 for balance)
    ↓
HDBSCAN (Find natural clusters, min_samples=1 for flexibility)
    ↓
Outlier Handling:
  ├→ approximate_predict (try to assign with confidence)
  └→ NearestCentroid (fallback to closest cluster)
    ↓
Similarity Links (Top-3 nodes per cosine similarity)
    ↓
PageRank Graph (Calculate node importance within cluster)
    ↓
KeyBERT Keyword Extraction (Extract key topics from cluster text)
    ↓
Auto Naming (Use top keyword or central node title)
    ↓
Interactive Graph Visualization (D3.js with cached positions)
```

### Data Model

**Collection** → **Cluster** → **Node**

```javascript
{
  id: 1,
  name: "My Knowledge Base",
  mongo_id: "ObjectId(...)",  // MongoDB document ID
  clusters: [
    {
      id: 0,
      name: "machine learning",           // Auto-named from KeyBERT
      cx: 400,                            // cluster center X
      cy: 300,                            // cluster center Y
      nodes: [
        {
          id: "node_1",
          title: "Neural Networks Basics",
          summary: "Introduction to neural networks...",
          embedding: [0.234, 0.567, ...], // 384-D Sentence Transformer vector
          similar_to: ["node_2", "node_5"],// Top-3 similar nodes
          x: 410,                          // Position on canvas
          y: 295,
          collection_id: 1
        },
        ...
      ]
    },
    ...
  ]
}
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip
- Modern web browser (Chrome/Firefox/Safari)
- Virtual Environment (recommended)
- Gemini API key (for RAG features)
- MongoDB Atlas account (or local MongoDB instance)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/valerian060/Infinite-Desk.git
cd Infinite-Desk
git checkout test  # Switch to latest branch with MongoDB + async
```

#### 2. Setup Backend

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pydantic numpy hdbscan sentence-transformers umap-learn scikit-learn networkx httpx motor keybert
```

#### 3. Configure MongoDB

Edit `backend/main.py` and update MongoDB connection:

```python
# Hardcoded MongoDB URI and details
MONGO_URI = "mongodb+srv://username:password@cluster.mongodb.net/"
DB_NAME = "infinite_desk_demo"
COLLECTION_NAME = "collections"
```

#### 4. Configure Gemini API

Edit `backend/main.py` and add your Gemini API key:

```python
apiKey = "your-gemini-api-key-here"
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"
```

#### 5. Run Backend Server

```bash
cd backend
python main.py
# Server runs at http://127.0.0.1:8000
# Models load automatically on startup (~10 seconds)
```

#### 6. Open Frontend

```bash
# Using Python
cd frontend
python -m http.server 8001
# Visit http://localhost:8001
```

---

## 📖 Usage Guide

### 1. **Login / Sign Up**

- Navigate to `auth.html` or `login.html`
- Demo credentials: `demo@infinitedesk.com` / `demo123`
- Create an account or use demo account to explore

### 2. **Select a Collection**

- Use the **Collection Dropdown** in the top bar
- Switch between different knowledge bases

### 3. **Explore the Graph**

- **Zoom**: Scroll to zoom in/out
- **Pan**: Click and drag to move around
- **Hover**: Hover over nodes to see tooltips
- **Click**: Select a node to highlight connections

### 4. **Semantic Search**

- Use the **Search Box** to query your knowledge base
- Type natural language queries (e.g., "machine learning algorithms")
- Results ranked by embedding similarity automatically
- Click **Recalculate Clustering** to re-run ML pipeline with updated embeddings

### 5. **AI-Powered RAG Query**

- Click **Ask AI** (available in top bar)
- Type your question in natural language
- System retrieves top-5 most relevant nodes using vector search
- Gemini LLM generates an answer based on retrieved context
- Query automatically rewritten for optimal semantic search

### 6. **Merge Clusters**

- Drag nodes to the **left merge area** (blue zone)
- Release to merge related clusters
- Useful for consolidating similar topics

### 7. **Delete Nodes**

- Drag nodes to the **right delete area** (red zone)
- Release to remove irrelevant notes

### 8. **Re-Cluster**

- Click **Recalculate Clustering** to run HDBSCAN again
- System re-encodes all notes, applies UMAP, and discovers new clusters
- Automatically reorganizes nodes based on semantic similarity
- Cluster names updated via KeyBERT + PageRank analysis

### 9. **Save Layout**

- Arrange nodes manually by dragging
- Click **Save Layout** to persist positions
- Positions saved to MongoDB for next session

---

## 📁 File Structure

```
Infinite-Desk/
├── backend/
│   ├── main.py                    # FastAPI app with full ML pipeline + MongoDB
│   ├── collections.json           # Initial mock data (optional)
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── index.html                 # Main application UI
│   ├── auth.html                  # Combined login/signup page
│   ├── login.html                 # Standalone login page
│   ├── main.js                    # D3.js graph logic + API calls
│   ├── auth.js                    # Authentication handling
│   ├── login.js                   # Login form logic
│   ├── styles.css                 # Main application styles
│   └── auth.css                   # Auth page styles
└── README.md                       # This file
```

---

## 🔌 API Endpoints

### Collections

**GET** `/api/collections`
- Returns all collections with clusters and nodes
- Response: `List[CollectionData]`
- Fetched from MongoDB

### Semantic Operations (ML-Powered)

**POST** `/api/ai/recluster/{collection_id}`
- Trigger HDBSCAN re-clustering on all notes
- Pipeline: Embeddings → UMAP → HDBSCAN → Soft Reassignment → KeyBERT Naming
- Returns: Updated collection with new clusters
- Persisted to MongoDB
- Example: `POST /api/ai/recluster/1`

**POST** `/api/ai/query/{collection_id}`
- Semantic search across all nodes in a collection
- Body: `{"text": "your query"}`
- Top-N most similar nodes ranked by cosine similarity
- Returns: `List[QueryResult]` with similarity scores

**POST** `/api/rag/query/{collection_id}`
- RAG-based query with Gemini API integration
- Body: `{"query": "your question", "k": 5}`
- Steps:
  1. Rewrite query using LLM for optimal search
  2. Retrieve top-5 most relevant nodes via vector search
  3. Generate answer using Gemini with retrieved context
- Returns: `{ "response": "AI answer", "context": "retrieved nodes" }`

### Node Management

**POST** `/api/nodes`
- Add a new node to a collection
- Auto-assigned to nearest cluster using NearestCentroid
- Auto-generates embedding via Sentence Transformers
- Body: `{ collection_id, title, summary, x, y }`
- Saved to MongoDB

**DELETE** `/api/collections/{collection_id}/nodes/{node_id}`
- Remove a node from specified collection
- Updates persisted in MongoDB
- Returns: Success message

### Cluster Operations

**POST** `/api/clusters/merge`
- Merge two clusters
- Body: `{ collection_id, cluster1_id, cluster2_id }`
- Cluster1 receives all nodes from Cluster2
- Cluster2 deleted, IDs reindexed
- Changes persisted to MongoDB

**POST** `/api/clusters/rename`
- Manually rename a cluster (overrides auto-naming)
- Body: `{ collection_id, cluster_id, new_name }`
- Persisted to MongoDB

### Layout Persistence

**POST** `/api/collections/{collection_id}/save`
- Save node positions after user drags
- Body: `List[NodeData]` with updated x, y coordinates
- Changes immediately saved to MongoDB

---

## 🎨 UI Components

### Top Bar

- **Collection Dropdown** — Switch between knowledge bases
- **Search Box** — Semantic search with ML ranking
- **Recalculate Clustering Button** — Re-run full ML pipeline
- **Save Layout Button** — Persist graph positions to MongoDB
- **Ask AI Button** — Open RAG query dialog (future)

### Side Areas

- **Left (Merge Area)** — Drag nodes here to merge clusters
- **Right (Delete Area)** — Drag nodes here to delete them
- **Visual Feedback** — Color changes indicate active zones

### Canvas

- **SVG Visualization** — D3.js force-directed graph
- **Nodes** — Represented as circles (colored by cluster)
- **Links** — White edges showing similar_to relationships
- **Cluster Labels** — Centered text for each cluster (auto-named by KeyBERT)
- **Tooltips** — Hover to see node details

---

## 🔧 Configuration

### API Base URL

Edit in `frontend/main.js`:

```javascript
const API_BASE = "http://127.0.0.1:8000";
```

For Hugging Face hosted backend, update to the Spaces URL.

### MongoDB Connection

Edit in `backend/main.py`:

```python
MONGO_URI = "mongodb+srv://username:password@cluster.mongodb.net/"
DB_NAME = "infinite_desk_demo"
COLLECTION_NAME = "collections"
```

### ML Hyperparameters

Edit in `backend/main.py`:

```python
# UMAP configuration (optimized for 8D output)
reducer = umap.UMAP(
    n_neighbors=12,       # Balance between local and global structure
    n_components=8,       # 8D for optimal HDBSCAN performance
    metric="cosine",
    random_state=42,
)

# HDBSCAN configuration (tuned for fewer outliers)
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=3,   # Minimum points per cluster
    min_samples=1,        # Flexible outlier assignment
    metric="euclidean",
    cluster_selection_epsilon=0.05,  # Merge nearby clusters
    prediction_data=True,
)
```

### Embedding Model

Edit in `backend/main.py`:

```python
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
```

Alternatives:
- `all-MiniLM-L6-v2` (faster, smaller)
- `all-mpnet-base-v2` (higher quality, larger)
- `paraphrase-multilingual-mpnet-base-v2` (multilingual, high quality)

### Gemini API Configuration

Edit in `backend/main.py`:

```python
apiKey = "your-gemini-api-key"
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"
```

---

## 🚀 Deployment

### Hugging Face Spaces (Backend)

1. Create a Hugging Face Spaces repo
2. Push `backend/` folder with `requirements.txt`
3. Configure MongoDB URI as a secret
4. Configure Gemini API key as a secret
5. Spaces will auto-deploy on push

### Render.com (Alternative Backend Hosting)

1. Push code to GitHub
2. Connect repository to Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn backend.main:app --host 0.0.0.0`
5. Add environment variables: `MONGO_URI`, `GEMINI_API_KEY`
6. Deploy!

### GitHub Pages (Frontend)

1. Place `frontend/` files in `/docs` folder
2. Enable GitHub Pages in repository settings
3. Update `API_BASE` to point to your Hugging Face/Render backend

---

## 📊 ML Pipeline Details

### 1. Embedding Generation

- **Model**: Sentence Transformers `paraphrase-multilingual-MiniLM-L12-v2`
- **Dimension**: 384-D vectors
- **Input**: `{title}. {summary}` for each note
- **Normalization**: L2 normalized for cosine similarity
- **Caching**: Embeddings cached in EMBEDDING_CACHE for performance

### 2. Dimensionality Reduction (UMAP)

- **Purpose**: Project high-dimensional embeddings to lower-dimensional space for efficient clustering
- **Parameters**: 
  - `n_neighbors=12` — Balance local and global structure
  - `n_components=8` — Optimize for HDBSCAN clustering
  - `metric="cosine"` — Respects semantic similarity

### 3. Density-Based Clustering (HDBSCAN)

- **Advantage**: Discovers arbitrary-shaped clusters, handles outliers gracefully
- **Min Cluster Size**: 3 (minimum points per cluster)
- **Min Samples**: 1 (flexible outlier assignment)
- **Outlier Handling**: Nodes labeled with -1 flag

### 4. Soft Reassignment (Outlier Recovery)

```python
# Step 1: approximate_predict — Try to assign with confidence threshold
pred_labels, strengths = prediction.approximate_predict(clusterer, X[outliers])
if strength > 0.6:  # High confidence
    assign to predicted cluster
    
# Step 2: NearestCentroid — Fallback for remaining outliers
clf.fit(X[valid_labels], valid_labels)
assign = clf.predict(X[remaining_outliers])
```

### 5. Similarity Link Computation

- **Method**: Cosine similarity between embedding vectors
- **Top-N**: Top-3 most similar nodes per node
- **Threshold**: Only links with similarity > 0.5

### 6. KeyBERT-Based Auto Naming

- **Extraction**: KeyBERT extracts top keywords from cluster corpus
- **Fallback**: Uses PageRank score (node centrality) as fallback
- **Cluster Name**: Most relevant keyword or central node title

---

## 🔄 Async Architecture Benefits

- **Non-Blocking I/O**: All MongoDB queries are async (Motor driver)
- **Better Throughput**: Multiple requests handled concurrently
- **Scalability**: Ready for production with many concurrent users
- **Error Handling**: Graceful fallbacks for network/API failures

---

## 🧪 Testing

### Test Semantic Search

```bash
curl -X POST http://127.0.0.1:8000/api/ai/query/1 \
  -H "Content-Type: application/json" \
  -d '{"text": "machine learning algorithms"}'
```

### Test RAG Query

```bash
curl -X POST http://127.0.0.1:8000/api/rag/query/1 \
  -H "Content-Type: application/json" \
  -d '{"query": "How does neural networks work?", "k": 5}'
```

### Test Reclustering

```bash
curl -X POST http://127.0.0.1:8000/api/ai/recluster/1
```

### Test MongoDB Connection

The backend will log on startup:
```
MongoDB connection initialized for DB: infinite_desk_demo
```

---

## 🐛 Known Limitations

- HDBSCAN clustering computation can be slow for 1000+ nodes
- Gemini API quota limits apply to RAG queries
- MongoDB free tier has storage limits

---

## 📝 Future Enhancements

- [ ] Vector database (Qdrant) for faster similarity search
- [ ] User authentication with JWT
- [ ] Real-time sync with WebSockets
- [ ] Batch embedding computation optimization
- [ ] Support for multiple LLM providers (Claude, OpenAI, etc.)
- [ ] Document upload (PDF, DOCX) with automatic summarization
- [ ] Graph export (JSON, GraphML)
- [ ] Collaborative editing
- [ ] Mobile app
- [ ] GPU acceleration for embeddings

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Vector database integration
- Real-time collaboration
- Performance optimizations for large datasets
- Additional LLM providers
- UI/UX enhancements
- Test coverage
- Documentation improvements

---

## 📄 License

Open source. See LICENSE for details.

---

## 🙌 Credits

Built by **Valerian060**

**Technology Stack:**
- **D3.js** — Interactive data visualization
- **Sentence Transformers** — Modern semantic embeddings
- **KeyBERT** — Keyword extraction
- **HDBSCAN** — Density-based clustering
- **UMAP** — Fast dimensionality reduction
- **FastAPI** — Modern Python backend framework
- **Motor** — Async MongoDB driver
- **Gemini API** — Generative AI integration

---

## 📬 Questions?

Open an issue on GitHub or check out related projects:
- [Threaded - NLP Powered Forum](https://github.com/valerian060/Threaded---NLP-Powered-Forum)
- [AI Diagnostic Orchestrator](https://github.com/valerian060/AI-Diagnostic-Orchestrator)
- [KeyLines - Smart Bookmarking Chrome Extension](https://github.com/valerian060/KeyLines)

**Explore your knowledge universe! 🌌**
