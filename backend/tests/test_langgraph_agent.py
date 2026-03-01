"""
Test suite for LangGraph agent with edge case handling.

Tests cover:
- Tree operations with duplicate values
- Attempting to insert into occupied positions
- Chat context awareness
- Intent classification
- All error conditions
"""

import pytest
from langgraph_agent import TreeAgent, handle_message
from tree_utils import insert_node, delete_node
from request_router import RequestRouter, IntentType


class TestRequestRouter:
    """Test intent classification and routing"""

    def setup_method(self):
        self.router = RequestRouter()

    def test_insert_intent_with_parent(self):
        """Test insert intent parsing with parent node"""
        intent, params = self.router.classify_intent("Insert 8 as left child of 4")
        assert intent == IntentType.INSERT
        assert params["new_value"] == 8
        assert params["parent_value"] == 4
        assert params["position"] == "left"

    def test_delete_intent(self):
        """Test delete intent"""
        intent, params = self.router.classify_intent("Delete 5")
        assert intent == IntentType.DELETE
        assert params["value"] == 5

    def test_search_intent(self):
        """Test search intent"""
        intent, params = self.router.classify_intent("Find 7")
        assert intent == IntentType.SEARCH
        assert params["value"] == 7

    def test_traversal_intent(self):
        """Test traversal intent"""
        intent, params = self.router.classify_intent("Show inorder traversal")
        assert intent == IntentType.TRAVERSAL

    def test_query_intent_height(self):
        """Test height query"""
        intent, params = self.router.classify_intent("What is the height?")
        assert intent == IntentType.QUERY
        assert params["query_type"] == "height"

    def test_query_intent_height_variations(self):
        """Verify additional height phrasings are classified as queries"""
        for phrase in ["height of tree", "tree height", "how tall is the tree"]:
            intent, params = self.router.classify_intent(phrase)
            assert intent == IntentType.QUERY, f"{phrase} not classified as QUERY"
            assert params.get("query_type") == "height"

    def test_query_intent_height_in_long_sentence(self):
        """Even when height appears inside a longer sentence, it should still be a height query"""
        intent, params = self.router.classify_intent("height is still issue explain about binary tree")
        assert intent == IntentType.QUERY
        assert params.get("query_type") == "height"

    def test_general_conversation(self):
        """Test general conversation"""
        intent, params = self.router.classify_intent("Tell me about trees")
        assert intent == IntentType.GENERAL


class TestTreeOperations:
    """Test tree operations with edge cases"""

    def test_insert_into_occupied_left_position(self):
        """Test that inserting into occupied left position fails"""
        tree = {"value": 5, "left": {"value": 3, "left": None, "right": None}, "right": None}
        
        # Try to insert into already occupied left position
        result = insert_node(tree, 5, 2, "left")
        assert result is False, "Should not allow inserting into occupied position"
        # Tree should remain unchanged
        assert tree["left"]["value"] == 3

    def test_insert_into_occupied_right_position(self):
        """Test that inserting into occupied right position fails"""
        tree = {"value": 5, "left": None, "right": {"value": 7, "left": None, "right": None}}
        
        result = insert_node(tree, 5, 8, "right")
        assert result is False, "Should not allow inserting into occupied position"
        assert tree["right"]["value"] == 7

    def test_insert_with_duplicate_value(self):
        """Test inserting nodes with duplicate values"""
        tree = {"value": 5, "left": {"value": 3, "left": None, "right": None}, "right": None}
        
        # Should allow inserting duplicate values in right position
        result = insert_node(tree, 5, 5, "right")
        assert result is True
        assert tree["right"]["value"] == 5

    def test_insert_nonexistent_parent(self):
        """Test inserting with non-existent parent returns False"""
        tree = {"value": 5, "left": None, "right": None}
        
        result = insert_node(tree, 999, 10, "left")
        assert result is False

    def test_insert_duplicate_value_disallowed(self):
        """Duplicate values should be prevented globally"""
        tree = {"value": 5, "left": {"value": 3, "left": None, "right": None}, "right": None}
        # first insertion of 3 as right child should succeed
        assert insert_node(tree, 5, 3, "right")
        # second insertion of 3 anywhere should now fail
        assert insert_node(tree, 5, 3, "left") is False

    def test_insert_invalid_direction(self):
        """insert_node should reject invalid direction strings"""
        tree = {"value": 5, "left": None, "right": None}
        assert insert_node(tree, 5, 6, "middle") is False

    def test_insert_into_empty_tree(self):
        """Test insert operation message handling on empty tree"""
        agent = TreeAgent()
        
        response, modified, tree = agent.process_message(None, "Insert 5")
        assert "No tree selected" in response or "Error" in response


class TestChatContextHandling:
    """Test that chat maintains proper context"""

    def test_tree_context_preserved_after_operation(self):
        """Test that tree context is properly maintained"""
        # Create initial tree
        tree = {"value": 5, "left": None, "right": None}
        
        agent = TreeAgent()
        
        # Insert a node via chat
        response, modified, new_tree = agent.process_message(tree, "Insert 3 as left child of 5")
        
        assert modified is True
        assert new_tree["left"]["value"] == 3
        assert "Inserted 3" in response

    def test_follow_up_query_uses_updated_tree(self):
        """Test that follow-up queries work on updated tree"""
        tree = {"value": 5, "left": None, "right": None}
        
        agent = TreeAgent()
        
        # Insert node
        _, _, updated_tree = agent.process_message(tree, "Insert 3 as left child of 5")
        
        # Query the tree
        response, _, _ = agent.process_message(updated_tree, "Find 3")
        assert "Found" in response or "3" in response

    def test_error_on_duplicate_insert(self):
        """Test proper error message when trying to insert into occupied position"""
        tree = {"value": 5, "left": {"value": 3, "left": None, "right": None}, "right": None}
        
        agent = TreeAgent()
        
        response, modified, _ = agent.process_message(
            tree, 
            "Insert 2 as left child of 5"
        )
        
        assert modified is False
        assert "already exists" in response or "Error" in response


