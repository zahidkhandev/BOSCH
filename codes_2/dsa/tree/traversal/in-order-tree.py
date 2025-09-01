# class Node:
#     def __init__(self, key):
#         self.key = key
#         self.left = None
#         self.right = None
 
# def inorder(root):
#     if root:
#         inorder(root.left)         # 1. Traverse left
#         print(root.key, end=" ")   # 2. Visit root
#         inorder(root.right)        # 3. Traverse right
 
# # Example Tree
# root = Node(1)
# root.left = Node(2)
# root.right = Node(3)
# root.left.left = Node(4)
# root.left.right = Node(5)
# root.right.left = Node(6)
 
# print("Inorder Traversal:")
# inorder(root)
# # print(root)


class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
 
    def insert(self, data):
        if self.data is None:
            self.data = data
        else: 
            if data < self.data:
                if self.left is None:
                    self.left = Node(data)
                else:
                   self.left.insert(data)
            else:
                if data > self.data:
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

# Inorder traversal is a depth-first traversal method that follows this sequence:

#     Left subtree is visited first.
#     Root node is processed next.
#     Right subtree is visited last.
#     LEFT => ROOT => RIGHT

# https://www.geeksforgeeks.org/dsa/inorder-traversal-of-binary-tree/


def inOrderPrint(root):
    if(root is None): 
        return
    inOrderPrint(root.left)
    print(root.data)
    inOrderPrint(root.right)

inOrderPrint(root)