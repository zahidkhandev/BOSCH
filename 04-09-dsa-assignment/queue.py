class Node:
    def __init__(self, value):
        self.data = value
        self.next = None


class Queue:
    def __init__(self):
        self.length = 0
        self.first = None
        self.last = None

    def enqueue(self, value):
        new_node = Node(value)

        if(self.last is None):
            self.first = self.last = new_node
            self.length += 1
            return
        
        self.last.next = new_node
        self.last = new_node
        self.length +=1

    def dequeue(self):
        if self.isEmpty():
            return "The queue is empty"
        
        temp = self.first
        self.first = temp.next
        self.length -= 1
        if self.first is None:
            self.rear = None
        return f"Dequeued element {temp.data}"

    def isEmpty(self):
        return self.length == 0
    
    def peek(self):
        if self.isEmpty():
            return "Empty Queue!"

        else:
            return f"Peeked element: {self.first.data}"


    def size(self):
        return self.length
    
queue = Queue()
queue.enqueue("A")
queue.enqueue("B")
queue.enqueue("C")

print(f"Size of queue: {queue.size()}")
print(f"Queue is empty: {queue.isEmpty()}")
print(queue.peek())
print(queue.dequeue())
print(queue.peek())
print(queue.dequeue())
print(queue.peek())
print(queue.dequeue())
print(queue.peek())
print(f"Size of queue: {queue.size()}")
print(f"Queue is empty: {queue.isEmpty()}")
