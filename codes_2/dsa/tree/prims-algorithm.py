
# https://www.geeksforgeeks.org/dsa/prims-minimum-spanning-tree-mst-greedy-algo-5/
# first index of file ->
import heapq

mst = []
usedVertices = set()

with open("PrimsMST_inputs/PrimsMST_input0.txt") as file:
    numVertices = int(file.readline())
    edges = [[] for _ in range(numVertices)]
    for line in file.readlines():
        edge = tuple(map(int, line.split(" ")))
        if edge( )
