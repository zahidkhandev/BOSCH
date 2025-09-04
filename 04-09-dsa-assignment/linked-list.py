class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            return
        last_node = self.head
        while last_node.next:
            last_node = last_node.next
        last_node.next = new_node

    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def delete(self, data):
        current_node = self.head

        if current_node and current_node.data == data:
            self.head = current_node.next
            current_node = None  
            return

        prev_node = None
        while current_node and current_node.data != data:
            prev_node = current_node
            current_node = current_node.next

        if current_node is None:
            print(f"Data '{data}' not found in the list.")
            return

        prev_node.next = current_node.next
        current_node = None

    def display(self):
        elements = []
        current_node = self.head
        while current_node:
            elements.append(str(current_node.data))
            current_node = current_node.next
        print(" -> ".join(elements))


linkedList = LinkedList()

linkedList.append("A")
linkedList.append("B")
linkedList.display()
linkedList.prepend("C")
linkedList.display()
linkedList.prepend("D")
linkedList.prepend("E")
linkedList.append("F")
linkedList.display()
linkedList.delete("A")
linkedList.display()
