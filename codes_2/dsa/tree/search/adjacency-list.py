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
                if self.right is None:
                    self.right = Node(data)
                else: 
                    self.right.insert(data)

root = Node('g')
root.insert("c")
root.insert("b")
root.insert("a")
root.insert("e")
root.insert("d")
root.insert("f")
root.insert("i")
root.insert("h")
root.insert("j")
root.insert("k")

# Contains a dictionary of the children of each node in the tree
# Lets take root node g -> it has children c and i, so the Adjacency list is g : [c,i]

dictionary = {}

def makeList(root):
    if root is None:
        return
    dictionary[root.data] =[]
    makeList(root.left)
    if root.left:
        dictionary[root.data].append(root.left.data)
    if root.right: 
        dictionary[root.data].append(root.right.data)
    makeList(root.right)

    return dictionary

aList = makeList(root)
print(aList)