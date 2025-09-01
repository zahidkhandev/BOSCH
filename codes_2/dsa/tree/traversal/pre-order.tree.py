class Node: 
    def __init__(self, data):
        self.data = data
        self.right = None
        self.left = None
    
    def insert (self, data):
        if self.data == None:
            self.data = data
        else: 
            if data < self.data:
                if self.left is None:
                    self.left = Node(data)
                else:
                    self.left.insert(data)
            else:
                if self.right is None:
                    self.right = Node(data)
                else:
                    self.right.insert(data)


root = Node("g")
root.insert("c")
root.insert("d")
root.insert("z")
root.insert("e")
root.insert("f")
root.insert("h")
root.insert("o")
root.insert("j")
root.insert("k")
root.insert("a")

# Preorder traversal is a tree traversal method that follows the Root-Left-Right order:

#     The root node of the subtree is visited first.
#     Next, the left subtree is recursively traversed.
#     Finally, the right subtree is recursively traversed.

#     Root => Left => Right


# https://www.geeksforgeeks.org/dsa/preorder-traversal-of-binary-tree/

def preOrderPrint(root):

    if root is None:
        return
    
    print(root.data, end=" ")
    preOrderPrint(root.left)
    preOrderPrint(root.right)

preOrderPrint(root)