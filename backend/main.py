import os
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base, User, TreeSession, ChatMessage
from schemas import (
    UserCreate,
    UserLogin,
    TreeCreate,
    TreeResponse,
    TreeInsertRequest,
    TreeValueRequest,
    TreeUpdateNodeRequest,
    TreeSearchResponse,
    ChatRequest,
    ChatResponse,
)
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    get_current_user,
)
from fastapi.security import OAuth2PasswordRequestForm
from tree_utils import (
    calculate_height,
    find_leaf_nodes,
    insert_node,
    delete_node,
    update_node,
    inorder_traversal,
    preorder_traversal,
    postorder_traversal,
)
from ai_agent import handle_message as ai_handle_message
from sqlalchemy.orm.attributes import flag_modified
from fastapi.middleware.cors import CORSMiddleware
import re
import time
import logging
from fastapi import Request

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app instance early so middleware decorators can reference it
app = FastAPI()

# Simple in-memory rate limiter: {ip: [timestamps]}
RATE_LIMIT = int(__import__('os').environ.get('RATE_LIMIT', '60'))  # requests
RATE_WINDOW = int(__import__('os').environ.get('RATE_WINDOW_SECONDS', '60'))  # seconds
_rate_store: dict = {}


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    try:
        client_ip = request.client.host
    except Exception:
        client_ip = 'unknown'

    now = time.time()
    entry = _rate_store.get(client_ip, [])
    # keep only timestamps inside window
    entry = [ts for ts in entry if now - ts < RATE_WINDOW]
    if len(entry) >= RATE_LIMIT:
        logger.warning(f"Rate limit exceeded for {client_ip}")
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})

    entry.append(now)
    _rate_store[client_ip] = entry

    response = await call_next(request)
    return response


# Prometheus metrics endpoint and basic instrumentation
try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

    REQUEST_COUNT = Counter('app_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'http_status'])
    REQUEST_LATENCY = Histogram('app_request_latency_seconds', 'Request latency', ['endpoint'])

    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        resp_time = time.time() - start
        endpoint = request.url.path
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(resp_time)
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, http_status=str(response.status_code)).inc()
        return response

    @app.get('/metrics')
    def metrics():
        return generate_latest()
except Exception:
    logger.info('prometheus_client not installed; metrics endpoint disabled')

# app already created above; configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "https://agentic-tree-2.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handler for validation errors
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return {"detail": exc.errors()}

# Create tables in database

if os.environ.get("RUNNING_TESTS") != "1":
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Backend is working 🚀"}


