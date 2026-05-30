# 資料結構
# 程式結構

# list
# 可以修改
scores = [89, 92, 76, 91, 77]
print(scores)
print(scores[0])
print(scores[1])
print(scores[2])
print(scores[3])
print(scores[4])
#print(scores[5])
scores[0] = 100
print(scores)


#====================

#tuple
#tuple建立後,不可以修改內容,read only
# 何時使用,暫時儲存
scores1 = (85, 92, 87, 73, 59)
print(scores1)
print(scores1[0])
print(scores1[1])
print(scores1[2])
print(scores1[3])
print(scores1[4])
#scores1[0] = 100

#==================

# dictionary
students = {
	'chinese':89,
	'english':94,
	'math':65,
	'history':92,
	'discover': 95}
	
print(students)
print(students['chinese'])
print(students['math'])
print(students['discover'])
print(students['english'])
print(students['history'])