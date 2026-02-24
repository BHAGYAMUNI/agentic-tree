import React from 'react';
import '../styles/tree-list-panel.css';

/**
 * TreeListPanel Component
 * Displays tree management UI
 */
function TreeListPanel({
  trees,
  selectedTree,
  loading,
  newTreeName,
  renameValue,
  renamingTreeId,
  onNewTreeNameChange,
  onCreateTree,
  onSelectTree,
  onDeleteTree,
  onStartRename,
  onRenameTree,
  onCancelRename,
  onRenameValueChange,
}) {
  return (
    <div className="tree-list-panel-container">
      <div className="tree-list-panel-header">
        <h3>🌳 Your Trees</h3>
      </div>

      <div className="tree-list-panel-body">
        <div className="tree-create-form">
          <input
            type="text"
            value={newTreeName}
            onChange={(e) => onNewTreeNameChange(e.target.value)}
            placeholder="Enter tree name"
            disabled={loading}
          />
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={onCreateTree}
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create'}
          </button>
        </div>

        <div className="tree-list">
          {loading && trees.length === 0 && <p className="loading-text">Loading trees...</p>}
          {!loading && trees.length === 0 && (
            <p className="tree-list-empty">No trees yet. Create your first tree.</p>
          )}

          {trees.map((tree) => (
            <div
              key={tree.id}
              className={`tree-list-item ${selectedTree?.id === tree.id ? 'selected' : ''}`}
              onClick={() => onSelectTree(tree)}
            >
              {renamingTreeId === tree.id ? (
                <div className="tree-rename-form">
                  <input
                    type="text"
                    value={renameValue}
                    onChange={(e) => onRenameValueChange(e.target.value)}
                    autoFocus
                  />
                  <button
                    type="button"
                    className="btn btn-primary btn-xs"
                    onClick={(event) => onRenameTree(tree.id, event)}
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary btn-xs"
                    onClick={(event) => {
                      event.stopPropagation();
                      onCancelRename();
                    }}
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <>
                  <span className="tree-name">{tree.name}</span>
                  <div className="tree-item-actions">
                    <button
                      type="button"
                      className="btn-icon"
                      title="Rename"
                      onClick={(event) => onStartRename(tree, event)}
                    >
                      ✏️
                    </button>
                    <button
                      type="button"
                      className="btn-icon danger"
                      title="Delete"
                      onClick={(event) => onDeleteTree(tree.id, event)}
                    >
                      🗑️
                    </button>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default TreeListPanel;
