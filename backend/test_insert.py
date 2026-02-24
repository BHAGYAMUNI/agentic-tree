#!/usr/bin/env python3

from tree_utils import insert_node

# Create the tree from the screenshot
tree = {
    "value": 9,
    "left": {
        "value": 16,
        "left": {
            "value": 1,
            "left": None,
            "right": None
        },
        "right": {
            "value": 2,
            "left": None,
            "right": None
        }
    },
    "right": {
        "value": 13,
        "left": None,
        "right": None
    }
}

print("=== BEFORE INSERT ===")
print(tree)
print()

# Try to insert 20 as left child of 13
result = insert_node(tree, 13, 20, "left")

print("=== AFTER INSERT ===")
print(f"Insert result: {result}")
print(tree)
print()

# Verify the structure is correct
def print_tree(node, depth=0):
    if node is None:
        return
    indent = "  " * depth
    print(f"{indent}Node {node['value']}")
    if node['left']:
        print(f"{indent}  Left:")
        print_tree(node['left'], depth + 2)
    if node['right']:
        print(f"{indent}  Right:")
        print_tree(node['right'], depth + 2)

print("=== TREE STRUCTURE ===")
print_tree(tree)
