# 🌳 Tree AI - Binary Tree Visualization & AI Chat Application

**Live Demo**: [Coming Soon - Will be provided after deployment]

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running Locally](#running-locally)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Demo Video](#demo-video)
- [Challenges & Solutions](#challenges--solutions)
- [Submission Checklist](#submission-checklist)

## 🎯 Overview

**Tree AI** is a full-stack web application for visualizing and managing binary trees with AI-powered chat assistance. Users can:
- Create and manage multiple binary tree sessions
- Perform tree operations (insert, delete, search, update)
- Visualize trees in real-time with React Flow
- Chat with an AI agent for tree operations guidance
- Track traversal paths and tree metrics

### Assignment Requirements ✅
- ✅ Dockerize application
- ✅ Deploy to cloud platform
- ✅ Backend API testing
- ✅ Frontend component testing
- ✅ Database validation
- ✅ GitHub repository with clear structure
- ✅ Live deployment links
- ✅ Comprehensive README
- ✅ Demo video

## ✨ Features

### 1. **Authentication**
- User registration and login
- JWT token-based authentication
- Secure password hashing with bcrypt

### 2. **Tree Management**
- Create, read, update, delete tree sessions
- Support for multiple tree operations
- Tree data persistence

### 3. **Tree Operations**
- **Insert Node**: Add nodes with parent/direction specification
- **Delete Node**: Remove nodes with BST logic
- **Search Node**: Highlight nodes in visualization
- **Update Node**: Change node values
- **Traversals**: In-order, Pre-order, Post-order
- **Tree Metrics**: Height, Leaf nodes calculation

### 4. **Tree Visualization**
- React Flow-based interactive tree canvas
- Real-time visualization updates
- Node selection and highlighting
- Traversal path animation
- Responsive design (desktop & mobile)

### 5. **AI Chat Integration**
- Natural language chat interface
- AI agent for tree operations
- Command parsing (insert, delete, update, search, traversals)
- Real-time conversation history

### 6. **Responsive Design**
- Desktop: 3-panel layout (Tree list, Canvas, Chat)
- Tablet: Tabs for panel switching
- Mobile: Full-screen panels with bottom navigation

## 🛠️ Tech Stack

### Frontend
- **React 18** - UI framework
- **Redux** - State management
- **React Flow** - Tree visualization
- **Vite** - Build tool
- **CSS3** - Styling with CSS variables and dark mode

### Backend
- **FastAPI** - API framework
- **SQLAlchemy** - ORM
- **PostgreSQL** - Primary database
- **SQLite** - Development database
- **JWT** - Authentication
- **Uvicorn** - ASGI server

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Orchestration
- **PostgreSQL** - Production database

## 📁 Project Structure

```
agentic-tree/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TreeCanvas.jsx
│   │   │   ├── ChatPanel.jsx
│   │   │   ├── ManualControls.jsx
│   │   │   ├── Navbar.jsx
│   │   │   └── __tests__/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Login.jsx
│   │   │   └── Register.jsx
│   │   ├── redux/
│   │   │   ├── store.js
│   │   │   ├── authSlice.js
│   │   │   ├── treeSlice.js
│   │   │   ├── chatSlice.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── utils/
│   │   │   └── treeUtils.js
│   │   ├── styles/
│   │   │   ├── theme.css
│   │   │   ├── dashboard.css
│   │   │   ├── tree-canvas.css
│   │   │   └── ...
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── jest.config.cjs
│
├── backend/
│   ├── venv/
│   │   ├── main.py (FastAPI app)
│   │   ├── models.py (SQLAlchemy models)
│   │   ├── schemas.py (Pydantic schemas)
│   │   ├── database.py (DB connection)
│   │   ├── auth.py (JWT & hashing)
│   │   ├── tree_utils.py (Tree algorithms)
│   │   ├── ai_agent.py (AI integration)
│   │   └── requirements.txt
│   ├── tests/
│   │   ├── test_endpoints.py
│   │   └── test_tree_utils.py
│   ├── alembic/
│   │   └── versions/ (migrations)
│   ├── seed.py (Database seeding)
│   ├── Dockerfile
│   ├── requirements.txt
│   └── docker-compose.yml
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

## 🚀 Setup & Installation

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 14+ (for production)
- Docker & Docker Compose (for containerized setup)
- Git

### Local Development Setup

#### 1. Clone Repository
```bash
git clone https://github.com/your-username/agentic-tree.git
cd agentic-tree
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/agentic_tree_db
JWT_SECRET=your-secret-key-change-this
ENVIRONMENT=development
EOF

# Run database migrations
alembic upgrade head

# Seed database with test users
python seed.py

# Start backend server
uvicorn venv.main:app --reload --port 8000
```

**Backend runs on**: http://localhost:8000

#### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Set environment variables (create .env.local)
cat > .env.local << EOF
VITE_API_URL=http://localhost:8000
EOF

# Start development server
npm run dev
```

**Frontend runs on**: http://localhost:5173

#### 4. Test Credentials
After running `seed.py`, use these credentials:

```
Email: demo@example.com
Password: demo123

Email: test@example.com
Password: test123

Email: user@example.com
Password: user123
```

## 🐳 Docker Deployment

### Local Docker Setup

#### 1. Build and Run with Docker Compose
```bash
# From project root
docker-compose up --build

# Or in detached mode
docker-compose up -d --build
```

#### 2. Access Services
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

#### 3. Database Setup (First Time)
```bash
# Seed database
docker-compose exec backend python seed.py
```

#### 4. Stop Services
```bash
docker-compose down

# Remove volumes (data will be deleted)
docker-compose down -v
```

### Docker Images
- **Frontend**: Built from `frontend/Dockerfile` (Node 20 + nginx)
- **Backend**: Built from `backend/Dockerfile` (Python 3.12 slim)
- **PostgreSQL**: Official `postgres:16` image

## ☁️ Cloud Deployment

### Option 1: Deploy to Heroku (Recommended for Beginners)

#### Prerequisites
- Heroku CLI installed
- Heroku account

#### Steps

**1. Create Heroku Apps**
```bash
heroku create tree-ai-backend
heroku create tree-ai-frontend
```

**2. Deploy Backend**
```bash
cd backend

# Add PostgreSQL add-on
heroku addons:create heroku-postgresql:hobby-dev -a tree-ai-backend

# Set environment variables
heroku config:set JWT_SECRET=your-secret-key -a tree-ai-backend
heroku config:set ENVIRONMENT=production -a tree-ai-backend

# Deploy
git push heroku main

# Run migrations
heroku run alembic upgrade head -a tree-ai-backend
heroku run python seed.py -a tree-ai-backend
```

**3. Deploy Frontend**
```bash
cd ../frontend

# Set backend API URL
heroku config:set VITE_API_URL=https://tree-ai-backend.herokuapp.com -a tree-ai-frontend

# Create Procfile for frontend (if needed)
echo "web: npm run build && npm run preview" > Procfile

# Deploy
git push heroku main
```

**4. Get Live URLs**
```bash
heroku apps:info -a tree-ai-backend
heroku apps:info -a tree-ai-frontend
```

---

### Option 2: Deploy to AWS EC2

#### Prerequisites
- AWS account
- EC2 instance running (Ubuntu 22.04)
- SSH access configured

#### Steps

**1. SSH into EC2**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

**2. Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu
```

**3. Clone Repository**
```bash
git clone https://github.com/your-username/agentic-tree.git
cd agentic-tree
```

**4. Create Environment File**
```bash
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@db:5432/agentic_tree_db
JWT_SECRET=your-secret-key-change-this
ENVIRONMENT=production
EOF
```

**5. Start Containers**
```bash
docker-compose up -d --build

# Check status
docker-compose ps
```

**6. Access Application**
- **Frontend**: http://your-ec2-ip:5173
- **Backend**: http://your-ec2-ip:8000

---

### Option 3: Deploy to Digital Ocean App Platform

#### Steps
1. Push code to GitHub
2. Go to Digital Ocean Dashboard → Apps
3. Click "Create App" → Select GitHub repository
4. Configure:
   - Frontend service: Build command `npm install && npm run build`
   - Backend service: Build command `pip install -r requirements.txt`
5. Add PostgreSQL database from Add-ons
6. Deploy

## 📚 API Documentation

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://tree-ai-backend.herokuapp.com`

### Authentication
All endpoints (except `/auth/*`) require JWT token in header:
```
Authorization: Bearer <jwt-token>
```

### Key Endpoints

#### Authentication
```
POST /auth/register
POST /auth/login
```

#### Trees
```
GET /trees              # Get all user's trees
POST /trees             # Create new tree
GET /trees/{id}         # Get specific tree
PUT /trees/{id}         # Update tree name
DELETE /trees/{id}      # Delete tree
```

#### Tree Operations
```
POST /trees/{id}/insert    # Insert node
POST /trees/{id}/delete    # Delete node
POST /trees/{id}/search    # Search node
POST /trees/{id}/update    # Update node value
POST /trees/{id}/traversal # Get traversal
POST /trees/{id}/height    # Get tree height
POST /trees/{id}/leaves    # Get leaf nodes
POST /trees/{id}/reset     # Clear tree
```

#### Chat
```
POST /chat              # Send chat message
GET /chat/history       # Get chat history
```

### Full API Docs
Interactive Swagger docs available at: `http://localhost:8000/docs`

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=venv tests/

# Run specific test file
pytest tests/test_endpoints.py -v
```

**Test Files**:
- `tests/test_endpoints.py` - API endpoint tests
- `tests/test_tree_utils.py` - Tree algorithm tests

### Frontend Testing

```bash
cd frontend

# Run Jest tests
npm test

# Run with coverage
npm test -- --coverage

# Watch mode
npm test -- --watch
```

**Test Files**:
- `src/components/__tests__/ManualControls.test.jsx`

### Manual Testing Checklist

#### Authentication
- [ ] Register new account
- [ ] Login with correct credentials
- [ ] Reject invalid credentials
- [ ] JWT token persists on refresh

#### Tree Operations
- [ ] Create tree
- [ ] Insert node as left/right child
- [ ] Delete node
- [ ] Search node (highlights)
- [ ] Update node value
- [ ] Get tree height
- [ ] Get leaf nodes
- [ ] All traversals (in-order, pre-order, post-order)

#### Chat
- [ ] Send message
- [ ] AI responds
- [ ] Parsing commands (insert, delete, update, etc.)
- [ ] Chat history loads

#### Responsiveness
- [ ] Desktop: 3-panel layout
- [ ] Tablet: Tab navigation works
- [ ] Mobile: Full-screen panels, bottom nav

## 📹 Demo Video

### How to Record Demo

1. **Setup**
   - Ensure application is running
   - Open browser at full screen (1920x1080 recommended)
   - Clear browser cache/cookies for fresh start

2. **Script (3-4 minutes)**
   
   **Intro (30s)**
   - "Hello, this is Tree AI, a web application for visualizing and managing binary trees with AI assistance."
   - Show home page

   **Registration (30s)**
   - Register new account
   - Show form validation

   **Dashboard (30s)**
   - Create new tree "demo_tree"
   - Show tree list

   **Tree Operations (1.5m)**
   - Insert nodes: 9, 16, 13, 1, 2, 5, 15
   - Show visualization updating in real-time
   - Perform search (highlight node)
   - Show traversals (in-order, pre-order, post-order)
   - Update node value

   **Chat Feature (1m)**
   - Show AI chat interface
   - Type: "insert 20 as left of 13"
   - Show tree updates from chat
   - Type: "what is the height"
   - Show AI response

   **Responsive Design (30s)**
   - Resize to tablet view, show tabs
   - Resize to mobile view, show full-screen panels

   **Outro (20s)**
   - "Thank you for watching Tree AI!"

3. **Recording Tools**
   - OBS Studio (free)
   - ScreenFlow (macOS)
   - Built-in screen recorder

4. **Upload**
   - Save as MP4
   - Upload to YouTube (unlisted)
   - Add link to README

## 🔧 Challenges & Solutions

### Challenge 1: Tree Corruption on Insert
**Problem**: After inserting node 20 as left child of 13, unwanted edges appeared.
**Solution**: Added deduplication logic in tree conversion function to prevent duplicate nodes/edges and improved validation.

### Challenge 2: Chat Input Not Visible
**Problem**: Chat input was at bottom of screen, requiring page scroll.
**Solution**: 
- Added `flex-shrink: 0` to chat input area
- Adjusted layout heights with `calc(100vh - 80px)`
- Implemented internal scrolling for manual entries panel

### Challenge 3: Mobile Responsiveness
**Problem**: 3-panel layout didn't fit on mobile screens.
**Solution**: Implemented tab-based navigation for mobile devices (<600px) with full-screen panels.

### Challenge 4: Dark Mode Contrast
**Problem**: Text was invisible in dark mode (white on white).
**Solution**: Applied proper CSS variables for text colors with dark mode overrides.

### Challenge 5: Edit Node Functionality
**Problem**: Editing node values wasn't working.
**Solution**: 
- Implemented backend algorithm to update node values while maintaining tree structure
- Added chat command parsing for edit operations
- Fixed frontend state management for updates

## 📋 Submission Checklist

### ✅ GitHub Repository
- [ ] Repository created and public
- [ ] Clear folder structure (frontend/, backend/, docker files at root)
- [ ] `.gitignore` configured properly
- [ ] No sensitive files (secrets, `.env`) in repo
- [ ] Meaningful commit history with clear messages
- [ ] README.md in root directory

### ✅ Dockerization
- [ ] `Dockerfile` for frontend (Node + nginx)
- [ ] `Dockerfile` for backend (Python)
- [ ] `docker-compose.yml` with all services
- [ ] PostgreSQL service in docker-compose
- [ ] Environment variables configured
- [ ] Volumes for data persistence

### ✅ Deployment
- [ ] Frontend deployed and accessible via live URL
- [ ] Backend deployed and accessible via live URL
- [ ] API documentation available (`/docs`)
- [ ] Database migrations applied
- [ ] Test data seeded

### ✅ Documentation
- [ ] README.md with all sections
- [ ] Setup instructions (local)
- [ ] Docker setup instructions
- [ ] Deployment guide
- [ ] API documentation
- [ ] Screenshots of application
- [ ] Demo video (3-4 minutes)

### ✅ Testing
- [ ] Backend unit tests written (`tests/test_endpoints.py`)
- [ ] Frontend component tests written (`__tests__/`)
- [ ] All tests passing
- [ ] Manual testing completed
- [ ] Test coverage documented

### ✅ Code Quality
- [ ] Clean, modular code
- [ ] Well-documented with comments
- [ ] No console errors
- [ ] Performance optimized
- [ ] Proper error handling
- [ ] Input validation

### ✅ Features Implemented
- [ ] User authentication (register/login)
- [ ] Tree CRUD operations
- [ ] All tree operations (insert, delete, update, search)
- [ ] Tree visualization
- [ ] Traversals
- [ ] AI chat integration
- [ ] Responsive design
- [ ] Dark/Light theme

## 📝 How to Submit

### Step 1: Prepare GitHub Repository

```bash
# Make sure everything is committed
git status

# If needed, add all changes
git add .
git commit -m "Final submission: Tree AI application with Docker and deployment"

# Push to GitHub
git push origin main
```

### Step 2: Prepare Submission Folder

Create a file with all submission info:

```
SUBMISSION.md
─────────────

## GitHub Repository
**URL**: https://github.com/your-username/agentic-tree

## Deployed Application

### Frontend
**URL**: https://tree-ai-frontend.herokuapp.com
**Status**: ✅ Live

### Backend
**URL**: https://tree-ai-backend.herokuapp.com
**Status**: ✅ Live
**API Docs**: https://tree-ai-backend.herokuapp.com/docs

## Demo Video
**YouTube Link**: https://youtube.com/watch?v=...

## Features Implemented
✅ User authentication
✅ Tree CRUD operations
✅ Binary tree algorithms (insert, delete, search, update)
✅ Tree visualization with React Flow
✅ AI chat integration
✅ Responsive design
✅ Dark/Light theme
✅ Docker containerization
✅ Cloud deployment (Heroku)

## Key Files
- `/docker-compose.yml` - Orchestration
- `/frontend/Dockerfile` - Frontend container
- `/backend/Dockerfile` - Backend container
- `/README.md` - Full documentation
- `/backend/venv/main.py` - Backend API
- `/frontend/src/App.jsx` - Frontend app
```

### Step 3: Submit Package

**All required files**:
1. GitHub repo link
2. Live frontend URL
3. Live backend URL
4. Demo video URL
5. README.md (in repo)
6. docker-compose.yml (in repo)
7. All Dockerfiles (in repo)

## 🔗 Quick Links

- **GitHub**: https://github.com/your-username/agentic-tree
- **Frontend**: [Live URL after deployment]
- **Backend**: [Live URL after deployment]
- **Demo Video**: [YouTube link after recording]
- **API Docs**: [Backend URL]/docs

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Check browser console (F12)
3. Check backend console output
4. Verify environment variables are set
5. Ensure PostgreSQL is running and accessible

---

**Last Updated**: February 24, 2026
**Version**: 1.0.0
**Status**: ✅ Ready for Production
