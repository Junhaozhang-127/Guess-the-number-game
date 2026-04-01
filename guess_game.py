import random
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List


WINDOW_WIDTH = 820
WINDOW_HEIGHT = 700
AUTO_GUESS_DELAY_MS = 500


def generate_secret_number() -> str:
    """生成一个4位随机数字字符串，允许0开头，允许重复。"""
    return "".join(str(random.randint(0, 9)) for _ in range(4))


def check_guess(secret: str, guess: str) -> int:
    """
    只统计“位置和数字都正确”的个数。
    例如：
    secret = '1234', guess = '1299' -> 返回 2
    """
    return sum(1 for s, g in zip(secret, guess) if s == g)


def generate_all_candidates() -> List[str]:
    """生成所有4位数字候选：0000 ~ 9999。"""
    return ["{0:04d}".format(num) for num in range(10000)]


def filter_candidates(candidates: List[str], guess: str, correct_count: int) -> List[str]:
    """
    根据某次猜测结果过滤候选池。
    保留所有满足：与 guess 对比时，正确位数等于 correct_count 的候选。
    """
    return [candidate for candidate in candidates if check_guess(candidate, guess) == correct_count]


class NumberGuessingGameGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("猜四位数字游戏")
        self.root.geometry("{0}x{1}".format(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.root.resizable(False, False)
        self.root.configure(bg="#e9eef5")

        self._setup_style()

        # 玩家猜数模式状态
        self.player_secret = generate_secret_number()
        self.player_guess_count = 0
        self.player_ai_running = False
        self.player_candidates = generate_all_candidates()

        # AI猜数模式状态
        self.ai_guess_count = 0
        self.ai_candidates = generate_all_candidates()
        self.ai_current_guess = ""
        self.ai_records = []

        # 页面
        self.player_frame = ttk.Frame(self.root, style="Card.TFrame")
        self.ai_frame = ttk.Frame(self.root, style="Card.TFrame")

        self._build_player_frame()
        self._build_ai_frame()

        self.show_player_mode()

    def _setup_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure("Card.TFrame", background="#f7f9fc")
        style.configure(
            "Title.TLabel",
            font=("Microsoft YaHei", 20, "bold"),
            foreground="#1f2d3d",
            background="#f7f9fc",
        )
        style.configure(
            "SubTitle.TLabel",
            font=("Microsoft YaHei", 12, "bold"),
            foreground="#26384a",
            background="#f7f9fc",
        )
        style.configure(
            "Rule.TLabel",
            font=("Microsoft YaHei", 10),
            foreground="#41566d",
            background="#f7f9fc",
            justify="left",
        )

        style.configure("Accent.TButton", font=("Microsoft YaHei", 10, "bold"), padding=(12, 7))
        style.configure("Secondary.TButton", font=("Microsoft YaHei", 10), padding=(12, 7))
        style.configure("AI.TButton", font=("Microsoft YaHei", 10, "bold"), padding=(12, 7))
        style.configure("Switch.TButton", font=("Microsoft YaHei", 10), padding=(12, 7))
        style.configure("Record.TButton", font=("Microsoft YaHei", 9), padding=(10, 6))

        style.configure("Accent.TButton", foreground="#ffffff", background="#2d7ff9")
        style.map("Accent.TButton", background=[("active", "#1f6fe2"), ("pressed", "#195ec2")])
        style.configure("AI.TButton", foreground="#ffffff", background="#169d87")
        style.map("AI.TButton", background=[("active", "#128b78"), ("pressed", "#0f7768")])
        style.configure("Secondary.TButton", foreground="#1f2d3d", background="#e4ebf5")
        style.map("Secondary.TButton", background=[("active", "#d7e1ef"), ("pressed", "#c9d7ea")])
        style.configure("Switch.TButton", foreground="#1f2d3d", background="#eaf0f8")
        style.map("Switch.TButton", background=[("active", "#dde7f4"), ("pressed", "#d1dded")])
        style.configure("Record.TButton", foreground="#2f4154", background="#ecf1f8")
        style.map("Record.TButton", background=[("active", "#dfe7f3"), ("pressed", "#d5deed")])

    def _build_player_frame(self) -> None:
        for col in range(4):
            self.player_frame.columnconfigure(col, weight=1)

        title = ttk.Label(self.player_frame, text="玩家猜数模式", style="Title.TLabel")
        title.grid(row=0, column=0, columnspan=4, pady=(24, 12))

        rule_text = (
            "游戏规则：\n"
            "1. 系统随机生成一个4位数字（允许0开头，允许重复）\n"
            "2. 你每次输入4位数字后，系统返回“位置和数字都正确”的个数\n"
            "3. 返回4表示完全猜中"
        )
        rule_frame = ttk.Frame(self.player_frame, style="Card.TFrame")
        rule_frame.grid(row=1, column=0, columnspan=4, padx=28, pady=(0, 18), sticky="ew")

        ttk.Label(rule_frame, text=rule_text, style="Rule.TLabel").pack(padx=20, pady=14)

        ttk.Label(self.player_frame, text="你的猜测：", style="SubTitle.TLabel").grid(
            row=2, column=0, padx=5, pady=10
        )

        vcmd_guess = (self.root.register(self._validate_guess_input), "%P")
        self.player_guess_entry = ttk.Entry(
            self.player_frame,
            font=("Microsoft YaHei", 15),
            width=14,
            justify="center",
            validate="key",
            validatecommand=vcmd_guess,
        )
        self.player_guess_entry.grid(row=2, column=1, padx=8, pady=12, ipady=3)

        ttk.Button(
            self.player_frame,
            text="手动提交",
            command=self.player_submit_guess,
            style="Accent.TButton",
        ).grid(row=2, column=2, padx=8, pady=12)

        ttk.Button(
            self.player_frame,
            text="AI自动猜",
            command=self.player_ai_auto_guess,
            style="AI.TButton",
        ).grid(row=2, column=3, padx=8, pady=12)

        ttk.Button(
            self.player_frame,
            text="重置游戏",
            command=self.player_reset_game,
            style="Secondary.TButton",
        ).grid(row=3, column=1, padx=8, pady=10)

        ttk.Button(
            self.player_frame,
            text="切换到AI猜数模式",
            command=self.show_ai_mode,
            style="Switch.TButton",
        ).grid(row=3, column=2, padx=8, pady=10)

        self.player_feedback_label = tk.Label(
            self.player_frame,
            text="请输入4位数字开始游戏，或点击“AI自动猜”查看自动推理过程。",
            font=("Microsoft YaHei", 12),
            bg="#e9eef5",
            fg="#2d6ea3",
            wraplength=720,
            justify="center",
        )
        self.player_feedback_label.grid(row=4, column=0, columnspan=4, padx=20, pady=14)

        self.player_count_label = tk.Label(
            self.player_frame,
            text="当前猜测次数：0",
            font=("Microsoft YaHei", 10),
            bg="#e9eef5",
            fg="#627283",
        )
        self.player_count_label.grid(row=5, column=0, columnspan=4, pady=(0, 24))

    def _build_ai_frame(self) -> None:
        for col in range(5):
            self.ai_frame.columnconfigure(col, weight=1)

        title = ttk.Label(self.ai_frame, text="AI猜数模式（玩家反馈版）", style="Title.TLabel")
        title.grid(row=0, column=0, columnspan=5, pady=(24, 12))

        rule_text = (
            "游戏规则：\n"
            "1. 请你先在心里想一个4位数字（允许0开头，允许重复）\n"
            "2. AI每轮会猜一个数\n"
            "3. 你只需要反馈“位置和数字都正确”的个数（0~4）\n"
            "4. 当你反馈4时，表示AI猜中了"
        )
        rule_frame = ttk.Frame(self.ai_frame, style="Card.TFrame")
        rule_frame.grid(row=1, column=0, columnspan=5, padx=28, pady=(0, 18), sticky="ew")
        ttk.Label(rule_frame, text=rule_text, style="Rule.TLabel").pack(padx=20, pady=14)

        ttk.Label(self.ai_frame, text="AI当前猜测：", style="SubTitle.TLabel").grid(
            row=2, column=0, padx=5, pady=10, sticky="e"
        )
        self.ai_guess_display = ttk.Label(
            self.ai_frame,
            text="未开始",
            font=("Microsoft YaHei", 18, "bold"),
            foreground="#c66a16",
        )
        self.ai_guess_display.grid(row=2, column=1, padx=8, pady=12, sticky="w")

        ttk.Label(self.ai_frame, text="你的反馈（0~4）：", style="SubTitle.TLabel").grid(
            row=2, column=2, padx=5, pady=10, sticky="e"
        )

        vcmd_feedback = (self.root.register(self._validate_feedback_input), "%P")
        self.feedback_entry = ttk.Entry(
            self.ai_frame,
            font=("Microsoft YaHei", 14),
            width=8,
            justify="center",
            validate="key",
            validatecommand=vcmd_feedback,
            state="disabled",
        )
        self.feedback_entry.grid(row=2, column=3, padx=8, pady=12, sticky="w", ipady=2)

        ttk.Button(
            self.ai_frame,
            text="开始AI猜测",
            command=self.start_ai_first_guess,
            style="AI.TButton",
        ).grid(row=2, column=4, padx=8, pady=12)

        ttk.Button(
            self.ai_frame,
            text="提交反馈",
            command=self.submit_feedback,
            style="Accent.TButton",
        ).grid(row=3, column=3, padx=8, pady=10)

        ttk.Button(
            self.ai_frame,
            text="重置模式",
            command=self.reset_ai_guess_mode,
            style="Secondary.TButton",
        ).grid(row=3, column=2, padx=8, pady=10)

        ttk.Button(
            self.ai_frame,
            text="返回玩家猜数模式",
            command=self.show_player_mode,
            style="Switch.TButton",
        ).grid(row=3, column=1, padx=8, pady=10)

        ttk.Label(self.ai_frame, text="游戏记录", style="SubTitle.TLabel").grid(
            row=4, column=0, columnspan=5, padx=20, pady=(10, 5), sticky="w"
        )

        self.record_text = tk.Text(
            self.ai_frame,
            width=84,
            height=15,
            font=("Consolas", 10),
            bg="#f3f7fd",
            fg="#243647",
            bd=0,
            highlightthickness=1,
            highlightbackground="#d8e2ef",
            highlightcolor="#9fb4cc",
            wrap="word",
        )
        self.record_text.grid(row=5, column=0, columnspan=5, padx=24, pady=6)
        self.record_text.config(state="disabled")

        ttk.Button(
            self.ai_frame,
            text="清空记录",
            command=self.clear_record,
            style="Record.TButton",
        ).grid(row=6, column=0, columnspan=5, pady=10)

        self.ai_guess_count_label = tk.Label(
            self.ai_frame,
            text="AI猜测次数：0",
            font=("Microsoft YaHei", 10),
            bg="#e9eef5",
            fg="#627283",
        )
        self.ai_guess_count_label.grid(row=7, column=0, columnspan=5, pady=(0, 24))

    @staticmethod
    def _validate_guess_input(new_value: str) -> bool:
        if new_value == "":
            return True
        return len(new_value) <= 4 and new_value.isdigit()

    @staticmethod
    def _validate_feedback_input(new_value: str) -> bool:
        if new_value == "":
            return True
        return len(new_value) == 1 and new_value.isdigit() and 0 <= int(new_value) <= 4

    def show_player_mode(self) -> None:
        self.ai_frame.pack_forget()
        self.player_frame.pack(fill="both", expand=True, padx=14, pady=14)
        self.root.title("猜四位数字游戏 - 玩家猜数模式")

    def show_ai_mode(self) -> None:
        self.player_frame.pack_forget()
        self.ai_frame.pack(fill="both", expand=True, padx=14, pady=14)
        self.root.title("猜四位数字游戏 - AI猜数模式")

    def player_submit_guess(self, guess=None) -> None:
        user_guess = guess if guess is not None else self.player_guess_entry.get().strip()

        if len(user_guess) != 4 or not user_guess.isdigit():
            self.player_feedback_label.config(
                text="输入错误：必须输入4位数字，例如 0000、1234。",
                fg="#e74c3c",
            )
            return

        self.player_guess_count += 1
        self.player_count_label.config(text="当前猜测次数：{0}".format(self.player_guess_count))

        correct = check_guess(self.player_secret, user_guess)

        if correct == 4:
            self.player_feedback_label.config(
                text="恭喜，你猜对了！答案是 {0}\n总猜测次数：{1}".format(
                    self.player_secret, self.player_guess_count
                ),
                fg="#27ae60",
            )
            self.player_guess_entry.config(state="disabled")
            self.player_ai_running = False
            messagebox.showinfo(
                "游戏胜利",
                "答案：{0}\n总猜测次数：{1}".format(self.player_secret, self.player_guess_count),
            )
            return

        feedback_text = "你猜的是 {0}，位置和数字都正确的个数：{1}".format(user_guess, correct)

        if self.player_ai_running:
            self.player_candidates = filter_candidates(self.player_candidates, user_guess, correct)
            feedback_text += "\nAI过滤后剩余候选数：{0}".format(len(self.player_candidates))

        self.player_feedback_label.config(text=feedback_text, fg="#3498db")

        if guess is None:
            self.player_guess_entry.delete(0, tk.END)

    def player_ai_auto_guess(self) -> None:
        if self.player_ai_running:
            return

        self.player_ai_running = True
        self.player_guess_entry.config(state="disabled")

        def next_guess():
            if not self.player_ai_running:
                return

            if not self.player_candidates:
                self.player_feedback_label.config(text="候选池为空，自动猜测失败。", fg="#e74c3c")
                self.player_ai_running = False
                return

            current_guess = self.player_candidates[0]
            self.player_submit_guess(current_guess)

            if check_guess(self.player_secret, current_guess) != 4:
                self.root.after(AUTO_GUESS_DELAY_MS, next_guess)

        next_guess()

    def player_reset_game(self) -> None:
        self.player_secret = generate_secret_number()
        self.player_guess_count = 0
        self.player_ai_running = False
        self.player_candidates = generate_all_candidates()

        self.player_guess_entry.config(state="normal")
        self.player_guess_entry.delete(0, tk.END)

        self.player_feedback_label.config(
            text="游戏已重置。请输入4位数字开始游戏，或点击“AI自动猜”。",
            fg="#3498db",
        )
        self.player_count_label.config(text="当前猜测次数：0")

    def start_ai_first_guess(self) -> None:
        if not self.ai_candidates:
            self._add_record("候选池为空，无法开始。")
            return

        self.ai_guess_count = 1
        self.ai_current_guess = self.ai_candidates[0]
        self.ai_guess_display.config(text=self.ai_current_guess)
        self.ai_guess_count_label.config(text="AI猜测次数：{0}".format(self.ai_guess_count))

        self.feedback_entry.config(state="normal")
        self.feedback_entry.delete(0, tk.END)

        self._add_record("第1轮：AI猜测 {0}，请反馈正确个数（0~4）。".format(self.ai_current_guess))

    def submit_feedback(self) -> None:
        feedback = self.feedback_entry.get().strip()
        if feedback == "":
            messagebox.showwarning("输入错误", "请输入 0~4 之间的整数。")
            return

        if not feedback.isdigit() or not 0 <= int(feedback) <= 4:
            messagebox.showwarning("输入错误", "请输入 0~4 之间的整数。")
            self.feedback_entry.delete(0, tk.END)
            return

        feedback_num = int(feedback)

        if self.ai_current_guess == "":
            messagebox.showwarning("操作错误", "请先点击“开始AI猜测”。")
            return

        self._add_record("你的反馈：{0}".format(feedback_num))

        if feedback_num == 4:
            self._add_record("AI猜中啦！答案就是 {0}".format(self.ai_current_guess))
            messagebox.showinfo(
                "AI猜中",
                "AI用 {0} 次猜中了：{1}".format(self.ai_guess_count, self.ai_current_guess),
            )
            self.feedback_entry.delete(0, tk.END)
            self.feedback_entry.config(state="disabled")
            return

        self.ai_candidates = filter_candidates(self.ai_candidates, self.ai_current_guess, feedback_num)

        if self.ai_current_guess in self.ai_candidates:
            self.ai_candidates.remove(self.ai_current_guess)

        if not self.ai_candidates:
            self._add_record("候选池已为空。你的反馈可能前后矛盾，请重置后重试。")
            messagebox.showwarning("无解", "候选池为空，你前面的反馈可能不一致。")
            self.feedback_entry.delete(0, tk.END)
            return

        self.ai_guess_count += 1
        self.ai_current_guess = self.ai_candidates[0]
        self.ai_guess_display.config(text=self.ai_current_guess)
        self.ai_guess_count_label.config(text="AI猜测次数：{0}".format(self.ai_guess_count))

        self._add_record(
            "第{0}轮：AI新猜测 {1}，当前剩余候选数：{2}".format(
                self.ai_guess_count, self.ai_current_guess, len(self.ai_candidates)
            )
        )

        self.feedback_entry.delete(0, tk.END)

    def reset_ai_guess_mode(self) -> None:
        self.ai_guess_count = 0
        self.ai_candidates = generate_all_candidates()
        self.ai_current_guess = ""
        self.ai_records = []

        self.ai_guess_display.config(text="未开始")
        self.ai_guess_count_label.config(text="AI猜测次数：0")
        self.feedback_entry.config(state="disabled")
        self.feedback_entry.delete(0, tk.END)

        self.record_text.config(state="normal")
        self.record_text.delete("1.0", tk.END)
        self.record_text.config(state="disabled")

    def clear_record(self) -> None:
        self.ai_records = []
        self.record_text.config(state="normal")
        self.record_text.delete("1.0", tk.END)
        self.record_text.config(state="disabled")

    def _add_record(self, content: str) -> None:
        self.ai_records.append(content)
        self.record_text.config(state="normal")
        self.record_text.insert(tk.END, content + "\n")
        self.record_text.see(tk.END)
        self.record_text.config(state="disabled")


def main() -> None:
    root = tk.Tk()
    NumberGuessingGameGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
