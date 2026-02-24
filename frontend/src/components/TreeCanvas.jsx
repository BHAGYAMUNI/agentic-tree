import React, { useCallback, useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import ReactFlow, {
  Controls,
  Background,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { setHighlightedNode } from '../redux/treeSlice';
import '../styles/tree-canvas.css';

/**
 * TreeCanvas Component
 * Visualizes binary tree using React Flow with node/edge animations
 * Features:
 * - Vertical tree layout
 * - Node selection highlighting
 * - Traversal path visualization
 * - Auto-layout on tree updates
 */
function TreeCanvas() {
  const dispatch = useDispatch();
  const { selectedTree, treeNodes, treeEdges, highlightedNode, traversalPath } = useSelector(
    (state) => state.tree
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(treeNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(treeEdges);

  // Update nodes when tree visualization changes.
  // Positions are already computed in convertTreeToFlowData, so we just apply them.
  useEffect(() => {
    setNodes(treeNodes);
    setEdges(treeEdges);
  }, [treeNodes, treeEdges, setNodes, setEdges]);

  // Update node styles when highlighted node changes
  useEffect(() => {
    setNodes((nds) =>
      nds.map((node) => {
        const isHighlighted = highlightedNode === node.id;
        const isInTraversalPath = traversalPath.includes(node.id);

        return {
          ...node,
          style: {
            ...node.style,
            borderColor: isHighlighted ? '#48bb78' : isInTraversalPath ? '#f093fb' : '#667eea',
            borderWidth: isHighlighted || isInTraversalPath ? 3 : 2,
            background: isInTraversalPath ? 'rgba(240, 147, 251, 0.1)' : '#fff',
            boxShadow:
              isHighlighted || isInTraversalPath
                ? '0 0 0 4px rgba(102, 126, 234, 0.2)'
                : 'none',
          },
        };
      })
    );
  }, [highlightedNode, traversalPath, setNodes]);

  // Handle node click to highlight
  const handleNodeClick = (event, node) => {
    dispatch(setHighlightedNode(node.id));
  };

  // Handle empty state
  if (!selectedTree || nodes.length === 0) {
    return (
      <div className="tree-canvas-container">
        <div className="tree-canvas-header">
          <h3>🌳 Tree Visualization</h3>
        </div>
        <div className="tree-canvas-body">
          <div className="no-tree-message">
            <p>No tree loaded. Create or select a tree to visualize.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="tree-canvas-container">
      <div className="tree-canvas-header">
        <h3>🌳 Tree Visualization: {selectedTree?.name || 'Tree'}</h3>
      </div>
      <div className="tree-canvas-body">
        <div className="react-flow-wrapper">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={handleNodeClick}
            fitView
          >
            <Background />
            <Controls />
          </ReactFlow>
        </div>
      </div>
    </div>
  );
}

export default TreeCanvas;
