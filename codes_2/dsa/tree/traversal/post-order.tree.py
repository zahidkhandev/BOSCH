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

# Postorder traversal is a tree traversal method that follows the Left-Right-Root order:

    # The left subtree is visited first.
    # The right subtree is visited next.s
    # The root node is processed last.
    
    # LEFT => RIGHT => ROOT 


# https://www.geeksforgeeks.org/dsa/postorder-traversal-of-binary-tree/

root2 = Node(1)
root2.left = Node(2)
root2.right = Node(3)
root2.left.left = Node(4)
root2.left.right = Node(5)
root2.right.right = Node(6)

# root2.insert(2)
# root2.insert(3)
# root2.insert(4)
# root2.insert(5)
# root2.insert(6)

def postOrderPrint(root):

    if root is None:
        return
    
    postOrderPrint(root.left)
    postOrderPrint(root.right)

    print(root.data, end=" ")

postOrderPrint(root2)