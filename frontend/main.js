// main.js
// Knowledge Galaxy frontend (D3.js v7) designed to work with the API schema provided

const API_BASE = "http://127.0.0.1:8000";
const svg = d3.select("#galaxySvg");
const wrap = document.getElementById("canvasWrap");
const tooltip = d3.select(".tooltip");
let width = wrap.clientWidth;
let height = wrap.clientHeight;
svg.attr("width", width).attr("height", height);

let currentTransform = d3.zoomIdentity;
let collections = [];
let currentCollection = null;
let clusters = [];
let nodes = [];
let links = [];
let mergeBuffer = [];
const mergeAreaEl = d3.select("#leftMergeArea");
const deleteAreaEl = d3.select("#rightDeleteArea");
const statusEl = document.getElementById("status");
const EDGE_MARGIN = 120;

// glow filter
const defs = svg.append("defs");
defs.append("filter").attr("id","glow")
  .html(`<feGaussianBlur stdDeviation="4" result="coloredBlur"/>
         <feMerge>
           <feMergeNode in="coloredBlur"/>
           <feMergeNode in="SourceGraphic"/>
         </feMerge>`);

const g = svg.append("g");
const linksLayer = g.append("g").attr("class","links");
const clustersLayer = g.append("g").attr("class","clusters");
const nodesLayer = g.append("g").attr("class","nodes");
const colorScale = d3.scaleOrdinal(d3.schemeTableau10);

// ------------------ ZOOM ------------------
const zoom = d3.zoom()
  .scaleExtent([0.25,6])
  .on("zoom", event => {
    currentTransform = event.transform;
    g.attr("transform", currentTransform);
  });
svg.call(zoom);

// ------------------ COLLECTIONS ------------------
async function loadCollections(){
  try{
    const res = await fetch(`${API_BASE}/api/collections`);
    collections = await res.json();
    const sel = document.getElementById("collectionSelect");
    sel.innerHTML = "";
    collections.forEach(c=>{
      const opt = document.createElement("option");
      opt.value=c.id; opt.textContent=c.name; sel.appendChild(opt);
    });
    if(collections.length>0){
      sel.value=collections[0].id;
      sel.addEventListener("change", ()=> loadCollectionById(+sel.value));
      await loadCollectionById(collections[0].id);
    }
  }catch(e){ console.error(e); notify("Failed to fetch collections") }
}

async function loadCollectionById(collectionId){
  const coll = collections.find(c=>c.id==collectionId);
  if(!coll){ notify("Collection not found"); return; }
  currentCollection = coll;
  clusters = JSON.parse(JSON.stringify(coll.clusters));

  // assign random cluster positions if missing
  clusters.forEach(cl=>{
    cl.cx = cl.cx || Math.random()*(width-300)+150;
    cl.cy = cl.cy || Math.random()*(height-300)+150;
    cl.nodes = cl.nodes || [];
  });

  // flatten nodes
  nodes = [];
  clusters.forEach(cl=>{
    cl.nodes.forEach(n=>{
      const node = typeof n==="string"?{}:JSON.parse(JSON.stringify(n));
      node.id = node.id || `nid_${Math.random().toString(36).slice(2,9)}`;
      node.title = node.title || "Untitled";
      node.summary = node.summary || "";
      node.cluster_id = cl.id;
      node.x = node.x || (cl.cx + (Math.random()-0.5)*80);
      node.y = node.y || (cl.cy + (Math.random()-0.5)*80);
      nodes.push(node);
    });
  });

  buildLinks();
  render();
}

function buildLinks(){
  links = [];
  const nodeById = new Map(nodes.map(n=>[n.id,n]));
  nodes.forEach(n=>{
    if(Array.isArray(n.similar_to)){
      n.similar_to.forEach(tid=>{
        const t = nodeById.get(tid);
        if(t) links.push({source:n.id, target:t.id});
      });
    }
  });
}

