# LangGraph Chat Command Types - Complete Overview

## 📌 Architecture: LangGraph Exclusive

**All chat messages are now routed exclusively through LangGraph + LangChain.**
---

## 🎯 Command Categories & Examples

### 1. **INSERT Operations** (Tree Modifications)

Insert nodes into the tree at specified positions.

| Pattern | Example | Auto-Insert Behavior |
|---------|---------|-------------------|
| Root insertion | "insert 10 as root" | Creates first node |
| Left child | "insert 5 as left child of 10" | Explicit direction |
| Right child | "insert 9 as right child of 10" | Explicit direction |
| Ambiguous (auto-slot) | "insert 5 under 10" | If 10 has 1 free slot → auto-select it |
| Ambiguous (clarify) | "insert 5 under 10" | If 10 has 0 or 2 free slots → ask "left or right?" |

**Flexible phrasing supported:**
- "insert 5 as left child of 10"
- "insert 5 to left of 10"
- "add 5 as left child of 10"
- "insert 5 left of 10"
- "insert 5 under 10" (auto-smart)

---

### 2. **DELETE Operations** (Tree Modifications)

Remove nodes from the tree with safe promotion.

| Command | Effect |
|---------|--------|
| "delete 5" | Remove node 5, promote single child (if exists) |
| "remove 5" | Same as delete |
| "delete 5 force" | Delete even if node has 2 children (removes subtree) |

**Rules:**
- Single child → promoted to parent's position
- Two children → requires "force" flag (entire subtree removed)
- Leaf node → simply removed

---

### 3. **UPDATE Operations** (Tree Modifications)

Change a node's value to a different number.

| Command | Effect |
|---------|--------|
| "update 5 to 8" | Change node 5's value to 8 |
# Supported LangGraph Commands (compact)

This file lists only the commands the agent currently supports — phrasing variations work but must express the same operation.

## Insert
- Insert root: `Insert 10 as root`
- Insert left child: `Insert 5 as left child of 10` or `Insert 5 to left of 10`
- Insert right child: `Insert 9 as right child of 10` or `Insert 9 to right of 10`
- Ambiguous parent (auto): `Insert 5 under 10` — agent will auto-select the single free slot or ask `left or right?`

## Delete
- `Delete 5` or `Remove 5` — deletes node (promotes single child)
- `Delete 5 force` — delete node and subtree even if two children

## Update
- `Update 5 to 8` or `Change 5 to 8`

## Search
- `Search 5`, `Find 5`, `Search for 5`

## Query (metrics)
- Height: `height` / `What is the height?`
- Count: `count nodes` / `How many nodes?`
- Leaves: `show leaves` / `leaf nodes`

## Traversals
- `inorder` / `show inorder`
- `preorder` / `show preorder`
- `postorder` / `show postorder`

## General (Q&A)
- The agent answers tree-related questions and can provide explanations (e.g., "How do you insert a node?", "What is a binary tree?").
- For broad chat-style answers enable an LLM: set `USE_LLM_AGENT=1` and provide `OPENAI_API_KEY`.

## Rejection cases (brief)
- Non-numeric values rejected (node values must be numbers)
- Duplicate values rejected
- Invalid directions (only `left` / `right`) rejected
- Operations on non-existent parents rejected

---
Note: This file intentionally lists only supported commands — examples or phrasing not listed here are unsupported and will be rejected.


| Traversal | Examples | Order |
