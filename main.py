#!/bin/python3

import math
import os
import random
import re
import sys



#
# Complete the 'findSmallestMissingPositive' function below.
#
# The function is expected to return an INTEGER.
# The function accepts INTEGER_ARRAY orderNumbers as parameter.
#

def findSmallestMissingPositive(orderNumbers):
    # Write your code here
    
    orderNumbers.sort()
    missing = 0
    

    for index, value in enumerate(orderNumbers):
        print(value, index)
        # if i == orderNumbers[i]:
        #     pass
        # else:
        #     # print("missing")
        #     missing = i
        #     break
    
    # print(missing)

    return missing

if __name__ == '__main__':
    # orderNumbers_count = int(input().strip())

    orderNumbers =  [3, 4, -1, 1]

    # for _ in range(orderNumbers_count):
    #     orderNumbers_item = int(input().strip())
    #     orderNumbers.append(orderNumbers_item)

    result = findSmallestMissingPositive(orderNumbers)

    print(result)
