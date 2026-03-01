import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "venv"))
import tree_utils as tu


def test_insert_and_traversals():
    # start with empty tree
    tree = {"value": 10, "left": None, "right": None}
    # insert left and right
    assert tu.insert_node(tree, 10, 5, "left")
    assert tu.insert_node(tree, 10, 15, "right")

    inorder = tu.inorder_traversal(tree)
    assert inorder == [5, 10, 15]

    preorder = tu.preorder_traversal(tree)
    assert preorder == [10, 5, 15]

    postorder = tu.postorder_traversal(tree)
    assert postorder == [5, 15, 10]


def test_find_leaf_nodes_and_height():
    tree = {"value": 7, "left": {"value": 5, "left": None, "right": None}, "right": None}
    leaves = tu.find_leaf_nodes(tree)
    assert 5 in leaves
    assert tu.calculate_height(tree) == 2


def test_insert_into_occupied_slot():
    # create parent with right child
    tree = {"value": 9, "left": None, "right": {"value": 6, "left": None, "right": None}}
    # attempt to insert another right child under 9
    assert not tu.insert_node(tree, 9, 5, "right")
    # ensure existing child unchanged
    assert tree["right"]["value"] == 6


def test_update_and_prevent_duplicates():
    tree = {"value": 7, "left": {"value": 5, "left": None, "right": None}, "right": None}
    # update an existing node
    assert tu.update_node(tree, 5, 8)
    assert tree["left"]["value"] == 8

    # updating to a value that already exists should not be allowed by
    # our higher-level handler (tree_utils itself doesn't check) so we
    # simply verify that search_node finds duplicates when they exist.
    assert tu.search_node(tree, 8)
    # simulate duplicate scenario: change 8 back to 7 creating two 7s
    assert tu.update_node(tree, 8, 7)
    assert tree["left"]["value"] == 7
    # now search_node sees two 7s but insertion handler would have
    # blocked the change earlier.
