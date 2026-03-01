import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setHighlightedNode, setTraversalPath, setTreeVisualization } from '../redux/treeSlice';
import { treeAPI } from '../services/api';
import { convertTreeToFlowData } from '../utils/treeUtils';
import '../styles/manual-controls.css';

/**
 * ManualControls Component
 * Provides UI for tree operations:
 * - Insert node (with parent, value, direction)
 * - Delete node
 * - Search node
 * - Reset tree
 */
function ManualControls() {
  const dispatch = useDispatch();
  const { selectedTree } = useSelector((state) => state.tree);

  // Form state
  const [parentValue, setParentValue] = useState('');
  const [newNodeValue, setNewNodeValue] = useState('');
  const [direction, setDirection] = useState('left');
  const [deleteValue, setDeleteValue] = useState('');
  const [editNodeId, setEditNodeId] = useState('');
  const [editNodeValue, setEditNodeValue] = useState('');
  const [searchValue, setSearchValue] = useState('');
  const [traversalResult, setTraversalResult] = useState(null);

  // maximum allowed node value (must mirror backend MAX_NODE_VALUE)
  const MAX_NODE_VALUE = 1000000000;

  // Status state
  const [status, setStatus] = useState(null);
  const [statusType, setStatusType] = useState('info'); // 'success', 'error', 'info'
  const [loading, setLoading] = useState(false);

  // Helper to show status message
  const showStatus = (message, type = 'info', duration = 3000) => {
    setStatus(message);
    setStatusType(type);
    setTimeout(() => setStatus(null), duration);
  };

  // Validate tree is selected
  const validateTree = () => {
    if (!selectedTree) {
      showStatus('Please select or create a tree first', 'error');
      return false;
    }
    return true;
  };

  // Refresh tree visualization after a manual operation
  const refreshTreeVisualization = async () => {
    if (!selectedTree) return;
    try {
      const response = await treeAPI.getTree(selectedTree.id);
      const treeData = response.tree_data;
      console.log('Refreshed tree data:', treeData);
      const { nodes, edges } = convertTreeToFlowData(treeData);
      dispatch(setTreeVisualization({ nodes, edges }));
    } catch (error) {
      console.error('Failed to refresh tree after manual operation:', error);
    }
  };

  // ==================== INSERT NODE ====================
  const handleInsertNode = async (e) => {
    e.preventDefault();
    if (!validateTree()) return;
    if (!newNodeValue.trim()) {
      showStatus('Please enter a value for the new node', 'error');
      return;
    }

    let parentInt = null;
    if (parentValue.trim()) {
      parentInt = parseInt(parentValue);
      if (isNaN(parentInt)) {
        showStatus('Parent value must be a number', 'error');
        return;
      }
    } else if (selectedTree && selectedTree.tree_data !== null) {
      // non-empty tree requires parent
      showStatus('Please enter the parent node value', 'error');
      return;
    }

    const newValInt = parseInt(newNodeValue);
    if (isNaN(newValInt)) {
      showStatus('New node value must be a number', 'error');
      return;
    }
    if (Math.abs(newValInt) > MAX_NODE_VALUE) {
      showStatus(`Node value too large; max ${MAX_NODE_VALUE}`, 'error');
      return;
    }

    setLoading(true);
    // debounce to avoid repeated clicks
    if (handleInsertNode._locked) return;
    handleInsertNode._locked = true;
    setTimeout(() => { handleInsertNode._locked = false; }, 800);
    try {
      await treeAPI.insertNode(
        selectedTree.id,
        parentInt,
        newValInt,
        direction
      );

      setParentValue('');
      setNewNodeValue('');
      setDirection('left');

      showStatus(`Node ${newNodeValue} inserted successfully!`, 'success');
      await refreshTreeVisualization();
    } catch (error) {
      const msg = error.message || 'Failed to insert node';
      showStatus(msg, 'error');
      // also display a browser alert so the user can't miss it
      alert(msg);
    } finally {
      setLoading(false);
    }
  };

  // ==================== DELETE NODE ====================
  const handleDeleteNode = async (e) => {
    e.preventDefault();
    if (!validateTree()) return;
    if (!deleteValue.trim()) {
      showStatus('Please enter node value to delete', 'error');
      return;
    }

    setLoading(true);
    try {
      await treeAPI.deleteNode(selectedTree.id, parseInt(deleteValue));
      setDeleteValue('');
      showStatus(`Node ${deleteValue} deleted successfully!`, 'success');
      await refreshTreeVisualization();
    } catch (error) {
      const msg = error.message || 'Failed to delete node';
      showStatus(msg, 'error');
      alert(msg);
    } finally {
      setLoading(false);
    }
  };

  // ==================== EDIT NODE ====================
  const handleEditNode = async (e) => {
    e.preventDefault();
    if (!validateTree()) return;
    if (!editNodeId.trim() || !editNodeValue.trim()) {
      showStatus('Please fill all fields', 'error');
      return;
    }

    const newVal = parseInt(editNodeValue);
    if (Math.abs(newVal) > MAX_NODE_VALUE) {
      showStatus(`Node value too large; max ${MAX_NODE_VALUE}`, 'error');
      return;
    }

    setLoading(true);
    try {
      // Backend API call to update node value
      await treeAPI.updateNode(
        selectedTree.id,
        parseInt(editNodeId),
        parseInt(editNodeValue)
      );

      setEditNodeId('');
      setEditNodeValue('');

      showStatus(`Node updated successfully!`, 'success');
      await refreshTreeVisualization();
    } catch (error) {
      const msg = error.message || 'Failed to edit node';
      showStatus(msg, 'error');
      alert(msg);
    } finally {
      setLoading(false);
    }
  };

  // ==================== SEARCH NODE ====================
  const handleSearchNode = async (e) => {
    e.preventDefault();
    if (!validateTree()) return;
    if (!searchValue.trim()) {
      showStatus('Please enter a value to search', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await treeAPI.searchNode(selectedTree.id, parseInt(searchValue));

      if (response.found) {
        dispatch(setHighlightedNode(String(response.node_id)));
        showStatus(`Node ${searchValue} found!`, 'success');
      } else {
        const msg = `Node ${searchValue} not found in tree`;
        showStatus(msg, 'info');
        alert(msg);
      }
      setSearchValue('');
    } catch (error) {
      const msg = error.message || 'Search failed';
      showStatus(msg, 'error');
      alert(msg);
    } finally {
      setLoading(false);
    }
  };

  // ==================== RESET TREE ====================
  const handleResetTree = async () => {
    if (!validateTree()) return;

    const confirmed = window.confirm('Are you sure you want to delete all nodes? This cannot be undone.');
    if (!confirmed) return;

    setLoading(true);
    try {
      await treeAPI.resetTree(selectedTree.id);
      dispatch(setHighlightedNode(null));
      dispatch(setTraversalPath([]));
      showStatus('Tree reset successfully!', 'success');
      await refreshTreeVisualization();
    } catch (error) {
      const msg = error.message || 'Failed to reset tree';
      showStatus(msg, 'error');
      alert(msg);
    } finally {
      setLoading(false);
    }
  };

  // ==================== TRAVERSAL ANIMATION ====================
  const handleTraversal = async (type) => {
    if (!validateTree()) return;

    setLoading(true);
    try {
      const response = await treeAPI.getTraversal(selectedTree.id, type);
      const order = response.order || [];

      if (order.length === 0) {
        showStatus(`No nodes for ${type} traversal`, 'info');
        dispatch(setTraversalPath([]));
        setTraversalResult(null);
        return;
      }

      // Map values to node ids (we use value as id in convertTreeToFlowData)
      dispatch(setTraversalPath(order.map((v) => String(v))));
      
      // Store traversal result for better display
      const traversalName = type.charAt(0).toUpperCase() + type.slice(1);
      setTraversalResult({
        type: traversalName,
        values: order
      });
      
      showStatus(`${traversalName} traversal completed!`, 'success');
    } catch (error) {
      const msg = error.message || 'Failed to get traversal';
      showStatus(msg, 'error');
      alert(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="manual-controls-container">
      <div className="manual-controls-header">
        <h3>⚙️ Manual Controls</h3>
      </div>

      <div className="manual-controls-body">
        {/* INSERT NODE SECTION */}
        <div className="control-section">
          <div className="control-section-title" style={{marginTop:"20px"}}>Insert Node</div>

          <form onSubmit={handleInsertNode}>
            <div className="control-group">
              <label className="control-label">Parent Node Value</label>
              <input
                type="number"
                value={parentValue}
                onChange={(e) => setParentValue(e.target.value)}
                placeholder="e.g., 10"
                disabled={loading}
              />
            </div>

            <div className="control-group">
              <label className="control-label">New Node Value</label>
              <input
                type="number"
                value={newNodeValue}
                onChange={(e) => setNewNodeValue(e.target.value)}
                placeholder="e.g., 5"
                disabled={loading}
              />
            </div>

            <div className="control-group">
              <label className="control-label">Direction</label>
              <select value={direction} onChange={(e) => setDirection(e.target.value)} disabled={loading}>
                <option value="left">Left Child</option>
                <option value="right">Right Child</option>
              </select>
            </div>

            <button type="submit" className="btn btn-primary btn-sm w-full" disabled={loading}>
              {loading ? '⏳ Inserting...' : '➕ Insert Node'}
            </button>
          </form>
        </div>

        {/* DELETE NODE SECTION */}
        <div className="control-section">
          <div className="control-section-title">🗑️ Delete Node</div>

          <form onSubmit={handleDeleteNode}>
            <div className="control-group">
              <label className="control-label">Node Value</label>
              <div className="control-input-group">
                <input
                  type="number"
                  value={deleteValue}
                  onChange={(e) => setDeleteValue(e.target.value)}
                  placeholder="e.g., 5"
                  disabled={loading}
                />
                <button type="submit" className="btn btn-danger btn-sm" disabled={loading}>
                  {loading ? '⏳' : '🗑️'}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* EDIT NODE SECTION */}
        <div className="control-section">
          <div className="control-section-title">✏️ Edit Node</div>

          <form onSubmit={handleEditNode}>
            <div className="control-group">
              <label className="control-label">Node ID</label>
              <input
                type="number"
                value={editNodeId}
                onChange={(e) => setEditNodeId(e.target.value)}
                placeholder="Enter node ID"
                disabled={loading}
              />
            </div>

            <div className="control-group">
              <label className="control-label">New Value</label>
              <input
                type="number"
                value={editNodeValue}
                onChange={(e) => setEditNodeValue(e.target.value)}
                placeholder="Enter new value"
                disabled={loading}
              />
            </div>

            <button type="submit" className="btn btn-primary btn-sm w-full" disabled={loading}>
              {loading ? '⏳ Updating...' : '✏️ Update Node'}
            </button>
          </form>
        </div>

        {/* SEARCH NODE SECTION */}
        <div className="control-section">
          <div className="control-section-title">🔍 Search Node</div>

          <form onSubmit={handleSearchNode}>
            <div className="control-group">
              <label className="control-label">Node Value</label>
              <div className="control-input-group">
                <input
                  type="number"
                  value={searchValue}
                  onChange={(e) => setSearchValue(e.target.value)}
                  placeholder="e.g., 7"
                  disabled={loading}
                />
                <button type="submit" className="btn btn-primary btn-sm" disabled={loading}>
                  {loading ? '⏳' : '🔍'}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* RESET & TRAVERSAL SECTION */}
        <div className="control-section">
          <div className="control-section-title">🌳 Tree Actions</div>

          <button
            className="btn btn-danger w-full"
            onClick={handleResetTree}
            disabled={loading || !selectedTree}
          >
            🔄 Reset Tree
          </button>

          <div className="traversal-buttons">
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={loading || !selectedTree}
              onClick={() => handleTraversal('preorder')}
            >
              ◀ Pre-order
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={loading || !selectedTree}
              onClick={() => handleTraversal('inorder')}
            >
              ◀ In-order
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              disabled={loading || !selectedTree}
              onClick={() => handleTraversal('postorder')}
            >
              ◀ Post-order
            </button>
          </div>
        </div>

        {/* STATUS MESSAGE */}
        {status && (
          <div className={`control-status ${statusType}`}>
            {status}
          </div>
        )}

        {/* TRAVERSAL RESULT DISPLAY */}
        {traversalResult && (
          <div className="control-section" style={{backgroundColor: 'rgba(59, 130, 246, 0.08)', borderLeft: '4px solid #3b82f6'}}>
            <div className="traversal-result-label">
              📊 {traversalResult.type} Traversal Result
            </div>
            <div className="traversal-result-values">
              {traversalResult.values.join(' → ')}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ManualControls;
