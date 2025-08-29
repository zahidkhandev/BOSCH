import sys

l = len(sys.argv)
small = 0
large = 0

for i in range (1, l):
    if(float(sys.argv[i]) > large):
        large = float(sys.argv[i])
    else:
        small = float(sys.argv[i])

print(small)
print(large)