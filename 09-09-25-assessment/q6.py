class SinglyLinkedListNode:
    def __init__(self, data):
        self.data = data
        self.next = None

def reverse(head):
    last_node = None
    current_node = head
    while current_node is not None:
        next_node = current_node.next
        current_node.next = last_node
        last_node = current_node
        current_node = next_node
    
    return last_node

head = SinglyLinkedListNode(1)
node2 = SinglyLinkedListNode(2)
node3 = SinglyLinkedListNode(3)

head.next = node2
node2.next = node3

def printLinkedList(head):
    current = head
    while current:
        print(current.data, end=" -> ")
        current = current.next
    print("NULL")

print("Original list:")
printLinkedList(head)

reversed_list_head = reverse(head)

print("Reversed list:")
printLinkedList(reversed_list_head)