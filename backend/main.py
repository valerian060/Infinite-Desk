from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

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

# --- MOCK DATA (Multiple Collections) ---
CS_MOCK_COLLECTIONS: List[CollectionData] = [
    {
        "id": 1,
        "name": "CS Core Knowledge (8 Clusters - Expanded)",
        "clusters": [
            {
                "id": 101,
                "name": "Algorithms & Complexity",
                # Initial center positions for the force layout
                "cx": 200, "cy": 150,
                "nodes": [
                    {"id": "A1", "title": "Big O Notation", "summary": "Formal notation for expressing the worst-case complexity of an algorithm.", "similar_to": ["A2", "D1"], "embedding": []},
                    {"id": "A2", "title": "Merge Sort", "summary": "A stable, $O(n \log n)$ divide-and-conquer sorting algorithm.", "similar_to": ["A1", "A3"], "embedding": []},
                    {"id": "A3", "title": "Dijkstra's Algorithm", "summary": "Finds the shortest paths between nodes in a graph, $O((V+E)\log V)$.", "similar_to": ["A2", "D3"], "embedding": []},
                    {"id": "A4", "title": "Dynamic Programming (DP)", "summary": "Solving complex problems by breaking them down into simpler subproblems and storing results.", "similar_to": ["A1", "D2"], "embedding": []},
                    {"id": "A5", "title": "NP-Completeness", "summary": "Class of decision problems for which verification is polynomial time.", "similar_to": ["A1"], "embedding": []},
                ]
            },
            {
                "id": 102,
                "name": "Data Structures",
                "cx": 500, "cy": 150,
                "nodes": [
                    {"id": "D1", "title": "Hash Map Collisions", "summary": "Dealing with separate chaining vs. open addressing in Hash Maps.", "similar_to": ["A1", "D2"], "embedding": []},
                    {"id": "D2", "title": "Linked List vs Array", "summary": "Trade-offs: $O(1)$ insertion vs. $O(1)$ random access.", "similar_to": ["D1", "D3"], "embedding": []},
                    {"id": "D3", "title": "Tree Traversal (BFS/DFS)", "summary": "In-order, pre-order, post-order, and level-order traversals.", "similar_to": ["A3", "D2"], "embedding": []},
                    {"id": "D4", "title": "AVL Trees", "summary": "Self-balancing binary search tree where balance factor is $\pm 1$ or $0$.", "similar_to": ["D3", "A2"], "embedding": []},
                ]
            },
            {
                "id": 103,
                "name": "Operating Systems",
                "cx": 800, "cy": 150,
                "nodes": [
                    {"id": "O1", "title": "Threading vs. Process", "summary": "Differences between parallelism (processes) and concurrency (threads).", "similar_to": ["O2"], "embedding": []},
                    {"id": "O2", "title": "Deadlocks Conditions", "summary": "Mutual exclusion, Hold and wait, No preemption, Circular wait.", "similar_to": ["O1", "O3"], "embedding": []},
                    {"id": "O3", "title": "Virtual Memory/Paging", "summary": "Mapping virtual addresses to physical memory pages.", "similar_to": ["O2"], "embedding": []},
                    {"id": "O4", "title": "Process Scheduling", "summary": "Algorithms like Round Robin, FCFS, and shortest job first.", "similar_to": ["O1", "O2"], "embedding": []},
                ]
            },
            {
                "id": 104,
                "name": "Web Development (Frontend)",
                "cx": 200, "cy": 450,
                "nodes": [
                    {"id": "W1", "title": "React Hooks", "summary": "useState, useEffect, useContext - managing state and side effects.", "similar_to": ["W2", "P1"], "embedding": []},
                    {"id": "W2", "title": "REST API Principles", "summary": "Uniform interface, statelessness, cacheability.", "similar_to": ["W1", "B1"], "embedding": []},
                    {"id": "W3", "title": "Tailwind CSS Utility-First", "summary": "Composing complex interfaces from small, constrained utility classes.", "similar_to": ["W1"], "embedding": []},
                    {"id": "W4", "title": "Component Lifecycles", "summary": "Mounting, updating, and unmounting phases in component design.", "similar_to": ["W1", "W2"], "embedding": []},
                ]
            },
            {
                "id": 105,
                "name": "Databases & SQL",
                "cx": 500, "cy": 450,
                "nodes": [
                    {"id": "B1", "title": "Normalization (3NF)", "summary": "Reducing redundancy and improving data integrity to the third normal form.", "similar_to": ["B2", "W2"], "embedding": []},
                    {"id": "B2", "title": "ACID Properties", "summary": "Atomicity, Consistency, Isolation, Durability in transactions.", "similar_to": ["B1"], "embedding": []},
                    {"id": "B3", "title": "SQL Join Types", "summary": "INNER, LEFT, RIGHT, FULL joins and their uses.", "similar_to": ["B1"], "embedding": []},
                    {"id": "B4", "title": "Indexing", "summary": "Creating indexes to speed up data retrieval operations, typically at the cost of write speed.", "similar_to": ["B1", "D1"], "embedding": []},
                ]
            },
            {
                "id": 106,
                "name": "Python/Fundamentals",
                "cx": 800, "cy": 450,
                "nodes": [
                    {"id": "P1", "title": "Python Decorators", "summary": "Using '@' syntax to wrap functions and modify behavior.", "similar_to": ["P2", "W1"], "embedding": []},
                    {"id": "P2", "title": "Generators vs. Lists", "summary": "Memory efficiency and lazy evaluation using the 'yield' keyword.", "similar_to": ["P1", "D1"], "embedding": []},
                    {"id": "P3", "title": "Lambda Functions", "summary": "Small, anonymous functions used inline with map/filter.", "similar_to": ["P1"], "embedding": []},
                    {"id": "P4", "title": "Global Interpreter Lock (GIL)", "summary": "A mechanism used in CPython to ensure only one thread executes Python bytecode at a time.", "similar_to": ["O1", "P1"], "embedding": []},
                ]
            },
            {
                "id": 107,
                "name": "Computer Networks",
                "cx": 350, "cy": 750,
                "nodes": [
                    {"id": "N1", "title": "TCP vs UDP", "summary": "TCP is connection-oriented and reliable; UDP is connectionless and fast.", "similar_to": ["N2"], "embedding": []},
                    {"id": "N2", "title": "OSI Model Layers", "summary": "Seven layers: Physical, Data Link, Network, Transport, Session, Presentation, Application.", "similar_to": ["N1", "N3"], "embedding": []},
                    {"id": "N3", "title": "IP Addressing (Subnetting)", "summary": "Dividing an IP network into smaller subnetworks (classes A, B, C).", "similar_to": ["N2", "N4"], "embedding": []},
                    {"id": "N4", "title": "HTTP Status Codes", "summary": "1xx Informational, 2xx Success, 3xx Redirection, 4xx Client Error, 5xx Server Error.", "similar_to": ["W2", "N1"], "embedding": []},
                ]
            },
            {
                "id": 108,
                "name": "Software Engineering",
                "cx": 650, "cy": 750,
                "nodes": [
                    {"id": "S1", "title": "Agile vs Waterfall", "summary": "Iterative and incremental (Agile) vs. sequential design (Waterfall).", "similar_to": ["S2"], "embedding": []},
                    {"id": "S2", "title": "Design Patterns", "summary": "Reusable solutions to common software design problems (e.g., Factory, Singleton).", "similar_to": ["S1", "P1"], "embedding": []},
                    {"id": "S3", "title": "Unit Testing/TDD", "summary": "Writing tests for small, isolated pieces of code before (TDD) or after implementation.", "similar_to": ["S1"], "embedding": []},
                    {"id": "S4", "title": "Version Control (Git)", "summary": "Distributed revision control for tracking changes in source code.", "similar_to": ["S3"], "embedding": []},
                ]
            }
        ]
    },
    # --- SECOND COLLECTION: Web Design Fundamentals (3 Clusters) ---
    {
        "id": 2,
        "name": "Web Design Fundamentals (3 Clusters)",
        "clusters": [
            {
                "id": 201,
                "name": "UX Principles",
                "cx": 250, "cy": 250,
                "nodes": [
                    {"id": "U1", "title": "Gestalt Laws", "summary": "Principles of perception (proximity, similarity) in interface design.", "similar_to": ["U2", "X1", "C4"], "embedding": []},
                    {"id": "U2", "title": "Fitts' Law", "summary": "Time to acquire a target is a function of the distance and size of the target.", "similar_to": ["U1", "U3"], "embedding": []},
                    {"id": "U3", "title": "Hicks' Law", "summary": "Time to make a decision increases with the number and complexity of choices.", "similar_to": ["U2", "X2"], "embedding": []},
                    {"id": "U4", "title": "Mental Models", "summary": "User's internal representation of how a system works.", "similar_to": ["U1"], "embedding": []},
                ]
            },
            {
                "id": 202,
                "name": "Modern CSS Layout",
                "cx": 550, "cy": 250,
                "nodes": [
                    {"id": "C1", "title": "CSS Grid vs. Flexbox", "summary": "Grid (2D) for major layouts, Flexbox (1D) for component alignment.", "similar_to": ["C2", "U1"], "embedding": []},
                    {"id": "C2", "title": "BEM Naming", "summary": "Block-Element-Modifier convention for modular CSS.", "similar_to": ["C1", "C3"], "embedding": []},
                    {"id": "C3", "title": "CSS Variables", "summary": "Using custom properties for global theme management.", "similar_to": ["C2", "C4"], "embedding": []},
                    {"id": "C4", "title": "Container Queries", "summary": "Styling elements based on their container size, not the viewport.", "similar_to": ["C3", "X3"], "embedding": []},
                ]
            },
            {
                "id": 203,
                "name": "Accessibility (A11y)",
                "cx": 400, "cy": 550,
                "nodes": [
                    {"id": "X1", "title": "ARIA Roles and Labels", "summary": "Providing semantic meaning to content for assistive technologies.", "similar_to": ["X2", "U3"], "embedding": []},
                    {"id": "X2", "title": "WCAG Color Contrast", "summary": "Minimum ratio requirements (AA or AAA) for text and background.", "similar_to": ["X1", "U3"], "embedding": []},
                    {"id": "X3", "title": "Keyboard Navigation", "summary": "Ensuring all interactive elements are reachable via Tab and Enter keys.", "similar_to": ["X1", "C4"], "embedding": []},
                    {"id": "X4", "title": "Screen Reader Best Practices", "summary": "Techniques for optimizing content for sequential reading.", "similar_to": ["X1"], "embedding": []},
                ]
            }
        ]
    }
]

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
    """Returns the list of collections (Knowledge Bases), containing 8 mock clusters."""
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
