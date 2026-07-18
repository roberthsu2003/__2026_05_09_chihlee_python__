import csv
import random

surnames = [
    "陳", "林", "黃", "張", "李", "王", "吳", "劉", "蔡", "楊",
    "許", "鄭", "謝", "郭", "洪", "曾", "邱", "廖", "賴", "徐",
    "周", "葉", "蘇", "莊", "呂", "江", "何", "蕭", "羅", "高",
    "潘", "簡", "朱", "鍾", "彭", "游", "詹", "胡", "施", "沈"
]

male_names = [
    "俊傑", "志明", "家豪", "建宏", "承翰", "柏翰", "冠廷", "宗翰",
    "彥廷", "子軒", "浩然", "偉成", "國華", "志豪", "文傑", "明哲",
    "家銘", "彥宏", "裕傑", "威廷", "柏宏", "冠宇", "承恩", "子謙",
    "浩宇", "偉誠", "國棟", "志偉", "文傑", "明軒", "家豪", "彥霖",
    "裕豪", "威霆", "柏融", "冠霖", "承翰", "子睿", "浩銘", "偉軒"
]

female_names = [
    "淑芬", "美玲", "雅婷", "怡君", "雅琪", "欣怡", "佳蓉", "思穎",
    "靜宜", "佳穎", "婉君", "淑惠", "雅慧", "怡萱", "欣蓉", "佳玲",
    "思涵", "靜嫻", "佳樺", "婉婷", "淑娟", "美慧", "雅芬", "怡伶",
    "欣潔", "佳霖", "思瑩", "靜芬", "佳蓉", "婉慧", "淑華", "美惠",
    "雅萍", "怡靜", "欣儒", "佳瑩", "思蓉", "靜儀", "佳玲", "婉茹"
]

random.seed(42)

with open("students.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["編號", "姓名", "性別"])
    for i in range(1, 201):
        surname = random.choice(surnames)
        gender = random.choice(["男", "女"])
        if gender == "男":
            name = surname + random.choice(male_names)
        else:
            name = surname + random.choice(female_names)
        writer.writerow([i, name, gender])

print("已產生 students.csv，共 200 筆資料")
