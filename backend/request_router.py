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
    RESET = "reset"      # clear/reset whole tree
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
                r'^edit\s+(\S+)\s+to\s+(\S+)$',
            ],
            IntentType.SEARCH: [
                r'^search\s+for\s+(\S+)$',
                r'^search\s+node\s+(\S+)$',
                r'^search\s+(\S+)$',
                r'^find\s+node\s+(\S+)$',
                r'^find\s+(\S+)$',
            ],
            IntentType.TRAVERSAL: [
                # allow optional space/hyphen between pre/in/post and order, with or without the word 'traversal'
                r'^(in[- ]?order|pre[- ]?order|post[- ]?order)(?:\s+traversal)?$',
                r'^show\s+(in[- ]?order|pre[- ]?order|post[- ]?order)$',
            ],
            IntentType.QUERY: [
                # height queries
                r'^what\s+is\s+the\s+height$',
                r'^height$',
                r'^height\s+of\s+tree$',
                r'^tree\s+height$',
                r'^how\s+tall(?:\s+is)?(?:\s+the)?\s+tree$',
                # leaf/leaves queries
                r'^show\s+leaves?$',
                r'^show\s+leaf\s+nodes?$',
                r'^leaf\s+nodes?$',
                r'^what\s+are\s+the\s+leaves\??$',
                # count queries
                r'^(how\s+many\s+nodes|number\s+of\s+nodes|count\s+nodes|show\s+count(\s+of\s+nodes)?)$',
            ],
            IntentType.RESET: [
                r'^(?:reset|clear|wipe)(?:\s+tree)?$',
                r'^delete\s+all$',
            ],
        }

    def classify_intent(self, user_message: str):
        message_lower = user_message.lower().strip()

        # quick substring-based intents for noisy or compound inputs
        # this sits before the strict regex patterns to catch cases like
        # "height is still issue" or "height of tree please" where the
        # anchored regex would not match the full string.
        if re.search(r"\bheight\b|\btall\b", message_lower) and not any(word in message_lower for word in ["insert", "delete", "update"]):
            return IntentType.QUERY, {"query_type": "height"}
        if re.search(r"\bleaf\b|\bleaves\b", message_lower) and not any(word in message_lower for word in ["insert", "delete", "update"]):
            return IntentType.QUERY, {"query_type": "leaves"}
        if re.search(r"\bhow many\b|\bcount\b|\bnumber of\b", message_lower):
            return IntentType.QUERY, {"query_type": "count"}
        if re.search(r"\bin[- ]?order\b|\bpre[- ]?order\b|\bpost[- ]?order\b", message_lower):
            # choose first word as traversal type, strip hyphens/spaces
            first = re.search(r"\bin[- ]?order\b|\bpre[- ]?order\b|\bpost[- ]?order\b", message_lower).group(0)
            tt = first.replace("-", "").replace(" ", "")
            return IntentType.TRAVERSAL, {"traversal_type": tt}

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
                # normalize forms like "pre order" or "pre-order" to "preorder"
                traversal_type = groups[0].lower().replace("-", "").replace(" ", "")
                params["traversal_type"] = traversal_type
            return params
        elif intent_type == IntentType.QUERY:
            # Determine what kind of query (allow many natural wordings)
            msg = message.lower()
            if "height" in msg or "tall" in msg or "tree height" in msg or "height of tree" in msg or "how tall" in msg:
                params["query_type"] = "height"
            elif "leaf" in msg or "leav" in msg:  # match "leaf" or "leaves"
                params["query_type"] = "leaves"
            elif "how many" in msg or "number of" in msg or "count" in msg:
                params["query_type"] = "count"
            return params

        return params

    def is_tree_action(self, intent_type: IntentType) -> bool:
        """Check if intent is a tree modification action"""
        return intent_type in [
            IntentType.INSERT,
            IntentType.DELETE,
            IntentType.UPDATE,
            IntentType.RESET,  # resetting the tree also modifies state
        ]

    def is_tree_query(self, intent_type: IntentType) -> bool:
        """Check if intent is a tree query (read-only)"""
        return intent_type in [
            IntentType.SEARCH,
            IntentType.TRAVERSAL,
            IntentType.QUERY,
        ]
