# Tree Visualization Frontend

A modern, responsive React application for visualizing and manipulating binary trees with AI-powered chat assistance.

## Features

✨ **Core Features**
- 🌳 Binary Tree Visualization using React Flow
- 💬 AI-powered Chat Panel for tree discussions
- ⚙️ Manual Controls for tree operations (insert, delete, search)
- 🎨 Modern, responsive UI with light/dark theme toggle
- 🔐 JWT-based authentication
- 📱 Mobile-responsive design

## Tech Stack

- **Frontend Framework**: React 19
- **State Management**: Redux Toolkit
- **Tree Visualization**: React Flow
- **Routing**: React Router v7
- **Styling**: Pure CSS (no frameworks)
- **Build Tool**: Vite
- **API Communication**: Fetch API

## Project Structure

```
src/
├── components/
│   ├── Navbar.jsx          # Top navigation bar
│   ├── TreeCanvas.jsx      # Tree visualization component
│   ├── ManualControls.jsx  # Tree operation controls
│   └── ChatPanel.jsx       # AI chat interface
├── pages/
│   ├── Login.jsx           # Login page
│   ├── Register.jsx        # Registration page
│   └── Dashboard.jsx       # Main dashboard
├── redux/
│   ├── store.js            # Redux store configuration
│   ├── authSlice.js        # Auth state management
│   ├── treeSlice.js        # Tree state management
│   └── chatSlice.js        # Chat state management
├── services/
│   └── api.js              # Backend API service
├── styles/
│   ├── theme.css           # Global styles and theme
│   ├── navbar.css
│   ├── dashboard.css
│   ├── tree-canvas.css
│   ├── manual-controls.css
│   ├── chat-panel.css
│   └── auth.css
├── utils/
│   └── treeUtils.js        # Tree conversion and utilities
├── App.jsx                 # Main app component
└── main.jsx                # Entry point
```

## Installation

### Prerequisites
- Node.js 16+
- npm or yarn

### Setup

1. **Install dependencies**
```bash
cd frontend
npm install
```

2. **Configure environment variables**
Create a `.env` file in the frontend directory:
```
VITE_API_URL=http://localhost:8000/api
```

3. **Start development server**
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Building for Production

```bash
npm run build
npm run preview
```

## Key Components

### Navbar
- App title with logo
- Theme toggle (light/dark)
- User email display
- Logout button

### TreeCanvas
- React Flow-based tree visualization
- Node selection highlighting
- Traversal path visualization
- Auto-layout for large trees
- Interactive node clicking

### ManualControls
- Insert node (specify parent, value, direction)
- Delete node by value
- Search node by value
- Reset entire tree
- Status feedback messages

### ChatPanel
- Send/receive messages
- Typing indicator animation
- Auto-scroll to latest message
- Export chat as JSON
- Clear chat history

### Dashboard
- Tree list with CRUD operations
- Create new trees
- Rename trees inline
- Delete trees with confirmation
- Load and visualize selected tree
- Responsive 3-panel layout

### Auth Pages
- Professional login/register forms
- Form validation
- Error handling
- Password strength checking
- Loading states

## Redux State Structure

### authSlice
```javascript
{
  user: { email, id },
  token: string,
  isAuthenticated: boolean,
  loading: boolean,
  error: string
}
```

### treeSlice
```javascript
{
  trees: [],
  selectedTree: {},
  treeNodes: [],      // React Flow nodes
  treeEdges: [],      // React Flow edges
  highlightedNode: null,
  traversalPath: [],
  loading: boolean,
  error: string
}
```

### chatSlice
```javascript
{
  messages: [{ id, text, sender, timestamp }],
  typing: boolean,
  loading: boolean,
  error: string
}
```

## API Integration

All API calls are centralized in `src/services/api.js`:

- **Auth**: Login, Register, Get Current User
- **Trees**: CRUD operations, tree visualization
- **Tree Operations**: Insert, Delete, Search, Reset
- **Chat**: Send message, Get history, Clear chat

## Styling

The app uses a custom CSS theme system with:
- CSS custom properties for colors, spacing, shadows
- Light and dark theme support
- Responsive design with mobile-first approach
- Modern SaaS-style UI

### Theme Variables
- Primary color: `#667eea`
- Secondary color: `#764ba2`
- Success: `#48bb78`
- Error: `#f56565`
- Warning: `#ed8936`

## Responsive Design

- **Desktop** (1200px+): 3-column layout (Tree list, Canvas, Controls+Chat)
- **Tablet** (768px-1199px): 2-column layout (Canvas, Controls+Chat)
- **Mobile** (<768px): Stacked single column

## Development Tips

1. **Adding New Features**
   - Create Redux slices for new state
   - Create component in appropriate folder
   - Add styles in styles/ directory
   - Update API service for backend calls

2. **Debugging**
   - Redux DevTools for state inspection
   - Console for API errors
   - Network tab for backend communication

3. **Performance**
   - React Flow handles large trees efficiently
   - Redux prevents unnecessary re-renders
   - Lazy loading for tree visualization

## Known Limitations

- Tree canvas requires backend API running
- Chat requires proper backend AI endpoint
- Theme preference stored in localStorage
- Tree data must conform to backend format

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Contributing

1. Follow existing code style
2. Use functional components only
3. Add comments for complex logic
4. Test before committing

## License

MIT

## Support

For issues or questions, contact the development team.

---

**Note**: This frontend requires the corresponding FastAPI backend to be running. See backend documentation for setup instructions.
