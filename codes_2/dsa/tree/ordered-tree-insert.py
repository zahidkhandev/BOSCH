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