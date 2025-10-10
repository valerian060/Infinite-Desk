// Login functionality with API backend
const API_BASE = 'http://127.0.0.1:8000/api';

document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const messageElement = document.getElementById('loginMessage');
    const submitBtn = document.getElementById('loginSubmitBtn');
    const btnText = document.getElementById('loginBtnText');
    const spinner = document.getElementById('loginSpinner');
    
    // Show loading state
    submitBtn.disabled = true;
    btnText.classList.add('hidden');
    spinner.classList.remove('hidden');
    messageElement.textContent = '';
    messageElement.className = 'message';
    
    try {
        // Call backend API
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Success! Store user session
            localStorage.setItem('infiniteDeskUser', JSON.stringify({
                id: data.user.id,
                email: data.user.email,
                name: data.user.name,
                loggedIn: true
            }));
            
            // Remember me
            if (document.getElementById('rememberMe').checked) {
                localStorage.setItem('rememberedEmail', email);
            }
            
            // Show success
            messageElement.textContent = 'Login successful! Redirecting...';
            messageElement.classList.add('success');
            
            // Redirect
            setTimeout(() => {
                window.location.href = 'frontend/index.html';
            }, 1000);
            
        } else {
            throw new Error(data.detail || 'Login failed');
        }
        
    } catch (error) {
        messageElement.textContent = error.message || 'Invalid email or password';
        messageElement.classList.add('error');
        
        // Reset button
        submitBtn.disabled = false;
        btnText.classList.remove('hidden');
        spinner.classList.add('hidden');
    }
});

// Load remembered email
window.addEventListener('DOMContentLoaded', function() {
    if (localStorage.getItem('rememberedEmail')) {
        document.getElementById('loginEmail').value = localStorage.getItem('rememberedEmail');
        document.getElementById('rememberMe').checked = true;
    }
    
    // Check if already logged in
    const currentUser = localStorage.getItem('infiniteDeskUser');
    if (currentUser) {
        const user = JSON.parse(currentUser);
        if (user.loggedIn) {
            window.location.href = 'frontend/index.html';
        }
    }
});
