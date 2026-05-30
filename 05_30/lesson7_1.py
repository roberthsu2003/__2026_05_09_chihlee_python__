try:
	with open("student.txt", "r", encoding="utf-8") as file:
			data = file.read()
			print(data)
except Exception as e:
	print("發生錯誤:", e)
