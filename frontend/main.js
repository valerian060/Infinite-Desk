const svg = d3.select("#canvas");
const g = svg.append("g");
const tooltip = d3.select(".tooltip");
const width = window.innerWidth;
const height = window.innerHeight;
svg.attr("width", width).attr("height", height);

let clusters = [];
let nodesData = [];

// Fetch data from FastAPI backend
fetch("http://127.0.0.1:8000/api/nodes")
  .then(res => res.json())
  .then(data => {
    clusters = data.clusters.map((c, i) => ({
      id: i,
      name: c.cluster_name,
      color: c.color,
      nodes: c.nodes
    }));

    nodesData = clusters.flatMap(c => 
      c.nodes.map(n => ({
        ...n,
        cluster_id: c.id,
        color: c.color
      }))
    );

    renderGalaxy();
  });

function renderGalaxy() {
  const colorScale = d3.scaleOrdinal(d3.schemeTableau10);

  const simulation = d3.forceSimulation(nodesData)
    .force("charge", d3.forceManyBody().strength(-80))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(30))
    .force("cluster", clusteringForce(0.06))
    .on("tick", ticked);

  const nodes = g.selectAll(".node")
    .data(nodesData)
    .enter()
    .append("g")
    .attr("class", "node");

  nodes.append("circle")
    .attr("r", 18)
    .attr("fill", d => d.color)
    .on("mouseover", (event, d) => {
      tooltip.transition().duration(100).style("opacity", 1);
      tooltip.html(`<strong>${d.title}</strong><br>${d.content || d.summary}`);
    })
    .on("mousemove", (event) => {
      tooltip.style("left", event.pageX + 10 + "px")
             .style("top", event.pageY - 20 + "px");
    })
    .on("mouseout", () => tooltip.transition().duration(300).style("opacity", 0));

  nodes.append("text")
    .text(d => d.title)
    .attr("dy", 4)
    .attr("opacity", 0.3);

  const clusterLabels = g.selectAll(".cluster-label")
    .data(clusters)
    .enter()
    .append("text")
    .attr("class", "cluster-label")
    .text(d => d.name)
    .attr("x", d => getClusterCenter(d.id).x)
    .attr("y", d => getClusterCenter(d.id).y)
    .on("click", (event, d) => renameCluster(event, d));

  svg.call(d3.zoom().scaleExtent([0.4, 10]).on("zoom", (event) => {
    g.attr("transform", event.transform);
    const scale = event.transform.k;
    nodes.select("text").attr("opacity", scale > 2 ? 1 : 0.3);
  }));

  document.getElementById("searchBar").addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase();
    nodes.select("circle")
      .attr("opacity", d => d.title.toLowerCase().includes(q) ? 1 : 0.15);
    nodes.select("text")
      .attr("opacity", d => d.title.toLowerCase().includes(q) ? 1 : 0.1);
  });

  document.getElementById("addNode").addEventListener("click", () => {
    alert("🚀 Add new nodes or clusters — coming soon!");
  });

  function ticked() {
    nodes.attr("transform", d => `translate(${d.x},${d.y})`);
  }

  function clusteringForce(strength) {
    return alpha => {
      for (const d of nodesData) {
        const c = getClusterCenter(d.cluster_id);
        d.vx += (c.x - d.x) * strength * alpha;
        d.vy += (c.y - d.y) * strength * alpha;
      }
    };
  }

  function getClusterCenter(clusterId) {
    const angle = (clusterId / clusters.length) * 2 * Math.PI;
    const radius = 300;
    return {
      x: width / 2 + Math.cos(angle) * radius,
      y: height / 2 + Math.sin(angle) * radius
    };
  }

  function renameCluster(event, cluster) {
    const input = d3.select("body").append("input")
      .attr("class", "rename-input")
      .style("left", event.pageX + "px")
      .style("top", event.pageY + "px")
      .attr("value", cluster.name)
      .on("keydown", (e) => {
        if (e.key === "Enter") {
          cluster.name = e.target.value;
          clusterLabels.filter(d => d.id === cluster.id).text(cluster.name);
          input.remove();
        }
      })
      .on("blur", () => input.remove())
      .node();
    input.focus();
  }
}
