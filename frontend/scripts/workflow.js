// Workflow Page JavaScript

// Intersection Observer for animations
const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.classList.add('animate');
            }, index * 150);
        }
    });
}, {
    threshold: 0.15,
    rootMargin: '0px 0px -100px 0px'
});

document.querySelectorAll('.workflow-item').forEach(el => observer.observe(el));

// Enhanced visualization creation
function createEnhancedViz(id, config) {
    const container = document.getElementById(id);
    if (!container) return;
    
    const width = container.offsetWidth;
    const height = container.offsetHeight;
    const svg = container.querySelector('.links-svg');
    
    // Add cluster glows
    config.nodes.forEach((node, i) => {
        const glow = document.createElement('div');
        glow.className = 'cluster-glow';
        glow.style.left = (node.x * width - 80) + 'px';
        glow.style.top = (node.y * height - 80) + 'px';
        glow.style.width = '160px';
        glow.style.height = '160px';
        glow.style.animationDelay = (i * 0.5) + 's';
        container.appendChild(glow);
    });
    
    // Create nodes
    config.nodes.forEach((node, i) => {
        const nodeGroup = document.createElement('div');
        nodeGroup.className = 'node-group';
        nodeGroup.style.left = (node.x * width) + 'px';
        nodeGroup.style.top = (node.y * height) + 'px';
        nodeGroup.style.animationDelay = (i * 0.3) + 's';
        
        const circle = document.createElement('div');
        circle.className = 'node-circle';
        circle.style.backgroundColor = node.color;
        circle.style.borderColor = node.border;
        circle.style.color = node.color;
        
        nodeGroup.appendChild(circle);
        container.appendChild(nodeGroup);
        
        setTimeout(() => nodeGroup.style.opacity = '1', i * 200);
    });

    // Draw enhanced links
    if (config.links) {
        setTimeout(() => {
            config.links.forEach((link, i) => {
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', link.x1 * width);
                line.setAttribute('y1', link.y1 * height);
                line.setAttribute('x2', link.x2 * width);
                line.setAttribute('y2', link.y2 * height);
                line.setAttribute('class', 'node-link');
                line.style.animationDelay = (i * 0.2) + 's';
                svg.appendChild(line);
            });
        }, 800);
    }
}

// Initialize visualizations with enhanced configs
setTimeout(() => {
    createEnhancedViz('viz1', {
        nodes: [{ x: 0.5, y: 0.5, color: '#00f2ff', border: '#00b4d8' }]
    });
    
    createEnhancedViz('viz2', {
        nodes: [
            { x: 0.25, y: 0.4, color: '#6366f1', border: '#4f46e5' },
            { x: 0.5, y: 0.3, color: '#f59e0b', border: '#d97706' },
            { x: 0.75, y: 0.5, color: '#10b981', border: '#059669' },
            { x: 0.5, y: 0.7, color: '#ec4899', border: '#db2777' }
        ]
    });
    
    createEnhancedViz('viz3', {
        nodes: [
            { x: 0.3, y: 0.5, color: '#6366f1', border: '#4f46e5' },
            { x: 0.7, y: 0.5, color: '#00f2ff', border: '#00b4d8' }
        ]
    });
    
    createEnhancedViz('viz4', {
        nodes: [
            { x: 0.35, y: 0.5, color: '#00f2ff', border: '#00b4d8' },
            { x: 0.65, y: 0.5, color: '#fcd34d', border: '#f59e0b' }
        ]
    });
    
    createEnhancedViz('viz5', {
        nodes: [
            { x: 0.3, y: 0.5, color: '#a78bfa', border: '#8b5cf6' },
            { x: 0.7, y: 0.5, color: '#00f2ff', border: '#00b4d8' }
        ]
    });
    
    createEnhancedViz('viz6', {
        nodes: [
            { x: 0.2, y: 0.35, color: '#ec4899', border: '#db2777' },
            { x: 0.35, y: 0.55, color: '#ec4899', border: '#db2777' },
            { x: 0.5, y: 0.4, color: '#ec4899', border: '#db2777' },
            { x: 0.65, y: 0.5, color: '#6366f1', border: '#4f46e5' },
            { x: 0.8, y: 0.45, color: '#6366f1', border: '#4f46e5' }
        ],
        links: [
            { x1: 0.2, y1: 0.35, x2: 0.35, y2: 0.55 },
            { x1: 0.35, y1: 0.55, x2: 0.5, y2: 0.4 },
            { x1: 0.65, y1: 0.5, x2: 0.8, y2: 0.45 }
        ]
    });
    
    createEnhancedViz('viz7', {
        nodes: [{ x: 0.5, y: 0.5, color: '#10b981', border: '#059669' }]
    });
    
    createEnhancedViz('viz8', {
        nodes: [
            { x: 0.25, y: 0.4, color: '#00f2ff', border: '#00b4d8' },
            { x: 0.5, y: 0.5, color: '#fcd34d', border: '#f59e0b' },
            { x: 0.75, y: 0.6, color: '#10b981', border: '#059669' }
        ],
        links: [
            { x1: 0.25, y1: 0.4, x2: 0.5, y2: 0.5 },
            { x1: 0.5, y1: 0.5, x2: 0.75, y2: 0.6 }
        ]
    });
    
    createEnhancedViz('viz9', {
        nodes: [{ x: 0.5, y: 0.5, color: '#ef4444', border: '#dc2626' }]
    });
    
    createEnhancedViz('viz10', {
        nodes: [
            { x: 0.25, y: 0.4, color: '#ec4899', border: '#db2777' },
            { x: 0.5, y: 0.5, color: '#6366f1', border: '#4f46e5' },
            { x: 0.75, y: 0.6, color: '#10b981', border: '#059669' }
        ],
        links: [
            { x1: 0.25, y1: 0.4, x2: 0.75, y2: 0.6 },
            { x1: 0.25, y1: 0.4, x2: 0.5, y2: 0.5 },
            { x1: 0.5, y1: 0.5, x2: 0.75, y2: 0.6 }
        ]
    });
}, 200);
