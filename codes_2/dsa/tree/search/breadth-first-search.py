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

# Also called as level first search
# Order of traversal of search -> gcibehjadfk (From level 0 to levl n)
# Level n is the last row of the tree, level 0 is the level or root, next level is level 1 then 2 then to n

# Algorithm:
# -> It uses a queue and a list of nodes
# -> If you visit a node visit its children in the same manner
# -> Push root to queue, and add it to visit nodes
# -> Itereate the queue and check the next level (childrne of root) and pop the root node form the queue
# -> Itereate next and go to the next node and add their children to the queue and perform the level search again to their children, and pop each one as we search their children
# -> Add every node to the visited nodes list as we progress down and down the next next level.


def breadth_fist_search(root, searchTerm):
    pass

breadth_fist_search(root, 'g')