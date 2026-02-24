# 🔧 TECHNICAL FLOW & LOGIC EXPLANATION

**Deep Dive**: Complete technical flow with code references  
**Date**: February 24, 2026  
**Level**: Intermediate/Advanced

---

# 📚 TABLE OF CONTENTS

1. [User Registration Flow](#1-user-registration-flow)
2. [User Login Flow](#2-user-login-flow)
3. [Create Tree Flow](#3-create-tree-flow)
4. [Insert Node Flow](#4-insert-node-flow)
5. [Delete Node Flow](#5-delete-node-flow)
6. [Chat Message Flow](#6-chat-message-flow)
7. [Edit Node Flow](#7-edit-node-flow)
8. [Save/Load Tree Flow](#8-saveload-tree-flow)
9. [Tree Visualization Flow](#9-tree-visualization-flow)

---

# 1️⃣ USER REGISTRATION FLOW

## What Happens When User Clicks "Register"

### STEP 1: Frontend - User Enters Email & Password

**File**: `frontend/src/pages/Register.jsx` (lines 40-80)

```javascript
// User fills form
<input value={email} onChange={(e) => setEmail(e.target.value)} />
<input value={password} onChange={(e) => setPassword(e.target.value)} />
<input value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
<button onClick={handleRegister}>Register</button>

// When user clicks button, handleRegister is called
const handleRegister = async () => {
  // 1. Validation
  if (!email.trim() || !password.trim()) {
    setLocalError('Email and password required');
    return;
  }
  
  // 2. Check if passwords match
  if (password !== confirmPassword) {
    setLocalError('Passwords do not match');
    return;
  }
  
  // 3. Set loading state (shows spinner)
  dispatch(setLoading(true));
  
  // 4. Call API
  const response = await authAPI.register(email, password);
};
```

**What happens**: 
- Email and password are stored in React state (`email`, `password`)
- Form validation happens
- `dispatch(setLoading(true))` updates Redux to show loading spinner

### STEP 2: Frontend - Call Backend API

**File**: `frontend/src/services/api.js` (lines 80-85)

```javascript
export const authAPI = {
  register: (email, password) =>
    apiCall('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),  // ← Send this data
    }),
};
```

**What happens**:
- JavaScript object `{ email, password }` is converted to JSON string
- HTTP POST request is created
- Headers include: `Content-Type: application/json`
- Request is sent to: `http://localhost:8000/auth/register`

**Network Request**:
```
POST /auth/register HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "email": "alice@example.com",
  "password": "MySecret123"
}
```

### STEP 3: Backend - Receive Request

**File**: `backend/venv/main.py` (lines 131-160)

```python
@app.post("/auth/register")  # ← Endpoint that listens for POST /auth/register
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    This function receives the registration request
    
    Parameters:
    - user: Pydantic model with email, password (automatically parsed from JSON)
    - db: Database session (automatically provided by dependency injection)
    """
    
    # STEP 1: Log the request
    logger.info(f"Registration attempt: {user.email}")
    
    # STEP 2: Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    
    if existing_user:
        logger.warning(f"Registration failed: Email already registered - {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
```

**What happens**:
- FastAPI automatically validates JSON matches `UserCreate` schema
- If validation fails, returns 400 error
- Database connection is provided automatically
- Logger records this action

### STEP 4: Backend - Hash Password (Security)

**File**: `backend/venv/auth.py` (lines 20-30)

```python
def hash_password(password: str) -> str:
    """Convert plain text password to hashed version using bcrypt"""
    # Algorithm: bcrypt (very secure, one-way hashing)
    # Raw password: "MySecret123"
    # Hashed: "$2b$12$R9h7cIPz0gi.URnnGcHzB.eYUpQMN7iL7cHHf7P4F8K7sK5bSVhTe"
    return get_password_hash(password)

# In main.py registration function:
hashed_pw = hash_password(user.password)
```

**What happens**:
- Password is hashed using bcrypt algorithm
- Hashing is ONE-WAY (cannot be reversed)
- Even if database is hacked, password cannot be read
- Same password always produces same hash (deterministic)

### STEP 5: Backend - Create User Record

**File**: `backend/venv/main.py` (lines 142-150)

```python
# Create new user object (doesn't save yet)
new_user = User(
    email=user.email,                    # "alice@example.com"
    hashed_password=hashed_pw            # Long hashed string
)

# Add to database
db.add(new_user)

# Commit changes (actually saves to database)
db.commit()

# Refresh to get the auto-generated ID
db.refresh(new_user)
```

**What happens**:
- Python object created in memory
- `db.add()` stages it for insertion
- `db.commit()` executes INSERT query to database
- `db.refresh()` fetches the auto-generated ID from database

**Database Action**:
```sql
INSERT INTO users (email, hashed_password, created_at)
VALUES ('alice@example.com', '$2b$12$R9h7...', NOW())
RETURNING id, email, hashed_password, created_at;

-- Result: ID 5 is assigned
```

### STEP 6: Backend - Generate JWT Tokens

**File**: `backend/venv/auth.py` (lines 50-70)

```python
def create_access_token(data: dict) -> str:
    """
    Create JWT access token (expires in 30 minutes)
    
    Token contains:
    - "sub" (subject): user's email
    - "exp" (expiration): when token expires
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    
    # Sign with secret key (SUPER SECRET!)
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,  # Example: "my-super-secret-key-do-not-share"
        algorithm="HS256"
    )
    return encoded_jwt

# In registration:
access_token = create_access_token(data={"sub": new_user.email})
refresh_token = create_refresh_token(data={"sub": new_user.email})
```

**What happens**:
- JWT token created (looks like: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZUBleGFtcGxlLmNvbSIsImV4cCI6MTcxOTk...`)
- Token contains user's email encrypted
- Token expires after 30 minutes (for security)
- Refresh token expires after 90 days (for refreshing access token)

### STEP 7: Backend - Send Response

**File**: `backend/venv/main.py` (lines 153-159)

```python
return {
    "access_token": access_token,      # Long JWT string
    "refresh_token": refresh_token,    # Another JWT string
    "token_type": "bearer",            # Type of token
    "email": new_user.email,           # User's email
    "user_id": new_user.id,            # Database ID
}
```

**HTTP Response**:
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "email": "alice@example.com",
  "user_id": 5
}
```

### STEP 8: Frontend - Process Response

**File**: `frontend/src/pages/Register.jsx` (lines 70-85)

```javascript
try {
  // Response from backend
  const response = await authAPI.register(email, password);
  
  // Extract data from response
  const { access_token, refresh_token, email, user_id } = response;
  
  // Save tokens to browser storage (localStorage)
  localStorage.setItem('access_token', access_token);
  localStorage.setItem('refresh_token', refresh_token);
  
  // Update Redux store with user data
  dispatch(setUser({
    user: { email: response.email, id: response.user_id },
    access_token: response.access_token,
    refresh_token: response.refresh_token,
  }));
  
  // Navigate to dashboard
  navigate('/dashboard');
  
} catch (error) {
  setLocalError(error.message);
}
```

**What happens**:
- Tokens stored in browser's localStorage (persists across page reloads)
- Redux updated with user info
- Browser redirected to dashboard page
- User is now logged in!

### Registration Complete ✅

```
User Input
    ↓
Frontend Validation ✓
    ↓
API Call (JSON)
    ↓
Backend Receives Request
    ↓
Check if email exists ✓
    ↓
Hash Password
    ↓
Create User in Database
    ↓
Generate JWT Tokens
    ↓
Send Response
    ↓
Frontend Save Tokens
    ↓
Update Redux
    ↓
Redirect to Dashboard
    ↓
User Logged In ✅
```

---

# 2️⃣ USER LOGIN FLOW

## What Happens When User Clicks "Login"

### Similar to Registration But:

**File**: `backend/venv/main.py` (lines 161-195)

```python
@app.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    
    # STEP 1: Find user by email
    db_user = db.query(User).filter(User.email == user.email).first()
    
    # STEP 2: Check if user exists
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    # STEP 3: Verify password
    # Compares user's input password with hashed password in database
    # bcrypt automatically handles the comparison
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    # STEP 4: If all good, create tokens (same as registration)
    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_refresh_token(data={"sub": db_user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "email": db_user.email,
        "user_id": db_user.id,
    }
```

**Key Difference**: Verifies password before creating tokens

---

# 3️⃣ CREATE TREE FLOW

## Complete Technical Flow: User Clicks "Create Tree"

### STEP 1: Frontend - User Enters Tree Name

**File**: `frontend/src/components/TreeListPanel.jsx` (lines 40-60)

```javascript
// User sees this form:
<input 
  type="text" 
  value={newTreeName}
  onChange={(e) => setNewTreeName(e.target.value)}
  placeholder="Enter tree name"
/>
<button onClick={onCreateTree}>Create Tree</button>

// onCreateTree is a prop passed from Dashboard.jsx
// When clicked, the following function from Dashboard.jsx is called:
```

### STEP 2: Frontend - Prepare API Call

**File**: `frontend/src/pages/Dashboard.jsx` (lines 70-85)

```javascript
const handleCreateTree = async () => {
  // STEP 1: Validation
  if (!newTreeName.trim()) {
    alert('Please enter a tree name');
    return;
  }
  
  // STEP 2: Set loading state (shows spinner)
  setLoading(true);
  
  try {
    // STEP 3: Call backend API
    await treeAPI.createTree(newTreeName);
    
    // STEP 4: Clear input field
    setNewTreeName('');
    
    // STEP 5: Refresh tree list
    const response = await treeAPI.getTrees();
    dispatch(setTrees(response));
    
  } catch (error) {
    console.error('Failed to create tree:', error);
    alert('Failed to create tree');
  } finally {
    setLoading(false);
  }
};
```

**What happens**:
- Tree name validated (not empty)
- Loading spinner shown
- `treeAPI.createTree(newTreeName)` called

### STEP 3: Frontend - API Call

**File**: `frontend/src/services/api.js` (lines 120-135)

```javascript
export const treeAPI = {
  createTree: (name) =>
    apiCall('/trees', {
      method: 'POST',
      body: JSON.stringify({ 
        name: name,           // "My First Tree"
        tree_data: null       // No tree data yet
      }),
    }),
};
```

**Network Request**:
```
POST /trees HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "My First Tree",
  "tree_data": null
}
```

**Important**: Token is automatically added to Authorization header!

### STEP 4: Backend - Verify Token

**File**: `backend/venv/auth.py` (lines 100-120)

```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    This function runs BEFORE the tree creation function
    It verifies the JWT token is valid
    """
    try:
        # Decode token using secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        # Extract user's email from token
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    return email
```

**What happens**:
- JWT token is decoded (decrypted) using SECRET_KEY
- User's email extracted from token
- If token is invalid or expired, 401 error returned
- If valid, user's email passed to next function

### STEP 5: Backend - Create Tree Endpoint

**File**: `backend/venv/main.py` (lines 220-250)

```python
@app.post("/trees")
def create_tree(
    tree: TreeCreate,  # Receives: { "name": "My First Tree", "tree_data": null }
    current_user: str = Depends(get_current_user),  # Gets: "alice@example.com"
    db: Session = Depends(get_db)  # Gets: database connection
):
    """
    Creates a new tree for the current user
    """
    
    # STEP 1: Get user ID from database
    user = db.query(User).filter(User.email == current_user).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # STEP 2: Create new tree object
    new_tree = TreeSession(
        name=tree.name,              # "My First Tree"
        tree_data=tree.tree_data,    # None
        user_id=user.id,             # 5 (from User table)
        created_at=datetime.now(timezone.utc)
    )
    
    # STEP 3: Add to database
    db.add(new_tree)
    
    # STEP 4: Commit (actually insert)
    db.commit()
    
    # STEP 5: Refresh to get ID
    db.refresh(new_tree)
    
    # STEP 6: Return tree object
    return {
        "id": new_tree.id,           # 1 (auto-generated ID)
        "name": new_tree.name,       # "My First Tree"
        "tree_data": new_tree.tree_data,  # None
        "created_at": new_tree.created_at
    }
```

**Database Action**:
```sql
INSERT INTO tree_sessions (name, tree_data, user_id, created_at)
VALUES ('My First Tree', NULL, 5, NOW())
RETURNING id, name, tree_data, user_id, created_at;

-- Result:
-- id: 1
-- name: 'My First Tree'
-- tree_data: NULL
-- user_id: 5
-- created_at: 2026-02-24 10:30:00
```

**What happens**:
- New TreeSession object created in Python
- `db.add()` stages it
- `db.commit()` inserts into database with auto-generated ID
- Response sent back with tree object

### STEP 6: Backend - Send Response

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 1,
  "name": "My First Tree",
  "tree_data": null,
  "created_at": "2026-02-24T10:30:00"
}
```

### STEP 7: Frontend - Update UI

**File**: `frontend/src/pages/Dashboard.jsx` (lines 85-95)

```javascript
// Back in handleCreateTree function...

// Refresh list of all trees for current user
const response = await treeAPI.getTrees();
// response = [
//   { id: 1, name: "My First Tree", tree_data: null, created_at: "..." }
// ]

// Update Redux with new list
dispatch(setTrees(response));

// Clear input
setNewTreeName('');

// Hide loading spinner
setLoading(false);
```

**Redux Update** (in `frontend/src/redux/treeSlice.js`):
```javascript
setTrees: (state, action) => {
  state.trees = action.payload;  // [{ id: 1, name: "My First Tree", ... }]
}
```

### STEP 8: React Re-renders UI

**File**: `frontend/src/components/TreeListPanel.jsx` (lines 80-100)

```javascript
// Component receives updated props
function TreeListPanel({ trees }) {
  return (
    <div>
      <h3>Your Trees</h3>
      <ul>
        {trees.map((tree) => (
          <li key={tree.id}>
            <div onClick={() => onSelectTree(tree)}>
              {tree.name}
            </div>
            <button onClick={(e) => onDeleteTree(tree.id, e)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

**What happens**:
- React notices `trees` prop changed
- Component re-renders
- New tree appears in the list
- User sees "My First Tree" in the list

### Create Tree Complete ✅

```
User Types Tree Name
    ↓
Frontend Validation ✓
    ↓
API Call (POST /trees)
    ↓
Backend Verifies Token ✓
    ↓
Gets User ID from Database
    ↓
Creates TreeSession Object
    ↓
Inserts into Database
    ↓
Auto-generates ID (1)
    ↓
Sends Response with ID
    ↓
Frontend Refreshes Tree List
    ↓
Redux Updated
    ↓
React Re-renders
    ↓
User Sees Tree in List ✅
```

---

# 4️⃣ INSERT NODE FLOW

## Complete Technical Flow: User Clicks "Insert Node"

### STEP 1: Frontend - User Enters Node Value

**File**: `frontend/src/components/ManualControls.jsx` (lines 100-130)

```javascript
// User sees form:
<section className="controls-section">
  <h3>🔧 Insert Node</h3>
  <input
    type="number"
    value={insertValue}
    onChange={(e) => setInsertValue(e.target.value)}
    placeholder="Enter value"
  />
  <button onClick={handleInsert}>Insert</button>
</section>

// When user clicks Insert button:
const handleInsert = async (e) => {
  e.preventDefault();
  
  // STEP 1: Validation
  if (!insertValue.trim()) {
    showStatus('Please enter a value', 'error');
    return;
  }
  
  // Convert to integer
  const nodeValue = parseInt(insertValue);
  
  // STEP 2: Show loading state
  setLoading(true);
  
  try {
    // STEP 3: Call backend API
    const result = await treeAPI.insertNode(selectedTree.id, nodeValue);
    
    // STEP 4: Show success message
    showStatus(`Node ${nodeValue} inserted successfully!`, 'success');
    
    // STEP 5: Update tree visualization
    await refreshTreeVisualization();
    
    // STEP 6: Clear input
    setInsertValue('');
    
  } catch (error) {
    showStatus('Failed to insert node', 'error');
  } finally {
    setLoading(false);
  }
};
```

**What happens**:
- Node value validated (must be number)
- Loading shown
- `treeAPI.insertNode(treeId, nodeValue)` called

### STEP 2: Frontend - API Call

**File**: `frontend/src/services/api.js` (lines 140-145)

```javascript
insertNode: (treeId, value) =>
  apiCall(`/trees/${treeId}/insert`, {
    method: 'POST',
    body: JSON.stringify({ value: value }),  // Example: { "value": 5 }
  }),
```

**Network Request**:
```
POST /trees/1/insert HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "value": 5
}
```

### STEP 3: Backend - Insert Node Endpoint

**File**: `backend/venv/main.py` (lines 280-320)

```python
@app.post("/trees/{tree_id}/insert")
def insert_node(
    tree_id: int,  # Example: 1
    request: TreeInsertRequest,  # Contains: { "value": 5 }
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Insert a node into the tree
    """
    
    # STEP 1: Get tree from database
    tree = db.query(TreeSession).filter(
        TreeSession.id == tree_id,
        TreeSession.user_id == db.query(User).filter(User.email == current_user).first().id
    ).first()
    
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")
    
    # STEP 2: Get tree data (JSON stored in database)
    # First time: tree.tree_data = None
    # Later times: tree.tree_data = { "root": 10, "nodes": [...] }
    tree_data = tree.tree_data or {"root": None, "nodes": {}}
    
    # STEP 3: Convert JSON to Python dictionary
    # This is the tree structure stored as JSON in database
    
    # STEP 4: Call insert_node algorithm from tree_utils.py
    tree_data = insert_node_to_tree(tree_data, request.value)
    
    # STEP 5: Save updated tree back to database
    tree.tree_data = tree_data
    db.commit()
    db.refresh(tree)
    
    # STEP 6: Return updated tree
    return {
        "id": tree.id,
        "name": tree.name,
        "tree_data": tree.tree_data
    }
```

### STEP 4: Backend - Tree Algorithm

**File**: `backend/venv/tree_utils.py` (lines 50-100)

```python
def insert_node_to_tree(tree_data, value):
    """
    Insert a node with given value into the tree
    Uses binary search tree insertion logic
    """
    
    # If tree is empty, make this the root
    if tree_data.get("root") is None:
        tree_data["root"] = value
        tree_data["nodes"] = {value: {"left": None, "right": None}}
        return tree_data
    
    # Otherwise, find correct position
    root = tree_data["root"]
    current = root
    
    while True:
        if value < current:
            # Go left
            if tree_data["nodes"][current]["left"] is None:
                # Left is empty, insert here
                tree_data["nodes"][current]["left"] = value
                tree_data["nodes"][value] = {"left": None, "right": None}
                break
            else:
                # Left has node, continue there
                current = tree_data["nodes"][current]["left"]
        else:
            # Go right
            if tree_data["nodes"][current]["right"] is None:
                # Right is empty, insert here
                tree_data["nodes"][current]["right"] = value
                tree_data["nodes"][value] = {"left": None, "right": None}
                break
            else:
                # Right has node, continue there
                current = tree_data["nodes"][current]["right"]
    
    return tree_data
```

**Example: Insert 5 into empty tree**
```python
# Initial tree
tree_data = {"root": None, "nodes": {}}

# After insert_node_to_tree(tree_data, 5)
tree_data = {
  "root": 5,
  "nodes": {
    5: {"left": None, "right": None}
  }
}
```

**Example: Insert 3 into tree with 5**
```python
# Before
tree_data = {
  "root": 5,
  "nodes": {
    5: {"left": None, "right": None}
  }
}

# Algorithm:
# 3 < 5, so go left
# Left is None, so insert here

# After
tree_data = {
  "root": 5,
  "nodes": {
    5: {"left": 3, "right": None},
    3: {"left": None, "right": None}
  }
}
```

**Example: Insert 7 into tree with 5, 3**
```python
# Before
tree_data = {
  "root": 5,
  "nodes": {
    5: {"left": 3, "right": None},
    3: {"left": None, "right": None}
  }
}

# Algorithm:
# 7 > 5, so go right
# Right is None, so insert here

# After
tree_data = {
  "root": 5,
  "nodes": {
    5: {"left": 3, "right": 7},
    3: {"left": None, "right": None},
    7: {"left": None, "right": None}
  }
}
```

### STEP 5: Backend - Save to Database

**File**: `backend/venv/main.py` (lines 315-320)

```python
# tree_data is now Python dictionary
# Must convert to JSON to store in database

tree.tree_data = tree_data  # Converts dict to JSON automatically
db.commit()
db.refresh(tree)
```

**Database Update**:
```sql
UPDATE tree_sessions 
SET tree_data = '{"root": 5, "nodes": {"5": {"left": "3", "right": "7"}, ...}}'
WHERE id = 1;
```

### STEP 6: Backend - Send Response

```json
HTTP/1.1 200 OK

{
  "id": 1,
  "name": "My First Tree",
  "tree_data": {
    "root": 5,
    "nodes": {
      "5": {"left": 3, "right": 7},
      "3": {"left": null, "right": null},
      "7": {"left": null, "right": null}
    }
  }
}
```

### STEP 7: Frontend - Update Tree Visualization

**File**: `frontend/src/components/ManualControls.jsx` (lines 75-85)

```javascript
// After inserting node, refresh the tree visualization
const refreshTreeVisualization = async () => {
  // STEP 1: Get updated tree from backend
  const response = await treeAPI.getTree(selectedTree.id);
  const treeData = response.tree_data;
  
  // STEP 2: Convert backend tree format to React Flow format
  const { nodes, edges } = convertTreeToFlowData(treeData);
  
  // STEP 3: Update Redux store
  dispatch(setTreeVisualization({ nodes, edges }));
};
```

### STEP 8: Backend -> Convert to React Flow Format

**File**: `frontend/src/utils/treeUtils.js` (lines 10-60)

```javascript
export function convertTreeToFlowData(treeData) {
  """
  Convert backend tree format to React Flow format
  
  Backend format:
    {
      "root": 5,
      "nodes": {
        "5": {"left": 3, "right": 7},
        ...
      }
    }
  
  React Flow format:
    {
      "nodes": [
        { id: "5", data: { label: "5" }, position: { x: 0, y: 0 } },
        { id: "3", data: { label: "3" }, position: { x: -100, y: 100 } },
        ...
      ],
      "edges": [
        { id: "5-3", source: "5", target: "3" },
        ...
      ]
    }
  """
  
  const nodes = [];
  const edges = [];
  
  if (!treeData || !treeData.root) return { nodes, edges };
  
  // BFS to traverse tree and calculate positions
  const queue = [
    { id: treeData.root, x: 0, y: 0, index: 0 }
  ];
  
  while (queue.length > 0) {
    const { id, x, y, index } = queue.shift();
    
    // Add node for React Flow
    nodes.push({
      id: String(id),
      data: { label: String(id) },
      position: { x, y }
    });
    
    // Get children
    const nodeData = treeData.nodes[id];
    
    if (nodeData.left !== null) {
      const leftChild = nodeData.left;
      const leftX = x - 150 / Math.pow(2, index + 1);
      const leftY = y + 100;
      
      nodes.push({
        id: String(leftChild),
        data: { label: String(leftChild) },
        position: { x: leftX, y: leftY }
      });
      
      edges.push({
        id: `${id}-${leftChild}`,
        source: String(id),
        target: String(leftChild)
      });
      
      queue.push({ id: leftChild, x: leftX, y: leftY, index: index + 1 });
    }
    
    if (nodeData.right !== null) {
      const rightChild = nodeData.right;
      const rightX = x + 150 / Math.pow(2, index + 1);
      const rightY = y + 100;
      
      nodes.push({
        id: String(rightChild),
        data: { label: String(rightChild) },
        position: { x: rightX, y: rightY }
      });
      
      edges.push({
        id: `${id}-${rightChild}`,
        source: String(id),
        target: String(rightChild)
      });
      
      queue.push({ id: rightChild, x: rightX, y: rightY, index: index + 1 });
    }
  }
  
  return { nodes, edges };
}
```

**What happens**:
- Backend tree structure converted to visual format
- Each node gets x, y coordinates for positioning
- Edges created for connections
- React Flow can now render it

### STEP 9: Redux Update

**File**: `frontend/src/redux/treeSlice.js` (lines 40-50)

```javascript
setTreeVisualization: (state, action) => {
  const { nodes, edges } = action.payload;
  state.visualization.nodes = nodes;
  state.visualization.edges = edges;
}
```

### STEP 10: React Re-renders Tree Canvas

**File**: `frontend/src/components/TreeCanvas.jsx` (lines 30-50)

```javascript
function TreeCanvas() {
  // Get nodes and edges from Redux
  const { nodes, edges } = useSelector(state => state.tree.visualization);
  
  return (
    <ReactFlowProvider>
      <ReactFlow nodes={nodes} edges={edges}>
        <Background />
        <Controls />
      </ReactFlow>
    </ReactFlowProvider>
  );
}
```

**What happens**:
- React Flow receives updated nodes and edges
- Automatically renders boxes for nodes
- Draws lines for edges
- Shows beautiful tree visualization!

### Insert Node Complete ✅

```
User Enters 5
    ↓
Frontend Validation ✓
    ↓
API Call (POST /trees/1/insert)
    ↓
Backend Verifies Token ✓
    ↓
Gets Tree from Database
    ↓
Calls insert_node Algorithm
    ↓
Algorithm finds correct position
    ↓
Updates tree_data dictionary
    ↓
Saves to Database
    ↓
Sends Response
    ↓
Frontend Converts to React Flow Format
    ↓
Updates Redux
    ↓
React Re-renders
    ↓
User Sees Tree Updated with Node 5 ✅
```

---

# 5️⃣ DELETE NODE FLOW

Similar to insert, but calls `delete_node_from_tree` algorithm:

**File**: `backend/venv/tree_utils.py` (lines 150-220)

```python
def delete_node_from_tree(tree_data, value):
    """
    Delete a node with given value from the tree
    Uses binary search tree deletion logic
    """
    
    def delete_recursive(node, target):
        if node is None:
            return None
        
        if target < node:
            # Target in left subtree
            left_child = tree_data["nodes"][node]["left"]
            tree_data["nodes"][node]["left"] = delete_recursive(left_child, target)
        
        elif target > node:
            # Target in right subtree
            right_child = tree_data["nodes"][node]["right"]
            tree_data["nodes"][node]["right"] = delete_recursive(right_child, target)
        
        else:
            # Found the node to delete
            left_child = tree_data["nodes"][node]["left"]
            right_child = tree_data["nodes"][node]["right"]
            
            # Case 1: No children (leaf node)
            if left_child is None and right_child is None:
                del tree_data["nodes"][node]
                return None
            
            # Case 2: One child
            if left_child is None:
                del tree_data["nodes"][node]
                return right_child
            if right_child is None:
                del tree_data["nodes"][node]
                return left_child
            
            # Case 3: Two children
            # Find in-order successor (smallest in right subtree)
            successor = find_min(right_child)
            tree_data["nodes"][node]["right"] = delete_recursive(right_child, successor)
            tree_data["nodes"][node].update({...tree_data["nodes"][successor]})
            tree_data["nodes"][node]["left"] = left_child
            tree_data["nodes"][node]["right"] = tree_data["nodes"][node]["right"]
            del tree_data["nodes"][successor]
            return node
        
        return node
    
    tree_data["root"] = delete_recursive(tree_data["root"], value)
    return tree_data
```

**Deletion Cases**:
1. **Leaf Node** (no children): Simply delete
2. **One Child**: Replace with child
3. **Two Children**: Find successor, replace, delete successor

---

# 6️⃣ CHAT MESSAGE FLOW

## Complete Flow: User Sends Chat Message

### STEP 1: Frontend - User Types Message

**File**: `frontend/src/components/ChatPanel.jsx` (lines 80-120)

```javascript
// User sees chat input:
<div className="chat-input-area">
  <input
    type="text"
    value={userInput}
    onChange={(e) => setUserInput(e.target.value)}
    placeholder="Ask about the tree..."
    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
  />
  <button onClick={handleSendMessage}>Send</button>
</div>

// When user clicks Send:
const handleSendMessage = async () => {
  // STEP 1: Validation
  if (!userInput.trim()) return;
  
  // STEP 2: Add user message to local state immediately
  const newMessage = {
    id: Date.now(),
    text: userInput,
    sender: "User",
    timestamp: new Date()
  };
  
  dispatch(addMessage(newMessage));  // Show message immediately
  
  // STEP 3: Clear input
  setUserInput('');
  
  // STEP 4: Show typing indicator
  setIsTyping(true);
  
  try {
    // STEP 5: Call backend API
    const response = await treeAPI.chatMessage(selectedTree.id, userInput);
    
    // STEP 6: Add AI response
    dispatch(addMessage({
      id: Date.now(),
      text: response.response,
      sender: "AI",
      timestamp: new Date()
    }));
    
  } catch (error) {
    console.error('Chat error:', error);
  } finally {
    setIsTyping(false);
  }
};
```

**What happens**:
- Message added to Redux immediately (optimistic update)
- Typing indicator shown
- API called

### STEP 2: Frontend - API Call

**File**: `frontend/src/services/api.js` (lines 165-175)

```javascript
chatMessage: (treeId, message) =>
  apiCall(`/trees/${treeId}/chat`, {
    method: 'POST',
    body: JSON.stringify({ message: message }),
  }),
```

**Network Request**:
```
POST /trees/1/chat HTTP/1.1

{
  "message": "Insert node 5"
}
```

### STEP 3: Backend - Chat Endpoint

**File**: `backend/venv/main.py` (lines 400-450)

```python
@app.post("/trees/{tree_id}/chat")
def chat(
    tree_id: int,
    request: ChatRequest,  # Contains: { "message": "Insert node 5" }
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Handle user's chat message and return AI response
    """
    
    # STEP 1: Get tree
    tree = db.query(TreeSession).filter(TreeSession.id == tree_id).first()
    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")
    
    # STEP 2: Get tree data
    tree_data = tree.tree_data or {"root": None, "nodes": {}}
    
    # STEP 3: Send to AI Agent
    ai_response = handle_message(
        user_message=request.message,  # "Insert node 5"
        tree_data=tree_data,           # Current tree structure
        tree_id=tree_id
    )
    
    # STEP 4: Save both messages to database
    # User message
    user_msg = ChatMessage(
        tree_id=tree_id,
        user_id=db.query(User).filter(User.email == current_user).first().id,
        message=request.message,
        sender="User",
        timestamp=datetime.now(timezone.utc)
    )
    db.add(user_msg)
    
    # AI response
    ai_msg = ChatMessage(
        tree_id=tree_id,
        user_id=db.query(User).filter(User.email == current_user).first().id,
        message=ai_response,
        sender="AI",
        timestamp=datetime.now(timezone.utc)
    )
    db.add(ai_msg)
    
    # Save to database
    db.commit()
    
    # STEP 5: Return response
    return {
        "response": ai_response,
        "tree_data": tree_data
    }
```

### STEP 4: Backend - AI Agent

**File**: `backend/venv/ai_agent.py` (lines 1-100)

```python
def handle_message(user_message, tree_data, tree_id):
    """
    Process user message and generate AI response
    Uses rule-based logic to understand intent
    """
    
    message_lower = user_message.lower()
    
    # INTENT 1: Insert Operation
    if any(word in message_lower for word in ["insert", "add", "put"]):
        # Extract number from message
        import re
        numbers = re.findall(r'\d+', user_message)
        
        if numbers:
            value = int(numbers[0])
            try:
                tree_data = insert_node_to_tree(tree_data, value)
                # Persist updated tree
                update_tree_in_db(tree_id, tree_data)
                return f"✅ Successfully inserted {value} into the tree!"
            except Exception as e:
                return f"❌ Error inserting {value}: {str(e)}"
        else:
            return "ℹ️ Please specify which number to insert (e.g., 'Insert 5')"
    
    # INTENT 2: Delete Operation
    elif any(word in message_lower for word in ["delete", "remove", "remove"]):
        numbers = re.findall(r'\d+', user_message)
        
        if numbers:
            value = int(numbers[0])
            try:
                tree_data = delete_node_from_tree(tree_data, value)
                update_tree_in_db(tree_id, tree_data)
                return f"✅ Successfully deleted {value} from the tree!"
            except Exception as e:
                return f"❌ Error deleting {value}: {str(e)}"
        else:
            return "ℹ️ Please specify which number to delete"
    
    # INTENT 3: Query - Height
    elif any(word in message_lower for word in ["height", "how tall"]):
        height = calculate_height(tree_data)
        return f"📏 The height of the tree is {height}"
    
    # INTENT 4: Query - Leaf Nodes
    elif any(word in message_lower for word in ["leaf", "leaves", "leaf nodes"]):
        leaves = find_leaf_nodes(tree_data)
        if leaves:
            return f"🍃 The leaf nodes are: {', '.join(map(str, leaves))}"
        else:
            return "🍃 The tree has no leaf nodes"
    
    # INTENT 5: Query - Traversal
    elif "traversal" in message_lower or "traverse" in message_lower:
        if "inorder" in message_lower or "in-order" in message_lower:
            result = inorder_traversal(tree_data)
        elif "preorder" in message_lower or "pre-order" in message_lower:
            result = preorder_traversal(tree_data)
        elif "postorder" in message_lower or "post-order" in message_lower:
            result = postorder_traversal(tree_data)
        else:
            result = inorder_traversal(tree_data)
        
        return f"📋 Traversal result: {', '.join(map(str, result))}"
    
    # Default: Unknown intent
    else:
        return "❓ I didn't understand that. Try: 'Insert 5', 'Delete 3', 'Height?', 'Leaf nodes?', etc."
```

**Example: User says "Insert 5"**
```
Message: "Insert 5"
    ↓
Detect "insert" keyword ✓
    ↓
Extract number: 5
    ↓
Call: insert_node_to_tree(tree_data, 5)
    ↓
Tree updated
    ↓
Save to database
    ↓
Return: "✅ Successfully inserted 5 into the tree!"
```

### STEP 5: Database - Save Messages

**File**: `backend/venv/main.py`

```python
# User message saved
INSERT INTO chat_messages (tree_id, user_id, message, sender, timestamp)
VALUES (1, 5, 'Insert 5', 'User', NOW());

# AI message saved
INSERT INTO chat_messages (tree_id, user_id, message, sender, timestamp)
VALUES (1, 5, '✅ Successfully inserted 5 into the tree!', 'AI', NOW());
```

### STEP 6: Frontend - Display Messages

**File**: `frontend/src/components/ChatPanel.jsx` (lines 40-75)

```javascript
// Get messages from Redux
const messages = useSelector(state => state.chat.messages);

return (
  <div className="chat-panel">
    <div className="chat-messages">
      {messages.map((msg) => (
        <div key={msg.id} className={`message ${msg.sender.toLowerCase()}`}>
          <div className="message-header">
            <strong>{msg.sender}</strong>
            <span className="timestamp">
              {msg.timestamp.toLocaleTimeString()}
            </span>
          </div>
          <div className="message-body">
            {msg.text}
          </div>
        </div>
      ))}
    </div>
  </div>
);
```

**Rendering**:
```
User: Insert 5
     10:30 AM
─────────────────

AI: ✅ Successfully inserted 5 into the tree!
    10:30:01 AM
─────────────────
```

### Chat Complete ✅

```
User Sends Message
    ↓
Frontend Shows Message Immediately
    ↓
API Call (POST /trees/1/chat)
    ↓
Backend Receives Message
    ↓
AI Agent Analyzes Intent
    ↓
Extract Operation & Parameters
    ↓
Perform Operation
    ↓
Save Messages to Database
    ↓
Return Response
    ↓
Frontend Displays AI Response with Timestamp
    ↓
User Sees Conversation ✅
```

---

# 7️⃣ EDIT NODE FLOW

## User Clicks Edit Node

**File**: `frontend/src/components/ManualControls.jsx` (lines 250-295)

```javascript
// Form:
<section className="controls-section">
  <h3>✏️ Edit Node</h3>
  <input
    type="number"
    value={editNodeId}
    onChange={(e) => setEditNodeId(e.target.value)}
    placeholder="Node value to edit"
  />
  <input
    type="number"
    value={editNodeValue}
    onChange={(e) => setEditNodeValue(e.target.value)}
    placeholder="New value"
  />
  <button onClick={handleEditNode}>Update</button>
</section>

const handleEditNode = async (e) => {
  e.preventDefault();
  
  // Validation
  if (!editNodeId.trim() || !editNodeValue.trim()) {
    showStatus('Please fill all fields', 'error');
    return;
  }
  
  // Convert to integers
  const nodeId = parseInt(editNodeId);
  const newValue = parseInt(editNodeValue);
  
  try {
    // Call backend
    await treeAPI.updateNode(selectedTree.id, nodeId, newValue);
    
    showStatus(`Node updated successfully!`, 'success');
    await refreshTreeVisualization();
    
    setEditNodeId('');
    setEditNodeValue('');
    
  } catch (error) {
    showStatus('Failed to update node', 'error');
  }
};
```

**API Call**:
```
POST /trees/1/update

{
  "node_id": 5,
  "new_value": 15
}
```

**Backend** (in main.py):
```python
@app.post("/trees/{tree_id}/update")
def update_node(tree_id, request, current_user, db):
    tree = db.query(TreeSession).filter(TreeSession.id == tree_id).first()
    tree_data = tree.tree_data
    
    # Update the node value in dictionary
    if request.node_id in tree_data["nodes"]:
        old_node = tree_data["nodes"][request.node_id]
        tree_data["nodes"][request.new_value] = old_node
        del tree_data["nodes"][request.node_id]
        
        # Update references
        for node in tree_data["nodes"].values():
            if node["left"] == request.node_id:
                node["left"] = request.new_value
            if node["right"] == request.node_id:
                node["right"] = request.new_value
        
        if tree_data["root"] == request.node_id:
            tree_data["root"] = request.new_value
    
    tree.tree_data = tree_data
    db.commit()
    
    return {"success": True, "tree_data": tree_data}
```

---

# 8️⃣ SAVE/LOAD TREE FLOW

## Save Tree as JSON

**Frontend**:
```javascript
const handleSaveTree = async () => {
  // Get tree from backend
  const response = await treeAPI.getTree(selectedTree.id);
  
  // Convert to JSON string
  const dataStr = JSON.stringify(response, null, 2);
  
  // Create blob (binary data)
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  
  // Create download link
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `tree-${selectedTree.name}-${Date.now()}.json`;
  
  // Trigger download
  link.click();
  
  // Clean up
  URL.revokeObjectURL(url);
};
```

**What happens**:
- Tree data converted to JSON string
- Browser creates file
- File downloaded to user's computer

## Load Tree from JSON

```javascript
const handleLoadTree = () => {
  // Create file input
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json';
  
  // When file selected
  input.onchange = (event) => {
    const file = event.target.files[0];
    
    // Read file
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        // Parse JSON
        const data = JSON.parse(e.target.result);
        
        console.log('Loaded tree data:', data);
        alert('Tree data loaded. Create a tree with this structure.');
        
      } catch (error) {
        alert('Failed to load tree file');
      }
    };
    
    reader.readAsText(file);
  };
  
  // Trigger file picker
  input.click();
};
```

---

# 9️⃣ TREE VISUALIZATION FLOW

## How Tree Gets Drawn

### Process:

1. **Backend stores tree as JSON**:
```json
{
  "root": 10,
  "nodes": {
    "10": {"left": 5, "right": 15},
    "5": {"left": 3, "right": 7},
    "15": {"left": 12, "right": 20},
    "3": {"left": null, "right": null},
    "7": {"left": null, "right": null},
    "12": {"left": null, "right": null},
    "20": {"left": null, "right": null}
  }
}
```

2. **Frontend converts to React Flow format**:
```javascript
{
  "nodes": [
    { id: "10", data: { label: "10" }, position: { x: 0, y: 0 } },
    { id: "5", data: { label: "5" }, position: { x: -150, y: 100 } },
    { id: "15", data: { label: "15" }, position: { x: 150, y: 100 } },
    { id: "3", data: { label: "3" }, position: { x: -225, y: 200 } },
    ...
  ],
  "edges": [
    { id: "10-5", source: "10", target: "5" },
    { id: "10-15", source: "10", target: "15" },
    { id: "5-3", source: "5", target: "3" },
    ...
  ]
}
```

3. **React Flow renders visually**:
```
         [10]
        /    \
      [5]    [15]
     / \     /  \
   [3][7]  [12][20]
```

---

# 🔄 COMPLETE USER SESSION FLOW

```
User Opens App
    ↓
Frontend loads (React)
    ↓
Redux store initialized
    ↓
Check localStorage for token
    ↓
No token found
    ↓
Redirect to Register page
    ↓
User registers
    ↓
Token saved in localStorage
    ↓
User redirected to Dashboard
    ↓
Frontend fetches user's trees
    ↓
Redux updated with tree list
    ↓
User sees tree list
    ↓
User clicks "Create Tree"
    ↓
Tree created in database
    ↓
Redux updated
    ↓
User sees tree in list
    ↓
User clicks tree name
    ↓
Tree visualization loaded
    ↓
React Flow renders tree
    ↓
User clicks "Insert 5"
    ↓
Node inserted into tree
    ↓
Tree visualization updated
    ↓
User sees tree change
    ↓
User types "Insert 7" in chat
    ↓
AI understands intent
    ↓
Node inserted
    ↓
User sees chat response
    ↓
User closes browser
    ↓
Token persists in localStorage
    ↓
User reopens browser
    ↓
Frontend checks token
    ↓
Token found & valid
    ↓
User automatically logged in
    ↓
Dashboard loads with saved trees
    ↓
User continues working
```

---

# 📊 DATA FLOW SUMMARY

```
FRONTEND STATE (Redux):
├── auth
│   ├── user (email, id)
│   ├── access_token
│   └── isAuthenticated
├── tree
│   ├── trees (list)
│   ├── selectedTree
│   ├── visualization (nodes, edges)
│   └── loading
└── chat
    └── messages

         ↕ (HTTP REST API)

BACKEND STATE (Database):
├── users table
│   ├── id
│   ├── email
│   └── hashed_password
├── tree_sessions table
│   ├── id
│   ├── name
│   ├── tree_data (JSON)
│   ├── user_id (FK)
│   └── created_at
└── chat_messages table
    ├── id
    ├── message
    ├── sender
    ├── tree_id (FK)
    ├── user_id (FK)
    └── timestamp
```

---

# 🎯 KEY CONCEPTS

## 1. Tokens (Security)
- User logs in → Backend sends JWT token
- Token stored in browser localStorage
- Every request includes token in Authorization header
- Backend verifies token before processing request

## 2. Database Transactions
- `db.add()` - Stage change
- `db.commit()` - Execute query
- `db.refresh()` - Reload from database

## 3. Redux (State Management)
- Centralized store holds all app state
- Components subscribe to store
- When state changes, components re-render
- Prevents prop drilling

## 4. React Flow (Visualization)
- Backend stores tree as JSON
- Frontend converts to nodes/edges
- React Flow renders visually
- User can pan/zoom

## 5. Tree Algorithms
- Binary Search Tree insertion
- In-order, pre-order, post-order traversals
- Height calculation
- Leaf node finding

---

# 🚀 Now You Understand Everything!

You know:
✅ How each button click flows through the app  
✅ What functions are called at each step  
✅ What happens in the database  
✅ How data is converted between formats  
✅ How frontend and backend communicate  
✅ How state is managed and updated  
✅ How UI re-renders with new data  

**You can now:**
- Trace through any user action
- Understand where data comes from/goes to
- Add new features
- Debug issues
- Optimize performance

---

**Questions?** Ask about any specific flow or function!