@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Registration attempt: {user.email}")
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        logger.warning(f"Registration failed: Email already registered - {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password before storing
    hashed_pw = hash_password(user.password)

    # Create new user
    new_user = User(email=user.email, hashed_password=hashed_pw)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Issue token immediately so frontend can log user in
    access_token = create_access_token(data={"sub": new_user.email})
    refresh_token = create_refresh_token(data={"sub": new_user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "email": new_user.email,
        "user_id": new_user.id,
    }


@app.post("/auth/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Simple JSON-based login to match frontend (email + password).
    """
    try:
        logger.info(f"Login attempt: {user_data.email}")
        user = db.query(User).filter(User.email == user_data.email).first()

        if not user:
            logger.warning(f"Login failed: User not found - {user_data.email}")
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        if not verify_password(user_data.password, user.hashed_password):
            logger.warning(f"Login failed: Invalid password - {user_data.email}")
            raise HTTPException(status_code=400, detail="Invalid credentials")

        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})
        
        logger.info(f"Login successful: {user_data.email}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "email": user.email,
            "user_id": user.id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=400, detail="Login failed")


@app.post("/login")
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@app.post("/auth/refresh")
def refresh_token_endpoint(payload: dict):
    token = payload.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="refresh_token required")

    email = verify_refresh_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_access_token(data={"sub": email})
    refresh_token = create_refresh_token(data={"sub": email})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@app.get("/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email,
        "id": current_user.id,
        "message": "You are authenticated 🎉",
    }

@app.post("/trees", response_model=TreeResponse)
def create_tree(tree: TreeCreate, 
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    new_tree = TreeSession(
        name=tree.name,
        tree_data=tree.tree_data,
        user_id=current_user.id
    )

    db.add(new_tree)
    db.commit()
    db.refresh(new_tree)

    return new_tree

@app.get("/trees", response_model=list[TreeResponse])
def get_trees(db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):

    trees = db.query(TreeSession).filter(
        TreeSession.user_id == current_user.id
    ).all()

    return trees

@app.get("/trees/{tree_id}", response_model=TreeResponse)
def get_tree(tree_id: int,
             db: Session = Depends(get_db),
             current_user: User = Depends(get_current_user)):

    tree = db.query(TreeSession).filter(
        TreeSession.id == tree_id,
        TreeSession.user_id == current_user.id
    ).first()

    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    return tree

@app.delete("/trees/{tree_id}")
def delete_tree(tree_id: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):

    tree = db.query(TreeSession).filter(
        TreeSession.id == tree_id,
        TreeSession.user_id == current_user.id
    ).first()

    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    db.delete(tree)
    db.commit()

    return {"message": "Tree deleted successfully"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest,
         db: Session = Depends(get_db),
         current_user: User = Depends(get_current_user)):

    tree = db.query(TreeSession).filter(
        TreeSession.id == request.tree_id,
        TreeSession.user_id == current_user.id
    ).first()

    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    user_message = (request.message or "").strip()
    if len(user_message) > 1000:
        raise HTTPException(status_code=400, detail="Message too long")

    # Delegate to AI agent scaffold which returns (response_text, modified, new_tree)
    response_text, modified, new_tree = ai_handle_message(tree.tree_data, request.message)

    # If agent modified the tree, persist changes (new_tree may be updated)
    if modified:
        tree.tree_data = new_tree
        flag_modified(tree, "tree_data")
        db.commit()
        db.refresh(tree)

    chat_entry = ChatMessage(
        message=request.message,
        response=response_text,
        user_id=current_user.id,
        tree_id=request.tree_id
    )

    db.add(chat_entry)
    db.commit()

    return {"response": response_text}

@app.put("/trees/{tree_id}", response_model=TreeResponse)
def update_tree(tree_id: int,
                updated_tree: TreeCreate,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):

    tree = db.query(TreeSession).filter(
        TreeSession.id == tree_id,
        TreeSession.user_id == current_user.id
    ).first()

    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    tree.name = updated_tree.name
    tree.tree_data = updated_tree.tree_data

    flag_modified(tree, "tree_data")
    db.commit()
    db.refresh(tree)

    return tree

@app.get("/chat/history/{tree_id}")
def get_chat_history(tree_id: int,
                     db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):

    chats = db.query(ChatMessage).filter(
        ChatMessage.tree_id == tree_id,
        ChatMessage.user_id == current_user.id
    ).all()

    return chats


@app.delete("/chat/history/{tree_id}")
def clear_chat_history(tree_id: int,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):

    db.query(ChatMessage).filter(
        ChatMessage.tree_id == tree_id,
        ChatMessage.user_id == current_user.id
    ).delete()
    db.commit()

    return {"message": "Chat history cleared"}


@app.post("/trees/{tree_id}/insert", response_model=TreeResponse)
def insert_node_endpoint(
    tree_id: int,
    payload: TreeInsertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Insert a node into the tree under a given parent.
    If the tree is empty, create a new root node.
    """
    tree = db.query(TreeSession).filter(
        TreeSession.id == tree_id,
        TreeSession.user_id == current_user.id,
    ).first()

    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    if tree.tree_data is None:
        # if no tree yet, create root node using new_value
        tree.tree_data = {"value": payload.new_value, "left": None, "right": None}
        flag_modified(tree, "tree_data")
        db.commit()
        db.refresh(tree)
        return tree

    if payload.parent_value is None:
        raise HTTPException(status_code=400, detail="Parent value is required for non-empty tree")

    print(f"[INSERT] Before: parent={payload.parent_value}, new={payload.new_value}, dir={payload.direction}")
    print(f"[INSERT] Tree structure before: {tree.tree_data}")
    
    inserted = insert_node(tree.tree_data, payload.parent_value, payload.new_value, payload.direction)
    
    print(f"[INSERT] Tree structure after: {tree.tree_data}")
    print(f"[INSERT] Inserted: {inserted}")
    
    if not inserted:
        raise HTTPException(status_code=400, detail="Parent node not found")

    flag_modified(tree, "tree_data")
    db.commit()
    db.refresh(tree)

    return tree


@app.post("/trees/{tree_id}/delete", response_model=TreeResponse)
def delete_node_endpoint(
    tree_id: int,
    payload: TreeValueRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a node by value from the tree.
    """
    tree = db.query(TreeSession).filter(
        TreeSession.id == tree_id,
        TreeSession.user_id == current_user.id,
    ).first()

    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    tree.tree_data = delete_node(tree.tree_data, payload.value)
    flag_modified(tree, "tree_data")
    db.commit()
    db.refresh(tree)

    return tree


@app.post("/trees/{tree_id}/update", response_model=TreeResponse)
def update_node_endpoint(
    tree_id: int,
    payload: TreeUpdateNodeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a node's value in the tree.
    """
    tree = db.query(TreeSession).filter(
        TreeSession.id == tree_id,
        TreeSession.user_id == current_user.id,
    ).first()

    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    tree.tree_data = update_node(tree.tree_data, payload.node_id, payload.new_value)
    flag_modified(tree, "tree_data")
    db.commit()
    db.refresh(tree)

    return tree


@app.post("/trees/{tree_id}/reset")
def reset_tree_endpoint(
    tree_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Reset a tree to empty state.
    """
    tree = db.query(TreeSession).filter(
        TreeSession.id == tree_id,
        TreeSession.user_id == current_user.id,
    ).first()

    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    tree.tree_data = None
    flag_modified(tree, "tree_data")
    db.commit()

    return {"message": "Tree reset successfully"}


@app.post("/trees/{tree_id}/search", response_model=TreeSearchResponse)
def search_node_endpoint(
    tree_id: int,
    payload: TreeValueRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Simple search: checks if a node with the given value exists.
    For this assignment, we treat the node_id as the node's value.
    """
    tree = db.query(TreeSession).filter(
        TreeSession.id == tree_id,
        TreeSession.user_id == current_user.id,
    ).first()

    if not tree or not tree.tree_data:
        raise HTTPException(status_code=404, detail="Tree not found")

    target = payload.value

    def dfs(node):
        if not node:
            return False
        if node.get("value") == target:
            return True
        return dfs(node.get("left")) or dfs(node.get("right"))

    found = dfs(tree.tree_data)

    if not found:
        return TreeSearchResponse(found=False, node_id=None)

    # Frontend highlights nodes by id; we will use the value as id (stringified)
    return TreeSearchResponse(found=True, node_id=target)


@app.get("/trees/{tree_id}/traversal")
def get_traversal(tree_id: int,
                  type: str = Query("inorder", pattern="^(inorder|preorder|postorder)$"),
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    """
    Return traversal order for a tree for animation on frontend.
    """
    tree = db.query(TreeSession).filter(
        TreeSession.id == tree_id,
        TreeSession.user_id == current_user.id,
    ).first()

    if not tree or not tree.tree_data:
        raise HTTPException(status_code=404, detail="Tree not found")

    if type == "inorder":
        result = inorder_traversal(tree.tree_data)
    elif type == "preorder":
        result = preorder_traversal(tree.tree_data)
    else:
        result = postorder_traversal(tree.tree_data)

    return {"type": type, "order": result}