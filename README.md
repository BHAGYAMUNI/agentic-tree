# Agentic Tree - Interactive Tree Data Structure Explorer

A full-stack web application for visualizing, manipulating, and intelligently analyzing binary tree data structures using **React**, **FastAPI**, and **AI/LLM** integration.

## 🌟 Features

### Frontend ✨ (Recently Enhanced)
- **3-Panel Layout**: Optimized Controls | Canvas | Chat interface
- **Enhanced Navigation**: Save/Load/Share tree operations from top bar
- **Visual Tree Rendering**: Interactive tree canvas with React Flow
- **Manual Controls**: Insert, delete, **edit**, search, and traverse nodes
- **Chat with Timestamps**: AI-powered interactions with timestamped messages
- **Traversal Animations**: Pre-order, in-order, and post-order traversal visualization
- **Mobile Responsive**: Fully responsive design (Desktop/Tablet/Mobile)
- **Dark Mode Support**: Built-in light/dark theme with CSS variables
- **Authentication**: Register, login, and token-based session management
- **Redux State Management**: Centralized tree and authentication state

### Backend
- **RESTful API**: FastAPI with full CRUD operations for trees
- **JWT Authentication**: Secure access tokens and refresh token flow
- **Tree Operations**: Insert, delete, reset, search, **update** nodes
- **Chat Integration**: AI-powered natural language interface (OpenAI GPT-3.5 Turbo)
- **Database**: SQLAlchemy ORM with PostgreSQL/SQLite support
- **Alembic Migrations**: Version-controlled database schema
- **Rate Limiting**: Built-in request throttling
- **Logging & Monitoring**: Structured logging and optional Prometheus metrics

### DevOps & Testing
- **Docker Compose**: Easy local development and production deployment
- **CI/CD**: GitHub Actions automated testing and builds
- **Backend Tests**: pytest suite for tree utilities and API endpoints
- **Frontend Tests**: Jest + React Testing Library (scaffolded)

---

## 📖 Recent UI Improvements (Feb 2026)

We've significantly enhanced the UI to match professional design standards:

✅ **3-Panel Layout** - Organized Controls | Tree Canvas | AI Chat interface  
✅ **Top Bar Actions** - Save/Load/Share tree operations at a glance  
✅ **Chat Timestamps** - Track when each interaction occurred  
✅ **Edit Node Feature** - Update node values directly (NEW)  
✅ **Mobile Responsive** - Works perfectly on all device sizes  
✅ **Organized Controls** - Better-organized tree operations panel  

📚 **Documentation**:
- [UI_IMPROVEMENTS.md](./UI_IMPROVEMENTS.md) - Complete feature guide with screenshots
- [SCREENSHOTS_GUIDE.md](./SCREENSHOTS_GUIDE.md) - How to capture and use screenshots
- [DEMO_VIDEO_GUIDE.md](./DEMO_VIDEO_GUIDE.md) - Video script and recording guide

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (optional; use Docker `frontend_dev` service if not installed)
- PostgreSQL 16 (or use Docker)

### Local Development (Backend Only)

```bash
# 1. Clone the repo
git clone <repo-url>
cd agentic-tree

# 2. Set up backend venv
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables (optional)
cp .env.example .env
# Edit .env with your settings

# 5. Run migrations
python -m alembic upgrade head

# 6. Start the server
uvicorn venv.main:app --reload
```

Backend runs at `http://localhost:8000`. API docs available at `/docs`.

### Full Stack (with Docker Compose)

```bash
docker-compose up
```

This starts:
- **Backend** at `http://localhost:8000`
- **PostgreSQL** at `localhost:5432`
- **Frontend** at `http://localhost:5174` (or port 5173 in frontend_dev service)

## 📚 Project Structure

```
agentic-tree/
├── backend/
│   ├── venv/
│   │   ├── main.py                 # FastAPI app and endpoints
│   │   ├── auth.py                 # JWT and password utilities
│   │   ├── models.py               # SQLAlchemy ORM models
│   │   ├── schemas.py              # Pydantic validation schemas
│   │   ├── database.py             # SQLAlchemy config
│   │   ├── tree_utils.py           # Tree algorithms (insert, delete, traversals)
│   │   ├── ai_agent.py             # Chat orchestrator (rule-based + LLM)
│   │   ├── ai_agent_adapter.py     # LLM adapter (OpenAI integration)
│   │   └── ...
│   ├── alembic/
│   │   ├── env.py                  # Alembic configuration
│   │   ├── versions/               # Migration files
│   │   └── ...
│   ├── tests/
│   │   ├── test_endpoints.py       # Integration tests
│   │   ├── test_tree_utils.py      # Unit tests for tree logic
│   │   └── ...
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Docker image for backend
│   ├── README_LLM.md              # LLM integration guide
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── components/             # React components
│   │   │   ├── TreeCanvas.jsx      # React Flow tree visualization
│   │   │   ├── ManualControls.jsx  # Insert/delete/search UI
│   │   │   ├── ChatPanel.jsx       # AI chat interface
│   │   │   ├── Navbar.jsx          # Header and logout
│   │   │   └── ...
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx       # Main tree app page
│   │   │   ├── Login.jsx           # Authentication page
│   │   │   ├── Register.jsx        # Registration page
│   │   │   └── ...
│   │   ├── redux/
│   │   │   ├── store.js            # Redux store setup
│   │   │   ├── authSlice.js        # Auth state and async thunks
│   │   │   ├── treeSlice.js        # Tree state
│   │   │   ├── chatSlice.js        # Chat state
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── api.js              # HTTP client with auto-refresh tokens
│   │   ├── styles/                 # CSS modules (theme, components)
│   │   └── ...
│   ├── package.json
│   ├── vite.config.js
│   ├── jest.config.cjs             # Jest testing configuration
│   ├── Dockerfile
│   ├── START_HERE.md               # Frontend setup guide
│   └── ...
├── docker-compose.yml              # Multi-service orchestration
├── .github/workflows/ci.yml        # GitHub Actions pipeline
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

## 🔧 Configuration

### Backend Environment Variables

```ini
# Database
DATABASE_URL=postgresql://postgres:Postgres123@localhost:5432/agentic_tree_db
# SQLite for local testing: sqlite:///agentic_tree.db

