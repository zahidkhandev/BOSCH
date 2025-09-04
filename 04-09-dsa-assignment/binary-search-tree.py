class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, value):
        if self.root is None:
            self.root = Node(value)
        else:
            self.insertRecursive(self.root, value)

    def insertRecursive(self, current_node, value):
        if value < current_node.value:
            if current_node.left is None:
                current_node.left = Node(value)
            else:
                self.insertRecursive(current_node.left, value)
        elif value > current_node.value:
            if current_node.right is None:
                current_node.right = Node(value)
            else:
                self.insertRecursive(current_node.right, value)

    def search(self, value):
        return self.searchRecursive(self.root, value)

    def searchRecursive(self, current_node, value):
        if current_node is None or current_node.value == value:
            return current_node is not None
        if value < current_node.value:
            return self.searchRecursive(current_node.left, value)
        else:
            return self.searchRecursive(current_node.right, value)

    def inorder(self):
        result = []
        self.inOrderRecursive(self.root, result)
        return result

    def inOrderRecursive(self, node, result):
        if node:
            self.inOrderRecursive(node.left, result)
            result.append(node.value)
            self.inOrderRecursive(node.right, result)

    def preorder(self):
        result = []
        self.preOrderRecursive(self.root, result)
        return result

    def preOrderRecursive(self, node, result):
        if node:
            result.append(node.value)
            self.preOrderRecursive(node.left, result)
            self.preOrderRecursive(node.right, result)

    def postorder(self):
        result = []
        self.postOrderRecursive(self.root, result)
        return result

    def postOrderRecursive(self, node, result):
        if node:
            self.postOrderRecursive(node.left, result)
            self.postOrderRecursive(node.right, result)
            result.append(node.value)

bst = BST()
elements = [50, 30, 70, 20, 40, 60, 80]
for el in elements:
    bst.insert(el)

print("Inorder traversal (should be sorted):", bst.inorder())
print("Preorder traversal:", bst.preorder())
print("Postorder traversal:", bst.postorder())
print("Searching for 40:", bst.search(40))
print("Searching for 99:", bst.search(99))