import sys

l = len(sys.argv)
excluded_list = sys.argv[1:]
normal_list = [int(x) for x in excluded_list]
print(normal_list)
normal_list.sort()
print(normal_list)

print("Second largest: ", normal_list[-2])