# JWT & Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# LLM (Optional)
USE_LLM_AGENT=1
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo

# Rate Limiting
RATE_LIMIT=60
RATE_WINDOW_SECONDS=60

# Logging
LOG_LEVEL=INFO
```

Copy `.env.example` to `.env` and update values as needed.

## 🧪 Testing

### Backend Tests

```bash
cd backend
python -m pytest -v backend/tests
```

Tests cover:
- Tree utilities (insert, delete, traversals)
- API endpoints (auth, create tree, chat)

### Frontend Tests

```bash
cd frontend
npm test
```

## 📖 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for **interactive Swagger UI**.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login (email + password) |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/me` | Get current user info |
| POST | `/trees` | Create a new tree |
| GET | `/trees` | List user's trees |
| GET | `/trees/{id}` | Get tree details |
| POST | `/trees/{id}/insert` | Insert a node |
| POST | `/trees/{id}/delete` | Delete a node |
| POST | `/trees/{id}/search` | Search for a node |
| GET | `/trees/{id}/traversal` | Get traversal order |
| POST | `/chat` | Chat with AI agent |

## 🤖 AI/LLM Integration

Optional **GPT-3.5 Turbo** integration for intelligent chat:

```bash
export OPENAI_API_KEY="sk-..."
export USE_LLM_AGENT=1
uvicorn venv.main:app --reload
```

See [README_LLM.md](backend/README_LLM.md) for full details.

## 🚢 Deployment

### Docker Compose (Local)

```bash
docker-compose up --build
```

Services start on:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5174`
- PostgreSQL: `localhost:5432`

### Production Checklist

- [ ] Use a production-grade database (PostgreSQL on AWS RDS, Azure Database, etc.)
- [ ] Set strong `SECRET_KEY` and credentials in environment
- [ ] Enable HTTPS/TLS on your domain
- [ ] Use a secret manager (AWS Secrets Manager, HashiCorp Vault)
- [ ] Set up rate limiting with Redis or a WAF
- [ ] Enable CORS only for your frontend domain
- [ ] Use a reverse proxy (Nginx, CloudFlare)
- [ ] Set up monitoring and alerting (DataDog, New Relic, etc.)
- [ ] Enable audit logging
- [ ] Run security scans (OWASP, Snyk)

## 📝 Documentation

- **Frontend**: See [START_HERE.md](frontend/START_HERE.md)
- **LLM Integration**: See [README_LLM.md](backend/README_LLM.md)
- **Alembic Migrations**: See [README_ALEMBIC.md](backend/README_ALEMBIC.md)
- **Observability**: See [README_OBSERVABILITY.md](backend/README_OBSERVABILITY.md)

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Verify venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Database errors

```bash
# Reset migrations (careful—deletes data!)
python -m alembic downgrade base
python -m alembic upgrade head

# Or use SQLite for testing
export DATABASE_URL=sqlite:///test.db
```

### Frontend can't connect to backend

- Check backend is running: `curl http://localhost:8000/`
- Verify `VITE_API_URL` in frontend `.env`
- Check CORS settings in backend [main.py](backend/venv/main.py)

## 📊 Architecture Diagram

```
┌─────────────────┐
│   Frontend      │
│   (React/Vite) │
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────────────────────────┐
│   Backend (FastAPI)                 │
├─────────────────────────────────────┤
│ • Auth (JWT)                        │
│ • Tree CRUD                         │
│ • Chat (Rule-based + LLM)          │
│ • Rate Limiting                     │
│ • Logging & Metrics                 │
└────────┬──────────────────┬──────────┘
         │                  │
         ↓                  ↓
    ┌─────────┐       ┌──────────────┐
    │PostgreSQL│       │ OpenAI API   │
    │Database │       │ (Optional)   │
    └─────────┘       └──────────────┘
```

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is open-source. See LICENSE file for details.

## 🙏 Acknowledgments

- **React Flow** for tree visualization
- **FastAPI** for the backend framework
- **SQLAlchemy** for ORM
- **OpenAI** for the LLM API
- All contributors and testers

## 📞 Support

For issues, questions, or feedback:
- Open a GitHub issue
- Check existing documentation
- Review backend logs: `docker-compose logs backend`
- Review frontend console: Browser DevTools → Console

---

**Happy tree exploring! 🌳**
