import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  setTrees,
  setSelectedTree,
  setTreeVisualization,
  clearTree,
  renameTree,
} from '../redux/treeSlice';
import { treeAPI } from '../services/api';
import { convertTreeToFlowData } from '../utils/treeUtils';
import TreeCanvas from '../components/TreeCanvas';
import ManualControls from '../components/ManualControls';
import ChatPanel from '../components/ChatPanel';
import Navbar from '../components/Navbar';
import TreeListPanel from '../components/TreeListPanel';
import '../styles/dashboard.css';
import '../styles/tree-list-panel.css';

/**
 * Dashboard Page
 * Main application page with tree operations, visualization, and AI chat
 * Layout:
 * - Top: Navbar with action buttons
 * - Main: three panels (Controls+TreeList | Canvas | Chat)
 */
function Dashboard() {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const { isAuthenticated } = useSelector((state) => state.auth);
  const { trees, selectedTree } = useSelector((state) => state.tree);

  const [newTreeName, setNewTreeName] = useState('');
  const [renameValue, setRenameValue] = useState('');
  const [renamingTreeId, setRenamingTreeId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mobilePanel, setMobilePanel] = useState('tree'); // 'tree', 'canvas', 'chat'
  const [leftPanelView, setLeftPanelView] = useState('create'); // 'create', 'manual' - for left panel sections

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // Initial load of trees
  useEffect(() => {
    const loadTrees = async () => {
      setLoading(true);
      try {
        const response = await treeAPI.getTrees();
        dispatch(setTrees(response));
      } catch (error) {
        console.error('Error loading trees:', error);
      } finally {
        setLoading(false);
      }
    };

    loadTrees();
  }, [dispatch]);

  // Create new tree session
  const handleCreateTree = async () => {
    if (!newTreeName.trim()) {
      alert('Please enter a tree name');
      return;
    }

    setLoading(true);
    try {
      await treeAPI.createTree(newTreeName);
      setNewTreeName('');

      const response = await treeAPI.getTrees();
      dispatch(setTrees(response));
    } catch (error) {
      console.error('Failed to create tree:', error);
      alert('Failed to create tree');
    } finally {
      setLoading(false);
    }
  };

  // Select a tree and load its structure
  const handleSelectTree = async (tree) => {
    dispatch(setSelectedTree(tree));
    
    // Auto-switch to manual controls view when tree is selected
    setLeftPanelView('manual');

    try {
      const response = await treeAPI.getTree(tree.id);
      const treeData = response.tree_data;

      const { nodes, edges } = convertTreeToFlowData(treeData);
      dispatch(setTreeVisualization({ nodes, edges }));
    } catch (error) {
      console.error('Error loading tree:', error);
    }
  };

  // Delete a tree
  const handleDeleteTree = async (treeId, event) => {
    event.stopPropagation();

    const confirmed = window.confirm('Are you sure you want to delete this tree?');
    if (!confirmed) return;

    setLoading(true);
    try {
      await treeAPI.deleteTree(treeId);
      if (selectedTree?.id === treeId) {
        dispatch(clearTree());
      }
      const response = await treeAPI.getTrees();
      dispatch(setTrees(response));
    } catch (error) {
      console.error('Failed to delete tree:', error);
      alert('Failed to delete tree');
    } finally {
      setLoading(false);
    }
  };

  // Start inline rename
  const startRename = (tree, event) => {
    event.stopPropagation();
    setRenamingTreeId(tree.id);
    setRenameValue(tree.name);
  };

  // Save new tree name
  const handleRenameTree = async (treeId, event) => {
    event.stopPropagation();

    if (!renameValue.trim()) {
      alert('Please enter a new name');
      return;
    }

    setLoading(true);
    try {
      await treeAPI.updateTree(treeId, renameValue);
      dispatch(renameTree({ treeId, newName: renameValue }));
      setRenamingTreeId(null);
      setRenameValue('');
    } catch (error) {
      console.error('Failed to rename tree:', error);
      alert('Failed to rename tree');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-root">
      <Navbar />

      <div className="dashboard-layout">
        {/* LEFT PANEL - Controls + Tree List */}
        <section className={`dashboard-panel dashboard-panel-left ${mobilePanel === 'tree' ? 'mobile-active' : 'mobile-hidden'}`}>
          {/* Left Panel Section Selector (for mobile/tablet) */}
          <div className="left-panel-selector">
            <button
              className={`left-panel-btn ${leftPanelView === 'create' ? 'active' : ''}`}
              onClick={() => setLeftPanelView('create')}
              title="Back to tree list"
            >
              🌳 Trees
            </button>
            <button
              className={`left-panel-btn ${leftPanelView === 'manual' ? 'active' : ''}`}
              onClick={() => setLeftPanelView('manual')}
              disabled={!selectedTree}
              title="Manual entries (select a tree first)"
            >
              ⚙️ Manual
            </button>
          </div>

          {/* Create/Tree List Section */}
          <div className={`left-panel-content create-section ${leftPanelView !== 'create' ? 'mobile-hidden-section' : ''}`}>
            <TreeListPanel
              trees={trees}
              selectedTree={selectedTree}
              loading={loading}
              newTreeName={newTreeName}
              renameValue={renameValue}
              renamingTreeId={renamingTreeId}
              onNewTreeNameChange={setNewTreeName}
              onCreateTree={handleCreateTree}
              onSelectTree={handleSelectTree}
              onDeleteTree={handleDeleteTree}
              onStartRename={startRename}
              onRenameTree={handleRenameTree}
              onCancelRename={() => {
                setRenamingTreeId(null);
                setRenameValue('');
              }}
              onRenameValueChange={setRenameValue}
            />
          </div>

          {/* Manual Entries Section with Back Button */}
          <div className={`left-panel-content manual-section ${leftPanelView !== 'manual' ? 'mobile-hidden-section' : ''}`}>
            {/* Back button visible on desktop when in manual view */}
            {selectedTree && (
              <div className="manual-section-header">
                <button 
                  className="back-to-trees-btn"
                  onClick={() => setLeftPanelView('create')}
                  title="Back to tree list"
                >
                  ← Back to Trees
                </button>
                <span className="selected-tree-name">{selectedTree.name}</span>
              </div>
            )}
            <ManualControls />
          </div>
        </section>

        {/* CENTER PANEL - Tree Canvas */}
        <section className={`dashboard-panel dashboard-panel-center ${mobilePanel === 'canvas' ? 'mobile-active' : 'mobile-hidden'}`}>
          <TreeCanvas />
        </section>

        {/* RIGHT PANEL - Chat */}
        <section className={`dashboard-panel dashboard-panel-right ${mobilePanel === 'chat' ? 'mobile-active' : 'mobile-hidden'}`}>
          <ChatPanel />
        </section>
      </div>

      {/* Mobile Navigation Bar */}
      <div className="mobile-nav-bar">
        <button 
          className={`mobile-nav-btn ${mobilePanel === 'tree' ? 'active' : ''}`}
          onClick={() => setMobilePanel('tree')}
          title="Trees & Controls"
        >
          🌳
        </button>
        <button 
          className={`mobile-nav-btn ${mobilePanel === 'canvas' ? 'active' : ''}`}
          onClick={() => setMobilePanel('canvas')}
          title="Tree Visualization"
        >
          📊
        </button>
        <button 
          className={`mobile-nav-btn ${mobilePanel === 'chat' ? 'active' : ''}`}
          onClick={() => setMobilePanel('chat')}
          title="AI Chat"
        >
          💬
        </button>
      </div>
    </div>
  );
}

export default Dashboard;
