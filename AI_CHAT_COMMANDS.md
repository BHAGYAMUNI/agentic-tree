# AI Chat Commands - Complete Reference Guide

This document provides a comprehensive guide to all commands that can be used in the AI chat interface of the Agentic Tree application. It covers successful operations, rejection cases, flexible phrasing, and maps to test cases.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Successful Commands](#successful-commands)
3. [Rejection Cases](#rejection-cases)
4. [Flexible Phrasing](#flexible-phrasing)
5. [Error Messages](#error-messages)
6. [Test Case Mapping](#test-case-mapping)

---

## Overview

The AI chat system uses **LangGraph agents** to intelligently interpret natural language commands and perform tree operations. The system supports:

- **Tree Operations:** Insert, delete, search, update nodes
- **Tree Queries:** Count nodes, height, leaf nodes, traversals
- **Flexible Input:** Multiple ways to phrase the same command
- **Smart Validation:** Catches errors and asks for clarification
- **Fallback:** Returns helpful error messages when operations fail

---

## Successful Commands

All successful commands return **HTTP 200** with a response containing the result or confirmation message.

### 1. INSERT OPERATIONS

#### 1.1 Insert Root Node
**Description:** Create the first node in an empty tree.

**Valid Syntax (Examples):**
```
"insert 10 as root"
"add 10 as root"
"create root node with value 10"
"insert root 10"
```

**Expected Response:**
```
"Successfully created root node with value 10"
"Root node with value 10 has been inserted"
```

**Test Case:** `test_c01_chat_insert_root`

---

#### 1.2 Insert Left Child
**Description:** Add a node as the left child of an existing parent node.

**Valid Syntax (Examples):**
```
"insert 5 as left child of 10"
"insert 5 to left of 10"
"add 5 as left child of 10"
"insert 5 left child of 10"
```

**Expected Response:**
```
"Successfully inserted 5 as left child of 10"
"Node 5 has been inserted as left child of 10"
```

**Test Case:** `test_c02_chat_insert_left_child`

---

#### 1.3 Insert Right Child
**Description:** Add a node as the right child of an existing parent node.

**Valid Syntax (Examples):**
```
"insert 9 as right child of 10"
"insert 9 to right of 10"
"add 9 as right child of 10"
"insert 9 right child of 10"
```

**Expected Response:**
```
"Successfully inserted 9 as right child of 10"
"Node 9 has been inserted as right child of 10"
```

**Test Case:** `test_c03_chat_insert_right_child`

---

### 2. DELETE OPERATIONS

#### 2.1 Delete Leaf Node
**Description:** Remove a node that has no children.

**Valid Syntax (Examples):**
```
"delete 3"
"remove 3"
"delete node 3"
"remove node 3"
```

**Expected Response:**
```
"Successfully deleted node 3"
"Node 3 has been removed"
```

**Prerequisites:**
- Node must exist in the tree
- Node must be a leaf (no children)

---

### 3. SEARCH OPERATIONS

#### 3.1 Search for a Node
**Description:** Check if a value exists in the tree.

**Valid Syntax (Examples):**
```
"search 9"
"find 9"
"is 9 in the tree?"
"search for 9"
"does tree contain 9?"
```

**Expected Response (Found):**
```
"Node 9 found in the tree"
"Yes, 9 exists in the tree"
```

**Expected Response (Not Found):**
```
"Node 9 not found"
"No, 9 does not exist in the tree"
```

**Test Case:** `test_c04_chat_search_node`

---

### 4. UPDATE OPERATIONS

#### 4.1 Update Node Value
**Description:** Change the value of an existing node.

**Valid Syntax (Examples):**
```
"update 9 to 11"
"change 9 to 11"
"change value of 9 to 11"
"update node 9 to 11"
```

**Expected Response:**
```
"Successfully updated node from 9 to 11"
"Node value changed from 9 to 11"
```

**Test Case:** `test_c05_chat_update_node`

---

### 5. QUERY OPERATIONS

#### 5.1 Get Tree Height
**Description:** Calculate the height of the tree (maximum distance from root to leaf).

**Valid Syntax (Examples):**
```
"height"
"what is the height?"
"tree height"
"get height"
"height of tree"
```

**Expected Response:**
```
"The height of the tree is 2"
"Tree height: 2 (3 levels from root)"
```

**Test Case:** `test_c06_chat_height_query`

---

#### 5.2 Get Leaf Nodes
**Description:** List all leaf nodes (nodes with no children).

**Valid Syntax (Examples):**
```
"leaf nodes"
"list leaves"
"what are the leaf nodes?"
"get leaf nodes"
"leaves"
```

**Expected Response:**
```
"Leaf nodes: 5, 9"
"The leaves of the tree are: 5 and 9"
```

**Test Case:** `test_c07_chat_leaves_query`

---

#### 5.3 Count Nodes
**Description:** Get the total number of nodes in the tree.

**Valid Syntax (Examples):**
```
"count nodes"
"how many nodes?"
"node count"
"total nodes"
"how many nodes in tree"
```

**Expected Response:**
```
"Total nodes in tree: 3"
"The tree contains 3 nodes"
```

**Test Case:** `test_c08_chat_count_query`

---

#### 5.4 Tree Traversal
**Description:** Get nodes in a specific order (in-order, pre-order, post-order).

**Valid Syntax (Examples):**
```
"inorder traversal"
"inorder"
"in-order"
"preorder traversal"
"postorder traversal"
"level order"
```

**Expected Response:**
```
"In-order traversal: 5, 10, 9"
"Pre-order: 10, 5, 9"
"Post-order: 5, 9, 10"
```

**Test Case:** `test_c09_chat_traversal`

---

## Rejection Cases

All rejection cases return **HTTP 200** with explanatory messages. The tree is NOT modified. User is asked to clarify or provide missing information.

### R1. Missing Direction in Insert

**Command Example:**
```
"insert 8 under 10"
"insert 8 into 10"
"add 8 to 10"
```

**Response:**
```
"Please specify the direction: should 8 be inserted as the left or right child of 10?"
"I need clarification - do you want to insert 8 as left or right child of 10?"
```

**Reason:** Insert command requires explicit left/right direction.

**Test Case:** `test_r01_missing_direction`

---

### R2. Invalid Direction

**Command Example:**
```
"insert 8 as middle child of 10"
"insert 8 as top child of 10"
"insert 8 as center child of 10"
```

**Response:**
```
"Invalid direction 'middle'. Please use 'left' or 'right'."
"Direction must be either 'left' or 'right', not 'middle'."
```

**Reason:** Only left and right children are valid in a binary tree.

**Test Case:** `test_r02_invalid_direction`

---

### R3. Duplicate Value Rejection

**Command Example:**
```
"insert 5 as right child of 10"
```
*where 5 already exists in the tree*

**Response:**
```
"Cannot insert: value 5 already exists in the tree"
"Error: 5 is already in the tree"
```

**Reason:** No duplicate values allowed in the tree.

**Test Case:** `test_r03_duplicate_insert_rejection`

---

### R4. Parent Node Not Found

**Command Example:**
```
"insert 8 as left child of 999"
```
*where 999 doesn't exist*

**Response:**
```
"Cannot find parent node 999 in the tree"
"Parent node 999 does not exist"
```

**Reason:** Cannot insert child without existing parent.

**Test Case:** `test_r04_insert_under_missing_parent`

---

### R5. Delete Node with Two Children (No Force)

**Command Example:**
```
"delete 10"
```
*where node 10 has both left and right children*

**Response:**
```
"Cannot delete node 10: it has two children. Use 'force delete' if you want to remove it anyway."
"This node has two children - please use 'force delete' to remove it."
```

**Reason:** Safety mechanism - unclear which child should replace the deleted node.

**Test Case:** `test_r05_delete_two_children_no_force`

---

### R6. Non-Numeric Value

**Command Example:**
```
"insert hello as left child of 10"
"insert abc to left of 10"
"add xyz as root"
```

**Response:**
```
"Values must be numeric. 'hello' is not a valid number."
"Please provide a numeric value, 'xyz' cannot be used."
```

**Reason:** Tree only stores numeric values.

**Test Case:** `test_r06_non_numeric_value`

---

### R7. Random Conversation

**Command Example:**
```
"how are you?"
"what's the weather like?"
"tell me a joke"
"what time is it?"
```

**Response:**
```
"I can help you with tree operations. Try asking: insert, delete, search, update, or query operations."
"I'm here to help with tree operations. Would you like to insert, delete, or search for nodes?"
```

**Behavior:** Tree remains unchanged. User is guided back to valid commands.

**Test Case:** `test_r07_random_conversation`

---

### R8. Malformed Command

**Command Example:**
```
"add something somewhere"
"do something with nodes"
"apply operation"
```

**Response:**
```
"I didn't understand that command. Please specify: what operation (insert/delete/search), what value, and any required details."
"Could you clarify? Try: insert [value] as [direction] child of [parent], or other tree operations."
```

**Behavior:** Tree remains unchanged. System asks for clarification.

**Test Case:** `test_r08_malformed_command`

---

## Flexible Phrasing

The system understands multiple ways to express the same command:

### Insert Command Variations

```
# Standard
"insert 5 as left child of 10"

# Alternative 1: "to left/right of"
"insert 5 to left of 10"
"insert 5 to right of 10"

# Alternative 2: Shortened
"insert 5 left of 10"
"insert 5 right of 10"

# Alternative 3: Using "add"
"add 5 as left child of 10"
"add 5 to left of 10"

# Alternative 4: Root insertion
"insert 10 as root"
"create root 10"
"set root to 10"

# All map to the same operation
```

### Delete Command Variations

```
"delete 3"
"remove 3"
"delete node 3"
"remove node 3"
"delete value 3"
```

### Search Command Variations

```
"search 9"
"find 9"
"find node 9"
"is 9 in tree?"
"does tree contain 9?"
"search for 9"
"look for 9"
```

### Query Command Variations

```
# Height queries
"height"
"what is the height?"
"tree height"
"calculate height"
"get height"

# Traversal queries
"inorder"
"in-order"
"inorder traversal"
"traverse inorder"
"show inorder"
```

---

## Error Messages

### HTTP 400 Errors

These are returned when the REST API (manual controls) receive invalid input. The AI chat layer (HTTP 200) handles these more gracefully with clarifying messages.

#### Message Too Long
```
Status: 400
Detail: "Message exceeds maximum length of 1000 characters"
```
**Test Case:** `test_e02_message_too_long`

#### Invalid Node Value
```
Status: 400
Detail: "Value must be a number, got: {value}"
```

#### Direction Invalid
```
Status: 400
Detail: "Direction must be 'left' or 'right', got: {direction}"
```

#### Occupied Slot
```
Status: 400
Detail: "Left child slot is already occupied"
"Right child slot is already occupied"
```

#### Parent Not Found
```
Status: 400
Detail: "Parent node with value {value} not found"
```

#### Duplicate Value
```
Status: 400
Detail: "Value {value} already exists in the tree"
```

### HTTP 404 Errors

#### Node Not Found (Delete)
```
Status: 404
Detail: "Node with value {value} not found"
```

---

## Test Case Mapping

### All Successful Chat Operations

| Test Case | Command Example | Operation Type |
|-----------|-----------------|-----------------|
| `test_c01_chat_insert_root` | "insert 10 as root" | Insert root |
| `test_c02_chat_insert_left_child` | "insert 5 as left child of 10" | Insert left |
| `test_c03_chat_insert_right_child` | "insert 9 as right child of 10" | Insert right |
| `test_c04_chat_search_node` | "search 9" | Search |
| `test_c05_chat_update_node` | "update 9 to 11" | Update |
| `test_c06_chat_height_query` | "height" | Query height |
| `test_c07_chat_leaves_query` | "leaf nodes" | Query leaves |
| `test_c08_chat_count_query` | "count nodes" | Query count |
| `test_c09_chat_traversal` | "inorder traversal" | Query traversal |

### All Rejection Cases

| Test Case | Command Example | Rejection Reason |
|-----------|-----------------|-----------------|
| `test_r01_missing_direction` | "insert 8 under 10" | Missing left/right direction |
| `test_r02_invalid_direction` | "insert 8 as middle child of 10" | Invalid direction |
| `test_r03_duplicate_insert_rejection` | "insert 5 as right child of 10" | Duplicate value exists |
| `test_r04_insert_under_missing_parent` | "insert 8 as left child of 999" | Parent doesn't exist |
| `test_r05_delete_two_children_no_force` | "delete 10" | Two children present |
| `test_r06_non_numeric_value` | "insert hello as left child of 10" | Non-numeric value |
| `test_r07_random_conversation` | "how are you?" | Not a tree operation |
| `test_r08_malformed_command` | "add something somewhere" | Unclear/malformed |

### Edge Cases & Stress Tests

| Test Case | Description |
|-----------|-------------|
| `test_e01_deep_chain_and_height` | Build deep tree (chain of 5 nodes) and verify height |
| `test_e02_message_too_long` | Reject message longer than 1000 characters |
| `test_e03_flexible_insert_phrasing` | Accept "to left of" / "to right of" syntax |

---

## Implementation Architecture

### Chat Processing Pipeline

```
User Message
    ↓
Message Length Validation (max 1000 chars)
    ↓
LangGraph Agent Intent Classification
    ↓
├─→ Tree Operation (insert/delete/search/update)
│   ├─→ Parameter Extraction
│   ├─→ Validation (direction, values, parent, etc.)
│   ├─→ Execute Operation
│   └─→ Return Result/Error
│
├─→ Query Operation (height/count/leaves/traversal)
│   ├─→ Parameter Extraction
│   ├─→ Execute Query
│   └─→ Return Result
│
└─→ Non-Operation Message
    └─→ Return Guidance Message
```

### Preprocessor Optimization

For simple queries (height, count, leaves, traversals), a preprocessor intercepts the message and returns results immediately without invoking the LLM, improving performance.

> **New behaviour (2026-03-01):** the insert logic has been made smarter. When
> you request something like "Insert 5 under 3" and node `3` has exactly one
> available child slot, the agent will automatically put the new value into
> that free slot instead of asking you to clarify left/right.  This change
> eliminates a common friction point while still prompting for a direction if
> both slots are empty.

Additionally, you can opt out of the preprocessor entirely with an
environment variable.  Set `FORCE_LLM_AGENT=1` on the backend and every chat
message – even trivial ones such as "height" – will be sent through the
LangGraph/LLM workflow.  This is mainly useful for testing or debugging the
agent behaviour.

---

## Quick Reference Table

| Operation | Command Template | Status |
|-----------|------------------|--------|
| Insert Root | "insert {value} as root" | ✅ Success |
| Insert Left | "insert {value} as left child of {parent}" | ✅ Success |
| Insert Right | "insert {value} as right child of {parent}" | ✅ Success |
| Delete Node | "delete {value}" | ✅ Success |
| Search Node | "search {value}" / "find {value}" | ✅ Success |
| Update Node | "update {old} to {new}" | ✅ Success |
| Height Query | "height" / "tree height" | ✅ Success |
| Leaf Query | "leaf nodes" / "leaves" | ✅ Success |
| Count Query | "count nodes" | ✅ Success |
| Traversal | "inorder" / "preorder" / "postorder" | ✅ Success |
| Missing Direction | "insert {value} under {parent}" | ❌ Rejection |
| Invalid Direction | "insert {value} as middle child" | ❌ Rejection |
| Duplicate Insert | "insert {existing_value}" | ❌ Rejection |
| Missing Parent | "insert {value} under {nonexistent}" | ❌ Rejection |
| Non-Numeric | "insert {string} as root" | ❌ Rejection |
| Random Chat | "how are you?" | ❌ Rejection |

---

## Best Practices for Users

1. **Be Specific:** Include direction (left/right) for insert operations
2. **Use Numeric Values:** All node values must be numbers
3. **Reference Existing Nodes:** When inserting children, parent must exist
4. **Try Alternative Phrasing:** System understands multiple ways to say the same thing
5. **Check Constraints:** No duplicate values, no special characters
6. **Use Clarifications:** If rejected, system suggests what's needed

---

## Running the Test Suite

Verify all commands work as expected:

```bash
cd backend
pip install -r requirements.txt

# Run all comprehensive tests
python -m pytest tests/test_comprehensive_verification.py -v

# Run only successful chat tests
python -m pytest tests/test_comprehensive_verification.py::TestAIChatValidCases -v

# Run only rejection tests
python -m pytest tests/test_comprehensive_verification.py::TestAIChatRejectionCases -v

# Run specific test
python -m pytest tests/test_comprehensive_verification.py::TestAIChatValidCases::test_c01_chat_insert_root -v
```

---

## Questions & Support

For issues or questions about specific commands:
1. Check the **Test Case Mapping** section
2. Review **Flexible Phrasing** examples
3. Verify input follows **Quick Reference Table**
4. Ensure values are numeric and unique
5. Check that parent nodes exist before referencing them

