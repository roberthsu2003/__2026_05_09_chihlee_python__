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

#==============
import csv

with open("考試分數_3年6班.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(row)