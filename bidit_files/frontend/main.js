// Infinite Desk - Floating Knowledge Map - Fixed Search (Names Only)
class InfiniteDesk {
    constructor() {
        this.API_BASE = 'http://127.0.0.1:8000/api';
        this.currentCollectionId = null;
        this.clusters = [];
        this.nodes = [];
        this.simulation = null;
        this.svg = null;
        this.g = null;
        this.zoom = null;

        this.colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', 
                       '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b',
                       '#8e44ad', '#2980b9', '#27ae60', '#d35400', '#7f8c8d'];
        this.width = window.innerWidth;
        this.height = window.innerHeight;

        this.CLUSTER_RADIUS = 35;
        this.NODE_RADIUS = 5;

        this.init();
    }

    async init() {
        console.log('Initializing Infinite Desk...');
        this.setupSVG();
        this.setupEventListeners();
        await this.loadData();
        this.hideLoading();
    }

    setupSVG() {
        console.log('Setting up SVG canvas...');
        this.svg = d3.select("#galaxy")
            .attr("width", this.width)
            .attr("height", this.height);

        const defs = this.svg.append("defs");
        const filter = defs.append("filter").attr("id", "glow");
        filter.append("feGaussianBlur").attr("stdDeviation", "3.5").attr("result", "coloredBlur");
        const feMerge = filter.append("feMerge");
        feMerge.append("feMergeNode").attr("in", "coloredBlur");
        feMerge.append("feMergeNode").attr("in", "SourceGraphic");

        const whiteGlow = defs.append("filter").attr("id", "whiteGlow");
        whiteGlow.append("feGaussianBlur").attr("stdDeviation", "5").attr("result", "coloredBlur");
        const wgMerge = whiteGlow.append("feMerge");
        wgMerge.append("feMergeNode").attr("in", "coloredBlur");
        wgMerge.append("feMergeNode").attr("in", "SourceGraphic");

        this.g = this.svg.append("g");

        this.zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on("zoom", (event) => {
                this.g.attr("transform", event.transform);
            });

        this.svg.call(this.zoom);

        this.g.append("g").attr("class", "connections");
        this.g.append("g").attr("class", "clusters");
        this.g.append("g").attr("class", "nodes");

        console.log('SVG setup complete');
    }

    setupEventListeners() {
        d3.select("#searchInput").on("input", (event) => this.filterItems(event.target.value));
        d3.select("#createClusterBtn").on("click", () => this.createNewCluster());
        d3.select("#createNodeBtn").on("click", () => this.createNewNode());
        window.addEventListener('resize', () => this.handleResize());
    }

    async loadData() {
        try {
            console.log('Loading data from API...');

            const collections = await this.fetchAPI('/collections');
            console.log('Collections loaded:', collections);

            if (!collections || collections.length === 0) {
                console.error('No collections found!');
                alert('No collections found. Please check if backend is running and data files exist.');
                return;
            }

            this.currentCollectionId = collections[0].id || collections[0]._id;
            console.log('Using collection:', this.currentCollectionId);

            const clustersData = await this.fetchAPI(`/collections/${this.currentCollectionId}/clusters`);
            console.log('Clusters loaded:', clustersData);
            this.clusters = clustersData || [];

            this.nodes = [];
            for (let cluster of this.clusters) {
                const clusterId = cluster.id || cluster._id;
                const clusterNodes = await this.fetchAPI(`/clusters/${clusterId}/nodes`);
                console.log(`Nodes for cluster ${clusterId}:`, clusterNodes);

                if (clusterNodes) {
                    clusterNodes.forEach(node => {
                        node.cluster_id = clusterId;
                        node.cluster = cluster;
                        this.nodes.push(node);
                    });
                }
            }

            console.log(`Total clusters: ${this.clusters.length}, Total nodes: ${this.nodes.length}`);

            if (this.clusters.length === 0) {
                console.error('No clusters loaded!');
                alert('No clusters found. Please check your data files.');
                return;
            }

            this.processData();
            this.render();

        } catch (error) {
            console.error('Failed to load data:', error);
            alert(`Failed to load data: ${error.message}\n\nMake sure:\n1. Backend is running at http://127.0.0.1:8000\n2. Data files exist in backend/data/`);
        }
    }

    processData() {
        console.log('Processing data...');

        this.clusters.forEach((cluster, i) => {
            cluster.color = cluster.color || this.colors[i % this.colors.length];
            cluster.x = cluster.x || (Math.random() - 0.5) * this.width * 0.5 + this.width / 2;
            cluster.y = cluster.y || (Math.random() - 0.5) * this.height * 0.5 + this.height / 2;
            cluster.radius = this.CLUSTER_RADIUS;
        });

        this.nodes.forEach(node => {
            const cluster = node.cluster;
            if (cluster) {
                if (!node.x || !node.y) {
                    const angle = Math.random() * Math.PI * 2;
                    const distance = 60 + Math.random() * 30;
                    node.x = cluster.x + Math.cos(angle) * distance;
                    node.y = cluster.y + Math.sin(angle) * distance;
                }
                node.color = node.color || cluster.color;
                node.radius = this.NODE_RADIUS;
            }
        });

        console.log('Data processing complete');
    }

    render() {
        console.log('Rendering clusters and nodes...');
        this.renderConnections();
        this.renderClusters();
        this.renderNodes();
        this.setupSimulation();
        console.log('Render complete');
    }

    renderConnections() {
        const connections = [];

        this.nodes.forEach(node => {
            const cluster = this.clusters.find(c => (c.id || c._id) === node.cluster_id);
            if (cluster) {
                connections.push({
                    source: node,
                    target: cluster,
                    color: cluster.color
                });
            }
        });

        this.g.select(".connections").selectAll(".node-connection")
            .data(connections)
            .join("line")
            .attr("class", "node-connection")
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y)
            .attr("stroke", d => d.color);
    }

    renderClusters() {
        const clusterGroups = this.g.select(".clusters")
            .selectAll(".cluster-group")
            .data(this.clusters, d => d.id || d._id)
            .join("g")
            .attr("class", "cluster-group")
            .attr("transform", d => `translate(${d.x},${d.y})`)
            .call(this.createClusterDragBehavior())
            .on("dblclick", (event, d) => {
                event.stopPropagation();
                this.showClusterActions(event, d);
            });

        clusterGroups.selectAll("*").remove();

        clusterGroups.append("circle")
            .attr("class", "cluster-circle")
            .attr("r", d => d.radius)
            .attr("fill", d => d.color)
            .attr("opacity", 0.8);

        clusterGroups.append("text")
            .attr("class", "cluster-label")
            .attr("y", d => -d.radius - 10)
            .text(d => d.name || d.user_defined_name || `Cluster ${d.cluster_label}`);
    }

    renderNodes() {
        const nodeGroups = this.g.select(".nodes")
            .selectAll(".node-group")
            .data(this.nodes, d => d.id || d._id)
            .join("g")
            .attr("class", "node-group")
            .attr("transform", d => `translate(${d.x},${d.y})`)
            .call(this.createNodeDragBehavior())
            .on("dblclick", (event, d) => {
                event.stopPropagation();
                this.showNodeActions(event, d);
            })
            .on("mouseover", (event, d) => this.showTooltip(event, d))
            .on("mouseout", () => this.hideTooltip());

        nodeGroups.selectAll("*").remove();

        nodeGroups.append("circle")
            .attr("class", "node-circle")
            .attr("r", d => d.radius)
            .attr("fill", d => d.color);

        nodeGroups.append("text")
            .attr("class", "node-label")
            .attr("y", d => -d.radius - 5)
            .text(d => d.title || "Untitled");
    }

    setupSimulation() {
        this.simulation = d3.forceSimulation()
            .nodes([...this.nodes, ...this.clusters])
            .force("charge", d3.forceManyBody().strength(-100))
            .force("collision", d3.forceCollide().radius(d => (d.radius || 5) + 15))
            .on("tick", () => this.ticked());

        this.simulation.alpha(0.3).restart();
    }

    ticked() {
        this.g.selectAll(".cluster-group")
            .attr("transform", d => `translate(${d.x},${d.y})`);

        this.g.selectAll(".node-group")
            .attr("transform", d => `translate(${d.x},${d.y})`);

        this.g.selectAll(".node-connection")
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
    }

    createClusterDragBehavior() {
        let initialClusterPos = { x: 0, y: 0 };
        let nodeOffsets = [];

        return d3.drag()
            .on("start", (event, d) => {
                event.sourceEvent.stopPropagation();
                if (!event.active) this.simulation.alphaTarget(0.3).restart();

                initialClusterPos = { x: d.x, y: d.y };

                nodeOffsets = this.nodes
                    .filter(n => n.cluster_id === (d.id || d._id))
                    .map(n => ({
                        node: n,
                        offsetX: n.x - d.x,
                        offsetY: n.y - d.y
                    }));

                d.fx = d.x;
                d.fy = d.y;
            })
            .on("drag", (event, d) => {
                d.fx = event.x;
                d.fy = event.y;
                d.x = event.x;
                d.y = event.y;

                nodeOffsets.forEach(({ node, offsetX, offsetY }) => {
                    node.x = d.x + offsetX;
                    node.y = d.y + offsetY;
                    node.fx = node.x;
                    node.fy = node.y;
                });

                this.ticked();
            })
            .on("end", (event, d) => {
                if (!event.active) this.simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;

                nodeOffsets.forEach(({ node }) => {
                    node.fx = null;
                    node.fy = null;
                });
            });
    }

    createNodeDragBehavior() {
        return d3.drag()
            .on("start", (event, d) => {
                event.sourceEvent.stopPropagation();
                if (!event.active) this.simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            })
            .on("drag", (event, d) => {
                d.fx = event.x;
                d.fy = event.y;
                d.x = event.x;
                d.y = event.y;
            })
            .on("end", (event, d) => {
                if (!event.active) this.simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            });
    }

    showClusterActions(event, cluster) {
        const existingModal = document.querySelector('.action-modal');
        if (existingModal) existingModal.remove();

        const modal = document.createElement('div');
        modal.className = 'action-modal';
        modal.style.left = '50%';
        modal.style.top = '50%';
        modal.style.transform = 'translate(-50%, -50%)';

        modal.innerHTML = `
            <h3>Cluster: ${cluster.name || 'Unnamed'}</h3>

            <div class="modal-section">
                <label>Edit Name:</label>
                <input type="text" id="clusterNameInput" value="${cluster.name || cluster.user_defined_name || ''}" placeholder="Enter cluster name..." />
            </div>

            <div class="button-group">
                <button class="btn-save">Save</button>
                <button class="btn-delete">Delete Cluster</button>
                <button class="btn-cancel">Cancel</button>
            </div>
        `;

        document.body.appendChild(modal);

        const nameInput = modal.querySelector('#clusterNameInput');
        nameInput.focus();
        nameInput.select();

        modal.querySelector('.btn-save').onclick = async () => {
            const newName = nameInput.value.trim();
            if (newName && newName !== cluster.name) {
                await this.updateClusterName(cluster, newName);
            }
            document.body.removeChild(modal);
        };

        modal.querySelector('.btn-delete').onclick = async () => {
            if (confirm(`Delete cluster "${cluster.name}" and all its nodes?`)) {
                await this.deleteCluster(cluster);
                document.body.removeChild(modal);
            }
        };

        modal.querySelector('.btn-cancel').onclick = () => {
            document.body.removeChild(modal);
        };
    }

    showNodeActions(event, node) {
        const existingModal = document.querySelector('.action-modal');
        if (existingModal) existingModal.remove();

        const modal = document.createElement('div');
        modal.className = 'action-modal';
        modal.style.left = '50%';
        modal.style.top = '50%';
        modal.style.transform = 'translate(-50%, -50%)';

        const nodeText = node.content?.text || '';

        modal.innerHTML = `
            <h3>Node: ${node.title || 'Untitled'}</h3>

            <div class="modal-section">
                <label>Edit Name:</label>
                <input type="text" id="nodeNameInput" value="${node.title || ''}" placeholder="Enter node name..." />
            </div>

            <div class="modal-section">
                <label>Node Content:</label>
                <textarea id="nodeContentInput" placeholder="Enter your text here...">${nodeText}</textarea>
            </div>

            <div class="button-group">
                <button class="btn-save">Save</button>
                <button class="btn-delete">Delete Node</button>
                <button class="btn-cancel">Cancel</button>
            </div>
        `;

        document.body.appendChild(modal);

        const nameInput = modal.querySelector('#nodeNameInput');
        const contentInput = modal.querySelector('#nodeContentInput');
        nameInput.focus();

        modal.querySelector('.btn-save').onclick = async () => {
            const newName = nameInput.value.trim();
            const newContent = contentInput.value;

            if (newName) {
                await this.updateNode(node, newName, newContent);
            }
            document.body.removeChild(modal);
        };

        modal.querySelector('.btn-delete').onclick = async () => {
            if (confirm(`Delete node "${node.title}"?`)) {
                await this.deleteNode(node);
                document.body.removeChild(modal);
            }
        };

        modal.querySelector('.btn-cancel').onclick = () => {
            document.body.removeChild(modal);
        };
    }

    async createNewCluster() {
        const existingModal = document.querySelector('.create-modal');
        if (existingModal) existingModal.remove();

        const modal = document.createElement('div');
        modal.className = 'create-modal';
        modal.style.left = '50%';
        modal.style.top = '50%';
        modal.style.transform = 'translate(-50%, -50%)';

        modal.innerHTML = `
            <h3>Create New Cluster</h3>
            <input type="text" id="newClusterName" placeholder="Enter cluster name..." />
            <div class="button-group">
                <button class="btn-save">Create</button>
                <button class="btn-cancel">Cancel</button>
            </div>
        `;

        document.body.appendChild(modal);

        const nameInput = modal.querySelector('#newClusterName');
        nameInput.focus();

        modal.querySelector('.btn-save').onclick = async () => {
            const name = nameInput.value.trim();
            if (!name) return;

            try {
                const newCluster = {
                    sheet_id: this.currentCollectionId,
                    cluster_label: this.clusters.length,
                    name: name,
                    user_defined_name: name,
                    color: this.colors[this.clusters.length % this.colors.length],
                    node_count: 0
                };

                const response = await this.fetchAPI('/clusters', 'POST', newCluster);

                newCluster._id = response._id || response.id;
                newCluster.id = newCluster._id;
                newCluster.x = this.width / 2 + (Math.random() - 0.5) * 200;
                newCluster.y = this.height / 2 + (Math.random() - 0.5) * 200;
                newCluster.radius = this.CLUSTER_RADIUS;
                this.clusters.push(newCluster);

                this.render();

            } catch (error) {
                console.error('Failed to create cluster:', error);
            }

            document.body.removeChild(modal);
        };

        modal.querySelector('.btn-cancel').onclick = () => {
            document.body.removeChild(modal);
        };

        nameInput.onkeydown = (e) => {
            if (e.key === 'Enter') {
                modal.querySelector('.btn-save').click();
            } else if (e.key === 'Escape') {
                document.body.removeChild(modal);
            }
        };
    }

    async createNewNode() {
        if (this.clusters.length === 0) {
            alert('Please create a cluster first!');
            return;
        }

        const existingModal = document.querySelector('.create-modal');
        if (existingModal) existingModal.remove();

        const modal = document.createElement('div');
        modal.className = 'create-modal';
        modal.style.left = '50%';
        modal.style.top = '50%';
        modal.style.transform = 'translate(-50%, -50%)';

        const clusterOptions = this.clusters.map(c => 
            `<option value="${c.id || c._id}">${c.name || c.user_defined_name || 'Cluster ' + c.cluster_label}</option>`
        ).join('');

        modal.innerHTML = `
            <h3>Create New Node</h3>
            <input type="text" id="newNodeName" placeholder="Enter node name..." />
            <select id="nodeClusterSelect">
                <option value="">Select Cluster</option>
                ${clusterOptions}
            </select>
            <div class="button-group">
                <button class="btn-save">Create</button>
                <button class="btn-cancel">Cancel</button>
            </div>
        `;

        document.body.appendChild(modal);

        const nameInput = modal.querySelector('#newNodeName');
        const clusterSelect = modal.querySelector('#nodeClusterSelect');
        nameInput.focus();

        modal.querySelector('.btn-save').onclick = async () => {
            const name = nameInput.value.trim();
            const clusterId = clusterSelect.value;

            if (!name || !clusterId) {
                alert('Please enter a name and select a cluster');
                return;
            }

            const cluster = this.clusters.find(c => (c.id || c._id) === clusterId);
            if (!cluster) return;

            try {
                const newNode = await this.fetchAPI('/nodes', 'POST', {
                    cluster_id: clusterId,
                    title: name,
                    content: { text: '' },
                    summary: '',
                    position: { 
                        x: cluster.x + (Math.random() - 0.5) * 80, 
                        y: cluster.y + (Math.random() - 0.5) * 80 
                    },
                    color: cluster.color,
                    similar_to: []
                });

                newNode.cluster = cluster;
                newNode.cluster_id = clusterId;
                newNode.radius = this.NODE_RADIUS;
                this.nodes.push(newNode);

                this.render();

            } catch (error) {
                console.error('Failed to create node:', error);
            }

            document.body.removeChild(modal);
        };

        modal.querySelector('.btn-cancel').onclick = () => {
            document.body.removeChild(modal);
        };

        nameInput.onkeydown = (e) => {
            if (e.key === 'Enter') {
                modal.querySelector('.btn-save').click();
            } else if (e.key === 'Escape') {
                document.body.removeChild(modal);
            }
        };
    }

    async updateClusterName(cluster, newName) {
        try {
            await this.fetchAPI(`/clusters/${cluster.id || cluster._id}`, 'PUT', {
                name: newName,
                user_defined_name: newName
            });

            cluster.name = newName;
            cluster.user_defined_name = newName;

            this.renderClusters();

        } catch (error) {
            console.error('Failed to update cluster:', error);
        }
    }

    async updateNode(node, newName, newContent) {
        try {
            await this.fetchAPI(`/nodes/${node.id || node._id}`, 'PUT', {
                title: newName,
                content: { text: newContent }
            });

            node.title = newName;
            if (!node.content) node.content = {};
            node.content.text = newContent;

            this.renderNodes();

        } catch (error) {
            console.error('Failed to update node:', error);
        }
    }

    async deleteCluster(cluster) {
        try {
            const nodesToDelete = this.nodes.filter(n => n.cluster_id === (cluster.id || cluster._id));

            for (let node of nodesToDelete) {
                await this.fetchAPI(`/nodes/${node.id || node._id}`, 'DELETE');
            }

            await this.fetchAPI(`/clusters/${cluster.id || cluster._id}`, 'DELETE');

            this.clusters = this.clusters.filter(c => (c.id || c._id) !== (cluster.id || cluster._id));
            this.nodes = this.nodes.filter(n => n.cluster_id !== (cluster.id || cluster._id));

            this.render();

        } catch (error) {
            console.error('Failed to delete cluster:', error);
        }
    }

    async deleteNode(node) {
        try {
            await this.fetchAPI(`/nodes/${node.id || node._id}`, 'DELETE');

            this.nodes = this.nodes.filter(n => (n.id || n._id) !== (node.id || node._id));

            this.render();

        } catch (error) {
            console.error('Failed to delete node:', error);
        }
    }

    showTooltip(event, node) {
        const tooltip = d3.select("#tooltip");
        const content = node.content?.text || 'No content';
        const preview = content.length > 150 ? content.substring(0, 150) + '...' : content;

        tooltip.html(`
            <strong>${node.title || 'Untitled'}</strong><br/>
            <em>Cluster: ${node.cluster?.name || 'Unknown'}</em><br/>
            ${preview}
        `)
        .style("left", (event.pageX + 10) + "px")
        .style("top", (event.pageY - 10) + "px")
        .classed("visible", true);
    }

    hideTooltip() {
        d3.select("#tooltip").classed("visible", false);
    }

    // FIXED: Search only cluster names and node titles (NOT content text)
    filterItems(searchTerm) {
        if (!searchTerm) {
            // Reset all to normal
            d3.selectAll(".cluster-group")
                .classed("search-blink", false)
                .style("opacity", 1)
                .style("filter", null);

            d3.selectAll(".node-group")
                .classed("search-blink", false)
                .style("opacity", 1)
                .style("filter", null);

            return;
        }

        const term = searchTerm.toLowerCase();

        // Search clusters by NAME only
        this.g.selectAll(".cluster-group")
            .each(function(d) {
                const name = (d.name || d.user_defined_name || '').toLowerCase();
                const matches = name.includes(term);

                d3.select(this)
                    .classed("search-blink", matches) // Blinking effect
                    .style("opacity", matches ? 1 : 0.2)
                    .style("filter", matches ? null : null);
            });

        // Search nodes by TITLE only (NOT content)
        this.g.selectAll(".node-group")
            .each(function(d) {
                const title = (d.title || '').toLowerCase();
                const matches = title.includes(term); // Only search title, not content

                d3.select(this)
                    .classed("search-blink", matches) // Blinking effect
                    .style("opacity", matches ? 1 : 0.2)
                    .style("filter", matches ? null : null);
            });
    }

    handleResize() {
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.svg.attr("width", this.width).attr("height", this.height);
        if (this.simulation) {
            this.simulation.alpha(0.3).restart();
        }
    }

    async fetchAPI(endpoint, method = 'GET', data = null) {
        const url = this.API_BASE + endpoint;
        console.log(`API ${method} ${url}`, data ? data : '');

        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };

        if (data) options.body = JSON.stringify(data);

        const response = await fetch(url, options);

        if (!response.ok) {
            throw new Error(`API call failed: ${response.status} ${response.statusText}`);
        }

        if (method === 'DELETE') return null;
        const result = await response.json();
        console.log('API response:', result);
        return result;
    }

    hideLoading() {
        d3.select("#loading").style("display", "none");
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing Infinite Desk...');
    new InfiniteDesk();
});