// Index Page JavaScript

// Generate Floating Dots
const section1 = document.getElementById('section1');
if (section1) {
    const dotCount = 20;
    for (let i = 0; i < dotCount; i++) {
        const dot = document.createElement('div');
        dot.className = 'floating-dot';
        dot.style.left = Math.random() * 100 + '%';
        dot.style.animationDuration = (15 + Math.random() * 20) + 's';
        dot.style.animationDelay = Math.random() * 10 + 's';
        section1.appendChild(dot);
    }
}

// Wrap each letter in span for hover effect
const brandTitle = document.getElementById('brandTitle');
if (brandTitle) {
    const text = brandTitle.textContent;
    brandTitle.innerHTML = '';
    for (let char of text) {
        const span = document.createElement('span');
        span.textContent = char;
        if (char === ' ') {
            span.style.width = '0.3em';
        }
        brandTitle.appendChild(span);
    }
}

// Change starfield opacity based on scroll position
window.addEventListener('scroll', () => {
    const scrollPosition = window.scrollY;
    const windowHeight = window.innerHeight;
    const starfield = document.getElementById('starfield');
    
    if (!starfield) return;
    
    if (scrollPosition < windowHeight) {
        starfield.className = 'star-field section-1';
    } else if (scrollPosition < windowHeight * 2) {
        starfield.className = 'star-field section-2';
    } else if (scrollPosition < windowHeight * 3) {
        starfield.className = 'star-field section-3';
    } else {
        starfield.className = 'star-field section-4';
    }
});

// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.2,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate');
        }
    });
}, observerOptions);

// Observe all animated elements
document.querySelectorAll('.section-heading, .intro-text, .feature-item, .step-item, .process-step, .visualization-area').forEach(el => {
    observer.observe(el);
});

// Create visualization nodes with connecting lines
function createVisualization(containerId, config) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const width = container.offsetWidth;
    const height = container.offsetHeight;
    const svg = container.querySelector('.links-svg');
    const allNodes = [];

    config.clusters.forEach((cluster, clusterIdx) => {
        const clusterX = cluster.x * width;
        const clusterY = cluster.y * height;
        
        const label = document.createElement('div');
        label.className = 'cluster-label';
        label.textContent = cluster.name;
        label.style.left = clusterX + 'px';
        label.style.top = (clusterY - 30) + 'px';
        container.appendChild(label);

        cluster.nodes.forEach((node, nodeIdx) => {
            const nodeGroup = document.createElement('div');
            nodeGroup.className = 'node-group';
            
            const angle = (nodeIdx / cluster.nodes.length) * 2 * Math.PI;
            const radius = 60;
            const nodeX = clusterX + Math.cos(angle) * radius;
            const nodeY = clusterY + Math.sin(angle) * radius;
            
            nodeGroup.style.left = nodeX + 'px';
            nodeGroup.style.top = nodeY + 'px';
            
            const circle = document.createElement('div');
            circle.className = 'node-circle';
            circle.style.backgroundColor = cluster.color;
            circle.style.borderColor = cluster.borderColor;
            
            nodeGroup.appendChild(circle);
            container.appendChild(nodeGroup);

            allNodes.push({ x: nodeX + 8, y: nodeY + 8, cluster: clusterIdx });

            setTimeout(() => {
                nodeGroup.style.opacity = '1';
            }, nodeIdx * 100);
        });
    });

    setTimeout(() => {
        allNodes.forEach((node, i) => {
            allNodes.forEach((otherNode, j) => {
                if (i < j) {
                    const distance = Math.sqrt(
                        Math.pow(node.x - otherNode.x, 2) + 
                        Math.pow(node.y - otherNode.y, 2)
                    );
                    
                    if (distance < 150) {
                        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                        line.setAttribute('x1', node.x);
                        line.setAttribute('y1', node.y);
                        line.setAttribute('x2', otherNode.x);
                        line.setAttribute('y2', otherNode.y);
                        line.setAttribute('class', 'node-link');
                        svg.appendChild(line);
                    }
                }
            });
        });
    }, 500);
}

// Initialize visualizations
setTimeout(() => {
    createVisualization('viz1', {
        clusters: [
            { name: 'Ideas', x: 0.3, y: 0.5, color: '#6366f1', borderColor: '#4f46e5', nodes: [1, 2, 3, 4, 5] },
            { name: 'Concepts', x: 0.7, y: 0.5, color: '#f59e0b', borderColor: '#d97706', nodes: [1, 2, 3, 4] }
        ]
    });

    createVisualization('viz2', {
        clusters: [
            { name: 'Your Notes', x: 0.5, y: 0.5, color: '#10b981', borderColor: '#059669', nodes: [1, 2, 3, 4, 5, 6] }
        ]
    });

    createVisualization('viz3', {
        clusters: [
            { name: 'Star', x: 0.5, y: 0.5, color: '#00f2ff', borderColor: '#00b4d8', nodes: [1] }
        ]
    });

    createVisualization('viz4', {
        clusters: [
            { name: 'Processing', x: 0.5, y: 0.5, color: '#a78bfa', borderColor: '#8b5cf6', nodes: [1, 2] }
        ]
    });

    createVisualization('viz5', {
        clusters: [
            { name: 'Constellation', x: 0.5, y: 0.5, color: '#ec4899', borderColor: '#db2777', nodes: [1, 2, 3, 4, 5, 6, 7] }
        ]
    });
}, 100);
