import sys

l = len(sys.argv)
small = float(sys.argv[1])
large = float(sys.argv[1])

for i in range (1, l):
    if(float(sys.argv[i]) > large):
        large = float(sys.argv[i])
    elif(float(sys.argv[i])< small):
        small = float(sys.argv[i])

print(small)
print(large)