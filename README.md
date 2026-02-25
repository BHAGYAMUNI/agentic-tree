# Agentic Tree - Binary Tree Data Structure Explorer

A full-stack web application for visualizing and intelligently analyzing binary tree data structures with AI chat integration.

**Live Demo:**
- Frontend: https://agentic-tree-2.onrender.com/register
- Backend API: https://agentic-tree-1.onrender.com/
- API Documentation: https://agentic-tree-1.onrender.com/docs

---

## 🌟 Features Implemented

### Core Functionality
- ✅ **User Authentication** - Register, login, JWT tokens with bcrypt password hashing
- ✅ **Binary Tree CRUD** - Create, insert, delete, search, update nodes
- ✅ **Tree Visualization** - Interactive React Flow canvas displaying binary trees
- ✅ **AI Chat Integration** - Ask questions about trees, get intelligent responses
- ✅ **Chat History** - Persistent storage of all chat interactions
- ✅ **Tree Operations** - Insert, delete, search, in-order/pre-order/post-order traversals
- ✅ **Responsive Design** - Works on desktop, tablet, and mobile devices
- ✅ **API Documentation** - Interactive Swagger UI at `/docs`

### Technology Stack
- **Frontend:** React 18, Redux, React Flow, Vite
- **Backend:** FastAPI, SQLAlchemy ORM, PostgreSQL
- **Authentication:** JWT tokens, bcrypt password hashing
- **AI Integration:** OpenAI GPT-3.5 Turbo (optional)
- **Testing:** pytest (backend), Jest (frontend)
- **Deployment:** Docker, docker-compose, Render

---

## 📸 Screenshots

### 1. Login Page
![Login](./frontend/public/screenshots/login.png)

### 2. Registration Page
![Register](./frontend/public/screenshots/register.png)

### 3. Dashboard - Tree Visualization
![Dashboard](./frontend/public/screenshots/dahsboard.png)

### 4. Tree Visualization (React Flow)
![Tree Visual](./frontend/public/screenshots/tree_Visual.png)

### 5. Manual Controls (Insert/Delete/Search)
![Manual Controls](./frontend/public/screenshots/manual.png)

### 6. AI Chat Interface
![Chat](./frontend/public/screenshots/chatbot.png)

### 7. Save/Load Operations
![Save](./frontend/public/screenshots/save.png)

---

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/BHAGYAMUNI/agentic-tree.git
cd agentic-tree

# Start all services
docker-compose up

# Access the application
Frontend: http://localhost:5174
Backend: http://localhost:8000
API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

**Prerequisites:** Python 3.11+, Node.js 18+, PostgreSQL 16

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
python -m alembic upgrade head
uvicorn venv.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Test Credentials
```
Email: raju@example.com
Password: 987654
```

---

## 📖 API Documentation

All endpoints are documented in the **interactive Swagger UI** at `/docs` when backend is running.

### Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/register` | POST | User registration |
| `/auth/login` | POST | User login |
| `/trees` | GET/POST | List or create trees |
| `/trees/{id}/insert` | POST | Insert node into tree |
| `/trees/{id}/delete` | POST | Delete node from tree |
| `/trees/{id}/search` | POST | Search for node |
| `/chat` | POST | Chat with AI agent |

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
```

**Coverage:**
- Tree algorithms (insert, delete, traversals, height, leaves)
- API endpoints (auth, tree CRUD, chat)
- JWT authentication and protected routes

### Frontend Tests
```bash
cd frontend
npm install
npm test
```

---

## 🛠️ Development Process

### Architecture
1. **Frontend (React + Redux)** - Interactive UI with state management
2. **Backend (FastAPI)** - RESTful API with JWT authentication
3. **Database (PostgreSQL)** - Persistent data storage with SQLAlchemy ORM
4. **AI Integration** - Optional OpenAI GPT-3.5 Turbo for intelligent chat

### Key Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Tree state synchronization | Redux state management for consistent UI updates |
| User authentication security | JWT tokens with bcrypt password hashing |
| Real-time visualization | React Flow for interactive tree rendering |
| AI chat responsiveness | Rule-based fallback when LLM unavailable |
| Database consistency | SQLAlchemy foreign keys with cascade delete |
| Responsive design | CSS grid/flexbox with mobile breakpoints |

---

## 📦 Deployment

### Architecture Overview

```
Frontend (Render Static Site)
↓
Backend API (Render Web Service - Docker)
↓
PostgreSQL (Render Managed Database)
```

### Local Development Setup

**Step 1: Dockerize the Application**

Created Dockerfiles for both services:

**Backend Dockerfile:**
- Based on Python 3.11 image
- Installed dependencies from requirements.txt
- Exposed port 8000
- Ran FastAPI with Uvicorn

**Frontend Dockerfile:**
- Multi-stage build
- Node 20 for build phase
- Nginx for serving production build
- Exposed port 80

**Docker Compose Orchestration:**

```bash
docker-compose up --build
```

This starts:
- Backend service (port 8000)
- Frontend service (port 5174)
- PostgreSQL database (port 5432)

**Step 2: Local Testing**

Verified all functionality:
```bash
# Test Swagger API docs
curl http://localhost:8000/docs

# Test registration & login
curl -X POST http://localhost:8000/auth/register

# Test tree operations
curl http://localhost:8000/trees

# Check database persistence
docker exec agentic-tree-db psql -U postgres -d agentic_tree_db
```

### Production Deployment (Render)

**Step 1: Database Setup**

Created managed PostgreSQL on Render:
- Persistent cloud database
- Not tied to container lifecycle
- Automatically backed up
- Connection via `DATABASE_URL` environment variable

**Step 2: Backend Deployment**

Deployed as **Render Web Service (Docker)**:

```
1. Connected GitHub repository
2. Set root directory: backend/
3. Selected Dockerfile
4. Added environment variables:
   - DATABASE_URL (from Render PostgreSQL)
   - SECRET_KEY (for JWT signing)
   - OPENAI_API_KEY (optional, for LLM)
   - JWT_ALGORITHM=HS256
   - ACCESS_TOKEN_EXPIRE_MINUTES=30
