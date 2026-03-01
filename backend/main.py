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
    MAX_NODE_VALUE,
)
from langgraph_agent import handle_message as ai_handle_message
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


@app.get("/agent-status")
def agent_status():
    """Simple endpoint to verify that the LangGraph agent code is active.

    Returns a small JSON blob indicating the agent implementation being
    used; clients (or users) can hit this URL to make sure the latest
    refactor hasn't reverted back to the old OpenAI call.  The log output
    from the agent also emits a message on every invocation (see
    backend/langgraph_agent.py).
    """
    return {
        "agent": "langgraph",
        "llm_enabled": os.environ.get("USE_LLM_AGENT", "0") in ("1", "true", "True"),
    }

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


@app.get("/health")
def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "service": "agentic-tree-backend"}


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

    # fetch and lock the row to avoid concurrent-modification races
    tree = db.query(TreeSession).filter(
        TreeSession.id == request.tree_id,
        TreeSession.user_id == current_user.id
    ).with_for_update().first()

    if not tree:
        # user might not have selected/created a tree yet
        return {"response": "Please select or create a tree first."}

    user_message = (request.message or "").strip()
    if len(user_message) > 1000:
        raise HTTPException(status_code=400, detail="Message too long")

    # Handle follow-up replies consisting of a direction only.  When the
    # previous chat entry asked "Do you want to insert X as left or right
    # child of Y?" we can synthesise a complete insertion command so that the
    # rest of the pipeline behaves exactly as if the user had sent the full
    # sentence.  This keeps the agent stateless while still supporting a
    # simple conversational pattern.
    dir_match = re.match(r'^(left|right)(?:\s+of\s+(\d+))?$', user_message.lower())
    if dir_match:
        direction = dir_match.group(1)
        override_parent = dir_match.group(2)
        # fetch the last user message for this tree
        last = db.query(ChatMessage).filter(
            ChatMessage.tree_id == request.tree_id,
            ChatMessage.user_id == current_user.id,
        ).order_by(ChatMessage.id.desc()).first()
        if last and 'left or right' in (last.response or '').lower():
            # attempt to extract numbers from the previous message
            nums = re.findall(r"\d+", last.message or "")
            if len(nums) >= 2:
                new_val = nums[0]
                parent_val = override_parent or nums[1]
                user_message = f"insert {new_val} as {direction} child of {parent_val}"
                msg_lower = user_message.lower()
    
    # Determine whether we should bypass all of the "preprocessor" logic
    # and send the message straight to the LLM/agent.  This is useful for

    # Determine whether we should bypass all of the "preprocessor" logic
    # and send the message straight to the LLM/agent.  This is useful for
    # debugging or for environments where we want *every* turn to flow
    # through the LangGraph workflow (for example, to exercise some of the
    # more subtle routing logic).  By default the preprocessor performs a
    # handful of quick checks for count/height/leaves/traversals/reset
    # in order to avoid the overhead of the agent, but this behaviour can
    # be disabled by setting the FORCE_LLM_AGENT environment variable.

    force_llm = os.environ.get("FORCE_LLM_AGENT", "0") in ("1", "true", "True")

    # Quick local handling for simple queries to avoid LangGraph runtime issues
    # (count, height, leaves, traversals, simple search/update).  Skipped
    # entirely when force_llm is True.
    import copy
    from tree_utils import (
        calculate_height,
        find_leaf_nodes,
        count_nodes,
        inorder_traversal,
        preorder_traversal,
        postorder_traversal,
        search_node,
        update_node,
    )

    msg_lower = user_message.lower()

    response_text = ""
    modified = False

    if not force_llm:
        # RESET TREE
        if re.search(r"\b(reset|clear|delete all|wipe)\b.*\b(tree|nodes)\b", msg_lower):
            tree.tree_data = None
            flag_modified(tree, "tree_data")
            db.commit()
            db.refresh(tree)
            response_text = "✓ Tree reset successfully."
            modified = True

        # COUNT
        elif re.search(r"\b(how many nodes|number of nodes|count nodes|show count( of nodes)?)\b", msg_lower):
            n = count_nodes(tree.tree_data)
            response_text = f"✓ Node count: {n}."
            modified = False

        # HEIGHT
        elif re.search(r"\b(height|what is the height)\b", msg_lower):
            h = calculate_height(tree.tree_data)
            response_text = f"✓ Tree height: {h}."
            modified = False

        # LEAVES
        elif re.search(r"\b(leaf|leaves|show leaf|show leaves)\b", msg_lower):
            leaves = find_leaf_nodes(tree.tree_data)
            response_text = f"✓ Leaf nodes: {', '.join(map(str, leaves)) if leaves else 'None'}."
            modified = False

        # TRAVERSALS
        elif m := re.search(r"\b(inorder|preorder|postorder)\b", msg_lower):
            t = m.group(1)
            if t == "inorder":
                seq = inorder_traversal(tree.tree_data)
            elif t == "preorder":
                seq = preorder_traversal(tree.tree_data)
            else:
                seq = postorder_traversal(tree.tree_data)
            response_text = f"{t.capitalize()} traversal: {', '.join(map(str, seq)) if seq else ''}"
            modified = False

        # INSERT (basic pre-checks to provide clear guidance)
        elif re.match(r"^\s*insert\b", msg_lower):
            # special-case: user asking to create or insert the root explicitly
            if "root" in msg_lower:
                # extract first number in message, if any
                mroot = re.search(r"(\d+)", msg_lower)
                if mroot:
                    val = int(mroot.group(1))
                    if not tree.tree_data:
                        if abs(val) > MAX_NODE_VALUE:
                            response_text = f"✗ Value too large; maximum allowed is {MAX_NODE_VALUE}."
                            modified = False
                        else:
                            tree.tree_data = {"value": val, "left": None, "right": None}
                            flag_modified(tree, "tree_data")
                            db.commit()
                            db.refresh(tree)
                            response_text = f"✓ Created root with value {val}."
                            modified = True
                        # we handled the message; skip further insert logic below
                        # note: chat entry persistence occurs later
                        # explicitly return early to avoid double-persisting
                        chat_entry = ChatMessage(
                            message=request.message,
                            response=response_text,
                            user_id=current_user.id,
                            tree_id=request.tree_id,
                        )
                        db.add(chat_entry)
                        db.commit()
                        return {"response": response_text}
                    else:
                        response_text = "Root already exists."
                        modified = False
                        chat_entry = ChatMessage(
                            message=request.message,
                            response=response_text,
                            user_id=current_user.id,
                            tree_id=request.tree_id,
                        )
                        db.add(chat_entry)
                        db.commit()
                        return {"response": response_text}
                else:
                    # user mentioned root but no number; ask for clarification
                    response_text = "Please specify a numeric value when creating the root node."
                    modified = False
                    chat_entry = ChatMessage(
                        message=request.message,
                        response=response_text,
                        user_id=current_user.id,
                        tree_id=request.tree_id,
                    )
                    db.add(chat_entry)
                    db.commit()
                    return {"response": response_text}
            m = re.match(r"^\s*insert(?:\s+node)?\s+(\S+)", msg_lower)
            if not m:
                response_text = "Please specify the value to insert."
                modified = False
            else:
                token = m.group(1)
                try:
                    val = int(token)
                except Exception:
                    response_text = "✗ Only numbers can be inserted."
                    modified = False
                else:
                    if abs(val) > MAX_NODE_VALUE:
                        response_text = f"✗ Value too large; maximum allowed is {MAX_NODE_VALUE}."
                        modified = False
                    else:
                        # If tree empty, delegate to agent to create root
                        if not tree.tree_data:
                            tree_copy = copy.deepcopy(tree.tree_data)
                            response_text, modified, new_tree = ai_handle_message(tree_copy, request.message)
                            if modified:
                                tree.tree_data = new_tree
                                flag_modified(tree, "tree_data")
                                db.commit()
                                db.refresh(tree)
                        else:
                            # if the user hasn't even named a parent we can't do anything
                            # useful locally; otherwise send the message to the agent and
                            # let its improved insert logic handle missing direction and
                            # single-slot auto-insertion.
                            if not re.search(r"\b(of|child|parent|under)\b", msg_lower):
                                response_text = "Please specify the parent node for the new value."
                                modified = False
                            else:
                                tree_copy = copy.deepcopy(tree.tree_data)
                                response_text, modified, new_tree = ai_handle_message(tree_copy, request.message)
                                if modified:
                                    tree.tree_data = new_tree
                                    flag_modified(tree, "tree_data")
                                    db.commit()
                                    db.refresh(tree)
        # SIMPLE SEARCH (e.g., 'search 5', 'search node 5', 'find 5')
        elif m := re.search(r"(?:search|find)(?:\s+(?:node|for))?\s+(\d+)", msg_lower):
            token = m.group(1)
            try:
                val = int(token)
                found = search_node(tree.tree_data, val)
                response_text = f"✓ Found node {val}." if found else f"✗ Node {val} not found in tree."
            except Exception:
                response_text = "Search value must be a number."
            modified = False

        # SIMPLE UPDATE (e.g., 'update 3 to 4' or 'update node 3 to 4')
        elif m := re.match(r"^(?:update|change)\s+(?:node\s+)?(\S+)\s+to\s+(\S+)$", msg_lower):
            old_token = m.group(1)
            new_token = m.group(2)
            try:
                old_val = int(old_token)
                new_val = int(new_token)
            except Exception:
                response_text = "Node values must be numbers."
                modified = False
            else:
                if abs(new_val) > MAX_NODE_VALUE:
                    response_text = f"✗ Value too large; maximum allowed is {MAX_NODE_VALUE}."
                    modified = False
                else:
                    if not search_node(tree.tree_data, old_val):
                        response_text = f"✗ Node {old_val} not found in tree."
                        modified = False
                    elif search_node(tree.tree_data, new_val) and new_val != old_val:
                        response_text = f"✗ Node with value {new_val} already exists; cannot update to duplicate."
                        modified = False
                    else:
                        update_node(tree.tree_data, old_val, new_val)
                        flag_modified(tree, "tree_data")
                        db.commit()
                        db.refresh(tree)
                        response_text = f"✓ Updated node {old_val} to {new_val}."
                        modified = True

        else:
            # Fallback to AI agent for more complex commands
            tree_copy = copy.deepcopy(tree.tree_data)
            response_text, modified, new_tree = ai_handle_message(tree_copy, request.message)

            # normalize any LangGraph internal errors to a user-friendly message
            if isinstance(response_text, str) and response_text.startswith("Error processing request:"):
                if "Can receive only one value per step" in response_text:
                    logger.warning("LangGraph concurrent-update error for message: %s", request.message)
                    response_text = (
                        "Sorry, I couldn't understand that command. "
                        "Please make sure to use numbers, e.g. 'Insert 5 as left child of 3'."
                    )
                else:
                    logger.error("AI agent error: %s", response_text)
                    response_text = "Sorry, I encountered an internal error processing your request."

            # If agent modified the tree, persist changes (new_tree may be updated)
            if modified:
                tree.tree_data = new_tree
                flag_modified(tree, "tree_data")
                db.commit()
                db.refresh(tree)
    else:
        # force_llm path: send every message straight to the agent without
        # any preprocessing.  we perform the same error normalization and
        # persistence afterwards.
        tree_copy = copy.deepcopy(tree.tree_data)
        response_text, modified, new_tree = ai_handle_message(tree_copy, request.message)

        if isinstance(response_text, str) and response_text.startswith("Error processing request:"):
            if "Can receive only one value per step" in response_text:
                logger.warning("LangGraph concurrent-update error for message: %s", request.message)
                response_text = (
                    "Sorry, I couldn't understand that command. "
                    "Please make sure to use numbers, e.g. 'Insert 5 as left child of 3'."
                )
            else:
                logger.error("AI agent error: %s", response_text)
                response_text = "Sorry, I encountered an internal error processing your request."

        if modified:
            tree.tree_data = new_tree
            flag_modified(tree, "tree_data")
            db.commit()
            db.refresh(tree)
        # (force_llm branch already handled normalization above, nothing else needed)

    # Persist chat entry and return response
    chat_entry = ChatMessage(
        message=request.message,
        response=response_text,
        user_id=current_user.id,
        tree_id=request.tree_id,
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
@app.post("/trees/{tree_id}/insert", response_model=TreeResponse)
def insert_node_endpoint(
    tree_id: int,
    payload: TreeInsertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tree = db.query(TreeSession).filter(
        TreeSession.id == tree_id,
        TreeSession.user_id == current_user.id,
    ).with_for_update().first()

    # always log incoming payload so we can surface issues later
    logger.info(f"insert_node_endpoint called with tree_id={tree_id} payload={payload.dict()}")

    if not tree:
        logger.warning(f"insert_node_endpoint: tree {tree_id} not found for user {current_user.id}")
        raise HTTPException(status_code=404, detail="Tree not found")

    # handle empty tree: create new root
    if tree.tree_data is None:
        try:
            new_root_val = int(payload.new_value)
        except Exception:
            logger.warning(f"insert_node_endpoint invalid new_value '{payload.new_value}' for empty tree")
            raise HTTPException(status_code=400, detail="Node value must be a number")
        if abs(new_root_val) > MAX_NODE_VALUE:
            raise HTTPException(status_code=400, detail=f"Node value {new_root_val} is too large; max {MAX_NODE_VALUE}")

        tree.tree_data = {"value": new_root_val, "left": None, "right": None}
        flag_modified(tree, "tree_data")
        db.commit()
        db.refresh(tree)
        return tree

    # non-empty tree requires parent_value
    if payload.parent_value is None:
        logger.warning(
            f"insert_node_endpoint attempt to add root to non-empty tree {tree_id}"
        )
        raise HTTPException(
            status_code=400,
            detail="Root already exists. Cannot insert new root."
        )

    try:
        new_val = int(payload.new_value)
        parent_val = int(payload.parent_value)
    except Exception as e:
        logger.warning(f"insert_node_endpoint invalid numeric input: {e}")
        raise HTTPException(status_code=400, detail="Node value must be a number")

    if abs(new_val) > MAX_NODE_VALUE:
        raise HTTPException(status_code=400, detail=f"Node value {new_val} is too large; max {MAX_NODE_VALUE}")

    try:
        tree.tree_data = insert_node(
            tree.tree_data,
            parent_val,
            new_val,
            payload.direction,
        )
    except ValueError as e:
        logger.warning(f"insert_node_endpoint validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            "insert_node_endpoint unexpected error",
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail="Invalid input.")

    flag_modified(tree, "tree_data")
    db.commit()
    db.refresh(tree)

    return tree

@app.post("/trees/{tree_id}/delete", response_model=TreeResponse)

@app.post("/trees/{tree_id}/delete", response_model=TreeResponse)
def delete_node_endpoint(
    tree_id: int,
    payload: TreeValueRequest,
    force: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tree = db.query(TreeSession).filter(
        TreeSession.id == tree_id,
        TreeSession.user_id == current_user.id,
    ).with_for_update().first()

    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")

    from tree_utils import get_node

    node = get_node(tree.tree_data, payload.value)

    if node is None:
        raise HTTPException(status_code=404, detail=f"Node {payload.value} not found")

    # If two children and not forced
    if node.get("left") is not None and node.get("right") is not None and not force:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Node {payload.value} has two children. "
                "Call with ?force=true to delete entire subtree."
            ),
        )

    try:
        tree.tree_data = delete_node(tree.tree_data, payload.value)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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

    # Validate numeric input and existence
    try:
        old_val = int(payload.node_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Old node id must be a number")

    try:
        new_val = int(payload.new_value)
    except Exception:
        raise HTTPException(status_code=400, detail="New node value must be a number")

    if abs(new_val) > MAX_NODE_VALUE:
        raise HTTPException(status_code=400, detail=f"Node value {new_val} is too large; max {MAX_NODE_VALUE}")

    from tree_utils import search_node

    if not search_node(tree.tree_data, old_val):
        raise HTTPException(status_code=404, detail=f"Node {old_val} not found")

    if old_val != new_val and search_node(tree.tree_data, new_val):
        raise HTTPException(status_code=400, detail=f"Node with value {new_val} already exists")

    updated = update_node(tree.tree_data, old_val, new_val)
    if not updated:
        raise HTTPException(status_code=400, detail="Update failed")

    tree.tree_data = updated
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

    if not tree:
        raise HTTPException(status_code=404, detail="Tree not found")
    if not tree.tree_data:
        raise HTTPException(status_code=400, detail="Tree is empty")

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