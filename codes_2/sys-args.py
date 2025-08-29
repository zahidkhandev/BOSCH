#  sys.argv is a list that contains command-line arguments passed to a Python script.
 
import sys
tot=0
k=len(sys.argv)
print("Size  =" , k)
print(sys.argv[0])
 
for i in range(1,k):
    tot=tot+ int(sys.argv[i])
 
print("Total  =" , tot)