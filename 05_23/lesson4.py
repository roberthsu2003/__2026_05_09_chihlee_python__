import tkinter as tk
from tkinter import messagebox
import random


class GuessNumberGame:
    def __init__(self, root):
        self.root = root
        self.root.title("猜數字遊戲")
        self.root.geometry("520x420")
        self.root.configure(bg="#f2f6ff")
        self.root.resizable(False, False)

        self.answer = random.randint(1, 100)
        self.count = 0

        # ===== 標題 =====
        title = tk.Label(
            root,
            text="🎯 猜數字遊戲",
            font=("Arial", 28, "bold"),
            bg="#f2f6ff",
            fg="#1f3c88"
        )
        title.pack(pady=(20, 10))

        # ===== 遊戲說明 =====
        instruction = tk.Label(
            root,
            text=(
                "遊戲玩法：\n"
                "電腦會隨機產生 1 ~ 100 的數字\n"
                "請輸入數字並按『開始猜』"
            ),
            font=("Arial", 14),
            bg="#f2f6ff",
            fg="#333333",
            justify="center"
        )
        instruction.pack(pady=10)

        # ===== 輸入區 =====
        input_frame = tk.Frame(root, bg="#f2f6ff")
        input_frame.pack(pady=15)

        self.entry = tk.Entry(
            input_frame,
            font=("Arial", 24),
            width=10,
            justify="center",
            bd=3
        )
        self.entry.grid(row=0, column=0, padx=10)
        self.entry.focus()

        # Enter 鍵送出
        self.entry.bind("<Return>", lambda event: self.check_number())

        self.guess_button = tk.Button(
            input_frame,
            text="開始猜",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            width=10,
            height=1,
            command=self.check_number,
            cursor="hand2"
        )
        self.guess_button.grid(row=0, column=1)

        # ===== 提示訊息 =====
        self.result_label = tk.Label(
            root,
            text="請輸入數字後開始挑戰！",
            font=("Arial", 18, "bold"),
            bg="#f2f6ff",
            fg="#ff6600"
        )
        self.result_label.pack(pady=20)

        # ===== 猜測次數 =====
        self.count_label = tk.Label(
            root,
            text="目前猜測次數：0",
            font=("Arial", 14),
            bg="#f2f6ff",
            fg="#444444"
        )
        self.count_label.pack()

        # ===== 按鈕區 =====
        button_frame = tk.Frame(root, bg="#f2f6ff")
        button_frame.pack(pady=30)

        restart_button = tk.Button(
            button_frame,
            text="重新開始",
            font=("Arial", 14, "bold"),
            bg="#2196F3",
            fg="white",
            width=12,
            command=self.restart_game,
            cursor="hand2"
        )
        restart_button.grid(row=0, column=0, padx=10)

        exit_button = tk.Button(
            button_frame,
            text="離開遊戲",
            font=("Arial", 14, "bold"),
            bg="#f44336",
            fg="white",
            width=12,
            command=root.quit,
            cursor="hand2"
        )
        exit_button.grid(row=0, column=1, padx=10)

    # ===== 猜數字 =====
    def check_number(self):
        user_input = self.entry.get()

        if user_input.strip() == "":
            messagebox.showwarning("提醒", "請先輸入數字！")
            return

        try:
            guess = int(user_input)

            if guess < 1 or guess > 100:
                messagebox.showwarning("範圍錯誤", "請輸入 1 ~ 100 的數字")
                return

            self.count += 1
            self.count_label.config(
                text=f"目前猜測次數：{self.count}"
            )

            if guess > self.answer:
                self.result_label.config(
                    text="📈 太大了，再小一點！",
                    fg="#d35400"
                )

            elif guess < self.answer:
                self.result_label.config(
                    text="📉 太小了，再大一點！",
                    fg="#8e44ad"
                )

            else:
                self.result_label.config(
                    text="🎉 恭喜猜對了！",
                    fg="#27ae60"
                )

                play_again = messagebox.askyesno(
                    "恭喜過關！",
                    f"答案就是 {self.answer}\n"
                    f"你總共猜了 {self.count} 次\n\n"
                    "是否再玩一次？"
                )

                if play_again:
                    self.restart_game()
                else:
                    self.root.quit()

            self.entry.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("輸入錯誤", "請輸入整數數字！")
            self.entry.delete(0, tk.END)

    # ===== 重新開始 =====
    def restart_game(self):
        self.answer = random.randint(1, 100)
        self.count = 0

        self.result_label.config(
            text="新的遊戲開始！請輸入數字",
            fg="#ff6600"
        )

        self.count_label.config(text="目前猜測次數：0")

        self.entry.delete(0, tk.END)
        self.entry.focus()


# ===== 主程式 =====
root = tk.Tk()
app = GuessNumberGame(root)
root.mainloop()