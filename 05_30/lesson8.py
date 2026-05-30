file = open("student.txt","r",encoding="utf-8")
print(type(file))
content = file.read()
print(content)
file.close()
file.closed

#=======================

with open("student.txt","r",encoding="utf-8") as file:
	content = file.read()

print(file.closed)