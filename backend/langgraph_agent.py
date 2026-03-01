"""
LangGraph-based Agentic Tree Agent

This module implements an agent using LangGraph that:
1. Classifies user intents using RequestRouter
2. Routes to appropriate tree operations or conversational responses
3. Maintains tree context throughout the interaction
4. Handles errors gracefully with fallback responses

Architecture:
- State: Maintains tree, message, intent, and response
- Nodes: classifier, tree_action, conversation, finalizer
- Edges: Dynamic routing based on classified intent
"""

import json
import re
from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages

# langgraph is a runtime dependency that may not be installed in every
# developer environment (particularly when Python hasn't been set up yet).
# the original import error that triggered the user's message was
# ``ModuleNotFoundError: No module named 'langgraph'``.  we catch it here
# so the stack trace is a little more friendly and points them at the
# requirements file or `pip install` command for resolution.
try:
    from langgraph.graph import StateGraph, END
except ImportError as import_err:  # pragma: no cover - environment issue
    raise ImportError(
        "langgraph is required for the AI agent. "
        "Install the backend dependencies (e.g. `pip install -r backend/requirements.txt` "
        "or `pip install langgraph langchain langchain-openai`)"
    ) from import_err
from langchain_openai import ChatOpenAI

# the human/system message classes are only needed if the LLM path is used.
# in some versions of `langchain` the module layout may change, and importing
# them at import-time can prevent the app from even starting. we perform a
# lazy import inside `_handle_general_conversation` instead and handle any
# ImportError there with a helpful message.
#
# (See https://github.com/langchain-ai/langchain/issues/*** for a discussion
# of layout changes between versions.)
from request_router import RequestRouter, IntentType
from tree_utils import (
    calculate_height,
    find_leaf_nodes,
    insert_node,
    delete_node,
    update_node,
    search_node,
    inorder_traversal,
    preorder_traversal,
    postorder_traversal,
)
import os

# simple logger so that we can confirm the agent is exercising the
# LangGraph workflow during runtime
import logging

logger = logging.getLogger(__name__)


# Type definitions for LangGraph state
class AgentState(TypedDict):
    tree: Annotated[Optional[dict], lambda x, y: y]
    user_message: str
    intent_type: IntentType
    intent_params: dict
    response: str
    tree_modified: bool
    error: Optional[str]
    pending_action: Optional[dict]


