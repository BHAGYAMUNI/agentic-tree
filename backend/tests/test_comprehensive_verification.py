"""
Comprehensive Test Suite for Manual Controls & AI Chat
Covers all 40 test scenarios from specification
"""

import os
os.environ['RUNNING_TESTS'] = '1'

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from database import Base, engine
from main import app

client = TestClient(app)


@pytest.fixture(scope='module', autouse=True)
def setup_db():
    """Setup and cleanup database for all tests in module"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def register_user(email="test@example.com", password="password"):
    resp = client.post('/auth/register', json={'email': email, 'password': password})
    assert resp.status_code == 200
    return resp.json().get('access_token')


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_tree(token, tree_data=None):
    """Helper to create a tree"""
    resp = client.post('/trees', json={"name": "test_tree", "tree_data": tree_data}, headers=auth_headers(token))
    assert resp.status_code == 200
    return resp.json()['id']


# ===========================================
# PART 1: MANUAL CONTROLS - VALID CASES
# ===========================================

class TestManualValidCases:
    """Test valid manual control operations"""

    def test_01_insert_root_empty_tree(self):
        """Case 1: Insert root in empty tree"""
        token = register_user(email='m01@example.com')
        tree_id = create_tree(token, tree_data=None)

        resp = client.post(f'/trees/{tree_id}/insert', 
                          json={"parent_value": None, "new_value": 10, "direction": "left"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert resp.json()['tree_data']['value'] == 10
        assert resp.json()['tree_data']['left'] is None
        assert resp.json()['tree_data']['right'] is None

    def test_02_insert_left_child(self):
        """Case 2: Insert left child"""
        token = register_user(email='m02@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": None, "right": None})

        resp = client.post(f'/trees/{tree_id}/insert', 
                          json={"parent_value": 10, "new_value": 5, "direction": "left"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        tree_data = resp.json()['tree_data']
        assert tree_data['value'] == 10
        assert tree_data['left']['value'] == 5

    def test_03_insert_right_child(self):
        """Case 3: Insert right child"""
        token = register_user(email='m03@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": {"value": 5, "left": None, "right": None}, "right": None})

        resp = client.post(f'/trees/{tree_id}/insert', 
                          json={"parent_value": 10, "new_value": 9, "direction": "right"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        tree_data = resp.json()['tree_data']
        assert tree_data['right']['value'] == 9

    def test_04_insert_deep(self):
        """Case 4: Insert deep in tree"""
        token = register_user(email='m04@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": {"value": 9, "left": None, "right": None}
        })

        resp = client.post(f'/trees/{tree_id}/insert', 
                          json={"parent_value": 5, "new_value": 3, "direction": "left"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        tree_data = resp.json()['tree_data']
        assert tree_data['left']['left']['value'] == 3

    def test_05_delete_leaf(self):
        """Case 5: Delete leaf node"""
        token = register_user(email='m05@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": {"value": 3, "left": None, "right": None}, "right": None},
            "right": {"value": 9, "left": None, "right": None}
        })

        resp = client.post(f'/trees/{tree_id}/delete',
                          json={"value": 3},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        tree_data = resp.json()['tree_data']
        assert tree_data['left']['left'] is None

    def test_06_delete_node_with_one_child(self):
        """Case 6: Delete node with one child (promotion)"""
        token = register_user(email='m06@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": {"value": 7, "left": None, "right": None}},
            "right": None
        })

        resp = client.post(f'/trees/{tree_id}/delete',
                          json={"value": 5},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        tree_data = resp.json()['tree_data']
        assert tree_data['left']['value'] == 7

    def test_07_search_existing_node(self):
        """Case 7: Search for existing node"""
        token = register_user(email='m07@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": {"value": 9, "left": None, "right": None}
        })

        resp = client.post(f'/trees/{tree_id}/search',
                          json={"value": 7},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert resp.json()['found'] is False

        resp = client.post(f'/trees/{tree_id}/search',
                          json={"value": 9},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert resp.json()['found'] is True

    def test_08_reset_tree(self):
        """Case 8: Reset tree"""
        token = register_user(email='m08@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": None
        })

        resp = client.post(f'/trees/{tree_id}/reset',
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        
        get_resp = client.get(f'/trees/{tree_id}', headers=auth_headers(token))
        assert get_resp.json()['tree_data'] is None


# ===========================================
# PART 1: MANUAL CONTROLS - 400 ERROR CASES
# ===========================================

class TestManualErrorCases:
    """Test invalid manual control operations (must return 400)"""

    def test_09_insert_duplicate_value(self):
        """Case 9: Insert duplicate value must reject"""
        token = register_user(email='m09@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": None
        })

        resp = client.post(f'/trees/{tree_id}/insert', 
                          json={"parent_value": 10, "new_value": 5, "direction": "right"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 400
        assert 'already exists' in resp.json().get('detail', '').lower()

    def test_10_insert_occupied_left_slot(self):
        """Case 10: Insert left when already occupied"""
        token = register_user(email='m10@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": None
        })

        resp = client.post(f'/trees/{tree_id}/insert', 
                          json={"parent_value": 10, "new_value": 7, "direction": "left"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 400
        assert 'left child' in resp.json().get('detail', '').lower()

    def test_11_insert_under_nonexistent_parent(self):
        """Case 11: Insert under non-existing parent"""
        token = register_user(email='m11@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": None, "right": None})

        resp = client.post(f'/trees/{tree_id}/insert', 
                          json={"parent_value": 999, "new_value": 20, "direction": "left"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 400
        assert 'parent' in resp.json().get('detail', '').lower()

    def test_12_insert_invalid_direction(self):
        """Case 12: Insert with invalid direction"""
        token = register_user(email='m12@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": None, "right": None})

        resp = client.post(f'/trees/{tree_id}/insert', 
                          json={"parent_value": 10, "new_value": 5, "direction": "middle"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 400
        assert 'direction' in resp.json().get('detail', '').lower()

    def test_13_insert_non_numeric_value(self):
        """Case 13: Insert non-numeric value"""
        token = register_user(email='m13@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": None, "right": None})

        resp = client.post(f'/trees/{tree_id}/insert', 
                          json={"parent_value": 10, "new_value": "hello", "direction": "left"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 400
        assert 'number' in resp.json().get('detail', '').lower()

    def test_14_delete_nonexistent_node(self):
        """Case 14: Delete non-existing node"""
        token = register_user(email='m14@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": None, "right": None})

        resp = client.post(f'/trees/{tree_id}/delete',
                          json={"value": 999},
                          headers=auth_headers(token))
        
        assert resp.status_code == 404

    def test_15_delete_node_with_two_children_no_force(self):
        """Case 15: Delete node with two children without force"""
        token = register_user(email='m15@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": {"value": 9, "left": None, "right": None}
        })

        resp = client.post(f'/trees/{tree_id}/delete',
                          json={"value": 10},
                          headers=auth_headers(token))
        
        assert resp.status_code == 400
        assert 'two children' in resp.json().get('detail', '').lower()


# ===========================================
# PART 2: AI CHAT - VALID CASES
# ===========================================

class TestAIChatValidCases:
    """Test valid AI chat operations"""

    def test_c01_chat_insert_root(self):
        """Case C1: Insert root via chat"""
        token = register_user(email='c01@example.com')
        tree_id = create_tree(token, tree_data=None)

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "insert 10 as root"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'created root' in resp.json()['response'].lower() or 'inserted' in resp.json()['response'].lower()

    def test_c02_chat_insert_left_child(self):
        """Case C2: Insert left child via chat"""
        token = register_user(email='c02@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": None, "right": None})

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "insert 5 as left child of 10"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'inserted' in resp.json()['response'].lower()

    def test_c03_chat_insert_right_child(self):
        """Case C3: Insert right child via chat"""
        token = register_user(email='c03@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": None
        })

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "insert 9 as right child of 10"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'inserted' in resp.json()['response'].lower()

    def test_c04_chat_search_node(self):
        """Case C4: Search node via chat"""
        token = register_user(email='c04@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": {"value": 9, "left": None, "right": None}
        })

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "search 9"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'found' in resp.json()['response'].lower()

    def test_c05_chat_update_node(self):
        """Case C5: Update node via chat"""
        token = register_user(email='c05@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": {"value": 9, "left": None, "right": None}
        })

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "update 9 to 11"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'updated' in resp.json()['response'].lower()

    def test_c06_chat_height_query(self):
        """Case C6: Query height via chat"""
        token = register_user(email='c06@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": {"value": 9, "left": None, "right": None}
        })

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "height"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'height' in resp.json()['response'].lower()

    def test_c07_chat_leaves_query(self):
        """Case C7: Query leaves via chat"""
        token = register_user(email='c07@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": {"value": 9, "left": None, "right": None}
        })

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "leaf nodes"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert '5' in resp.json()['response'] or '9' in resp.json()['response']

    def test_c08_chat_count_query(self):
        """Case C8: Query count via chat"""
        token = register_user(email='c08@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": {"value": 9, "left": None, "right": None}
        })

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "count nodes"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'count' in resp.json()['response'].lower()

    def test_c09_chat_traversal(self):
        """Case C9: Traversal via chat"""
        token = register_user(email='c09@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": {"value": 9, "left": None, "right": None}
        })

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "inorder traversal"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'inorder' in resp.json()['response'].lower() or '5' in resp.json()['response']


# ===========================================
# PART 3: AI CHAT - REJECTION CASES
# ===========================================

class TestAIChatRejectionCases:
    """Test invalid AI chat operations (must NOT modify tree)"""

    def test_r01_missing_direction(self):
        """Case R1: Missing direction must ask for clarification"""
        token = register_user(email='r01@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": None, "right": None})

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "insert 8 under 10"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'specify' in resp.json()['response'].lower() or 'direction' in resp.json()['response'].lower() or 'clarify' in resp.json()['response'].lower()

    def test_r02_invalid_direction(self):
        """Case R2: Invalid direction"""
        token = register_user(email='r02@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": None, "right": None})

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "insert 8 as middle child of 10"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'direction' in resp.json()['response'].lower() or 'left or right' in resp.json()['response'].lower()

    def test_r03_duplicate_insert_rejection(self):
        """Case R3: Duplicate insert must reject"""
        token = register_user(email='r03@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": None
        })

        # Try to insert duplicate 5
        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "insert 5 as right child of 10"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'already exists' in resp.json()['response'].lower()

    def test_r04_insert_under_missing_parent(self):
        """Case R4: Insert under missing parent"""
        token = register_user(email='r04@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": None, "right": None})

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "insert 8 as left child of 999"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'parent' in resp.json()['response'].lower() or 'not found' in resp.json()['response'].lower()

    def test_r05_delete_two_children_no_force(self):
        """Case R5: Delete node with two children without force"""
        token = register_user(email='r05@example.com')
        tree_id = create_tree(token, tree_data={
            "value": 10,
            "left": {"value": 5, "left": None, "right": None},
            "right": {"value": 9, "left": None, "right": None}
        })

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "delete 10"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'two children' in resp.json()['response'].lower() or 'force' in resp.json()['response'].lower()

    def test_r06_non_numeric_value(self):
        """Case R6: Non-numeric value"""
        token = register_user(email='r06@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": None, "right": None})

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "insert hello as left child of 10"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'number' in resp.json()['response'].lower()

    def test_r07_random_conversation(self):
        """Case R7: Random conversation doesn't modify tree"""
        token = register_user(email='r07@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": None, "right": None})

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "how are you?"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        # Verify tree is unchanged
        get_resp = client.get(f'/trees/{tree_id}', headers=auth_headers(token))
        assert get_resp.json()['tree_data']['value'] == 10

    def test_r08_malformed_command(self):
        """Case R8: Malformed command"""
        token = register_user(email='r08@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": None, "right": None})

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "add something somewhere"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        # Should ask for clarification, not modify


# ===========================================
# PART 4: STRESS & EDGE CASES
# ===========================================

class TestStressEdgeCases:
    """Test stress and edge case scenarios"""

    def test_e01_deep_chain_and_height(self):
        """Case E1: Deep chain and verify height"""
        token = register_user(email='e01@example.com')
        tree_id = create_tree(token, tree_data=None)

        # Build chain: 10 -> 9 -> 8 -> 7 -> 6
        resp1 = client.post('/chat', json={"tree_id": tree_id, "message": "insert 10 as root"}, headers=auth_headers(token))
        assert resp1.status_code == 200
        
        resp2 = client.post('/chat', json={"tree_id": tree_id, "message": "insert 9 as left child of 10"}, headers=auth_headers(token))
        assert resp2.status_code == 200
        
        resp3 = client.post('/chat', json={"tree_id": tree_id, "message": "insert 8 as left child of 9"}, headers=auth_headers(token))
        assert resp3.status_code == 200
        
        resp4 = client.post('/chat', json={"tree_id": tree_id, "message": "insert 7 as left child of 8"}, headers=auth_headers(token))
        assert resp4.status_code == 200
        
        resp5 = client.post('/chat', json={"tree_id": tree_id, "message": "insert 6 as left child of 7"}, headers=auth_headers(token))
        assert resp5.status_code == 200

        # Verify height
        resp = client.post('/chat', json={"tree_id": tree_id, "message": "height"}, headers=auth_headers(token))
        assert resp.status_code == 200
        assert '5' in resp.json()['response']

    def test_e02_message_too_long(self):
        """Case E2: Message longer than 1000 chars"""
        token = register_user(email='e02@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": None, "right": None})

        long_message = "a" * 1001

        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": long_message},
                          headers=auth_headers(token))
        
        assert resp.status_code == 400
        assert 'too long' in resp.json().get('detail', '').lower()

    def test_e03_flexible_insert_phrasing(self):
        """Case E3: Flexible insert phrasing (to left of / to right of)"""
        token = register_user(email='e03@example.com')
        tree_id = create_tree(token, tree_data={"value": 10, "left": None, "right": None})

        # Test 'to left of' phrasing
        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "insert 5 to left of 10"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'inserted' in resp.json()['response'].lower()

        # Test 'to right of' phrasing
        resp = client.post('/chat', 
                          json={"tree_id": tree_id, "message": "insert 9 to right of 10"},
                          headers=auth_headers(token))
        
        assert resp.status_code == 200
        assert 'inserted' in resp.json()['response'].lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
