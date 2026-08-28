# Infinite Desk 🌌

**A Semantic Knowledge Platform with Interactive D3.js Knowledge Graph Visualization**

Infinite Desk is a full-stack web application that helps you organize, visualize, and discover knowledge using semantic embeddings, UMAP dimensionality reduction, and HDBSCAN clustering. Explore your notes as an interactive, navigable knowledge universe.

**[Live Demo](https://infinitedesk.onrender.com)** • [GitHub](https://github.com/valerian060/Infinite-Desk)

---

## ✨ Features

- **Interactive Knowledge Graph** — Visualize all your notes as nodes in a D3.js force-directed graph
- **Semantic Clustering** — Automatic topic discovery using HDBSCAN clustering on dense embeddings
- **Smart Search** — Find related notes based on semantic similarity (cosine distance)
- **Drag-to-Merge** — Merge related clusters by dragging nodes to the merge zone
- **Drag-to-Delete** — Remove nodes by dragging them to the delete zone
- **Zoom & Pan** — Explore large knowledge bases with smooth D3 zoom/pan controls
- **Collection Management** — Organize multiple knowledge bases
- **Session Persistence** — All data stored with authentication
- **One-Click Jump** — Navigate directly to context within the knowledge graph

---

## 🏗️ Architecture

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, D3.js v7, JavaScript (ES6+), Tailwind CSS |
| **Backend** | FastAPI, Python, Pydantic |
| **Data Storage** | JSON-based collections, localStorage for sessions |
| **Visualization** | D3.js force simulation, SVG rendering |
| **ML** | Sentence Transformers, UMAP, HDBSCAN, scikit-learn |

### System Design

```
┌─────────────────────────────────────┐
│      Frontend (D3.js + JS)          │
│  - Interactive Graph Visualization  │
│  - Auth UI (Login/Signup)           │
│  - Collection Management            │
└──────────────┬──────────────────────┘
               │ HTTP/REST API
┌──────────────▼──────────────────────┐
│    FastAPI Backend                  │
│  - Collections API                  │
│  - Node Management                  │
│  - Cluster Operations               │
└──────────────┬──────────────────────┘
               │ Read/Write
┌──────────────▼──────────────────────┐
│    Data Layer                       │
│  - collections.json (mock data)     │
│  - localStorage (sessions)          │
└─────────────────────────────────────┘
```

### Data Model

**Collection** → **Cluster** → **Node**

```javascript
{
  id: 1,
  name: "My Knowledge Base",
  clusters: [
    {
      id: 1,
      name: "Machine Learning",
      cx: 400,        // cluster center X
      cy: 300,        // cluster center Y
      nodes: [
        {
          id: "node_1",
          title: "Neural Networks Basics",
          summary: "Introduction to neural networks...",
          similar_to: ["node_2", "node_5"],
          embedding: [0.234, 0.567, ...]  // Dense vector
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

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/valerian060/Infinite-Desk.git
cd Infinite-Desk
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
pip install fastapi uvicorn pydantic
```

#### 3. Prepare Mock Data

Create a `backend/collections.json` file with your knowledge base structure:

```json
[
  {
    "id": 1,
    "name": "Computer Science",
    "clusters": [
      {
        "id": 1,
        "name": "Algorithms",
        "cx": 300,
        "cy": 250,
        "nodes": [
          {
            "id": "algo_1",
            "title": "Binary Search",
            "summary": "Efficient search in sorted arrays",
            "similar_to": ["algo_2"],
            "embedding": []
          }
        ]
      }
    ]
  }
]
```

#### 4. Run Backend Server

```bash
cd backend
python main.py
# Server runs at http://127.0.0.1:8000
```

#### 5. Open Frontend

Open `index.html` in your browser (or use Live Server):

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

### 4. **Merge Clusters**

- Drag nodes to the **left merge area** (blue zone)
- Release to merge related clusters
- Useful for consolidating similar topics

### 5. **Delete Nodes**

- Drag nodes to the **right delete area** (red zone)
- Release to remove irrelevant notes

### 6. **Search**

- Use the search box to filter nodes by keywords
- Filtered nodes are highlighted in the graph

### 7. **Re-Cluster**

- Click **Recalculate Clustering** to run HDBSCAN again
- Automatically reorganizes nodes based on new embeddings

---

## 📁 File Structure

```
Infinite-Desk/
├── backend/
│   ├── main.py              # FastAPI server with endpoints
│   └── collections.json     # Mock knowledge base data
├── frontend/
│   ├── index.html           # Main application UI
│   ├── auth.html            # Combined login/signup page
│   ├── login.html           # Standalone login page
│   ├── main.js              # D3.js graph logic
│   ├── auth.js              # Authentication handling
│   ├── login.js             # Login form logic
│   ├── styles.css           # Main application styles
│   └── auth.css             # Auth page styles
└── README.md                # This file
```

---

## 🔌 API Endpoints

### Collections

**GET** `/api/collections`
- Returns all collections with clusters and nodes
- Response: `List[CollectionData]`

### Nodes

**POST** `/api/nodes`
- Add a new node to a collection
- Body: `{ title, summary, embedding, ... }`

**DELETE** `/api/nodes/{node_id}`
- Remove a node
- Returns: Success message

### Clusters

**POST** `/api/clusters/merge`
- Merge two clusters
- Body: `{ cluster_id_1, cluster_id_2 }`

### AI Operations

**POST** `/api/ai/recluster/{collection_id}`
- Trigger HDBSCAN re-clustering
- Returns: Updated cluster assignments

---

## 🎨 UI Components

### Top Bar

- **Collection Dropdown** — Switch between knowledge bases
- **Search Box** — Filter nodes by keywords
- **Recalculate Clustering Button** — Re-run ML clustering
- **Save Layout Button** — Persist graph positions

### Side Areas

- **Left (Merge Area)** — Drag nodes here to merge clusters
- **Right (Delete Area)** — Drag nodes here to delete them
- **Visual Feedback** — Color changes indicate active zones

### Canvas

- **SVG Visualization** — D3.js force-directed graph
- **Nodes** — Represented as circles (colored by cluster)
- **Links** — White edges showing node relationships
- **Cluster Labels** — Centered text for each cluster

---

## 🔧 Configuration

### API Base URL

Edit in `frontend/main.js`:

```javascript
const API_BASE = "http://127.0.0.1:8000";
```

### Canvas Dimensions

Automatically adjusts to window size. Modify in `frontend/main.js`:

```javascript
let width = wrap.clientWidth;
let height = wrap.clientHeight;
```

### Zoom Limits

Edit in `frontend/main.js`:

```javascript
const zoom = d3.zoom()
  .scaleExtent([0.25, 6])  // Min and max zoom levels
  .on("zoom", ...);
```

### Colors & Styling

- **Node Colors** — `d3.schemeTableau10` (change in `main.js`)
- **Background** — `#0a0a1a` (dark blue, edit in styles)
- **Accent** — `#00f2ff` (cyan, edit in styles)

---

## 🚀 Deployment

### Render.com (Live Demo)

1. Push code to GitHub
2. Connect repository to Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn backend.main:app --host 0.0.0.0`
5. Deploy!

### GitHub Pages (Frontend Only)

1. Place `frontend/` files in `/docs` folder
2. Enable GitHub Pages in repository settings
3. Update `API_BASE` to point to your backend server

---

## 📊 ML Pipeline (Planned)

When integrated with ML services:

1. **Embedding Generation** — Sentence Transformers encode all notes
2. **Dimensionality Reduction** — UMAP projects embeddings to 2D space
3. **Clustering** — HDBSCAN discovers topics automatically
4. **Similarity Search** — Cosine distance finds related notes
5. **Graph Layout** — D3 force simulation positions nodes

---

## 🛠️ Development Tips

### Debug Mode

Open browser DevTools (F12) and check console for:
- API call logs
- D3.js simulation statistics
- Node/cluster state updates

### Live Editing

- Edit `frontend/styles.css` — Changes reflect instantly (refresh browser)
- Edit `frontend/main.js` — Restart server and refresh
- Edit `backend/main.py` — Restart FastAPI server

### Test Data

Modify `backend/collections.json` to add more nodes:

```json
{
  "id": "test_node_1",
  "title": "Test Note",
  "summary": "This is a test",
  "similar_to": [],
  "embedding": []
}
```

---

## 📝 Future Enhancements

- [ ] Real ML pipeline integration (Sentence Transformers + HDBSCAN)
- [ ] Cloud sync across devices
- [ ] Full-text search with ranking
- [ ] Custom note templates
- [ ] Export to JSON/PDF/Markdown
- [ ] Dark mode UI toggle
- [ ] Real database backend (PostgreSQL)
- [ ] User authentication with JWT
- [ ] Collaborative editing
- [ ] Real-time sync with WebSockets

---

## 🐛 Known Limitations

- Mock data stored in JSON (not persistent)
- Embeddings currently empty (requires ML service)
- Single-user in-browser storage
- HDBSCAN clustering not yet integrated
- No real user accounts (demo mode only)

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- ML backend integration
- Real database implementation
- Performance optimizations
- UI/UX enhancements
- Test coverage

---

## 📄 License

Open source. See LICENSE for details.

---

## 🙌 Credits

Built by **Valerian060**

- **D3.js** — Interactive data visualization
- **FastAPI** — Modern Python backend framework
- **Tailwind CSS** — Utility-first styling

---

## 📬 Questions?

Open an issue on GitHub or check out related projects:
- [Threaded - NLP Powered Forum](https://github.com/valerian060/Threaded---NLP-Powered-Forum)
- [AI Diagnostic Orchestrator](https://github.com/valerian060/AI-Diagnostic-Orchestrator)

**Explore your knowledge universe! 🌌**
