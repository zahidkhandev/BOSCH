class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class Stack:
    def __init__(self):
        self.head = None
        self.size = 0

    def push(self, value):
        new_node = Node(value)
        if self.head:
            new_node.next = self.head
        self.head = new_node
        self.size += 1

    def pop(self):
        if self.is_empty():
            return "Stack is empty"
        p_node = self.head
        self.head = self.head.next
        self.size -= 1
        return p_node

    def peek(self):
        return self.head.value

    def is_empty(self):
        if self.size == 0:
            return True
        else:
            return False
    
    def size(self):
        return self.size

    def __str__(self):
        print(f"{self.head.value}")

stack = Stack()
stack.push("A")
stack.push("B")
# print(stack)
print(stack.peek())
# print(stack)

stack.push("C")
print(stack.peek())

stack.pop()
print(stack.peek())

print(stack.is_empty())
stack.pop()
stack.pop()

print(stack.is_empty())
