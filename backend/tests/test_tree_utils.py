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
