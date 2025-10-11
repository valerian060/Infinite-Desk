// Infinite Desk - Authentication Logic

// Simple in-memory user storage (in production, use a real database)
let users = [
    {
        email: 'demo@infinitedesk.com',
        password: 'demo123',
        name: 'Demo User'
    }
];

// Load users from localStorage if available
if (localStorage.getItem('infiniteDeskUsers')) {
    users = JSON.parse(localStorage.getItem('infiniteDeskUsers'));
}

// Tab switching
function switchTab(tab) {
    const loginTab = document.getElementById('loginTab');
    const signupTab = document.getElementById('signupTab');
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const loginError = document.getElementById('loginError');
    const signupError = document.getElementById('signupError');
    const signupSuccess = document.getElementById('signupSuccess');

    // Clear all messages
    loginError.classList.remove('show');
    signupError.classList.remove('show');
    signupSuccess.classList.remove('show');

    if (tab === 'login') {
        loginTab.classList.add('active');
        signupTab.classList.remove('active');
        loginForm.classList.remove('hidden');
        signupForm.classList.add('hidden');
    } else {
        signupTab.classList.add('active');
        loginTab.classList.remove('active');
        signupForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
    }
}

// Login form submission
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const errorElement = document.getElementById('loginError');

    // Find user
    const user = users.find(u => u.email === email && u.password === password);

    if (user) {
        // Success! Store session
        localStorage.setItem('infiniteDeskUser', JSON.stringify({
            email: user.email,
            name: user.name,
            loggedIn: true
        }));

        // Show success message
        errorElement.textContent = 'Login successful! Redirecting...';
        errorElement.style.color = '#2ecc71';
        errorElement.classList.add('show');

        // Redirect to main app after 1 second
        setTimeout(() => {
            window.location.href = 'frontend/index.html';
        }, 1000);

    } else {
        // Error
        errorElement.textContent = 'Invalid email or password. Try demo@infinitedesk.com / demo123';
        errorElement.style.color = '#ff4b2b';
        errorElement.classList.add('show');
    }
});

// Signup form submission
document.getElementById('signupForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const name = document.getElementById('signupName').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('signupConfirmPassword').value;
    const agreeTerms = document.getElementById('agreeTerms').checked;
    const errorElement = document.getElementById('signupError');
    const successElement = document.getElementById('signupSuccess');

    // Clear previous messages
    errorElement.classList.remove('show');
    successElement.classList.remove('show');

    // Validation
    if (password !== confirmPassword) {
        errorElement.textContent = 'Passwords do not match!';
        errorElement.classList.add('show');
        return;
    }

    if (password.length < 6) {
        errorElement.textContent = 'Password must be at least 6 characters long!';
        errorElement.classList.add('show');
        return;
    }

    if (!agreeTerms) {
        errorElement.textContent = 'Please agree to the Terms & Conditions!';
        errorElement.classList.add('show');
        return;
    }

    // Check if user already exists
    const existingUser = users.find(u => u.email === email);
    if (existingUser) {
        errorElement.textContent = 'Email already registered! Please login instead.';
        errorElement.classList.add('show');
        return;
    }

    // Create new user
    const newUser = {
        email: email,
        password: password,
        name: name
    };

    users.push(newUser);

    // Save to localStorage
    localStorage.setItem('infiniteDeskUsers', JSON.stringify(users));

    // Show success message
    successElement.textContent = 'Account created successfully! Logging you in...';
    successElement.classList.add('show');

    // Auto login and redirect
    localStorage.setItem('infiniteDeskUser', JSON.stringify({
        email: newUser.email,
        name: newUser.name,
        loggedIn: true
    }));

    // Redirect after 2 seconds
    setTimeout(() => {
        window.location.href = 'frontend/index.html';
    }, 2000);
});

// Check if already logged in
window.addEventListener('DOMContentLoaded', function() {
    const currentUser = localStorage.getItem('infiniteDeskUser');
    if (currentUser) {
        const user = JSON.parse(currentUser);
        if (user.loggedIn) {
            // Already logged in, redirect to app
            window.location.href = 'frontend/index.html';
        }
    }
});

// Remember me functionality
const rememberCheckbox = document.getElementById('rememberMe');
const loginEmailInput = document.getElementById('loginEmail');

// Load remembered email
if (localStorage.getItem('rememberedEmail')) {
    loginEmailInput.value = localStorage.getItem('rememberedEmail');
    rememberCheckbox.checked = true;
}

// Save email when remember me is checked
document.getElementById('loginForm').addEventListener('submit', function() {
    if (rememberCheckbox.checked) {
        localStorage.setItem('rememberedEmail', loginEmailInput.value);
    } else {
        localStorage.removeItem('rememberedEmail');
    }
});