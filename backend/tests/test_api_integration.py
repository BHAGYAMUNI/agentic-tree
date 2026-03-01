import os
os.environ['RUNNING_TESTS'] = '1'

import pytest
from fastapi.testclient import TestClient
from database import Base, engine, SessionLocal
from main import app
from sqlalchemy.orm import Session

client = TestClient(app)


@pytest.fixture(scope='module', autouse=True)
def setup_db():
    # Create tables in in-memory DB
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def register_user(email="test@example.com", password="password"):
    resp = client.post('/auth/register', json={'email': email, 'password': password})
    assert resp.status_code == 200
    data = resp.json()
    token = data.get('access_token')
    return token


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_insert_root_and_prevent_overwrite():
    token = register_user()

    # Create empty tree
    resp = client.post('/trees', json={"name": "t1", "tree_data": None}, headers=auth_headers(token))
    assert resp.status_code == 200
    tree = resp.json()
    tree_id = tree['id']

    # Insert root via REST
    resp = client.post(f'/trees/{tree_id}/insert', json={"parent_value": None, "new_value": 6, "direction": "left"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()['tree_data']['value'] == 6

    # verify that attempting to create another root returns the proper message
    resp = client.post(f'/trees/{tree_id}/insert', json={"parent_value": None, "new_value": 12, "direction": "left"}, headers=auth_headers(token))
    assert resp.status_code == 400
    assert 'root already exists' in resp.json().get('detail', '').lower()

    # Insert right child 9
    resp = client.post(f'/trees/{tree_id}/insert', json={"parent_value": 6, "new_value": 9, "direction": "right"}, headers=auth_headers(token))
    assert resp.status_code == 200

    # Attempt to insert 7 as right child of 6 -> should be rejected
    resp = client.post(f'/trees/{tree_id}/insert', json={"parent_value": 6, "new_value": 7, "direction": "right"}, headers=auth_headers(token))
    assert resp.status_code == 400
    assert 'already exists' in resp.json().get('detail', '').lower()

    # invalid direction should be rejected with clear message
    resp = client.post(f'/trees/{tree_id}/insert', json={"parent_value": 6, "new_value": 8, "direction": "middle"}, headers=auth_headers(token))
    assert resp.status_code == 400
    assert 'invalid direction' in resp.json().get('detail', '').lower()

    # non-existent parent should produce 400 or 404 depending on validation
    resp = client.post(f'/trees/{tree_id}/insert', json={"parent_value": 99, "new_value": 11, "direction": "left"}, headers=auth_headers(token))
    assert resp.status_code == 400 or resp.status_code == 404
    assert 'parent' in resp.json().get('detail', '').lower()

    # inserting a non-numeric value should be handled gracefully
    resp = client.post(f'/trees/{tree_id}/insert', json={"parent_value": 6, "new_value": "foo", "direction": "left"}, headers=auth_headers(token))
    assert resp.status_code == 400
    assert 'number' in resp.json().get('detail', '').lower()


def test_value_limit_rejected():
    token = register_user(email='big@example.com')
    # start with a tree that has a single root
    resp = client.post('/trees', json={"name": "tbig", "tree_data": {"value":1, "left": None, "right": None}}, headers=auth_headers(token))
    assert resp.status_code == 200
    tree_id = resp.json()['id']

    too_large = 10**12  # well above the 1e9 limit

    # manual insert should be rejected with clear message
    resp = client.post(f'/trees/{tree_id}/insert', json={"parent_value": 1, "new_value": too_large, "direction": "left"}, headers=auth_headers(token))
    assert resp.status_code == 400
    assert 'too large' in resp.json().get('detail', '').lower()

    # chat insert should also reject
    resp = client.post('/chat', json={"tree_id": tree_id, "message": f"Insert {too_large} as left child of 1"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert 'too large' in resp.json()['response'].lower()

    # manual update to an excessive value should be blocked
    resp = client.post(f'/trees/{tree_id}/update', json={"old_value": 1, "new_value": too_large}, headers=auth_headers(token))
    assert resp.status_code == 400
    assert 'too large' in resp.json().get('detail', '').lower()

    # chat update likewise
    resp = client.post('/chat', json={"tree_id": tree_id, "message": f"Update 1 to {too_large}"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert 'too large' in resp.json()['response'].lower()


    def test_chat_search_operations():
        token = register_user(email='search@example.com')
        resp = client.post('/trees', json={"name": "tsearch", "tree_data": {"value":1, "left": None, "right": None}}, headers=auth_headers(token))
        tree_id = resp.json()['id']

        # search for existing node should indicate found
        resp = client.post('/chat', json={"tree_id": tree_id, "message": "search 1"}, headers=auth_headers(token))
        assert resp.status_code == 200
        assert 'found' in resp.json()['response'].lower()

        # search for missing node should clearly state not found
        resp = client.post('/chat', json={"tree_id": tree_id, "message": "find 5"}, headers=auth_headers(token))
        assert resp.status_code == 200
        assert 'not found' in resp.json()['response'].lower()

        # non-numeric search returns explanatory message
        resp = client.post('/chat', json={"tree_id": tree_id, "message": "search hello"}, headers=auth_headers(token))
        assert resp.status_code == 200
        assert 'must be a number' in resp.json()['response'].lower()


    def test_chat_reset_operations():
    token = register_user(email='reset@example.com')
    resp = client.post('/trees', json={"name": "treset", "tree_data": {"value":10, "left": {"value":5, "left": None, "right": None}, "right": None}}, headers=auth_headers(token))
    tree_id = resp.json()['id']

    # verify tree has nodes before reset
    get_resp = client.get(f'/trees/{tree_id}', headers=auth_headers(token))
    assert get_resp.json()['tree_data'] is not None

    # various reset phrasings should work
    for phrase in ["reset tree", "clear tree", "delete all", "wipe tree"]:
        resp = client.post('/chat', json={"tree_id": tree_id, "message": phrase}, headers=auth_headers(token))
        assert resp.status_code == 200
        assert 'reset' in resp.json()['response'].lower()
        # verify tree is empty
        get_resp = client.get(f'/trees/{tree_id}', headers=auth_headers(token))
        assert get_resp.json()['tree_data'] is None
        # recreate for next iteration
        client.put(f'/trees/{tree_id}', json={"name": "treset", "tree_data": {"value":10, "left": {"value":5, "left": None, "right": None}, "right": None}}, headers=auth_headers(token))


def test_chat_flexible_insert_phrasing():
    token = register_user(email='flexinsert@example.com')
    resp = client.post('/trees', json={"name": "tflex", "tree_data": {"value":10, "left": None, "right": None}}, headers=auth_headers(token))
    tree_id = resp.json()['id']

    # test 'to left of' phrasing
    resp = client.post('/chat', json={"tree_id": tree_id, "message": "insert 5 to left of 10"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert 'inserted' in resp.json()['response'].lower() or 'left' in resp.json()['response'].lower()

    # verify the node was actually inserted
    get_resp = client.get(f'/trees/{tree_id}', headers=auth_headers(token))
    assert get_resp.json()['tree_data']['left']['value'] == 5

    # test 'to right of' phrasing
    resp = client.post('/chat', json={"tree_id": tree_id, "message": "insert 15 to right of 10"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert 'inserted' in resp.json()['response'].lower() or 'right' in resp.json()['response'].lower()

    get_resp = client.get(f'/trees/{tree_id}', headers=auth_headers(token))
    assert get_resp.json()['tree_data']['right']['value'] == 15

    # ------------------------------------------------------------------
    # also verify traversal/query semantics are flexible
    # ------------------------------------------------------------------
    # inorder should be available as plain 'in order' or 'pre order'
    for phrase, expect in [
        ("in order", "inorder traversal"),
        ("pre order", "preorder traversal"),
        ("postorder", "postorder traversal"),
    ]:
        resp = client.post('/chat', json={"tree_id": tree_id, "message": phrase}, headers=auth_headers(token))
        assert resp.status_code == 200
        assert expect in resp.json()['response'].lower()

    # leaves query with plural/singular variations
    resp = client.post('/chat', json={"tree_id": tree_id, "message": "show leaves"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert 'leaf' in resp.json()['response'].lower()

    # height query variations
    for height_phrase in ["height of tree", "tree height", "how tall is the tree", "how tall tree"]:
        resp = client.post('/chat', json={"tree_id": tree_id, "message": height_phrase}, headers=auth_headers(token))
        assert resp.status_code == 200
        assert 'height' in resp.json()['response'].lower()

    # asking for an explanation about binary trees should not return the
    # current tree info
    resp = client.post('/chat', json={"tree_id": tree_id, "message": "explain about binary tree"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert 'binary tree' in resp.json()['response'].lower()
    assert 'current tree info' not in resp.json()['response'].lower()

        token = register_user(email='rootphrases@example.com')
        # start with an empty tree
        resp = client.post('/trees', json={"name": "troot", "tree_data": None}, headers=auth_headers(token))
        tree_id = resp.json()['id']

        # various root-creation commands should work
        for phrase in [
            "insert root as 11",
            "insert root node 12",
            "create root 13",
            "insert root 14",
        ]:
            resp = client.post('/chat', json={"tree_id": tree_id, "message": phrase}, headers=auth_headers(token))
            assert resp.status_code == 200
            assert 'created root' in resp.json()['response'].lower() or 'inserted' in resp.json()['response'].lower()
            # reset tree for next iteration
            client.post(f'/trees/{tree_id}/reset', headers=auth_headers(token))

        # if root already exists, mention it
        client.post(f'/trees/{tree_id}/insert', json={"parent_value": None, "new_value": 5, "direction": "left"}, headers=auth_headers(token))
        resp = client.post('/chat', json={"tree_id": tree_id, "message": "insert root as 99"}, headers=auth_headers(token))
        assert resp.status_code == 200
        assert 'root already exists' in resp.json()['response'].lower()

def test_duplicate_value_rejected():
    token = register_user(email='dup@example.com')
    resp = client.post('/trees', json={"name": "tdup", "tree_data": {"value":10, "left": {"value":5, "left": None, "right": None}, "right": None}}, headers=auth_headers(token))
    assert resp.status_code == 200
    tree_id = resp.json()['id']

    # try to insert duplicate value 5 anywhere
    resp = client.post(f'/trees/{tree_id}/insert', json={"parent_value": 10, "new_value": 5, "direction": "right"}, headers=auth_headers(token))
    assert resp.status_code == 400
    assert 'already exists' in resp.json().get('detail', '').lower()

    # occupancy error should also carry descriptive text
    resp = client.post(f'/trees/{tree_id}/insert', json={"parent_value": 10, "new_value": 5, "direction": "left"}, headers=auth_headers(token))
    assert resp.status_code == 400
    assert 'left child of 10 already exists' in resp.json().get('detail', '').lower()


def test_update_synonym_edit():
    token = register_user(email='edit@example.com')
    resp = client.post('/trees', json={"name": "tedit", "tree_data": {"value":10, "left": None, "right": None}}, headers=auth_headers(token))
    assert resp.status_code == 200
    tree_id = resp.json()['id']

    # update using the word "edit"
    resp = client.post('/chat', json={"tree_id": tree_id, "message": "edit 10 to 20"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert 'updated' in resp.json()['response'].lower() or 'edit' in resp.json()['response'].lower()

    # verify the value changed
    get_resp = client.get(f'/trees/{tree_id}', headers=auth_headers(token))
    assert get_resp.json()['tree_data']['value'] == 20


def test_general_chat_fallback():
    """Ensure that non-tree questions still elicit a reasonable response."""
    token = register_user(email='general@example.com')
    resp = client.post('/trees', json={"name": "tgeneral", "tree_data": None}, headers=auth_headers(token))
    tree_id = resp.json()['id']

    resp = client.post('/chat', json={"tree_id": tree_id, "message": "How are you?"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()['response']  # should be some string


def test_insert_under_two_children_rejected():
    token = register_user(email='two@example.com')
    # create tree with two children
    resp = client.post('/trees', json={"name": "ttwo", "tree_data": {"value":10, "left": {"value":5, "left": None, "right": None}, "right": {"value":9, "left": None, "right": None}}}, headers=auth_headers(token))
    tree_id = resp.json()['id']

    # ambiguous insert without direction should be rejected (node full)
    resp = client.post('/chat', json={"tree_id": tree_id, "message": "Insert 7 under 10"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert 'already has two children' in resp.json()['response'].lower() or 'already has two children' in resp.json().get('response','').lower()


def test_auto_insert_single_free_slot():
    """If a parent has exactly one empty child position, the agent should
    automatically choose that slot even if direction isn't stated.
    """

    token = register_user(email='autoslot@example.com')
    # create a tree where node 9 has a right child but left is empty
    resp = client.post('/trees', json={"name": "tauto", "tree_data": {"value":9, "left": None, "right": {"value":6, "left": None, "right": None}}}, headers=auth_headers(token))
    tree_id = resp.json()['id']

    # chat request without explicit direction but with parent
    resp = client.post('/chat', json={"tree_id": tree_id, "message": "Insert 5 under 9"}, headers=auth_headers(token))
    assert resp.status_code == 200
    # because only left slot is free, node 5 should be inserted there
    assert 'inserted' in resp.json()['response'].lower() and 'left' in resp.json()['response'].lower()

    # verify the modification persisted
    get_resp = client.get(f'/trees/{tree_id}', headers=auth_headers(token))
    assert get_resp.status_code == 200
    assert get_resp.json()['tree_data']['left']['value'] == 5


def test_insert_under_both_slots_questioned():
    """When both child positions of a parent are empty, the agent should still
    ask the user to clarify left vs right rather than guessing.
    """

    token = register_user(email='ambiguous@example.com')
    # parent node 4 with no children
    resp = client.post('/trees', json={"name": "tambig", "tree_data": {"value":4, "left": None, "right": None}}, headers=auth_headers(token))
    tree_id = resp.json()['id']

    resp = client.post('/chat', json={"tree_id": tree_id, "message": "Insert 7 under 4"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert 'left or right' in resp.json()['response'].lower()


def test_force_llm_preprocessor(monkeypatch):
    """Setting FORCE_LLM_AGENT should bypass the quick preprocessor entirely.
    We patch the agent to prove it was invoked.
    """

    # make sure environment variable is set for this test
    monkeypatch.setenv('FORCE_LLM_AGENT', '1')

    token = register_user(email='forcer@example.com')
    resp = client.post('/trees', json={"name": "tforce", "tree_data": {"value":1, "left": None, "right": None}}, headers=auth_headers(token))
    tree_id = resp.json()['id']

    # patch the ai_handle_message used by /chat to return a recognisable string
    import main as main_module

    def fake_agent(tree, message):
        return ("LLM_CALLED", False, tree)

    monkeypatch.setattr(main_module, 'ai_handle_message', fake_agent)

    # even though 'height' would normally be handled by preprocessor, we
    # expect our fake agent response when force_llm is True
    resp = client.post('/chat', json={"tree_id": tree_id, "message": "What is the height"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()['response'] == 'LLM_CALLED'

    # cleanup env var
    monkeypatch.delenv('FORCE_LLM_AGENT', raising=False)


def test_delete_promote_single_child():
    token = register_user(email='del@example.com')
    # tree where 5 has single child 7
    resp = client.post('/trees', json={"name": "tdel", "tree_data": {"value":10, "left": {"value":5, "left": None, "right": {"value":7, "left": None, "right": None}}, "right": None}}, headers=auth_headers(token))
    tree_id = resp.json()['id']

    # delete 5 without force -> should be allowed and promote 7
    resp = client.post(f'/trees/{tree_id}/delete', json={"value":5}, headers=auth_headers(token))
    assert resp.status_code == 200
    tree = resp.json()
    assert tree['tree_data']['left']['value'] == 7


def test_update_node_and_duplicate_prevention():
    token = register_user(email='upd@example.com')
    # start with simple tree
    resp = client.post('/trees', json={"name": "tupd", "tree_data": {"value":20, "left": {"value":10, "left": None, "right": None}, "right": None}}, headers=auth_headers(token))
    tree_id = resp.json()['id']

    # valid update should succeed
    resp = client.post(f'/trees/{tree_id}/update', json={"old_value": 10, "new_value": 15}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert resp.json()['tree_data']['left']['value'] == 15

    # attempt duplicate update (20 already present) must be rejected
    resp = client.post(f'/trees/{tree_id}/update', json={"old_value": 15, "new_value": 20}, headers=auth_headers(token))
    assert resp.status_code == 400
    assert 'already exists' in resp.json().get('detail', '').lower()

    # non-numeric new value should be handled as a validation error
    resp = client.post(f'/trees/{tree_id}/update', json={"old_value": 15, "new_value": "foo"}, headers=auth_headers(token))
    assert resp.status_code in (400, 422)


def test_attempt_second_child_rejected():
    token = register_user(email='slot@example.com')
    # create tree where 9 already has right child 6
    resp = client.post('/trees', json={"name": "tslot", "tree_data": {"value":9, "left": None, "right": {"value":6, "left": None, "right": None}}}, headers=auth_headers(token))
    tree_id = resp.json()['id']

    # first insert attempt of another right child should be rejected
    resp = client.post(f'/trees/{tree_id}/insert', json={"parent_value": 9, "new_value": 5, "direction": "right"}, headers=auth_headers(token))
    assert resp.status_code == 400
    assert 'right child' in resp.json().get('detail', '').lower()

    # chat attempt should also reject and not modify
    resp = client.post('/chat', json={"tree_id": tree_id, "message": "Insert 5 as right child of 9"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert 'right child' in resp.json()['response'].lower()

    # ambiguous insertion without specifying parent/direction should ask for clarification
    resp = client.post('/chat', json={"tree_id": tree_id, "message": "Insert 11"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert 'specify the parent' in resp.json()['response'].lower()

    # tree_data should remain unchanged (right child of 9 still 6)
    get_resp = client.get(f'/trees/{tree_id}', headers=auth_headers(token))
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data['tree_data']['right']['value'] == 6

    # if both slots are filled, chat without direction should mention both children
    resp = client.post('/chat', json={"tree_id": tree_id, "message": "Insert 7 under 9"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert 'already has two children' in resp.json()['response'].lower()

    # invalid numeric value should return helpful message instead of crashing
    resp = client.post('/chat', json={"tree_id": tree_id, "message": "Insert hello as left child of 9"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert 'must be numbers' in resp.json()['response'].lower()
***

def test_agent_status_endpoint():
    # this endpoint should always be available and indicate we're using
    # the LangGraph-based agent
    resp = client.get('/agent-status')
    assert resp.status_code == 200
    data = resp.json()
    assert data.get('agent') == 'langgraph'


def test_chat_context_switching_and_fresh_fetch():
    token = register_user(email='ctx@example.com')
    # create two trees
    r1 = client.post('/trees', json={"name": "A", "tree_data": {"value":1, "left": None, "right": None}}, headers=auth_headers(token))
    r2 = client.post('/trees', json={"name": "B", "tree_data": {"value":2, "left": None, "right": None}}, headers=auth_headers(token))
    idA = r1.json()['id']
    idB = r2.json()['id']

    # Ask about root of B
    resp = client.post('/chat', json={"tree_id": idB, "message": "What is the root?"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert '2' in resp.json()['response'] or 'root' in resp.json()['response'].lower()

    # modify tree B manually, then ask chat about left child should see updated tree
    client.post(f'/trees/{idB}/insert', json={"parent_value":2, "new_value":5, "direction":"left"}, headers=auth_headers(token))
    resp = client.post('/chat', json={"tree_id": idB, "message": "What is the left child of 2?"}, headers=auth_headers(token))
    assert resp.status_code == 200
    assert '5' in resp.json()['response'] or 'left' in resp.json()['response'].lower()

    # verify chat history endpoint returns messages for B only
    hist = client.get(f'/chat/history/{idB}', headers=auth_headers(token))
    assert hist.status_code == 200
    msgs = hist.json()
    assert any('root' in m['response'].lower() for m in msgs)
    # tree A should have empty history initially
    histA = client.get(f'/chat/history/{idA}', headers=auth_headers(token))
    assert histA.status_code == 200
    assert histA.json() == []

    # clear B history and check
    client.delete(f'/chat/history/{idB}', headers=auth_headers(token))
    hist_after = client.get(f'/chat/history/{idB}', headers=auth_headers(token))
    assert hist_after.json() == []


if __name__ == '__main__':
    pytest.main()