class TreeAgent:
    """LangGraph-based agent for tree operations with context awareness"""

    def __init__(self):
        """Initialize the agent with router and optional LLM"""
        self.router = RequestRouter()
        self.llm = None
        
        # Initialize LLM if enabled
        if os.environ.get("USE_LLM_AGENT", "0") in ("1", "true", "True"):
            try:
                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self.llm = ChatOpenAI(
                        api_key=api_key,
                        model="gpt-3.5-turbo",
                        temperature=0,
                        max_tokens=500,
                    )
            except Exception as e:
                print(f"Warning: Could not initialize LLM: {e}")
                self.llm = None

        # Build the workflow graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Flow:
        1. classifier: Determine intent
        2. Route based on intent_type:
           - INSERT/DELETE/UPDATE -> tree_action node
           - SEARCH/TRAVERSAL/QUERY -> conversation node
           - GENERAL -> conversation node
           - INVALID -> error handler
        3. finalizer: Prepare response
        """
        graph = StateGraph(AgentState)

        # Define nodes
        graph.add_node("classifier", self._classify_intent)
        graph.add_node("tree_action", self._handle_tree_action)
        graph.add_node("conversation", self._handle_conversation)
        graph.add_node("finalizer", self._finalize_response)

        # Define edges
        graph.add_edge("classifier", "tree_action")  # Default
        graph.set_entry_point("classifier")

        # Conditional routing based on intent
        def route_after_classification(state: AgentState) -> str:
            """Route to appropriate handler based on classified intent"""
            intent_type = state["intent_type"]
            
            if self.router.is_tree_action(intent_type):
                return "tree_action"
            elif self.router.is_tree_query(intent_type) or intent_type == IntentType.GENERAL:
                return "conversation"
            else:
                return "conversation"

        graph.add_conditional_edges(
            "classifier",
            route_after_classification,
            {
                "tree_action": "tree_action",
                "conversation": "conversation",
            }
        )

        # Both paths lead to finalizer
        graph.add_edge("tree_action", "finalizer")
        graph.add_edge("conversation", "finalizer")
        graph.add_edge("finalizer", END)

        return graph.compile()

    def _classify_intent(self, state: AgentState):

        user_message = state["user_message"]
        message_lower = user_message.lower().strip()

        # ---------------------------------------------------
        # 🔹 STEP 1: Handle clarification follow-up
        # ---------------------------------------------------
        pending = state.get("pending_action")

        if pending and pending.get("type") == "insert":

            if "left" in message_lower:
                return {
                    "intent_type": IntentType.INSERT,
                    "intent_params": {
                        "new_value": pending["new_value"],
                        "parent_value": pending["parent_value"],
                        "position": "left"
                    },
                    "pending_action": None
                }

            if "right" in message_lower:
                return {
                    "intent_type": IntentType.INSERT,
                    "intent_params": {
                        "new_value": pending["new_value"],
                        "parent_value": pending["parent_value"],
                        "position": "right"
                    },
                    "pending_action": None
                }

        # ---------------------------------------------------
        # 🔹 STEP 2: Normal classification
        # ---------------------------------------------------
        intent_type, params = self.router.classify_intent(user_message)

        logger.info(f"Classified intent={intent_type} params={params}")

        return {
            "intent_type": intent_type,
            "intent_params": params or {},
            "tree_modified": False,
            "error": None,
            "pending_action": None
        }

    def _handle_tree_action(self, state: AgentState):

        tree = state["tree"]
        intent_type = state["intent_type"]
        params = state["intent_params"]

        # -----------------------------
        # EMPTY TREE HANDLING
        # -----------------------------
        if tree is None:

            if intent_type == IntentType.INSERT:
                new_value = params.get("new_value")

                try:
                    val = int(new_value)
                except Exception:
                    return {
                        "response": "Node value must be a number.",
                        "tree_modified": False
                    }

                return {
                    "tree": {"value": val, "left": None, "right": None},
                    "response": f"Created root node with value {val}.",
                    "tree_modified": True
                }

            return {
                "response": "No tree selected.",
                "tree_modified": False
            }

        # -----------------------------
        # TREE EXISTS
        # -----------------------------
        try:

            if intent_type == IntentType.INSERT:
                return self._handle_insert(state, tree, params)

            if intent_type == IntentType.DELETE:
                return self._handle_delete(state, tree, params)

            if intent_type == IntentType.UPDATE:
                return self._handle_update(state, tree, params)

            if intent_type == IntentType.SEARCH:
                return self._handle_search(state, tree, params)

            if intent_type == IntentType.QUERY:
                return self._handle_query(state, tree, params)

        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "error": str(e),
                "tree_modified": False
            }

        return {
            "response": "Unable to process request.",
            "tree_modified": False
        }

    def _handle_insert(self, state: AgentState, tree: dict, params: dict):

        new_value = params.get("new_value")
        parent_value = params.get("parent_value")
        position = params.get("position")

        # -----------------------------------------
        # 🔹 Validate numeric values
        # -----------------------------------------
        try:
            new_val_int = int(new_value)
        except Exception:
            return {
                "response": "Node value must be a number.",
                "tree_modified": False
            }

        try:
            parent_val_int = int(parent_value)
        except Exception:
            return {
                "response": "Parent value must be a number.",
                "tree_modified": False
            }

        from tree_utils import get_node, search_node

        parent_node = get_node(tree, parent_val_int)

        if parent_node is None:
            return {
                "response": f"Parent node {parent_val_int} not found.",
                "tree_modified": False
            }

        # -----------------------------------------
        # 🔹 If direction missing → clarification
        # -----------------------------------------
        if position not in ("left", "right"):

            left_child = parent_node.get("left")
            right_child = parent_node.get("right")

            if left_child is not None and right_child is not None:
                return {
                    "response": f"Node {parent_val_int} already has two children.",
                    "tree_modified": False
                }

            # Ask clarification
            return {
                "response": f"Do you want to insert {new_val_int} as left or right child of {parent_val_int}?",
                "tree_modified": False,
                "pending_action": {
                    "type": "insert",
                    "new_value": new_val_int,
                    "parent_value": parent_val_int
                }
            }

        # -----------------------------------------
        # 🔹 Check duplicate
        # -----------------------------------------
        if search_node(tree, new_val_int):
            return {
                "response": f"Node {new_val_int} already exists.",
                "tree_modified": False
            }

        # -----------------------------------------
        # 🔹 Check occupied position
        # -----------------------------------------
        if parent_node.get(position) is not None:
            return {
                "response": f"{position.capitalize()} child of {parent_val_int} already exists.",
                "tree_modified": False
            }

        # -----------------------------------------
        # 🔹 Perform insert
        # -----------------------------------------
        new_tree = insert_node(tree, parent_val_int, new_val_int, position)

        return {
            "tree": new_tree,
            "response": f"Inserted {new_val_int} as {position} child of {parent_val_int}.",
            "tree_modified": True,
            "pending_action": None
        }

    def _handle_delete(self, state: AgentState, tree: dict, params: dict) -> AgentState:
        """Handle node deletion"""
        value = params.get("value")
        force = params.get("force", False)

        try:
            val_int = int(value)
        except Exception:
            state["response"] = "Node value must be a number."
            state["tree_modified"] = False
            return state

        from tree_utils import get_node, search_node

        node = get_node(tree, val_int)
        if node is None:
            state["response"] = f"✗ Node {val_int} not found in tree."
            state["tree_modified"] = False
            return state

        # If node has two children and force not specified, ask for confirmation
        if node.get("left") is not None and node.get("right") is not None and not force:
            state["response"] = (
                f"✗ Node {val_int} has two children; deletion would remove its entire subtree. "
                f"Reply with 'Delete {val_int} force' to confirm."
            )
            state["tree_modified"] = False
            return state

        # Proceed with deletion
        new_tree = delete_node(tree, val_int)
        state["tree"] = new_tree
        state["response"] = f"✓ Deleted node {val_int}."
        state["tree_modified"] = True
        logger.info(f"Deleted node {val_int}; tree modified")

        return state

    def _handle_update(self, state: AgentState, tree: dict, params: dict) -> AgentState:
        """Handle node value updates"""
        old_value = params.get("old_value")
        new_value = params.get("new_value")

        # ensure numeric values
        try:
            old_val_int = int(old_value)
        except Exception:
            state["response"] = "Error: old node value must be a number."
            state["tree_modified"] = False
            return state

        try:
            new_val_int = int(new_value)
        except Exception:
            state["response"] = "Error: new node value must be a number."
            state["tree_modified"] = False
            return state

        # enforce maximum value cap
        from tree_utils import MAX_NODE_VALUE
        if abs(new_val_int) > MAX_NODE_VALUE:
            state["response"] = f"✗ Value too large; maximum allowed is {MAX_NODE_VALUE}."
            state["tree_modified"] = False
            return state

        # ensure the node to change actually exists
        if not search_node(tree, old_val_int):
            state["response"] = f"✗ Node {old_val_int} not found in tree."
            state["tree_modified"] = False
            return state

        # don't allow changing to a value that already exists elsewhere
        if new_val_int != old_val_int and search_node(tree, new_val_int):
            state["response"] = f"✗ Node with value {new_val_int} already exists; cannot update to duplicate."
            state["tree_modified"] = False
            return state

        # perform the update
        update_node(tree, old_val_int, new_val_int)
        state["response"] = f"✓ Updated node {old_val_int} to {new_val_int}."
        state["tree_modified"] = True
        logger.info(f"Updated node {old_val_int} to {new_val_int}")
        return state

    def _handle_search(self, state: AgentState, tree: dict, params: dict) -> AgentState:
        """Handle node search (query operation)"""
        value = params.get("value")

        try:
            val_int = int(value)
        except Exception:
            state["response"] = "Search value must be a number."
            state["tree_modified"] = False
            return state

        found = search_node(tree, val_int)
        if found:
            state["response"] = f"✓ Found node {val_int} in the tree."
        else:
            state["response"] = f"✗ Node {val_int} not found in the tree."
        return state

    def _handle_query(self, state: AgentState, tree: dict, params: dict) -> AgentState:
        """Handle read-only queries such as height, leaves, and node count."""
        query_type = params.get("query_type")

        from tree_utils import calculate_height, find_leaf_nodes, count_nodes

        if query_type == "height":
            h = calculate_height(tree)
            state["response"] = f"✓ Tree height is {h}."
            state["tree_modified"] = False
            return state

        if query_type == "leaves":
            leaves = find_leaf_nodes(tree)
            state["response"] = f"✓ Leaf nodes: {', '.join(map(str, leaves)) if leaves else 'None'}."
            state["tree_modified"] = False
            return state

        if query_type == "count":
            n = count_nodes(tree)
            state["response"] = f"✓ Node count: {n}."
            state["tree_modified"] = False
            return state

        # fallback
        state["response"] = "I'm not sure which query you mean. Try 'height', 'leaf nodes', or 'count nodes'."
        state["tree_modified"] = False
        return state

    def _handle_conversation(self, state: AgentState):

        tree = state["tree"]
        intent_type = state["intent_type"]
        params = state["intent_params"]

        if tree is None:
            return {
                "response": "No tree selected.",
                "tree_modified": False
            }

        try:
            if intent_type == IntentType.TRAVERSAL:
                return self._handle_traversal(state, tree, params)

            if intent_type == IntentType.QUERY:
                return self._handle_query(state, tree, params)

            if intent_type == IntentType.GENERAL:
                return self._handle_general_conversation(state, tree, params)

            if intent_type == IntentType.SEARCH:
                return self._handle_search(state, tree, params)

        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "error": str(e),
                "tree_modified": False
            }

        return {
            "response": "Unable to process request.",
            "tree_modified": False
        }

    def _handle_traversal(self, state: AgentState, tree: dict, params: dict) -> AgentState:
        """Handle tree traversal queries"""
        traversal_type = (params.get("traversal_type") or "inorder").lower()

        if traversal_type == "inorder":
            result = inorder_traversal(tree)
            seq = ", ".join(map(str, result)) if isinstance(result, list) else str(result)
            state["response"] = f"Inorder traversal: {seq}"
        elif traversal_type == "preorder":
            result = preorder_traversal(tree)
            seq = ", ".join(map(str, result)) if isinstance(result, list) else str(result)
            state["response"] = f"Preorder traversal: {seq}"
        elif traversal_type == "postorder":
            result = postorder_traversal(tree)
            seq = ", ".join(map(str, result)) if isinstance(result, list) else str(result)
            state["response"] = f"Postorder traversal: {seq}"
        else:
            state["response"] = "Supported traversals: inorder, preorder, postorder"

        return state

    def _handle_query(self, state: AgentState, tree: dict, params: dict) -> AgentState:
        """Handle tree property queries (height, leaves, count)"""
        query_type = (params.get("query_type") or "height").lower()

        from tree_utils import calculate_height, find_leaf_nodes, count_nodes

        if query_type == "height":
            height = calculate_height(tree)
            state["response"] = f"✓ Tree height: {height}"
        elif query_type == "leaves":
            leaves = find_leaf_nodes(tree)
            state["response"] = f"✓ Leaf nodes: {', '.join(map(str, leaves)) if leaves else 'None'}"
        elif query_type == "count":
            n = count_nodes(tree)
            state["response"] = f"✓ Node count: {n}"
        else:
            state["response"] = "Supported queries: height, leaves, count"

        state["tree_modified"] = False
        return state

    def _handle_general_conversation(self, state: AgentState, tree: dict, 
                                     params: dict) -> AgentState:
        """Handle general conversation with optional LLM"""
        user_query = params.get("query", state["user_message"])

        # Create context about the tree
        tree_info = self._get_tree_info(tree)

        if self.llm:
            try:
                # Use LLM for intelligent conversation.  we lazily import the
                # message classes here so that the server can start even if the
                # installed langchain version has moved them around or is
                # otherwise incompatible.  if the import fails we raise a clear
                # error that tells the developer how to fix the situation.
                try:
                    from langchain.schema import HumanMessage, SystemMessage
                except ImportError:
                    # try alternate location used by some releases
                    try:
                        from langchain.schema.messages import HumanMessage, SystemMessage
                    except ImportError as e:
                        raise ImportError(
                            "Unable to import HumanMessage/SystemMessage from "
                            "langchain. Please ensure `langchain` is installed "
                            "and up to date (`pip install -U langchain`). "
                            "If you are using a very new or very old version of "
                            "langchain the package layout may have changed; "
                            "adjust the import or pin the version in "
                            "backend/requirements.txt."
                        ) from e

                system_prompt = f"""You are a helpful assistant discussing binary trees.
