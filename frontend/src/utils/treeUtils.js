/**
 * Tree Visualization Utilities
 * Convert backend tree data to React Flow format and handle layout
 */

/**
 * Convert nested binary tree data from backend to React Flow nodes and edges.
 * Backend tree format (tree_data) is a nested object:
 * { value: number, left: {...} | null, right: {...} | null } | null
 */
export const convertTreeToFlowData = (treeData) => {
  if (!treeData) {
    return { nodes: [], edges: [] };
  }

  const nodes = [];
  const edges = [];
  const nodeIds = new Set(); // Track node IDs to prevent duplicates
  const edgeIds = new Set(); // Track edge IDs to prevent duplicates

  // Base spacing between nodes (used as a hint before final layout)
  const verticalSpacing = 160;
  const horizontalSpacing = 220;

  // Compute positions relative to parent so left/right sides remain consistent.
  const traverseRelative = (node, depth, parentX = 0, parentId = null, isLeft = null) => {
    if (!node) return;

    // Offset decreases with depth so deeper children are closer horizontally
    const offset = horizontalSpacing / Math.pow(2, Math.max(0, depth));
    const x = depth === 0 ? 0 : parentX + (isLeft ? -offset : offset);
    const y = depth * verticalSpacing;

    // Use the node value as the React Flow node id so search/traversal
    // can highlight nodes by value easily.
    const nodeId = String(node.value);

    // Debug: Log the node being processed
    console.log(`Processing node: value=${node.value}, parentId=${parentId}, nodeId=${nodeId}`);

    // Prevent duplicate nodes
    if (!nodeIds.has(nodeId)) {
      nodeIds.add(nodeId);
      nodes.push({
        id: nodeId,
        data: { label: String(node.value) },
        position: { x, y },
        style: {
          background: 'var(--bg-primary)',
          color: 'var(--text-primary)',
          border: '2px solid var(--primary)',
          borderRadius: '8px',
          padding: '8px 16px',
          minWidth: '60px',
          fontSize: '13px',
          fontWeight: 'bold',
          textAlign: 'center',
        },
      });
    }

    if (parentId) {
      const edgeId = `e-${parentId}-${nodeId}`;
      // Prevent duplicate edges
      if (!edgeIds.has(edgeId)) {
        edgeIds.add(edgeId);
        console.log(`Creating edge: ${edgeId}`);
        edges.push({
          id: edgeId,
          source: parentId,
          target: nodeId,
          animated: true,
        });
      }
    }

    // Children: compute positions relative to current node
    const nextDepth = depth + 1;
    if (node.left) {
      console.log(`  -> Processing left child of ${node.value}`);
      traverseRelative(node.left, nextDepth, x, nodeId, true);
    }
    if (node.right) {
      console.log(`  -> Processing right child of ${node.value}`);
      traverseRelative(node.right, nextDepth, x, nodeId, false);
    }
  };
  // Start traversal from root
  console.log('Starting tree conversion, treeData:', treeData);
  traverseRelative(treeData, 0, 0, null, null);
  console.log('Final nodes:', nodes.length);
  console.log('Final edges:', edges.length, edges);

  return { nodes, edges };
};

/**
 * Calculate layout for nodes using Dagre-like algorithm
 * This provides better node positioning for large trees
 */
export const calculateTreeLayout = (nodes, edges) => {
  // Simple vertical tree layout
  const levelMap = new Map(); // Level -> nodes
  const processedNodes = new Set();

  // Find root node (node with no incoming edges)
  const nodeIds = new Set(nodes.map((n) => n.id));
  const targetsWithIncoming = new Set(edges.map((e) => e.target));
  const rootId = nodes.find((n) => !targetsWithIncoming.has(n.id))?.id;

  if (!rootId) return nodes;

  // BFS to assign levels
  const queue = [[rootId, 0]];
  const parentMap = new Map();

  while (queue.length > 0) {
    const [nodeId, level] = queue.shift();

    if (!levelMap.has(level)) {
      levelMap.set(level, []);
    }
    levelMap.get(level).push(nodeId);
    processedNodes.add(nodeId);

    // Find children
    const childEdges = edges.filter((e) => e.source === nodeId);
    childEdges.forEach((edge) => {
      if (!processedNodes.has(edge.target)) {
        queue.push([edge.target, level + 1]);
        parentMap.set(edge.target, nodeId);
      }
    });
  }

  // Calculate positions (more spacious layout)
  const verticalGap = 180;
  const horizontalGap = 260;

  const updatedNodes = nodes.map((node) => {
    let level = 0;
    let indexInLevel = 0;

    for (const [lv, nodeList] of levelMap.entries()) {
      const idx = nodeList.indexOf(node.id);
      if (idx !== -1) {
        level = lv;
        indexInLevel = idx;
        break;
      }
    }

    const y = level * verticalGap;
    const levelCount = levelMap.get(level).length;
    const x = indexInLevel * horizontalGap - ((levelCount - 1) * horizontalGap) / 2;

    return {
      ...node,
      position: { x, y },
    };
  });

  return updatedNodes;
};

/**
 * Format timestamp to readable string
 */
export const formatTime = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Generate unique ID
 */
export const generateId = () => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Validate email format
 */
export const isValidEmail = (email) => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

/**
 * Validate password strength
 */
export const isValidPassword = (password) => {
  return password.length >= 6;
};
