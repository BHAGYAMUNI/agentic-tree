# 🎯 Quick Start Guide - Tree Visualization Frontend

## ⚡ 5-Minute Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
Create `.env` file:
```
VITE_API_URL=http://localhost:8000/api
```

### 3. Start Development Server
```bash
npm run dev
```

Visit: http://localhost:5173

---

## 🔑 Key Commands

```bash
# Development
npm run dev          # Start dev server on port 5173

# Production
npm run build        # Create optimized build
npm run preview      # Preview production build

# Code Quality
npm run lint         # Lint code
```

---

## 📝 Quick Reference

### Login/Register
1. Go to http://localhost:5173
2. Register new account or login
3. Enter email and password
4. Redirected to dashboard

### Create Tree
1. Enter tree name in left panel
2. Click "Create Tree"
3. Tree appears in list
4. Click to select and view

### Tree Operations

**Insert Node**
- Parent: Value of parent node
- New Value: Value for new node
- Direction: Left or Right
- Click "Insert Node"

**Delete Node**
- Enter node value
- Click delete button
- Node removed from tree

**Search Node**
- Enter node value
- Click search button
- Node highlighted in canvas

**Reset Tree**
- Click "Reset Tree"
- Confirm action
- All nodes deleted

### Chat
1. Type message in input
2. Press Enter or click send
3. Message appears with timestamp
4. Bot responds automatically
5. Typing indicator shows during response

### Theme
- Click moon/sun icon in navbar
- Theme changes instantly
- Persists to next session

### Logout
- Click "Logout" in navbar
- Redirected to login
- Session cleared

---

## 🗂️ File Locations

| Feature | File |
|---------|------|
| Navigation | `src/components/Navbar.jsx` |
| Tree Viz | `src/components/TreeCanvas.jsx` |
| Controls | `src/components/ManualControls.jsx` |
| Chat | `src/components/ChatPanel.jsx` |
| Login | `src/pages/Login.jsx` |
| Register | `src/pages/Register.jsx` |
| Dashboard | `src/pages/Dashboard.jsx` |
| Auth State | `src/redux/authSlice.js` |
| Tree State | `src/redux/treeSlice.js` |
| Chat State | `src/redux/chatSlice.js` |
| API Calls | `src/services/api.js` |
| Utilities | `src/utils/treeUtils.js` |
| Styles | `src/styles/*.css` |

---

## 🎨 Color Reference

```css
Primary:    #667eea (Purple-Blue)
Secondary:  #764ba2 (Purple)
Accent:     #f093fb (Pink)
Success:    #48bb78 (Green)
Error:      #f56565 (Red)
Warning:    #ed8936 (Orange)
Info:       #4299e1 (Blue)
```

---

## 🔗 API Endpoints Used

```
POST   /api/auth/register         # Register
POST   /api/auth/login            # Login
GET    /api/auth/me               # Get user

GET    /api/trees                 # List trees
POST   /api/trees                 # Create tree
GET    /api/trees/{id}            # Get tree
PUT    /api/trees/{id}            # Rename tree
DELETE /api/trees/{id}            # Delete tree

POST   /api/trees/{id}/insert     # Insert node
POST   /api/trees/{id}/delete     # Delete node
POST   /api/trees/{id}/search     # Search node
POST   /api/trees/{id}/reset      # Reset tree

POST   /api/chat                  # Send message
GET    /api/chat/history/{id}     # Get history
DELETE /api/chat/history/{id}     # Clear chat
```

---

## 🐛 Troubleshooting

### "Cannot connect to API"
- ✅ Backend running on localhost:8000?
- ✅ Check VITE_API_URL in .env
- ✅ Check browser console for errors

### "Login fails"
- ✅ Check email format
- ✅ Password at least 6 characters
- ✅ Verify credentials in backend

### "Trees not showing"
- ✅ Refresh page
- ✅ Clear localStorage
- ✅ Check Redux DevTools for state

### "Chat not working"
- ✅ Tree must be selected
- ✅ Check backend AI endpoint
- ✅ Look for API errors in console

### "Theme not changing"
- ✅ Check localStorage theme key
- ✅ Verify data-theme attribute
- ✅ Hard refresh browser

---

## 📊 Redux State Structure

```javascript
// Auth
{
  user: { email, id },
  token: "jwt_token",
  isAuthenticated: true,
  loading: false,
  error: null
}

// Tree
{
  trees: [],
  selectedTree: null,
  treeNodes: [],      // React Flow nodes
  treeEdges: [],      // React Flow edges
  highlightedNode: null,
  traversalPath: [],
  loading: false,
  error: null
}

// Chat
{
  messages: [
    { id, text, sender, timestamp }
  ],
  typing: false,
  loading: false,
  error: null
}
```

---

## 🎓 Learning Resources

- **React Docs**: https://react.dev
- **Redux Docs**: https://redux.js.org
- **React Flow**: https://reactflow.dev
- **Vite Docs**: https://vitejs.dev

---

## ✅ Verification Checklist

After setup, verify:
- [ ] Can access http://localhost:5173
- [ ] Can register new account
- [ ] Can login with credentials
- [ ] Can create new tree
- [ ] Can see tree in visualization
- [ ] Can insert node
- [ ] Can search node (highlights)
- [ ] Can send chat message
- [ ] Can toggle theme
- [ ] Can logout

---

## 🚀 Production Checklist

Before deploying:
- [ ] Set correct API URL in .env
- [ ] Build optimized version
- [ ] Test all features
- [ ] Check mobile responsiveness
- [ ] Verify error handling
- [ ] Check performance
- [ ] Test auth flow
- [ ] Verify localStorage
- [ ] Test in production env

---

## 💬 Code Examples

### Using Redux State
```javascript
const { isAuthenticated } = useSelector(state => state.auth);
const { trees, selectedTree } = useSelector(state => state.tree);
const { messages } = useSelector(state => state.chat);
```

### Dispatching Actions
```javascript
dispatch(setUser({ user, token }));
dispatch(setTrees(treeArray));
dispatch(addMessage({ text, sender }));
```

### Making API Calls
```javascript
const response = await treeAPI.getTrees();
const result = await chatAPI.sendMessage(treeId, message);
```

### Converting Tree Data
```javascript
const { nodes, edges } = convertTreeToFlowData(treeData);
```

---

## 🎯 Common Tasks

### Add New Feature
1. Create component in `src/components/`
2. Add Redux slice in `src/redux/`
3. Add API calls in `src/services/api.js`
4. Style in `src/styles/`
5. Import and use in page

### Fix Bug
1. Check Redux DevTools for state
2. Check network tab for API calls
3. Check browser console for errors
4. Look at component props
5. Verify CSS classes

### Deploy
1. `npm run build`
2. Copy `dist/` folder
3. Upload to web server
4. Configure CORS on backend
5. Test in production

---

## 📞 Getting Help

1. **Check documentation**
   - FRONTEND_README.md
   - IMPLEMENTATION_GUIDE.md
   - Code comments

2. **Debug tools**
   - Redux DevTools Extension
   - React Developer Tools
   - Browser DevTools Network tab

3. **Common issues**
   - API connection: Check .env
   - Auth issues: Check token in localStorage
   - Styling: Check CSS variables
   - State: Check Redux DevTools

---

## 🎉 You're Ready!

Everything is set up and ready to go. Start the dev server and begin building!

```bash
npm run dev
```

Good luck! 🚀

---

*Quick Reference Card - Save this for easy lookup!*