The current tree structure is:
{tree_info}

Provide concise, helpful responses about trees and data structures."""

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_query),
                ]

                response = self.llm.invoke(messages)
                state["response"] = response.content
            except Exception as e:
                state["response"] = self._get_fallback_response(user_query, tree_info)
        else:
            state["response"] = self._get_fallback_response(user_query, tree_info)

        return state

    def _get_tree_info(self, tree: dict) -> str:
        """Generate informative tree summary"""
        if tree is None:
            return "Empty tree"

        height = calculate_height(tree)
        leaves = find_leaf_nodes(tree)
        inorder = inorder_traversal(tree)

        return f"""
Tree Summary:
- Root: {tree.get('value')}
- Height: {height}
- In-order: {inorder}
- Leaves: {leaves}
"""

    def _get_fallback_response(self, query: str, tree_info: str) -> str:
        """Provide fallback response when LLM is unavailable"""
        lower_query = query.lower()

        if any(word in lower_query for word in ["help", "command", "how", "what"]):
            return (
                "I can help you with binary tree operations! Try commands like:\n"
                "- 'Insert 8 as left child of 4'\n"
                "- 'Delete 5'\n"
                "- 'Search for 7'\n"
                "- 'Show inorder traversal'\n"
                "- 'What is the height?'\n"
                "- 'Show leaf nodes'"
            )
        elif any(word in lower_query for word in ["tree", "structure"]):
            return f"Current tree info:{tree_info}"
        else:
            return "I'm a tree assistant. Ask me about tree operations or structure!"

    def _finalize_response(self, state: AgentState):

        # if not state.get("response"):
        #     return {"response": "Unable to process request."}

        return {}

    def process_message(self, tree: Optional[dict], user_message: str) -> tuple[str, bool, Optional[dict]]:
        """
        Main entry point: Process user message with tree context.
        
        Args:
            tree: Current tree structure
            user_message: User input message
            
        Returns:
            Tuple of (response_text, tree_modified, updated_tree)
        """
        # log entry so callers can see the LangGraph agent is being used
        logger.info(f"LangGraph agent processing message: {user_message!r}")

        # Create initial state
        initial_state: AgentState = {
            "tree": tree,
            "user_message": user_message,
            "intent_type": IntentType.INVALID,
            "intent_params": {},
            "response": "",
            "tree_modified": False,
            "error": None,
            "pending_action": None,
        }

        try:
            # Execute the graph
            final_state = self.graph.invoke(initial_state)

            # Extract results
            response = final_state.get("response", "Unable to process request.")
            tree_modified = final_state.get("tree_modified", False)
            updated_tree = final_state.get("tree", tree)

            return response, tree_modified, updated_tree

        except Exception as e:
            error_response = f"Error processing request: {str(e)}"
            return error_response, False, tree


# Singleton instance
_agent_instance = None


def get_agent() -> TreeAgent:
    """Get or create the global agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = TreeAgent()
    return _agent_instance


def handle_message(tree: Optional[dict], message: str) -> tuple[str, bool, Optional[dict]]:
    """
    Public function for backward compatibility.
    
    Process message with the LangGraph agent.
    
    Args:
        tree: Current tree structure
        message: User message
        
    Returns:
        Tuple of (response, tree_modified, new_tree)
    """
    agent = get_agent()
    return agent.process_message(tree, message)
