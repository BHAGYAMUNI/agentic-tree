def calculate_height(node):
    if node is None:
        return 0

    left_height = calculate_height(node.get("left"))
    right_height = calculate_height(node.get("right"))

    return max(left_height, right_height) + 1


def find_leaf_nodes(node, leaves=None):
    if leaves is None:
        leaves = []

    if node is None:
        return leaves

    if node.get("left") is None and node.get("right") is None:
        leaves.append(node.get("value"))

    find_leaf_nodes(node.get("left"), leaves)
    find_leaf_nodes(node.get("right"), leaves)

    return leaves

def insert_node(node, parent_value, new_value, position):
    if node is None:
        return False

    if node.get("value") == parent_value:
        if position == "left":
            node["left"] = {"value": new_value, "left": None, "right": None}
        elif position == "right":
            node["right"] = {"value": new_value, "left": None, "right": None}
        return True

    return (
        insert_node(node.get("left"), parent_value, new_value, position)
        or insert_node(node.get("right"), parent_value, new_value, position)
    )

def delete_node(node, value):
    if node is None:
        return None

    if node.get("value") == value:
        return None

    node["left"] = delete_node(node.get("left"), value)
    node["right"] = delete_node(node.get("right"), value)

    return node

def update_node(node, old_value, new_value):
    """
    Update a node's value in the tree.
    Returns the modified tree if updated, False if node not found.
    """
    if node is None:
        return node

    if node.get("value") == old_value:
        node["value"] = new_value
        return node

    # Try to find and update in left subtree
    if update_node(node.get("left"), old_value, new_value):
        return node
    
    # Try to find and update in right subtree
    if update_node(node.get("right"), old_value, new_value):
        return node
    
    return False

def inorder_traversal(node, result=None):
    if result is None:
        result = []

    if node:
        inorder_traversal(node.get("left"), result)
        result.append(node.get("value"))
        inorder_traversal(node.get("right"), result)

    return result


def preorder_traversal(node, result=None):
    if result is None:
        result = []

    if node:
        result.append(node.get("value"))
        preorder_traversal(node.get("left"), result)
        preorder_traversal(node.get("right"), result)

    return result


def postorder_traversal(node, result=None):
    if result is None:
        result = []

    if node:
        postorder_traversal(node.get("left"), result)
        postorder_traversal(node.get("right"), result)
        result.append(node.get("value"))

    return result


def search_node(node, value):
    """
    Search for a node with the given value in the tree.
    Returns True if found, False otherwise.
    """
    if node is None:
        return False

    if node.get("value") == value:
        return True

    return search_node(node.get("left"), value) or search_node(node.get("right"), value)