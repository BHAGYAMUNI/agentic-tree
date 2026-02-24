# Implementation Guide - Tree Visualization Frontend

## Overview

This document provides a complete guide to the frontend implementation, including code structure, architecture decisions, and how to extend the application.

---

## Part 1: Architecture Overview

### 1.1 Core Components

**Navbar** (`src/components/Navbar.jsx`)
- Displays app branding
- Theme toggle functionality
- User information display
- Logout action
- Responsive design

**TreeCanvas** (`src/components/TreeCanvas.jsx`)
- React Flow-based tree visualization
- Auto-layout with dagre-like algorithm
- Node highlighting on selection
- Traversal path animation
- Interactive controls (zoom, pan, fit)

**ManualControls** (`src/components/ManualControls.jsx`)
- Insert node operation form
- Delete node operation form
- Search node functionality
- Reset tree action
- Status feedback system

**ChatPanel** (`src/components/ChatPanel.jsx`)
- Real-time message display
- User input with validation
- Typing indicator animation
- Message export (JSON)
- Chat history management

### 1.2 Pages

**Login.jsx**
- Email and password authentication
- Form validation
- Redux auth state management
- Redirect to dashboard on success
- Error handling and display

**Register.jsx**
- New user registration
- Password confirmation
- Email validation
- Password strength checking
- Success feedback

**Dashboard.jsx**
- Main application container
- Tree list management (CRUD)
- Tree visualization loading
- Layout coordination
- Protected route

---

## Part 2: State Management (Redux)

### 2.1 Auth State (authSlice.js)

```javascript
// Actions
setUser({ user, token })       // Store user info
logout()                        // Clear auth state
setLoading(boolean)            // Loading state
setError(message)              // Error messages
initializeAuth()               // Initialize from localStorage
```

**Use Cases:**
- Protect routes based on authentication
- Display user email in navbar
- Manage login/register flows
- Handle token expiration

### 2.2 Tree State (treeSlice.js)

```javascript
// Actions
setTrees(array)                // Store list of trees
setSelectedTree(tree)          // Mark selected tree
setTreeVisualization({nodes, edges}) // React Flow data
setHighlightedNode(nodeId)     // Selection highlighting
setTraversalPath(array)        // Traversal visualization
addTree(tree)                  // Add new tree
deleteTree(treeId)             // Remove tree
renameTree({treeId, newName})  // Rename tree
clearTree()                    // Clear visualization
```

**Use Cases:**
- Display tree list in sidebar
- Manage tree visualization data
- Handle tree selection
- Track highlighted/searched nodes

### 2.3 Chat State (chatSlice.js)

```javascript
// Actions
addMessage({ text, sender })   // Add new message
setTyping(boolean)             // Typing indicator
clearMessages()                // Clear chat
setMessages(array)             // Set all messages
setLoading(boolean)            // Loading state
setError(message)              // Error messages
```

**Use Cases:**
- Store chat conversation
- Display typing indicator
- Manage message history
- Handle chat state

---

## Part 3: API Service Layer

### 3.1 API Structure

All API calls are defined in `src/services/api.js`:

```javascript
// Auth endpoints
authAPI.register(email, password)
authAPI.login(email, password)
authAPI.getCurrentUser()

// Tree endpoints
treeAPI.getTrees()                      // Get all trees
treeAPI.createTree(name)                // Create new tree
treeAPI.getTree(treeId)                 // Get tree details
treeAPI.updateTree(treeId, name)        // Rename tree
treeAPI.deleteTree(treeId)              // Delete tree

// Tree operations
treeAPI.insertNode(treeId, parentValue, newValue, direction)
treeAPI.deleteNode(treeId, value)
treeAPI.searchNode(treeId, value)
treeAPI.getTraversal(treeId, type)
treeAPI.resetTree(treeId)

// Chat endpoints
chatAPI.sendMessage(treeId, message)
chatAPI.getChatHistory(treeId)
chatAPI.clearChat(treeId)
```

### 3.2 Error Handling

- HTTP errors automatically redirect to login (401)
- User-friendly error messages
- Try-catch blocks in components
- Status feedback in UI

---

## Part 4: Utilities

### 4.1 Tree Conversion (treeUtils.js)

```javascript
// Convert backend tree format to React Flow format
convertTreeToFlowData(treeData)

// Calculate optimal node positioning
calculateTreeLayout(nodes, edges)

// Utility functions
formatTime(isoString)          // Format timestamps
generateId()                   // Generate unique IDs
isValidEmail(email)            // Email validation
isValidPassword(password)      // Password validation (6+ chars)
```

### 4.2 Tree Data Format

Backend format:
```javascript
{
  nodes: {
    1: { value: 10, left: 2, right: 3 },
    2: { value: 5, left: null, right: null },
    3: { value: 15, left: null, right: null }
  },
  root: 1
}
```

React Flow format:
```javascript
{
  nodes: [
    { id: '1', data: { label: '10' }, position: { x: 0, y: 0 } },
    { id: '2', data: { label: '5' }, position: { x: -100, y: 100 } },
    { id: '3', data: { label: '15' }, position: { x: 100, y: 100 } }
  ],
  edges: [
    { id: 'e-1-2', source: '1', target: '2' },
    { id: 'e-1-3', source: '1', target: '3' }
  ]
}
```

---

## Part 5: Styling System

### 5.1 Theme CSS (theme.css)

Uses CSS custom properties for theming:

```css
:root {
  --primary: #667eea;
  --secondary: #764ba2;
  --success: #48bb78;
  --error: #f56565;
  /* ... more colors ... */
  --spacing-md: 16px;
  --radius-md: 8px;
  /* ... more variables ... */
}
```

### 5.2 Light/Dark Mode

