"""
AI Agent scaffold

Provides a simple Supervisor interface that currently uses rule-based
handlers (existing logic) but is implemented as a module so it can be
replaced by a real LLM/agent (LangGraph / LangChain) later.

Functions:
- handle_message(tree, message) -> (response_text, tree_modified_flag)

"""
import re
from tree_utils import (
    calculate_height,
    find_leaf_nodes,
    insert_node,
    delete_node,
    update_node,
    inorder_traversal,
    preorder_traversal,
    postorder_traversal,
    search_node,
)
import os

USE_LLM = os.environ.get("USE_LLM_AGENT", "0") in ("1", "true", "True")

# Try to import adapter lazily when LLMS are enabled
_llm_adapter = None
if USE_LLM:
    try:
        from ai_agent_adapter import llm_handle_message as _llm_handle
        _llm_adapter = _llm_handle
    except Exception:
        _llm_adapter = None


def handle_message(tree, message):
    """Process the incoming chat message and return a response.

    Returns: (response_text, modified, new_tree)
    - response_text: string response to show the user
    - modified: boolean indicating whether the tree was modified
    - new_tree: the (possibly) updated tree structure to persist
    """
    if tree is None:
        return "No tree selected.", False, tree

    # If LLM adapter is enabled and available, delegate
    if USE_LLM and _llm_adapter:
        try:
            resp, modified, new_tree = _llm_adapter(tree, message)
            return resp, modified, new_tree
        except Exception:
            # If adapter fails, fall back to rule-based
            pass

    user_message = (message or "").lower()

    # Rule-based fallback (existing behavior)
    if tree is None:
        return "No tree selected.", False, tree

    # Basic supervisor logic (keeps current behavior)
    if "height" in user_message:
        height = calculate_height(tree)
        return f"The height of the tree is {height}.", False, tree
    elif "leaf" in user_message:
        leaves = find_leaf_nodes(tree)
        return f"Leaf nodes are: {leaves}", False, tree
    elif "insert" in user_message:
        numbers = list(map(int, re.findall(r"\d+", user_message)))

        if len(numbers) >= 2:
            new_value = numbers[0]
            parent_value = numbers[1]

            position = "left" if "left" in user_message else "right"

            inserted = insert_node(tree, parent_value, new_value, position)

            if inserted:
                return f"Inserted {new_value} as {position} child of {parent_value}.", True, tree
            else:
                return "Parent node not found.", False, tree
        else:
            return "Please provide the values to insert (e.g., 'Insert 8 as left child of 4').", False, tree
    elif "delete" in user_message:
        numbers = list(map(int, re.findall(r"\d+", user_message)))

        if numbers:
            value_to_delete = numbers[0]
            new_tree = delete_node(tree, value_to_delete)
            return f"Deleted node {value_to_delete}.", True, new_tree
        else:
            return "Please specify value to delete.", False, tree
    elif "update" in user_message or "change" in user_message or "edit" in user_message:
        numbers = list(map(int, re.findall(r"\d+", user_message)))

        if len(numbers) >= 2:
            old_value = numbers[0]
            new_value = numbers[1]
            updated_tree = update_node(tree, old_value, new_value)
            if updated_tree and updated_tree is not False:
                return f"Updated node {old_value} to {new_value}.", True, updated_tree
            else:
                return f"Node {old_value} not found.", False, tree
        else:
            return "Please provide both old and new values (e.g., 'update node 5 as 10' or 'change 5 to 10').", False, tree
    elif "search" in user_message or "find" in user_message:
        numbers = list(map(int, re.findall(r"\d+", user_message)))

        if numbers:
            value_to_search = numbers[0]
            found = search_node(tree, value_to_search)
            if found:
                return f"✓ Found node {value_to_search} in the tree.", False, tree
            else:
                return f"✗ Node {value_to_search} not found in the tree.", False, tree
        else:
            return "Please specify the value to search for (e.g., 'search for 5').", False, tree
    elif "inorder" in user_message:
        result = inorder_traversal(tree)
        return f"Inorder traversal: {result}", False, tree
    elif "preorder" in user_message:
        result = preorder_traversal(tree)
        return f"Preorder traversal: {result}", False, tree
    elif "postorder" in user_message:
        result = postorder_traversal(tree)
        return f"Postorder traversal: {result}", False, tree

    # Default fallback
    return "Sorry, I didn't understand that. Try commands like 'insert 8 as left child of 4', 'delete 5', 'update 5 as 10', 'search for 5', 'what is the height', or 'show inorder traversal'.", False, tree
