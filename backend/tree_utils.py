# =========================
# TREE UTILITY FUNCTIONS
# =========================

# maximum absolute value allowed for any node; keeps numbers reasonable and
# avoids users pasting in enormous integers that could break diagrams or
# confuse the agent.  Used both in endpoints and in the agent preprocessor.
MAX_NODE_VALUE = 1_000_000_000

def calculate_height(node):
    if node is None:
        return 0
    return max(calculate_height(node.get("left")),
               calculate_height(node.get("right"))) + 1


def find_leaf_nodes(node):
    if node is None:
        return []

    if node.get("left") is None and node.get("right") is None:
        return [node.get("value")]

    return find_leaf_nodes(node.get("left")) + find_leaf_nodes(node.get("right"))


def count_nodes(node):
    """Return the total number of nodes in the tree."""
    if node is None:
        return 0
    return 1 + count_nodes(node.get("left")) + count_nodes(node.get("right"))


# -------------------------
# SEARCH
# -------------------------

def search_node(node, value):
    if node is None:
        return False

    if node.get("value") == value:
        return True

    return (
        search_node(node.get("left"), value)
        or search_node(node.get("right"), value)
    )


def get_node(node, value):
    if node is None:
        return None

    if node.get("value") == value:
        return node

    left = get_node(node.get("left"), value)
    if left:
        return left

    return get_node(node.get("right"), value)


# -------------------------
# INSERT (STRICT BINARY)
# -------------------------

def insert_node(node, parent_value, new_value, position):

    if node is None:
        raise ValueError("Tree is empty.")

    if position not in ("left", "right"):
        raise ValueError("Invalid direction. Use left or right.")

    if abs(new_value) > MAX_NODE_VALUE:
        raise ValueError(f"Node value {new_value} is too large; must be <= {MAX_NODE_VALUE}.")

    if search_node(node, new_value):
        # duplicate anywhere in tree
        raise ValueError(f"Node with value {new_value} already exists in tree.")

    parent = get_node(node, parent_value)
    if parent is None:
        raise ValueError(f"Parent node {parent_value} not found.")

    if parent.get(position) is not None:
        raise ValueError(
            f"Cannot insert {new_value}: The {position} child of {parent_value} already exists."
        )

    parent[position] = {
        "value": new_value,
        "left": None,
        "right": None,
    }

    return node


# -------------------------
# DELETE (SAFE PROMOTION)
# -------------------------

def delete_node(node, value):
    """
    Safe delete behavior:

    - If leaf → remove
    - If one child → promote that child
    - If two children → remove entire subtree
      (caller should confirm before calling)
    """

    if node is None:
        return None

    if node.get("value") == value:
        left = node.get("left")
        right = node.get("right")

        if left is None and right is None:
            return None

        if left is not None and right is None:
            return left

        if right is not None and left is None:
            return right

        # both children exist
        return None

    node["left"] = delete_node(node.get("left"), value)
    node["right"] = delete_node(node.get("right"), value)

    return node


# -------------------------
# UPDATE
# -------------------------

def update_node(node, old_value, new_value):
    """
    Update a node value.

    Returns:
    - Modified tree
    - False if not found
    """

    if node is None:
        return False

    if abs(new_value) > MAX_NODE_VALUE:
        # signal failure so caller returns a helpful error
        return False

    if search_node(node, new_value) and old_value != new_value:
        return False

    if node.get("value") == old_value:
        node["value"] = new_value
        return node

    left_updated = update_node(node.get("left"), old_value, new_value)
    if left_updated:
        return node

    right_updated = update_node(node.get("right"), old_value, new_value)
    if right_updated:
        return node

    return False


# -------------------------
# TRAVERSALS
# -------------------------

def inorder_traversal(node):
    if node is None:
        return []
    return (
        inorder_traversal(node.get("left"))
        + [node.get("value")]
        + inorder_traversal(node.get("right"))
    )


def preorder_traversal(node):
    if node is None:
        return []
    return (
        [node.get("value")]
        + preorder_traversal(node.get("left"))
        + preorder_traversal(node.get("right"))
    )


def postorder_traversal(node):
    if node is None:
        return []
    return (
        postorder_traversal(node.get("left"))
        + postorder_traversal(node.get("right"))
        + [node.get("value")]
    )