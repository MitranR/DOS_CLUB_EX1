/* =========================================================
   Hospital Management System - API Client & Session Manager
   Handles backend REST communication and session storage.
   ========================================================= */

// Dynamic API Base: works if opened via FastAPI directly or as separate local static server
const API_BASE = window.location.origin.includes(':8000') 
  ? `${window.location.origin}/api` 
  : 'http://localhost:8000/api';

const TOKEN_KEY = 'hosp_auth_token';
const USER_KEY = 'hosp_auth_user';

// --- Session Helpers ---

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function getUser() {
  const user = localStorage.getItem(USER_KEY);
  return user ? JSON.parse(user) : null;
}

function setSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function isLoggedIn() {
  return !!getToken();
}

// --- Universal API Request Helper ---

async function apiRequest(endpoint, { method = 'GET', body = null, auth = false } = {}) {
  const headers = {
    'Content-Type': 'application/json',
  };

  if (auth) {
    const token = getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const options = {
    method,
    headers,
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.message || 'An error occurred while connecting to backend.');
    }

    return data;
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

// --- UI Alert Helpers ---

function showAlert(alertElId, message, isSuccess = false) {
  const el = document.getElementById(alertElId);
  if (!el) return;

  el.textContent = message;
  el.className = `alert ${isSuccess ? 'alert-success' : 'alert-error'}`;
  el.style.display = 'block';

  el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideAlert(alertElId) {
  const el = document.getElementById(alertElId);
  if (el) {
    el.style.display = 'none';
  }
}

// --- Navbar State Sync Across All Pages ---

function renderNavbar() {
  const navActions = document.getElementById('navActions');
  if (!navActions) return;

  const user = getUser();

  if (user && isLoggedIn()) {
    navActions.innerHTML = `
      <span style="font-weight: 700; font-size: 0.88rem; color: var(--primary-dark); margin-right: 0.35rem;">
        👋 ${user.full_name || user.username}
      </span>
      <a href="profile.html" class="btn btn-outline btn-sm">Profile</a>
      <a href="appointments.html" class="btn btn-outline btn-sm">Bookings</a>
      <button onclick="handleLogout()" class="btn btn-primary btn-sm">Logout</button>
    `;
  } else {
    navActions.innerHTML = `
      <a href="login.html" class="btn btn-outline btn-sm">Login</a>
      <a href="register.html" class="btn btn-green btn-sm">Create Account</a>
    `;
  }

  // Highlight active link in navbar
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}

async function handleLogout() {
  try {
    await apiRequest('/auth/logout', { method: 'POST', auth: true });
  } catch (e) {
    // Continue logout even if server is unreachable
  } finally {
    clearSession();
    window.location.href = 'login.html';
  }
}

// Auto-run navbar render
document.addEventListener('DOMContentLoaded', () => {
  renderNavbar();
});
