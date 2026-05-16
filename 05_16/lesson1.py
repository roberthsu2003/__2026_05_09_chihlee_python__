import random


def play_guess_number_game() -> None:
	answer = random.randint(1, 100)
	tries = 0

	print("=== 猜數字遊戲 ===")
	print("我想好了一個 1 到 100 的整數，來猜猜看吧！")
	print("輸入 q 可以離開遊戲。")

	while True:
		user_input = input("請輸入你猜的數字: ").strip()

		if user_input.lower() == "q":
			print(f"遊戲結束，答案是 {answer}。")
			break

		if not user_input.isdigit():
			print("請輸入有效的整數，或輸入 q 離開。")
			continue

		guess = int(user_input)
		if guess < 1 or guess > 100:
			print("請輸入 1 到 100 之間的整數。")
			continue

		tries += 1

		if guess < answer:
			print("太小了，再大一點！")
		elif guess > answer:
			print("太大了，再小一點！")
		else:
			print(f"恭喜答對！你總共猜了 {tries} 次。")
			break


if __name__ == "__main__":
	play_guess_number_game()
	print("遊戲結束，謝謝參加！")
