import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../redux/authSlice';
import { treeAPI } from '../services/api';
import '../styles/navbar.css';

/**
 * Navbar Component
 * Displays app title, action buttons (Save/Load/Share/Settings), theme toggle, user info, and logout
 */
function Navbar() {
  const dispatch = useDispatch();
  const { user, isAuthenticated } = useSelector((state) => state.auth);
  const { selectedTree } = useSelector((state) => state.tree);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);

  // Initialize theme from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setIsDarkMode(savedTheme === 'dark');
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  // Toggle theme
  const handleThemeToggle = () => {
    const newTheme = isDarkMode ? 'light' : 'dark';
    setIsDarkMode(!isDarkMode);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  // Handle logout
  const handleLogout = () => {
    dispatch(logout());
  };

  // Handle save tree
  const handleSaveTree = async () => {
    if (!selectedTree) {
      alert('Please select a tree first');
      return;
    }
    
    try {
      const response = await treeAPI.getTree(selectedTree.id);
      const dataStr = JSON.stringify(response, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `tree-${selectedTree.name}-${Date.now()}.json`;
      link.click();
      URL.revokeObjectURL(url);
      alert('Tree saved successfully!');
    } catch (error) {
      alert('Failed to save tree');
      console.error(error);
    }
  };

  // Handle load tree (opens file dialog)
  const handleLoadTree = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target.result);
          console.log('Loaded tree data:', data);
          alert('Tree data loaded. Please create a tree with this structure.');
        } catch (error) {
          alert('Failed to load tree file');
          console.error(error);
        }
      };
      reader.readAsText(file);
    };
    input.click();
  };

  // Handle share tree
  const handleShareTree = () => {
    if (!selectedTree) {
      alert('Please select a tree first');
      return;
    }
    setShowShareModal(true);
  };

  // Copy share link to clipboard
  const handleCopyShareLink = () => {
    const shareLink = `${window.location.origin}?tree=${selectedTree.id}`;
    navigator.clipboard.writeText(shareLink);
    alert('Share link copied to clipboard!');
  };

  return (
    <nav className="navbar">
      {/* App Title */}
      <div className="navbar-brand">
        <span className="navbar-brand-icon">🌳</span>
        <span>Tree AI</span>
      </div>

      {/* Center Action Buttons */}
      {isAuthenticated && (
        <div className="navbar-actions-center">
          <button
            className="navbar-action-btn"
            onClick={handleSaveTree}
            title="Save tree as JSON"
            disabled={!selectedTree}
          >
            💾 Save Tree
          </button>
          <button
            className="navbar-action-btn"
            onClick={handleLoadTree}
            title="Load tree from JSON"
          >
            📂 Load Tree
          </button>
          <button
            className="navbar-action-btn"
            onClick={handleShareTree}
            title="Share tree"
            disabled={!selectedTree}
          >
            🔗 Share
          </button>
        </div>
      )}

      {/* User Info */}
      {isAuthenticated && (
        <div className="navbar-user-info">
          <span>👤 {user?.email || 'User'}</span>
        </div>
      )}

      {/* Navbar Actions */}
      <div className="navbar-actions">
        {/* Theme Toggle Button */}
        <button
          className="theme-toggle"
          onClick={handleThemeToggle}
          title="Toggle theme"
        >
          {isDarkMode ? '☀️' : '🌙'}
        </button>

        {/* Settings Button */}
        {isAuthenticated && (
          <button
            className="theme-toggle"
            onClick={() => setShowSettings(!showSettings)}
            title="Settings"
          >
            ⚙️
          </button>
        )}

        {/* Logout Button */}
        {isAuthenticated && (
          <button className="btn btn-secondary btn-sm" onClick={handleLogout}>
            Logout
          </button>
        )}
      </div>

      {/* Share Modal */}
      {showShareModal && (
        <div className="modal-overlay" onClick={() => setShowShareModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Share Tree</h3>
            <p>Share this tree with others:</p>
            <div className="share-link-container">
              <input
                type="text"
                readOnly
                value={`${window.location.origin}?tree=${selectedTree?.id}`}
                className="share-link-input"
              />
              <button
                className="btn btn-primary btn-sm"
                onClick={handleCopyShareLink}
              >
                Copy Link
              </button>
            </div>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setShowShareModal(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}

export default Navbar;
