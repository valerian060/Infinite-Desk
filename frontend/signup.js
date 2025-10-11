// Signup functionality with API backend
const API_BASE = 'http://127.0.0.1:8000/api';

document.getElementById('signupForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('signupConfirmPassword').value;
    const agreeTerms = document.getElementById('agreeTerms').checked;
    const messageElement = document.getElementById('signupMessage');
    const submitBtn = document.getElementById('signupSubmitBtn');
    const btnText = document.getElementById('signupBtnText');
    const spinner = document.getElementById('signupSpinner');
    
    // Clear previous message
    messageElement.textContent = '';
    messageElement.className = 'message';
    
    // Validation
    if (password !== confirmPassword) {
        messageElement.textContent = 'Passwords do not match!';
        messageElement.classList.add('error');
        return;
    }
    
    if (password.length < 6) {
        messageElement.textContent = 'Password must be at least 6 characters long!';
        messageElement.classList.add('error');
        return;
    }
    
    if (!agreeTerms) {
        messageElement.textContent = 'Please agree to the Terms & Conditions!';
        messageElement.classList.add('error');
        return;
    }
    
    // Show loading state
    submitBtn.disabled = true;
    btnText.classList.add('hidden');
    spinner.classList.remove('hidden');
    
    try {
        // Call backend API
        const response = await fetch(`${API_BASE}/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Success! Auto-login
            localStorage.setItem('infiniteDeskUser', JSON.stringify({
                id: data.user.id,
                email: data.user.email,
                name: data.user.name,
                loggedIn: true
            }));
            
            // Show success
            messageElement.textContent = 'Account created! Redirecting...';
            messageElement.classList.add('success');
            
            // Redirect
            setTimeout(() => {
                window.location.href = 'frontend/index.html';
            }, 1500);
            
        } else {
            throw new Error(data.detail || 'Signup failed');
        }
        
    } catch (error) {
        messageElement.textContent = error.message || 'Failed to create account';
        messageElement.classList.add('error');
        
        // Reset button
        submitBtn.disabled = false;
        btnText.classList.remove('hidden');
        spinner.classList.add('hidden');
    }
});