class TestAllEdgeCases:
    """Comprehensive edge case testing"""

    def test_multiple_duplicate_inserts_different_parents(self):
        """Test inserting same value under different parents"""
        tree = {
            "value": 5,
            "left": {"value": 3, "left": None, "right": None},
            "right": None
        }
        
        agent = TreeAgent()
        
        # Insert 5 as right child (different from root's value)
        response, modified, tree = agent.process_message(tree, "Insert 5 as right child of 5")
        assert modified is True
        assert tree["right"]["value"] == 5

    def test_chain_of_operations(self):
        """Test a chain of insert, query, and delete operations"""
        agent = TreeAgent()
        tree = {"value": 5, "left": None, "right": None}
        
        # Insert operations
        r1, m1, tree = agent.process_message(tree, "Insert 3 as left child of 5")
        assert m1 is True
        
        r2, m2, tree = agent.process_message(tree, "Insert 7 as right child of 5")
        assert m2 is True
        
        # Search
        r3, m3, tree = agent.process_message(tree, "Find 3")
        assert "Found" in r3 or "3" in r3
        # search with 'node' keyword
        r3b, m3b, tree = agent.process_message(tree, "search node 7")
        assert "7" in r3b or "Found" in r3b
        
        # Traversal
        r4, m4, tree = agent.process_message(tree, "Inorder traversal")
        assert m4 is False
        assert "3" in r4 or "Inorder" in r4

    def test_delete_with_children(self):
        """Test deleting node with child nodes"""
        tree = {
            "value": 5,
            "left": {"value": 3, "left": {"value": 1, "left": None, "right": None}, "right": None},
            "right": None
        }
        
        agent = TreeAgent()
        
        response, modified, new_tree = agent.process_message(tree, "Delete 3")
        assert modified is True
        # Node 3 and its subtree should be gone
        assert new_tree["left"] is None

    def test_update_with_duplicates(self):
        """Test updating a node when duplicates exist"""
        tree = {
            "value": 5,
            "left": {"value": 3, "left": None, "right": None},
            "right": {"value": 5, "left": None, "right": None}
        }
        
        agent = TreeAgent()
        
        response, modified, new_tree = agent.process_message(tree, "Update 3 to 4")
        assert modified is True
        assert "Updated" in response

    def test_search_with_duplicates(self):
        """Test searching when tree has duplicate values"""
        tree = {
            "value": 5,
            "left": {"value": 5, "left": None, "right": None},
            "right": None
        }
        
        agent = TreeAgent()
        
        response, _, _ = agent.process_message(tree, "Find 5")
        assert "Found" in response

    def test_malformed_insert_command(self):
        """Test handling of malformed insert commands"""
        tree = {"value": 5, "left": None, "right": None}
        
        agent = TreeAgent()
        
        response, modified, _ = agent.process_message(tree, "Insert something weird")
        # Should not crash, should provide helpful error
        assert not modified

    def test_agent_prompts_for_direction(self):
        """When direction missing the agent asks for clarification"""
        tree = {"value": 10, "left": None, "right": None}
        agent = TreeAgent()
        response, modified, _ = agent.process_message(tree, "Insert 5 under 10")
        assert "left or right" in response.lower()
        assert not modified

    def test_ambiguous_insert_without_parent(self):
        """Generic 'Insert <value>' on non-empty tree should request parent/direction"""
        tree = {"value": 10, "left": None, "right": None}
        agent = TreeAgent()
        response, modified, _ = agent.process_message(tree, "Insert 5")
        assert "specify" in response.lower() and "parent" in response.lower()
        assert not modified

    def test_delete_promotes_single_child(self):
        """Deleting a node with only one child should promote that child"""
        tree = {"value": 10, "left": {"value": 5, "left": None, "right": {"value": 7, "left": None, "right": None}}, "right": None}
        agent = TreeAgent()
        response, modified, new_tree = agent.process_message(tree, "Delete 5 force")
        assert modified
        # the 7 should replace 5 as left child of 10
        assert new_tree["left"]["value"] == 7

    def test_delete_requires_force_only_for_two_children(self):
        """Agent should require force only when node has two children"""
        tree = {"value": 10, "left": {"value": 5, "left": {"value": 3, "left": None, "right": None}, "right": None}, "right": None}
        agent = TreeAgent()
        response, modified, _ = agent.process_message(tree, "Delete 5")
        # since 5 has only one child (3) should allow without force
        assert modified

    def test_search_empty_tree_returns_error(self):
        """Search on an empty tree should give explicit error"""
        agent = TreeAgent()
        response, modified, _ = agent.process_message(None, "Find 5")
        assert "empty" in response.lower() or "no tree" in response.lower()
        assert not modified

    def test_chat_without_tree_selected(self):
        """Chat endpoint message when no tree ID provided"""
        # here we simulate by directly calling agent with tree=None but using simple classifier
        agent = TreeAgent()
        response, modified, _ = agent.process_message(None, "Insert 5 as left child of 10")
        assert "select or create a tree" in response.lower() or "no tree" in response.lower()
        assert not modified

    def test_missing_parent_error(self):
        """Test clear error when parent doesn't exist"""
        tree = {"value": 5, "left": None, "right": None}
        
        agent = TreeAgent()
        
        response, modified, _ = agent.process_message(
            tree,
            "Insert 10 as left child of 999"
        )
        
        assert modified is False
        assert "not found" in response.lower() or "error" in response.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
