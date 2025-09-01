class Node:
  def __init__(self, data):
    self.data = data
    self.next = None
 
def findInList(head, findValue):
#   while head:
    if(head.next is None):
      if head.data == findValue:
        return head.data
      return -1
    
    if head.data == findValue:
      return head.data
    else:
      return findInList(head.next, findValue)
 
node1 = Node(7)
node2 = Node(11)
node3 = Node(3)
node4 = Node(2)
node5 = Node(9)
 
node1.next = node2
node2.next = node3
node3.next = node4
node4.next = node5

userInput = input("Enter no to find: ")
valueExists = findInList(node1,int(userInput))
if valueExists == -1:
  print("Value does not exist")
else:
  print("value eixsts")
 
# print("The largest value in the linked list is:", findLargestValue(node1))