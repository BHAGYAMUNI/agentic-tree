"""
Intent Classifier and Request Router for Agentic Tree

This module classifies user intents into two categories:
1. TREE_ACTION: Structural operations (insert, delete, search, update)
2. CONVERSATION: General questions (height, leaves, traversals, etc.)

The router ensures proper context handling and routes to appropriate handlers.
"""

import re
from enum import Enum
from typing import Dict, List, Optional


class IntentType(str, Enum):
    INSERT = "insert"
    DELETE = "delete"
    UPDATE = "update"
    SEARCH = "search"
    TRAVERSAL = "traversal"
    QUERY = "query"
    GENERAL = "general"
    INVALID = "invalid"


class RequestRouter:

    def __init__(self):
        self.intent_patterns = {
            IntentType.INSERT: [
                r'^insert\s+(\S+)\s+as\s+(left|right)\s+child\s+of\s+(\S+)$',
                r'^insert\s+(\S+)\s+to\s+(left|right)\s+of\s+(\S+)$',
                # allow abbreviated "as right of" syntax (no "child")
                r'^insert\s+(\S+)\s+as\s+(left|right)\s+of\s+(\S+)$',
                r'^add\s+(\S+)\s+as\s+(left|right)\s+child\s+of\s+(\S+)$',
                r'^insert\s+(\S+)\s+as\s+root$',
                # ambiguous bare insert – no parent/direction specified
                r'^insert\s+(\S+)$',
                # under-phrasing: assume parent but not direction
                r'^insert\s+(\S+)\s+under\s+(\S+)$',
                # capture arbitrary position (to detect invalid directions like "middle")
                r'^insert\s+(\S+)\s+as\s+(\S+)\s+child\s+of\s+(\S+)$',
            ],
            IntentType.DELETE: [
                r'^delete\s+(\d+)$',
                r'^remove\s+(\d+)$',
            ],
            IntentType.UPDATE: [
                r'^update\s+(\S+)\s+to\s+(\S+)$',
                r'^change\s+(\S+)\s+to\s+(\S+)$',
            ],
            IntentType.SEARCH: [
                r'^search\s+for\s+(\S+)$',
                r'^search\s+node\s+(\S+)$',
                r'^search\s+(\S+)$',
                r'^find\s+node\s+(\S+)$',
                r'^find\s+(\S+)$',
            ],
            IntentType.TRAVERSAL: [
                r'^(inorder|preorder|postorder)\s+traversal$',
                r'^show\s+(inorder|preorder|postorder)$',
            ],
            IntentType.QUERY: [
                r'^what\s+is\s+the\s+height$',
                r'^height$',
                r'^show\s+leaves$',
                r'^leaf\s+nodes$',
                r'^(how\s+many\s+nodes|number\s+of\s+nodes|count\s+nodes|show\s+count(\s+of\s+nodes)?)$',
            ],
        }

    def classify_intent(self, user_message: str):
        message_lower = user_message.lower().strip()

        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.match(pattern, message_lower)
                if match:
                    params = self._extract_parameters(intent_type, match, message_lower)
                    return intent_type, params

        return IntentType.GENERAL, {"query": user_message}

    def _extract_parameters(self, intent_type: IntentType, match: re.Match, 
                          message: str) -> Dict:
        """
        Extract structured parameters from regex match.
        
        Args:
            intent_type: Type of intent
            match: Regex match object
            message: Original message for context
            
        Returns:
            Dictionary of extracted parameters
        """
        params = {"original_message": message}

        if intent_type == IntentType.INSERT:
            groups = match.groups()
            # first group is value, may be non-numeric
            if groups:
                val = groups[0]
                try:
                    params["new_value"] = int(val)
                except Exception:
                    params["new_value"] = val
            # detect root insertion explicitly
            if "as root" in message:
                params["root"] = True
                return params
            # extract position and parent for full insert patterns
            # if the message uses "under" without specifying left/right we
            # will only have two capture groups (value, parent).  in that case
            # groups[1] should be treated as parent rather than position.
            if "under" in message and not re.search(r"\b(left|right)\b", message):
                if len(groups) >= 2:
                    try:
                        params["parent_value"] = int(groups[1])
                    except Exception:
                        params["parent_value"] = groups[1]
            else:
                if len(groups) >= 2:
                    params["position"] = groups[1].lower()
                if len(groups) >= 3:
                    try:
                        params["parent_value"] = int(groups[2])
                    except Exception:
                        params["parent_value"] = groups[2]
            return params

        elif intent_type == IntentType.DELETE:
            groups = match.groups()
            if groups:
                try:
                    params["value"] = int(groups[0])
                except Exception:
                    params["value"] = groups[0]  # Fallback to string
            return params

        elif intent_type == IntentType.UPDATE:
            groups = match.groups()
            if len(groups) >= 2:
                try:
                    params["old_value"] = int(groups[0])
                except Exception:
                    params["old_value"] = groups[0]
                try:
                    params["new_value"] = int(groups[1])
                except Exception:
                    params["new_value"] = groups[1]
            return params

        elif intent_type == IntentType.SEARCH:
            groups = match.groups()
            if groups:
                try:
                    params["value"] = int(groups[0])
                except Exception:
                    params["value"] = groups[0]
            return params

        elif intent_type == IntentType.TRAVERSAL:
            groups = match.groups()
            if groups:
                traversal_type = groups[0].lower().replace("-", "").replace(" ", "")
                params["traversal_type"] = traversal_type
            return params

        elif intent_type == IntentType.QUERY:
            # Determine what kind of query
            if "height" in message or "tall" in message:
                params["query_type"] = "height"
            elif "leaf" in message:
                params["query_type"] = "leaves"
            elif "how many" in message or "number of" in message or "count" in message:
                params["query_type"] = "count"
            return params

        return params

    def is_tree_action(self, intent_type: IntentType) -> bool:
        """Check if intent is a tree modification action"""
        return intent_type in [
            IntentType.INSERT,
            IntentType.DELETE,
            IntentType.UPDATE,
        ]

    def is_tree_query(self, intent_type: IntentType) -> bool:
        """Check if intent is a tree query (read-only)"""
        return intent_type in [
            IntentType.SEARCH,
            IntentType.TRAVERSAL,
            IntentType.QUERY,
        ]
