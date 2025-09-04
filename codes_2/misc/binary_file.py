f1=open("D7.jpg", "rb")
 
f2=open("doss_dinara.jpg", "wb")
 
data=f1.read()

f2.write(data)

print("New Image is available with the name: doss_dinara.jpg")
 