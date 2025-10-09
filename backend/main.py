from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend JS to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example dataset (replace later with DB or RAG)
data = {
    "clusters": [
        {
            "cluster_id": 0,
            "cluster_name": "Operating Systems",
            "color": "#ff6666",
            "nodes": [
                {"id": "n1", "title": "Deadlock Prevention", "content": "Avoid circular wait using resource ordering."},
                {"id": "n2", "title": "Process Scheduling", "content": "FCFS, SJF, Round Robin explained."},
                {"id": "n3", "title": "Semaphores", "content": "Used for synchronization, binary & counting."}
            ]
        },
        {
            "cluster_id": 1,
            "cluster_name": "DBMS",
            "color": "#66ccff",
            "nodes": [
                {"id": "n4", "title": "Normalization", "content": "1NF, 2NF, 3NF and BCNF rules."},
                {"id": "n5", "title": "ACID Properties", "content": "Atomicity, Consistency, Isolation, Durability."},
                {"id": "n6", "title": "SQL Joins", "content": "Inner, outer, left and right joins."}
            ]
        },
        {
            "cluster_id": 2,
            "cluster_name": "Computer Networks",
            "color": "#66ff66",
            "nodes": [
                {"id": "n7", "title": "Routing Algorithms", "content": "Distance vector and link state."},
                {"id": "n8", "title": "IP Addressing", "content": "IPv4, IPv6, subnetting basics."},
                {"id": "n9", "title": "OSI Model", "content": "7 layers of network communication."}
            ]
        }
    ]
}

@app.get("/")
def home():
    return {"message": "Infinite Desk API is running 🚀"}

@app.get("/api/nodes")
def get_nodes():
    return data


@app.post("/api/add_cluster")
async def add_cluster(request: Request):
    body = await request.json()
    new_cluster = {
        "cluster_id": len(data["clusters"]),
        "cluster_name": body["name"],
        "color": body.get("color", "#ffa500"),
        "nodes": []
    }
    data["clusters"].append(new_cluster)
    return {"status": "success", "clusters": data["clusters"]}
