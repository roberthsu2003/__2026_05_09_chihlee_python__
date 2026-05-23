import random

# 產生 1~100 的隨機整數
answer = random.randint(1, 100)
#print(answer)
count = 0

print("=== 猜數字遊戲 ===")
print("請猜一個 1 到 100 的數字")

while True:
    guess = int(input("請輸入數字: "))
    
    count += 1

    if guess > answer:
        print("太大了！")
    elif guess < answer:
        print("太小了！")
    else:
        print(f"恭喜猜對了！答案是 {answer}")
        print(f"你總共猜了 {count} 次")
        break