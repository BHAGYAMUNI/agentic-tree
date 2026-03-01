Agentic Tree - Binary Tree Data Structure Explorer

A full-stack web application for visualizing and intelligently analyzing Binary Tree data structures with LangGraph + LangChain AI agent integration for natural language tree operations.

🌐 Live Demo

Frontend: https://agentic-tree-2.onrender.com

Backend API: https://agentic-tree-1.onrender.com/

API Documentation: https://agentic-tree-1.onrender.com/docs

🌟 Features Implemented
Core Functionality

✅ User Authentication – Register, login, JWT-based authentication with bcrypt password hashing

✅ Binary Tree CRUD – Create, insert, delete, search, and update nodes

✅ Tree Visualization – Interactive React Flow canvas displaying Binary Tree structure

✅ AI Chat Integration – LangGraph + LangChain agent for natural language tree operations

✅ Intent Classification & Routing – Intelligent request router for separating conversational queries and structured tree operations

✅ Chat History – Persistent storage of chat interactions per tree

✅ Tree Operations Supported

Insert (left/right under parent)

Delete (with subtree handling)

Update node values

Search node

Height calculation

Leaf node detection

Node count

In-order, Pre-order, Post-order traversals

✅ Manual Controls – REST API endpoints for direct tree manipulation

✅ Flexible Natural Language Support – Accepts multiple phrasing styles (e.g., “insert 5 under 3”, “add 5 as left child of 3”)

✅ Tree Reset – Clear entire tree and start fresh

✅ Comprehensive Error Handling – Validation and user-friendly error messages

✅ Responsive UI – Works across desktop, tablet, and mobile devices

✅ Swagger API Documentation – Available at /docs

✅ Automated Test Suite – Backend and frontend tests integrated with CI

🛠 Technology Stack
Frontend

React 18

Redux Toolkit

React Flow (tree visualization)

Vite

Jest

Backend

FastAPI

SQLAlchemy ORM

PostgreSQL (Production)

SQLite (Testing)

JWT Authentication

bcrypt password hashing

AI Architecture

LangGraph – Agent workflow orchestration

LangChain – LLM integration & structured agent design

OpenAI GPT (optional, configurable via environment variables)

DevOps & Deployment

Docker

Docker Compose

Render (Frontend + Backend + PostgreSQL)

GitHub Actions (CI pipeline)

📸 Screenshots
1. Login Page

2. Registration Page

3. Dashboard - Tree Visualization

4. Tree Visualization (React Flow)

5. Manual Controls

6. AI Chat Interface

🚀 Quick Start
Option 1: Using Docker (Recommended)
git clone https://github.com/BHAGYAMUNI/agentic-tree.git
cd agentic-tree
docker-compose up --build

Access:

Frontend: http://localhost:5174

Backend: http://localhost:8000

Docs: http://localhost:8000/docs

Option 2: Local Development
Prerequisites

Python 3.11+

Node.js 18+

PostgreSQL 16+

Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m alembic upgrade head
uvicorn main:app --reload
Frontend
cd frontend
npm install
npm run dev
📖 API Endpoints
Endpoint	Method	Description
/auth/register	POST	Register user
/auth/login	POST	Login user
/trees	GET/POST	List or create trees
/trees/{id}	GET	Fetch tree details
/trees/{id}/insert	POST	Insert node manually
/trees/{id}/delete	POST	Delete node manually
/trees/{id}/search	POST	Search node manually
/trees/{id}/reset	POST	Reset tree
/chat	POST	Interact with AI agent
/health	GET	Health check endpoint
/agent-status	GET	Verify LangGraph agent activation
🤖 LangGraph + LangChain Agent Architecture

The backend implements a structured agent workflow using LangGraph.

Flow Overview
User Message
    ↓
LangGraph Workflow
    ├─ Intent Classification (Request Router)
    ├─ Parameter Extraction
    ├─ Validation
    ├─ Tree Operation Execution
    └─ Response Generation
Key Design Decisions

Clear separation between conversational and structured operations

Typed state management using LangGraph

Modular request router for intent classification

Deterministic tree logic separated from LLM reasoning

Optional LLM usage controlled via environment variable

This ensures:

Deterministic tree manipulation

Clean architecture

Scalable agent workflow

Interview-ready system design

🧪 Testing
Backend
cd backend
pytest -q

Includes:

Tree algorithm unit tests

API endpoint tests

LangGraph agent tests

Database integrity validation

Edge case coverage

Frontend
cd frontend
npm test
📦 Deployment Architecture
Frontend (Render Static Site)
        ↓
Backend API (Render Web Service - Docker)
        ↓
PostgreSQL (Render Managed Database)
Deployment Checklist

✅ Dockerized backend

✅ Dockerized frontend

✅ PostgreSQL cloud database

✅ Environment variables configured

✅ CORS configured

✅ CI pipeline configured

✅ Swagger docs available

✅ Health endpoint active

🔐 Security

Passwords hashed using bcrypt

JWT access tokens

Protected routes

CORS restricted to frontend domain

No plaintext password storage

📁 Project Structure
agentic-tree/
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── tree_utils.py
│   ├── langgraph_agent.py
│   ├── request_router.py
│   ├── database.py
│   ├── auth.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── components/
│   ├── redux/
│   ├── services/
│   └── package.json
├── docker-compose.yml
└── README.md
🎬 Demo Video

Watch full demo:
https://youtu.be/toXxtCOx6qc

🙏 Acknowledgments

React Flow

FastAPI

SQLAlchemy

LangChain

LangGraph

Render

Built for exploring Binary Tree data structures with modern AI-driven interaction.
