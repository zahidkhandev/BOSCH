x = ['ab', 'cd']
y = x.copy()
for i in x:
    # print(i.upper())
    y.append(i.upper())

print(y)