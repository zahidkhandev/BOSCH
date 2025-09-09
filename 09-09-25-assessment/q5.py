class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

root = Node(1)
root.left = Node(2)
root.right = Node(3)
root.left.right = Node(4)
root.left.left = Node(5)
root.right.right = Node(6)
root.right.left = Node(7)
# root.right.right.right = Node(8)
# root.right.right.left = Node(9)
# root.right.right.left.right = Node(10)
# root.right.right.left.left = Node(11)

def getHeight(root):
    if root is None:
        return 0
    queue = [root]
    height = 0
    while len(queue) > 0:
        level = len(queue)
        for i in range(level):
            current_node = queue.pop(0)
            if current_node.left:
                queue.append(current_node.left)
            if current_node.right:
                queue.append(current_node.right)
        height += 1
    return height


def preOrder(root):
    if root is None:
        return
    print(root.data, end=" ")
    preOrder(root.left)
    preOrder(root.right)

print("\nPre order print of the binary tree: ", end="")
preOrder(root)
print("\n")


print("Height of the binary tree: ", getHeight(root) ,end="\n\n")