```javascript
// Set theme
localStorage.setItem('theme', 'light' | 'dark')
document.documentElement.setAttribute('data-theme', theme)

// CSS targets theme
:root[data-theme="light"] { ... }
:root[data-theme="dark"] { ... }
```

### 5.3 Component Styles

Each component has a dedicated CSS file:
- `navbar.css` - Navigation bar
- `dashboard.css` - Dashboard layout
- `tree-canvas.css` - Tree visualization
- `manual-controls.css` - Control panel
- `chat-panel.css` - Chat interface
- `auth.css` - Login/Register pages

---

## Part 6: Key Features Implementation

### 6.1 Tree Visualization

**React Flow Configuration:**
- Nodes with custom styling
- Edges with animation
- Background grid
- Zoom/pan controls
- Fit view on load

**Layout Algorithm:**
- Vertical tree layout
- Level-based positioning
- Horizontal centering
- Dynamic node spacing

### 6.2 Node Highlighting

```javascript
// User clicks node -> highlight it
handleNodeClick(event, node) {
  dispatch(setHighlightedNode(node.id))
}

// Node styling updates based on highlighted state
node.style.borderColor = isHighlighted ? '#48bb78' : '#667eea'
node.style.background = isHighlighted ? 'rgba(72, 187, 120, 0.1)' : '#fff'
```

### 6.3 Search Functionality

```javascript
// User searches for node value
const response = await treeAPI.searchNode(treeId, value)

if (response.found) {
  // Highlight the found node
  dispatch(setHighlightedNode(String(response.node_id)))
}
```

### 6.4 Chat Integration

```javascript
// Send message
const response = await chatAPI.sendMessage(treeId, message)

// Display both user and bot messages
dispatch(addMessage({ text: userMessage, sender: 'user' }))
dispatch(addMessage({ text: response.response, sender: 'bot' }))

// Auto-scroll to latest message
useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
}, [messages])
```

### 6.5 Form Validation

```javascript
// Email validation
isValidEmail(email)

// Password validation
isValidPassword(password)  // minimum 6 characters

// Form submission
- Check all fields filled
- Validate email format
- Validate password strength
- Check password confirmation
- Show errors if validation fails
```

---

## Part 7: Common Development Tasks

### 7.1 Adding a New Tree Operation

1. **Add API endpoint** (api.js)
```javascript
treeAPI.newOperation = (treeId, params) =>
  apiCall(`/trees/${treeId}/operation`, {
    method: 'POST',
    body: JSON.stringify(params),
  })
```

2. **Add Redux action** (treeSlice.js)
```javascript
newOperationState: (state, action) => {
  // Update state
}
```

3. **Add UI handler** (Component.jsx)
```javascript
const handleNewOperation = async () => {
  const response = await treeAPI.newOperation(...)
  dispatch(newOperationState(response))
}
```

### 7.2 Adding a New Chat Feature

1. **Update Chat API** (api.js)
```javascript
chatAPI.newFeature = (treeId, params) =>
  apiCall('/chat/feature', { method: 'POST', body: ... })
```

2. **Update Chat Slice** (chatSlice.js)
```javascript
newFeatureAction: (state, action) => {
  // Update chat state
}
```

3. **Update ChatPanel** (ChatPanel.jsx)
```javascript
const handleNewFeature = async () => {
  const response = await chatAPI.newFeature(...)
  dispatch(newFeatureAction(response))
}
```

### 7.3 Styling a Component

1. **Create CSS file** in `src/styles/`
2. **Define component-specific classes**
3. **Use CSS variables** for colors/spacing
4. **Add responsive media queries**
5. **Import in component**

---

## Part 8: Testing Checklist

- [ ] User can register with valid email
- [ ] User can login with credentials
- [ ] Token is stored in localStorage
- [ ] User is redirected to login if not authenticated
- [ ] Theme toggle works and persists
- [ ] Trees can be created with unique names
- [ ] Trees can be renamed inline
- [ ] Trees can be deleted with confirmation
- [ ] Tree visualization loads correctly
- [ ] Nodes can be inserted with valid parent
- [ ] Nodes can be deleted
- [ ] Nodes can be searched and highlighted
- [ ] Chat messages are sent and displayed
- [ ] Chat auto-scrolls to bottom
- [ ] Chat can be exported as JSON
- [ ] Chat can be cleared
- [ ] Typing indicator appears during API call
- [ ] Error messages are displayed
- [ ] Loading states show correctly
- [ ] Responsive design works on mobile
- [ ] All form validations work
- [ ] API calls use correct endpoints
- [ ] Redux state updates correctly
- [ ] Navigation works correctly

---

## Part 9: Troubleshooting

### 9.1 Common Issues

**API calls fail**
- Check VITE_API_URL in .env
- Verify backend is running
- Check CORS headers

**Redux state not updating**
- Verify dispatch is called
- Check reducer logic
- Use Redux DevTools

**Styling issues**
- Check CSS import order
- Verify class names
- Check CSS variable values

**Theme not changing**
- Check localStorage
- Verify data-theme attribute
- Check CSS selectors

---

## Part 10: Performance Optimization

### 10.1 React Optimization
- Use React.memo for components
- useMemo for expensive calculations
- useCallback for event handlers

### 10.2 Redux Optimization
- Normalize state structure
- Use selectors for derived state
- Avoid deeply nested objects

### 10.3 Rendering Optimization
- Virtual scrolling for large lists
- Lazy loading for images
- Debounce search inputs

---

## Conclusion

This implementation provides a complete, production-ready frontend for the Tree Visualization application. All code is well-documented, follows best practices, and is designed to be easily extensible.

For questions or additional features, refer to the inline code comments and this guide.

**Happy coding! 🚀**
