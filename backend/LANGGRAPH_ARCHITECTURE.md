# LangGraph Agent Architecture - Complete Implementation

## Overview

The Agentic Tree application now uses a **LangGraph-based agent architecture** with a sophisticated **Request Router/Intent Classifier** that intelligently routes user requests to appropriate handlers.

### Architecture Diagram

```
User Message
    ↓
[REQUEST ROUTER - Intent Classification]
    ↓
    ├─→ TREE_ACTION (Insert/Delete/Update)
    │   └─→ Validate operation
    │   └─→ Execute with edge case handling
    │   └─→ Return modified tree + response
    │
    ├─→ TREE_QUERY (Search/Traversal/Height)
    │   └─→ Execute read-only operation
    │   └─→ Return response
    │
    └─→ CONVERSATION (General questions)
        └─→ Use LLM if available
        └─→ Fallback to knowledge base
        └─→ Return contextual response
    ↓
[Response to User]
```

---

## Component Details

### 1. **RequestRouter** (`request_router.py`)

**Purpose:** Classify user intent and extract structured parameters.

**Key Classes:**
- `IntentType`: Enum of 7 intent types
  - `INSERT`, `DELETE`, `UPDATE`, `SEARCH`
  - `TRAVERSAL`, `QUERY`, `GENERAL`
  - `INVALID`

**Capabilities:**
```python
router = RequestRouter()
intent_type, params = router.classify_intent("Insert 8 as left child of 4")
# Returns: (IntentType.INSERT, {"new_value": 8, "parent_value": 4, "position": "left"})
```

**Pattern Matching:**
- Multiple regex patterns for each intent
- Case-insensitive matching
- Parameter extraction

**Edge Cases Handled:**
- Malformed input
- Missing parameters
- Ambiguous commands (defaults to general conversation)

---

### 2. **LangGraph Agent** (`langgraph_agent.py`)

**Purpose:** Orchestrate tree operations and conversations using LangGraph workflow.

**Architecture:**

```
Entry Point: classifier
    ↓
    ├─→ [tree_action] → [finalizer] → EXIT
    └─→ [conversation] → [finalizer] → EXIT
```

**State Management:**
```python
class AgentState(TypedDict):
    tree: Optional[dict]           # Current tree
    user_message: str              # Original input
    intent_type: IntentType        # Classified intent
    intent_params: dict            # Extracted params
    response: str                  # Agent response
    tree_modified: bool            # Was tree changed?
    error: Optional[str]           # Error if any
```

**Node Functions:**

#### a) `_classify_intent` Node
- Calls RequestRouter
- Extracts intent and parameters
- Sets initial state

#### b) `_handle_tree_action` Node
Handles: INSERT, DELETE, UPDATE

**Edge Case Handling:**
```
INSERT Operation:
├─ Check if tree is empty
├─ Create root if needed
├─ Validate parent exists
├─ Check if position (left/right) is already occupied
│  └─ Return error if occupied
├─ Insert node
└─ Return success with modified flag

DELETE Operation:
├─ Validate node exists
├─ Delete node and subtree
└─ Return success

UPDATE Operation:
├─ Validate old_value exists
├─ Update node value
└─ Return success
```

#### c) `_handle_conversation` Node
Handles: SEARCH, TRAVERSAL, QUERY, GENERAL

**Features:**
- Read-only tree operations
- LLM-powered general conversation (if enabled)
- Fallback responses when LLM unavailable
- Tree context awareness

#### d) `_finalize_response` Node
- Ensures response is set
- Validates state

**Conditional Routing:**
```python
def route_after_classification(state) -> str:
    if is_tree_action(intent_type):
        return "tree_action"
    else:
        return "conversation"
```

---

## Tree Utilities Edge Cases

### Fixed in `tree_utils.py`

**Problem:** Original code didn't validate occupied positions

**Solution:** Added validation checks

```python
def insert_node(node, parent_value, new_value, position):
    # Find parent
    if node.get("value") == parent_value:
        if position == "left":
            if node["left"] is not None:
                return False  # ✓ Position occupied check
            node["left"] = {"value": new_value, "left": None, "right": None}
            return True
        # ... similar for right
    
    # Recursive search - check BOTH subtrees
    left_result = insert_node(node.get("left"), ...)
    if left_result:
        return True
    right_result = insert_node(node.get("right"), ...)
    return right_result
```

**Edge Cases Handled:**
1. ✓ Duplicate values allowed
2. ✓ Occupied position rejection
3. ✓ Parent not found
4. ✓ Empty tree root creation
5. ✓ Proper recursive search

---

## Intent Classification Examples

### Example 1: Insert Operation
```
User: "Insert 8 as left child of 4"
Router: IntentType.INSERT, {"new_value": 8, "parent_value": 4, "position": "left"}
Flow: INSERT → tree_action node → execute insert with validations
```

### Example 2: Duplicate Insert Attempt
```
User: "Insert 5 as left child of 5" (when 5 already has left child)
Router: IntentType.INSERT, {...}
Flow: tree_action node → check position occupied → return error
Response: "The left child of 5 already exists..."
```

### Example 3: Traversal Query
```
User: "Show me inorder traversal"
Router: IntentType.TRAVERSAL, {"traversal_type": "inorder"}
Flow: conversation node → execute inorder_traversal → return results
Response: "Inorder traversal: [1, 3, 5, 7, ...]"
```

### Example 4: General Conversation
```
User: "Tell me about binary trees"
Router: IntentType.GENERAL, {"query": "Tell me about binary trees"}
Flow: conversation node → call LLM with tree context → return response
Response: "Binary trees are data structures where each node has at most two children..."
```

