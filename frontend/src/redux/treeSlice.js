import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  trees: [], // List of saved trees
  selectedTree: null, // Currently loaded tree
  treeNodes: [], // React Flow nodes
  treeEdges: [], // React Flow edges
  loading: false,
  error: null,
  highlightedNode: null, // For selection highlighting
  traversalPath: [], // For step-by-step traversal visualization
};

const treeSlice = createSlice({
  name: 'tree',
  initialState,
  reducers: {
    // Set list of all trees
    setTrees: (state, action) => {
      state.trees = action.payload;
    },
    // Load a specific tree
    setSelectedTree: (state, action) => {
      state.selectedTree = action.payload;
    },
    // Update nodes and edges for visualization
    setTreeVisualization: (state, action) => {
      const { nodes, edges } = action.payload;
      state.treeNodes = nodes;
      state.treeEdges = edges;
    },
    // Highlight a node
    setHighlightedNode: (state, action) => {
      state.highlightedNode = action.payload;
    },
    // Set traversal path for visualization
    setTraversalPath: (state, action) => {
      state.traversalPath = action.payload;
    },
    // Add a new tree to the list
    addTree: (state, action) => {
      state.trees.push(action.payload);
    },
    // Delete a tree from the list
    deleteTree: (state, action) => {
      state.trees = state.trees.filter((tree) => tree.id !== action.payload);
    },
    // Update tree name
    renameTree: (state, action) => {
      const { treeId, newName } = action.payload;
      const tree = state.trees.find((t) => t.id === treeId);
      if (tree) {
        tree.name = newName;
      }
    },
    // Clear tree state
    clearTree: (state) => {
      state.selectedTree = null;
      state.treeNodes = [];
      state.treeEdges = [];
      state.highlightedNode = null;
      state.traversalPath = [];
    },
    // Loading and error states
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const {
  setTrees,
  setSelectedTree,
  setTreeVisualization,
  setHighlightedNode,
  setTraversalPath,
  addTree,
  deleteTree,
  renameTree,
  clearTree,
  setLoading,
  setError,
} = treeSlice.actions;

export default treeSlice.reducer;