5. Deployed
```

**Backend Live:** https://agentic-tree-1.onrender.com
**API Docs:** https://agentic-tree-1.onrender.com/docs

**Step 3: Frontend Deployment**

Deployed as **Render Static Site**:

```
1. Connected GitHub repository
2. Set root directory: frontend/
3. Build command:
   npm install --legacy-peer-deps && npm run build
4. Publish directory: dist/
5. Added environment variable:
   VITE_API_URL=https://agentic-tree-1.onrender.com
6. Deployed
```

**Frontend Live:** https://agentic-tree-2.onrender.com/register

**Step 4: CORS Configuration**

Since frontend and backend are on different domains, configured CORS in FastAPI:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://agentic-tree-2.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This allows secure cross-domain communication.

### Environment Variables (`.env`)

**Backend:**
```ini
# Database
DATABASE_URL=postgresql://user:password@host:5432/agentic_tree_db

# JWT Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# LLM (Optional)
USE_LLM_AGENT=1
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
```

**Frontend:**
```
VITE_API_URL=https://agentic-tree-1.onrender.com
```

### CI/CD Pipeline (Bonus)

Created GitHub Actions workflow that:
- Runs pytest for backend tests
- Runs Jest for frontend tests
- Validates database schema
- Ensures all tests pass before deployment

### Deployment Summary

| Component | Platform | Status |
|-----------|----------|--------|
| Backend | Render Web Service (Docker) | ✅ Live |
| Frontend | Render Static Site | ✅ Live |
| Database | Render PostgreSQL | ✅ Live |
| API Docs | `/docs` endpoint | ✅ Available |
| Health Check | `/health` endpoint | ✅ Working |

**Why Render?**

Assignment specified: *"Deploy to a cloud platform (e.g., Heroku, AWS EC2)"*

- "e.g." = examples, not exhaustive list
- Render provides:
  - Easy Docker deployment
  - Managed PostgreSQL
  - Free tier for learning
  - Native GitHub integration
  - Automatic redeploys on push

### Deployment Checklist

- ✅ Backend containerized with Docker
- ✅ Frontend containerized with Docker
- ✅ Local testing with docker-compose
- ✅ Database migrated to cloud (Render PostgreSQL)
- ✅ Backend deployed to Render
- ✅ Frontend deployed to Render
- ✅ Environment variables configured
- ✅ CORS enabled for frontend domain
- ✅ Health check endpoint working
- ✅ API documentation accessible
- ✅ CI/CD pipeline running

---

## 📁 Project Structure

```
agentic-tree/
├── backend/
│   ├── venv/
│   │   ├── main.py              # FastAPI app & endpoints
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── tree_utils.py        # Tree algorithms
│   │   ├── ai_agent.py          # AI orchestrator
│   │   ├── ai_agent_adapter.py  # LLM integration
│   │   └── auth.py              # JWT & password hashing
│   ├── tests/
│   │   ├── test_tree_utils.py   # Unit tests
│   │   └── test_endpoints.py    # Integration tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Pages (Login, Dashboard)
│   │   ├── redux/               # State management
│   │   └── services/            # API calls
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml           # Multi-service orchestration
└── README.md
```

---

## 📊 Database Schema

### Tables
- **users** - User accounts (email, password hash)
- **trees** - Binary tree data per user
- **chat_messages** - Chat history with timestamps

### Relationships
- User → Trees (one-to-many, cascade delete)
- Tree → Chat Messages (one-to-many, cascade delete)

---

## 🚢 Production Deployment Checklist

- ✅ Code pushed to GitHub
- ✅ Environment variables configured in cloud platform
- ✅ Database backup strategy in place
- ✅ API rate limiting enabled
- ✅ CORS configured for frontend domain only
- ✅ HTTPS/SSL enabled
- ✅ Backend and frontend both deployed
- ✅ Health check endpoint working (`/health`)
- ✅ API documentation accessible (`/docs`)
- ✅ Tests passing locally

---

## 🤖 AI Integration

The chat system uses **rule-based pattern matching** as the primary method, with optional **OpenAI GPT-3.5 Turbo** for more intelligent responses.

To enable LLM:
```bash
export OPENAI_API_KEY="sk-..."
export USE_LLM_AGENT=1
```

The system intelligently falls back to rule-based responses if LLM is unavailable.

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port already in use | Change port in docker-compose.yml or kill process using port |
| Database connection error | Verify DATABASE_URL and PostgreSQL is running |
| Frontend can't reach backend | Check CORS settings and API_URL in frontend config |
| Tests failing | Ensure all dependencies installed: `pip install -r requirements.txt` |

---

## 🎬 Demo Video

**Full 3-4 minute demo showing all features:**

[Watch Demo Video on YouTube](https://youtu.be/toXxtCOx6qc)

**Demo includes:**
- User registration and login
- Creating a binary tree
- Inserting and deleting nodes
- Real-time tree visualization
- AI chat interaction
- Responsive mobile view

---

## 🙏 Acknowledgments

- **React Flow** - Tree visualization library
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **OpenAI** - LLM API
- **Render** - Cloud deployment platform

---

## 📞 Support

For issues or questions:
- Check API documentation at `/docs`
- Review logs: `docker-compose logs backend`
- Check browser console: Browser DevTools → Console

---

**Built with ❤️ for learning tree data structures and AI integration.**
