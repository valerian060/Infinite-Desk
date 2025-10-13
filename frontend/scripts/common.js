// Common JavaScript for All Pages

// Generate Starfield
function generateStarfield(count = 150) {
    const starfield = document.getElementById('starfield');
    if (!starfield) return;
    
    for (let i = 0; i < count; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.animationDelay = Math.random() * 10 + 's';
        starfield.appendChild(star);
    }
}

// Initialize starfield
generateStarfield();