---

## Chat Context Handling

### Problem Fixed
Previously: Chat didn't maintain tree context properly

### Solution
1. **Explicit Tree Passing:** Tree passed through entire agent flow
2. **State Preservation:** AgentState maintains tree throughout
3. **Context Addition:** Tree info added to LLM prompts

```python
def _handle_general_conversation(self, state, tree, params):
    tree_info = self._get_tree_info(tree)
    
    system_prompt = f"""You are a helpful assistant discussing binary trees.
The current tree structure is:
{tree_info}

Provide concise responses about trees."""
    
    response = self.llm.invoke([SystemMessage(...), HumanMessage(...)])
```

---

## Integration with Backend

### Main.py Changes
```python
# OLD
from ai_agent import handle_message as ai_handle_message

# NEW
from langgraph_agent import handle_message as ai_handle_message
```

### Chat Endpoint (`/chat`)
No changes needed - same interface:
```python
@app.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db), ...):
    response_text, modified, new_tree = ai_handle_message(
        tree.tree_data,     # ← Tree context passed
        request.message     # ← User message
    )
    
    if modified:
        tree.tree_data = new_tree
        db.commit()
```

---

## Testing Edge Cases

### Test Suite: `test_langgraph_agent.py`

**Coverage:**
1. Intent classification (7+ intents)
2. Tree operations (insert, delete, update)
3. Edge cases (occupied positions, duplicates, missing parents)
4. Context handling (tree preservation across operations)
5. Error conditions (malformed commands, missing parents)
6. Chain operations (multiple inserts then query)

**Key Tests:**
```python
def test_insert_into_occupied_left_position():
    tree = {"value": 5, "left": {"value": 3, ...}, "right": None}
    result = insert_node(tree, 5, 2, "left")
    assert result is False  # ✓ Should reject

def test_insert_with_duplicate_value():
    tree = {"value": 5, "left": {"value": 3, ...}, "right": None}
    result = insert_node(tree, 5, 5, "right")
    assert result is True  # ✓ Allow duplicates in different positions

def test_error_on_duplicate_insert():
    agent = TreeAgent()
    response, modified, _ = agent.process_message(
        tree, 
        "Insert 2 as left child of 5"  # Already occupied
    )
    assert modified is False
    assert "already exists" in response
```

---

## Running the Application

### Installation
```bash
pip install -r requirements.txt
# Now includes: langgraph, langchain, langchain-openai
```

### Environment Variables
```bash
# Optional: Enable LLM for general conversation
export USE_LLM_AGENT=1
export OPENAI_API_KEY="sk-..."
```

### Running Tests
```bash
# Test intent classification
pytest tests/test_langgraph_agent.py::TestRequestRouter -v

# Test tree operations
pytest tests/test_langgraph_agent.py::TestTreeOperations -v

# Test all edge cases
pytest tests/test_langgraph_agent.py::TestAllEdgeCases -v

# Full test suite
pytest tests/test_langgraph_agent.py -v
```

### Running Server
```bash
uvicorn venv.main:app --reload
```

---

## Request Router / Intent Classifier Flow

### Detailed Classification Process

```
Input: "Insert 8 as left child of 4"
    ↓
[RequestRouter.classify_intent]
    ↓
1. Convert to lowercase: "insert 8 as left child of 4"
    ↓
2. Try INSERT patterns:
   Pattern: r'insert\s+(\d+)\s+as\s+(left|right)\s+child\s+of\s+(\d+)'
   Match: YES
    ↓
3. Extract parameters:
   - new_value: 8
   - position: "left"
   - parent_value: 4
    ↓
Return: (IntentType.INSERT, {
    "new_value": 8,
    "position": "left",
    "parent_value": 4,
    "original_message": "Insert 8 as left child of 4"
})
    ↓
[Router Decision]
    ↓
is_tree_action(INSERT) = True
    ↓
Route to: tree_action node (modification)
```

---

## Advantages of LangGraph Architecture

1. **Clear Separation of Concerns**
   - Router: Intent classification
   - Nodes: Specific operations
   - Graph: Workflow orchestration

2. **Easy to Extend**
   - Add new intents: Just add pattern to router
   - Add new operations: Create new node
   - Change flow: Modify graph edges

3. **Better Error Handling**
   - Each node handles its own errors
   - Graceful fallbacks
   - Meaningful error messages

4. **Context Awareness**
   - Tree state passed through entire flow
   - LLM receives tree context
   - Consistent conversation history

5. **Type Safety**
   - AgentState TypedDict defines structure
   - Mypy type checking possible
   - IDE autocomplete support

---

## Deployment Checklist

- ✅ Tree operations handle all edge cases
- ✅ Chat maintains context properly
- ✅ LangGraph + LangChain integrated
- ✅ Request Router classifies intents
- ✅ Modular folder structure
- ✅ Comprehensive test coverage
- ✅ Error handling and fallbacks
- ✅ Documentation complete

---

## Files Modified/Created

**New Files:**
- `request_router.py` - Intent classification
- `langgraph_agent.py` - LangGraph-based agent
- `tests/test_langgraph_agent.py` - Comprehensive tests

**Modified Files:**
- `tree_utils.py` - Fixed edge case handling
- `main.py` - Updated import to use langgraph_agent
- `requirements.txt` - Added langgraph, langchain-openai

**Documentation:**
- `LANGGRAPH_ARCHITECTURE.md` - This file
