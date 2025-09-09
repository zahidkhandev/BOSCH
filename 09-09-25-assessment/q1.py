n = int(input("Enter the no of strings: "))

def isBalanced(str):
    bracket_mapping = {"}": "{", ")": "(", "]": "["}
    li = []
    for bracket in str:
        if bracket in bracket_mapping.values():
            li.append(bracket)
        elif bracket in bracket_mapping.keys():
            if not li or bracket_mapping[bracket] != li.pop():
                return "NO"
    
    if not li:
        return "YES"
    else: 
        return "NO"
    

for i in range (n):
    str = input("Enter a bracket string: ")
    output = isBalanced(str)
    print(output)