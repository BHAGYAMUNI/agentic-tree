"""
LLM Adapter for AI agent integration.

Uses environment variables to configure an LLM provider. Supports OpenAI API.
If the LLM provider is not configured or packages are missing, the adapter
raises ImportError to allow the caller to fallback to rule-based logic.

Supported env vars:
- USE_LLM_AGENT=1 to enable LLM usage
- OPENAI_API_KEY for OpenAI API key
- OPENAI_MODEL defaults to 'gpt-3.5-turbo'

The adapter exposes a single function `llm_handle_message(tree, message)`
which returns (response_text, modified, new_tree).
"""
from __future__ import annotations
import os
import json
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

def _serialize_tree(tree) -> str:
    """Safely serialize tree to JSON string for prompt."""
    try:
        return json.dumps(tree, indent=2)
    except Exception as e:
        logger.warning(f"Failed to serialize tree to JSON: {e}")
        return str(tree)


def _parse_llm_response(response_text: str) -> dict:
    """Parse LLM response as JSON, with fallback."""
    try:
        # Try to extract JSON from the response
        lines = response_text.strip().split('\n')
        for line in lines:
            try:
                obj = json.loads(line)
                if isinstance(obj, dict) and 'response' in obj:
                    return obj
            except json.JSONDecodeError:
                pass
        # Try parsing the whole thing
        obj = json.loads(response_text)
        return obj
    except Exception as e:
        logger.warning(f"Failed to parse LLM JSON response: {e}. Returning raw response.")
        return {"response": response_text, "modified": False, "tree": None}


def llm_handle_message(tree, message) -> Tuple[str, bool, dict]:
    """Call OpenAI API to handle the message and optionally modify the tree.

    Returns: (response_text, modified_flag, new_tree)
    Raises: ImportError if OpenAI is not available or API key is missing.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ImportError("OPENAI_API_KEY environment variable not set")

    try:
        import openai
    except ImportError:
        raise ImportError("openai package not installed. Install with: pip install openai")

    openai.api_key = api_key
    model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

    prompt = (
        "You are an intelligent tree assistant.\n\n"
        "CURRENT TREE (JSON):\n" + _serialize_tree(tree) + "\n\n"
        "USER MESSAGE: \"" + (message or "") + "\"\n\n"
        "INSTRUCTIONS:\n"
        "1. Answer the user's question about the tree (e.g., height, leaves, structure).\n"
        "2. If the user asks to modify the tree (insert/delete), do so and set 'modified': true.\n"
        "3. Always respond with valid JSON containing exactly these fields:\n"
        "   - 'response': Your text answer to the user (string)\n"
        "   - 'modified': true if you modified the tree, false otherwise (boolean)\n"
        "   - 'tree': The updated tree object if modified, null otherwise\n\n"
        "EXAMPLE RESPONSE:\n"
        '{"response": "The tree has 3 nodes.", "modified": false, "tree": null}\n\n'
        "YOUR RESPONSE (JSON only):"
    )

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a tree data structure assistant. Respond only in valid JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500,
        )
        out = response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        raise ImportError(f"LLM provider error: {e}")

    # Parse the model output as JSON
    payload = _parse_llm_response(out)
    response_text = payload.get("response", "I encountered an issue processing your request.")
    modified = bool(payload.get("modified", False))
    new_tree = payload.get("tree") if modified else tree

    return response_text, modified, new_tree

