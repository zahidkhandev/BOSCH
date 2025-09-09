str1 = "{{[[(())]]}}"

str2 = "{{[[(())]]}"

def check_mapping(str):
    stack = []
    mapping = {"}": "{", ")": "(", "]": "["}

    for i in str:
        if i in mapping.values():
            stack.append(i)
        elif i in mapping.keys():
            if not stack or mapping[i] != stack.pop():
                return False
            
    return not stack

print(check_mapping(str1))
print(check_mapping(str2))