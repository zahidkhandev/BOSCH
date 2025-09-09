class SinglyLinkedListNode:
    def __init__(self, data):
        self.data = data
        self.next = None

def printLinkedList(head):
    current_node = head
    while current_node:
        print(current_node.data)
        current_node = current_node.next

head = SinglyLinkedListNode("A")
node_b = SinglyLinkedListNode("B")
node_c = SinglyLinkedListNode("C")

head.next = node_b
node_b.next = node_c

print("Printing from head:")
printLinkedList(head)

empty_head = None
print("Printing from empty head:")
printLinkedList(empty_head)