// ------------------ RENDER ------------------
function render(){
  linksLayer.selectAll("*").remove();
  nodesLayer.selectAll("*").remove();
  clustersLayer.selectAll("*").remove();

  // similarity links
  linksLayer.selectAll("line").data(links,d=>`${d.source}->${d.target}`).enter()
    .append("line").attr("stroke","#fff").attr("stroke-opacity",0.18).attr("stroke-width",1);

  // cluster groups
  const clusterG = clustersLayer.selectAll(".cluster-group").data(clusters,d=>d.id).enter()
    .append("g").attr("class","cluster-group");

  clusterG.append("circle")
    .attr("r",46)
    .attr("cx",d=>d.cx)
    .attr("cy",d=>d.cy)
    .attr("fill",d=>d.color||"#2a8")
    .attr("opacity",0.06);

  const labelText = clusterG.append("text")
    .attr("x",d=>d.cx)
    .attr("y",d=>d.cy-60)
    .text(d=>d.name)
    .attr("text-anchor","middle")
    .style("font-weight","700")
    .style("font-size","15px")
    .style("fill",d=>d.color||"#fff")
    .style("pointer-events","all")
    .style("cursor","grab")
    .on("click",(event,d)=> promptRenameCluster(d));

  // cluster drag moves cluster + nodes
  clusterG.call(d3.drag()
    .on("start",(event,d)=>event.sourceEvent.stopPropagation())
    .on("drag",(event,d)=>{
      const dx = event.dx, dy=event.dy;
      d.cx+=dx; d.cy+=dy;
      nodes.filter(n=>n.cluster_id===d.id).forEach(n=>{ n.x+=dx; n.y+=dy; });
      renderPositions();
    })
  );

  // nodes
  const nodeG = nodesLayer.selectAll(".node").data(nodes,d=>d.id).enter()
    .append("g").attr("class","node").attr("transform",d=>`translate(${d.x},${d.y})`)
    .style("cursor","grab");

  nodeG.append("circle")
    .attr("r",12)
    .attr("fill",d=>clusters.find(c=>c.id===d.cluster_id)?.color||"#999")
    .attr("stroke","#fff").attr("stroke-width",1.5)
    .attr("filter","url(#glow)");

  nodeG.append("text")
    .text(d=>d.title)
    .attr("dy",4)
    .attr("fill","#fff")
    .attr("text-anchor","middle")
    .style("font-size","9px")
    .style("pointer-events","none")
    .attr("opacity",0.85);

  // tooltip
  nodeG.on("mouseover",(event,d)=>{
    tooltip.style("left",(event.pageX+12)+"px")
      .style("top",(event.pageY-20)+"px")
      .style("opacity",1)
      .html(`<strong>${d.title}</strong><div style="margin-top:6px;font-size:12px">${d.summary||""}</div>`);
  }).on("mousemove",(event)=>{
    tooltip.style("left",(event.pageX+12)+"px").style("top",(event.pageY-20)+"px");
  }).on("mouseout",()=>tooltip.style("opacity",0));

  // ------------------ NODE DRAG (fixed offset) ------------------
  nodeG.call(d3.drag()
    .on("start",(event,d)=>{
      event.sourceEvent.stopPropagation();
      const mouseX = currentTransform.invertX(event.x);
      const mouseY = currentTransform.invertY(event.y);
      d._dragOffsetX = d.x - mouseX;
      d._dragOffsetY = d.y - mouseY;
      mergeAreaEl.classed("visible",true);
      deleteAreaEl.classed("visible",true);
    })
    .on("drag",(event,d)=>{
      const mouseX = currentTransform.invertX(event.x);
      const mouseY = currentTransform.invertY(event.y);
      d.x = mouseX + d._dragOffsetX;
      d.y = mouseY + d._dragOffsetY;
      d3.select(event.sourceEvent.target.parentNode).attr("transform",`translate(${d.x},${d.y})`);
      renderPositions();
    })
    .on("end",(event,d)=>{
      delete d._dragOffsetX; delete d._dragOffsetY;
      mergeAreaEl.classed("visible",false);
      deleteAreaEl.classed("visible",false);
      d.fx=null; d.fy=null;
      renderPositions();
      // merge/delete logic can go here
    })
  );

  startSimulation();
}

// ------------------ RENDER POSITIONS ------------------
function renderPositions(){
  nodesLayer.selectAll(".node").attr("transform",d=>`translate(${d.x},${d.y})`);
  linksLayer.selectAll("line")
    .attr("x1",d=>(nodes.find(n=>n.id===d.source)||{}).x||0)
    .attr("y1",d=>(nodes.find(n=>n.id===d.source)||{}).y||0)
    .attr("x2",d=>(nodes.find(n=>n.id===d.target)||{}).x||0)
    .attr("y2",d=>(nodes.find(n=>n.id===d.target)||{}).y||0);
  clustersLayer.selectAll(".cluster-group").select("text")
    .attr("x",d=>d.cx).attr("y",d=>d.cy-60);
}

// ------------------ SIMULATION ------------------
let sim;
function startSimulation(){
  if(sim) sim.stop();
  sim = d3.forceSimulation(nodes)
    .force("charge",d3.forceManyBody().strength(-20))
    .force("collide",d3.forceCollide().radius(16).strength(0.9))
    .force("x",d3.forceX().x(d=>{
      const c = clusters.find(cl=>cl.id===d.cluster_id);
      return c ? c.cx + Math.cos(Math.random()*2*Math.PI)*15 : width/2;
    }).strength(0.14))
    .force("y",d3.forceY().y(d=>{
      const c = clusters.find(cl=>cl.id===d.cluster_id);
      return c ? c.cy + Math.sin(Math.random()*2*Math.PI)*15 : height/2;
    }).strength(0.14))
    .alphaDecay(0.02)
    .on("tick",()=>renderPositions());
}

// ------------------ UTILS ------------------
function promptRenameCluster(cluster){
  const newName = prompt("Rename cluster", cluster.name);
  if(!newName) return;
  cluster.name = newName;
  clustersLayer.selectAll(".cluster-group").select("text").filter(d=>d.id===cluster.id).text(newName);
}

function notify(msg,t=2200){
  statusEl.textContent = msg;
  setTimeout(()=>{ if(statusEl.textContent===msg) statusEl.textContent=""; },t);
}

// ------------------ WINDOW RESIZE ------------------
window.addEventListener("resize",()=>{
  width = wrap.clientWidth; height = wrap.clientHeight;
  svg.attr("width",width).attr("height",height);
});

// ------------------ INIT ------------------
loadCollections().catch(e=>console.error(e));
