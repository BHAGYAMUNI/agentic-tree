import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "venv"))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register_login_create_tree_and_chat():
    email = f"test{os.getpid()}@example.com"
    password = "TestPass123"

    # Register
    r = client.post('/auth/register', json={"email": email, "password": password})
    assert r.status_code == 200
    tokens = r.json()
    access = tokens.get('access_token')
    assert access

    headers = {"Authorization": f"Bearer {access}"}

    # Create tree
    r = client.post('/trees', json={"name": "ci-tree", "tree_data": None}, headers=headers)
    assert r.status_code == 200
    tree = r.json()
    tree_id = tree['id']

    # Insert root
    r = client.post(f'/trees/{tree_id}/insert', json={"parent_value": None, "new_value": 7, "direction": "left"}, headers=headers)
    assert r.status_code == 200

    # Chat
    r = client.post('/chat', json={"tree_id": tree_id, "message": "What is the height"}, headers=headers)
    assert r.status_code == 200
    resp = r.json()
    assert 'height' in resp.get('response') or 'Height' in resp.get('response') or resp.get('response')
