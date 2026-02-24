/**
 * API Service Layer
 * Centralized location for all backend API calls
 */

// Normalize base URL: default to backend root, and strip a trailing '/api' if present
const rawBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_BASE_URL = rawBaseUrl.replace(/\/api\/?$/, '');

// Helper function to get auth token
const getAuthToken = () => localStorage.getItem('access_token');
const getRefreshToken = () => localStorage.getItem('refresh_token');

// Helper function to make API requests
const apiCall = async (endpoint, options = {}) => {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add auth token if available
  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle unauthorized: try refresh if refresh token present
  if (response.status === 401) {
    const refresh = getRefreshToken();
    if (refresh) {
      // Attempt refresh synchronously (best-effort)
      try {
        const r = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refresh }),
        });

        if (r.ok) {
          const d = await r.json();
          localStorage.setItem('access_token', d.access_token);
          localStorage.setItem('refresh_token', d.refresh_token);
          // retry original request with new token
          headers['Authorization'] = `Bearer ${d.access_token}`;
          const retryResp = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers,
          });
          const retryData = await retryResp.json();
          if (!retryResp.ok) throw new Error(retryData.message || 'API Error');
          return retryData;
        }
      } catch (e) {
        // fallthrough to logout
      }
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  }

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.message || 'API Error');
  }

  return data;
};

// ==================== AUTH ENDPOINTS ====================

export const authAPI = {
  // Register new user
  register: (email, password) =>
    apiCall('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  // Login user
  login: (email, password) =>
    apiCall('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  // Get current user info
  getCurrentUser: () => apiCall('/auth/me', { method: 'GET' }),
};

// ==================== TREE ENDPOINTS ====================

export const treeAPI = {
  // Get all saved trees
  getTrees: () => apiCall('/trees', { method: 'GET' }),

  // Create new tree
  createTree: (name) =>
    apiCall('/trees', {
      method: 'POST',
      body: JSON.stringify({ name }),
    }),

  // Get tree by ID
  getTree: (treeId) => apiCall(`/trees/${treeId}`, { method: 'GET' }),

  // Update tree name
  updateTree: (treeId, name) =>
    apiCall(`/trees/${treeId}`, {
      method: 'PUT',
      body: JSON.stringify({ name }),
    }),

  // Delete tree
  deleteTree: (treeId) =>
    apiCall(`/trees/${treeId}`, { method: 'DELETE' }),

  // ======== Tree Operations ========

  // Insert node
  insertNode: (treeId, parentValue, newValue, direction) =>
    apiCall(`/trees/${treeId}/insert`, {
      method: 'POST',
      body: JSON.stringify({ parent_value: parentValue, new_value: newValue, direction }),
    }),

  // Delete node
  deleteNode: (treeId, value) =>
    apiCall(`/trees/${treeId}/delete`, {
      method: 'POST',
      body: JSON.stringify({ value }),
    }),

  // Update node value
  updateNode: (treeId, nodeId, newValue) =>
    apiCall(`/trees/${treeId}/update`, {
      method: 'POST',
      body: JSON.stringify({ node_id: nodeId, new_value: newValue }),
    }),

  // Search node
  searchNode: (treeId, value) =>
    apiCall(`/trees/${treeId}/search`, {
      method: 'POST',
      body: JSON.stringify({ value }),
    }),

  // Get tree traversal (for visualization)
  getTraversal: (treeId, traversalType = 'inorder') =>
    apiCall(`/trees/${treeId}/traversal?type=${traversalType}`, {
      method: 'GET',
    }),

  // Reset tree (delete all nodes)
  resetTree: (treeId) =>
    apiCall(`/trees/${treeId}/reset`, {
      method: 'POST',
    }),
};

// ==================== CHAT ENDPOINTS ====================

export const chatAPI = {
  // Send message to AI chat
  sendMessage: (treeId, message) =>
    apiCall('/chat', {
      method: 'POST',
      body: JSON.stringify({ tree_id: treeId, message }),
    }),

  // Get chat history
  getChatHistory: (treeId) =>
    apiCall(`/chat/history/${treeId}`, { method: 'GET' }),

  // Clear chat history
  clearChat: (treeId) =>
    apiCall(`/chat/history/${treeId}`, { method: 'DELETE' }),
};

export default apiCall;
