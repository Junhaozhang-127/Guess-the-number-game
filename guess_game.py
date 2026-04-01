import random
import tkinter as tk
from tkinter import ttk, messagebox


def generate_secret_number():
    """生成4位随机数字（0可开头，数字可重复），返回字符串形式"""
    secret = ""
    for _ in range(4):
        secret += str(random.randint(0, 9))
    return secret


def check_guess(secret, guess):
    """对比猜测和答案，返回位置+数字都正确的个数"""
    correct_count = 0
    for s, g in zip(secret, guess):
        if s == g:
            correct_count += 1
    return correct_count


class NumberGuessingGameGUI:
    def __init__(self, root):
        # 主窗口配置（增大尺寸，优化布局）
        self.root = root
        self.root.title("🎮 猜四位数字游戏（双模式·记录版）")
        self.root.geometry("700x600")  # 增大窗口
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f8ff")

        # ========== 全局样式配置 ==========
        self.style = ttk.Style(root)
        self.style.theme_use("clam")
        # 标题样式
        self.style.configure("Title.TLabel", font=("微软雅黑", 18, "bold"), foreground="#2c3e50")
        # 子标题样式
        self.style.configure("SubTitle.TLabel", font=("微软雅黑", 14, "bold"), foreground="#2c3e50")
        # 规则样式
        self.style.configure("Rule.TLabel", font=("微软雅黑", 10), foreground="#34495e", justify="left")
        # 卡片样式
        self.style.configure("Card.TFrame", background="#f8f9fa")
        # 按钮样式
        self.style.configure("Accent.TButton", font=("微软雅黑", 10), foreground="#fff", background="#3498db")
        self.style.configure("Secondary.TButton", font=("微软雅黑", 10), foreground="#fff", background="#95a5a6")
        self.style.configure("AI.TButton", font=("微软雅黑", 10), foreground="#fff", background="#e67e22")
        self.style.configure("Switch.TButton", font=("微软雅黑", 10), foreground="#fff", background="#27ae60")
        self.style.configure("Record.TButton", font=("微软雅黑", 9), foreground="#fff", background="#9b59b6")

        # ========== 初始化两个模式的Frame ==========
        # 1. 玩家猜数模式Frame（核心调整：居中布局）
        self.player_frame = ttk.Frame(root, style="Card.TFrame")
        # 2. AI猜数模式Frame（原有布局不变）
        self.ai_guess_frame = ttk.Frame(root, style="Card.TFrame")

        # 初始化两个模式的界面
        self.init_player_frame()
        self.init_ai_guess_frame()

        # 默认显示玩家猜数模式
        self.player_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def init_player_frame(self):
        """初始化「玩家猜数模式」界面【核心修改：整体居中布局】"""
        # 关键：设置列自适应权重，让组件网格整体居中（4列都设为1，平均分配空间）
        for col in range(4):
            self.player_frame.columnconfigure(col, weight=1)
        # 行自适应（可选，让垂直方向也有弹性）
        for row in range(6):
            self.player_frame.rowconfigure(row, weight=1)

        # 标题：居中显示，跨4列
        title_label = ttk.Label(self.player_frame, text="玩家猜数模式", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=4, pady=(20, 10))  # 微调上下间距

        # 规则框：宽度自适应，跨4列，内容居中
        rule_frame = ttk.Frame(self.player_frame, style="Card.TFrame", width=600)  # 固定规则框宽度，更协调
        rule_frame.grid(row=1, column=0, columnspan=4, padx=20, pady=(0, 15))
        rule_frame.grid_propagate(False)  # 固定Frame宽度，不随内容变化
        rule_label = ttk.Label(
            rule_frame,
            text="📋 游戏规则：\n1. 系统随机生成4位数字（0可开头，数字可重复）\n2. 你输入数字后，查看「位置+数字都对」的个数\n3. 猜对（返回4）则胜利",
            style="Rule.TLabel"
        )
        rule_label.pack(padx=20, pady=10)  # 规则框内边距放大，内容更舒展

        # 游戏核心变量（玩家模式，原有不变）
        self.player_secret = generate_secret_number()
        self.player_guess_count = 0
        self.player_ai_guessing = False
        self.player_candidates = self.generate_all_candidates()

        # 输入区域：整体居中，取消sticky强制对齐
        ttk.Label(self.player_frame, text="你的猜测：", font=("微软雅黑", 12)).grid(row=2, column=0, padx=(0, 5), pady=10)
        self.player_guess_entry = ttk.Entry(self.player_frame, font=("微软雅黑", 14), width=10, justify="center")
        self.player_guess_entry.grid(row=2, column=1, padx=5, pady=10)
        vcmd = (self.root.register(self.validate_input), '%P')
        self.player_guess_entry.config(validate="key", validatecommand=vcmd)

        # 按钮组：整体居中，取消sticky，微调间距
        submit_btn = ttk.Button(self.player_frame, text="手动提交", command=self.player_submit_guess, style="Accent.TButton")
        submit_btn.grid(row=2, column=2, padx=5, pady=10)
        ai_btn = ttk.Button(self.player_frame, text="AI自动猜", command=self.player_ai_auto_guess, style="AI.TButton")
        ai_btn.grid(row=2, column=3, padx=(5, 0), pady=10)
        reset_btn = ttk.Button(self.player_frame, text="重置游戏", command=self.player_reset_game, style="Secondary.TButton")
        reset_btn.grid(row=3, column=1, padx=5, pady=10)
        switch_btn = ttk.Button(self.player_frame, text="切换为AI猜数模式", command=self.switch_to_ai_guess_mode, style="Switch.TButton")
        switch_btn.grid(row=3, column=2, padx=5, pady=10)

        # 反馈标签：居中显示，跨4列，换行自适应
        self.player_feedback_label = tk.Label(
            self.player_frame, text="请输入4位数字开始游戏～或点击「AI自动猜」体验高效算法",
            font=("微软雅黑", 12), bg="#f0f8ff", fg="#3498db", wraplength=600
        )
        self.player_feedback_label.grid(row=4, column=0, columnspan=4, pady=10)

        # 计数标签：居中显示，跨4列
        self.player_count_label = tk.Label(
            self.player_frame, text=f"当前猜测次数：{self.player_guess_count}",
            font=("微软雅黑", 10), bg="#f0f8ff", fg="#7f8c8d"
        )
        self.player_count_label.grid(row=5, column=0, columnspan=4, pady=(0, 20))

    def init_ai_guess_frame(self):
        """初始化「AI猜数模式」界面（原有布局不变）"""
        # 标题
        title_label = ttk.Label(self.ai_guess_frame, text="AI猜数模式（玩家反馈版）", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=5, pady=10)

        # 规则框（更新规则）
        rule_frame = ttk.Frame(self.ai_guess_frame, style="Card.TFrame")
        rule_frame.grid(row=1, column=0, columnspan=5, padx=20, pady=5, sticky="ew")
        rule_label = ttk.Label(
            rule_frame,
            text="📋 游戏规则：\n1. AI先猜测一个4位数，你根据自己想的数，反馈「位置+数字都对」的个数（0-4）\n2. AI根据你的反馈缩小范围，继续猜测\n3. 当你反馈4时，AI猜对，游戏结束\n4. 全程记录每一轮的猜测和反馈",
            style="Rule.TLabel"
        )
        rule_label.pack(padx=10, pady=8)

        # AI猜数模式核心变量（重构）
        self.ai_guess_count = 0  # AI猜测次数
        self.ai_guess_candidates = self.generate_all_candidates()  # AI候选池
        self.ai_current_guess = ""  # AI当前猜测数
        self.game_records = []  # 游戏记录列表

        # AI猜测展示区域
        ttk.Label(self.ai_guess_frame, text="AI当前猜测：", style="SubTitle.TLabel").grid(row=2, column=0, padx=10, pady=15, sticky="e")
        self.ai_guess_display = ttk.Label(
            self.ai_guess_frame, text="未开始", font=("微软雅黑", 16, "bold"), foreground="#e67e22"
        )
        self.ai_guess_display.grid(row=2, column=1, padx=5, pady=15)

        # 玩家反馈输入区域
        ttk.Label(self.ai_guess_frame, text="你的反馈（0-4）：", style="SubTitle.TLabel").grid(row=2, column=2, padx=10, pady=15, sticky="e")
        self.feedback_entry = ttk.Entry(self.ai_guess_frame, font=("微软雅黑", 16), width=5, justify="center")
        self.feedback_entry.grid(row=2, column=3, padx=5, pady=15)
        vcmd = (self.root.register(self.validate_feedback), '%P')
        self.feedback_entry.config(validate="key", validatecommand=vcmd)
        self.feedback_entry.config(state="disabled")  # 初始禁用

        # 按钮组（grid布局，分散摆放）
        start_ai_btn = ttk.Button(self.ai_guess_frame, text="开始AI第一轮猜测", command=self.start_ai_first_guess, style="AI.TButton")
        start_ai_btn.grid(row=2, column=4, padx=5, pady=15)
        submit_feedback_btn = ttk.Button(self.ai_guess_frame, text="提交反馈", command=self.submit_feedback, style="Accent.TButton")
        submit_feedback_btn.grid(row=3, column=3, padx=5, pady=10)
        reset_ai_btn = ttk.Button(self.ai_guess_frame, text="重置模式", command=self.reset_ai_guess_mode, style="Secondary.TButton")
        reset_ai_btn.grid(row=3, column=2, padx=5, pady=10)
        switch_back_btn = ttk.Button(self.ai_guess_frame, text="返回玩家猜数模式", command=self.switch_to_player_mode, style="Switch.TButton")
        switch_back_btn.grid(row=3, column=1, padx=5, pady=10)

        # 游戏记录区域（新增）
        ttk.Label(self.ai_guess_frame, text="📜 游戏记录", style="SubTitle.TLabel").grid(row=4, column=0, columnspan=5, padx=20, pady=5, sticky="w")
        self.record_text = tk.Text(self.ai_guess_frame, font=("微软雅黑", 10), width=75, height=10, bg="#f8f9fa", wrap="word")
        self.record_text.grid(row=5, column=0, columnspan=5, padx=20, pady=5)
        self.record_text.config(state="disabled")  # 只读，防止手动修改
        # 清空记录按钮
        clear_record_btn = ttk.Button(self.ai_guess_frame, text="清空记录", command=self.clear_record, style="Record.TButton")
        clear_record_btn.grid(row=6, column=0, columnspan=5, pady=5)

        # 计数标签
        self.ai_guess_count_label = tk.Label(
            self.ai_guess_frame, text=f"AI猜测次数：{self.ai_guess_count}",
            font=("微软雅黑", 10), bg="#f0f8ff", fg="#7f8c8d"
        )
        self.ai_guess_count_label.grid(row=7, column=0, columnspan=5, pady=5)

    # ========== 通用工具函数 ==========
    def generate_all_candidates(self):
        """生成所有4位数字候选池（0000-9999）"""
        candidates = []
        for num in range(10000):
            candidates.append(f"{num:04d}")
        return candidates

    def validate_input(self, new_value):
        """验证4位数字输入"""
        if not new_value:
            return True
        if len(new_value) > 4:
            return False
        return new_value.isdigit()

    def validate_feedback(self, new_value):
        """验证反馈输入（0-4的整数）"""
        if not new_value:
            return True
        if len(new_value) > 1:
            return False
        return new_value.isdigit() and 0 <= int(new_value) <= 4

    def add_record(self, content):
        """添加游戏记录到文本框"""
        self.game_records.append(content)
        self.record_text.config(state="normal")
        self.record_text.insert(tk.END, content + "\n")
        self.record_text.see(tk.END)  # 滚动到最后一行
        self.record_text.config(state="disabled")

    # ========== 模式切换函数 ==========
    def switch_to_ai_guess_mode(self):
        """切换到AI猜数模式"""
        self.player_frame.pack_forget()
        self.ai_guess_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.root.title("🎮 猜四位数字游戏（AI猜数模式·玩家反馈版）")

    def switch_to_player_mode(self):
        """切换回玩家猜数模式"""
        self.ai_guess_frame.pack_forget()
        self.player_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.root.title("🎮 猜四位数字游戏（玩家猜数模式）")

    # ========== 玩家猜数模式逻辑（原有，适配居中布局） ==========
    def player_submit_guess(self, guess=None):
        user_input = guess if guess else self.player_guess_entry.get().strip()
        if len(user_input) != 4:
            self.player_feedback_label.config(text="❌ 输入错误！必须输入4位数字（如0000、1234）", fg="#e74c3c")
            return

        self.player_guess_count += 1
        self.player_count_label.config(text=f"当前猜测次数：{self.player_guess_count}")
        correct = check_guess(self.player_secret, user_input)

        if correct == 4:
            self.player_feedback_label.config(
                text=f"🎉 猜对了！答案：{self.player_secret}\n总共猜测：{self.player_guess_count} 次",
                fg="#27ae60"
            )
            self.player_guess_entry.config(state="disabled")
            self.player_ai_guessing = False
            messagebox.showinfo("游戏胜利", f"答案：{self.player_secret}\n总猜测次数：{self.player_guess_count}")
        else:
            feedback_text = f"✅ 猜测「{user_input}」→ 位置+数字都对的个数：{correct}"
            if self.player_ai_guessing:
                feedback_text += f"\n🔍 AI过滤后剩余候选数：{len(self.player_candidates)}个"
            self.player_feedback_label.config(text=feedback_text, fg="#3498db")

            if self.player_ai_guessing:
                self.filter_candidates(self.player_candidates, user_input, correct)

        if not guess:
            self.player_guess_entry.delete(0, tk.END)

    def filter_candidates(self, candidates, guess, correct_count):
        """过滤候选池"""
        new_candidates = []
        for candidate in candidates:
            if check_guess(guess, candidate) == correct_count:
                new_candidates.append(candidate)
        self.player_candidates = new_candidates

    def player_ai_auto_guess(self):
        if self.player_ai_guessing:
            return
        self.player_ai_guessing = True
        self.player_guess_entry.config(state="disabled")

        def next_guess():
            if not self.player_ai_guessing:
                return
            if len(self.player_candidates) == 0:
                self.player_feedback_label.config(text="⚠️ 候选池为空，猜测失败", fg="#e74c3c")
                self.player_ai_guessing = False
                return
            next_guess_num = self.player_candidates[0]
            self.player_submit_guess(next_guess_num)
            if check_guess(self.player_secret, next_guess_num) != 4:
                self.root.after(500, next_guess)

        next_guess()

    def player_reset_game(self):
        self.player_secret = generate_secret_number()
        self.player_guess_count = 0
        self.player_candidates = self.generate_all_candidates()
        self.player_ai_guessing = False
        self.player_guess_entry.config(state="normal")
        self.player_guess_entry.delete(0, tk.END)
        self.player_feedback_label.config(text="请输入4位数字开始游戏～或点击「AI自动猜」体验高效算法", fg="#3498db")
        self.player_count_label.config(text=f"当前猜测次数：{self.player_guess_count}")

    # ========== AI猜数模式逻辑（重构核心，原有不变） ==========
    def start_ai_first_guess(self):
        """开始AI第一轮猜测"""
        if len(self.ai_guess_candidates) == 0:
            self.add_record("⚠️ 候选池为空，无法开始猜测")
            return
        # 选候选池第一个数作为第一轮猜测
        self.ai_current_guess = self.ai_guess_candidates[0]
        self.ai_guess_count += 1
        self.ai_guess_display.config(text=self.ai_current_guess)
        self.ai_guess_count_label.config(text=f"AI猜测次数：{self.ai_guess_count}")
        # 启用反馈输入框
        self.feedback_entry.config(state="normal")
        self.feedback_entry.delete(0, tk.END)
        # 添加记录
        self.add_record(f"第{self.ai_guess_count}轮：AI猜测 → {self.ai_current_guess}，请你反馈正确个数")

    def submit_feedback(self):
        """玩家提交反馈，AI过滤候选池并继续猜测"""
        feedback = self.feedback_entry.get().strip()
        if not feedback:
            messagebox.showwarning("输入错误", "请输入0-4之间的整数作为反馈！")
            return
        feedback_num = int(feedback)

        # 1. 记录本次反馈
        self.add_record(f"第{self.ai_guess_count}轮：你的反馈 → {feedback_num}")

        # 2. 判断是否猜对
        if feedback_num == 4:
            self.ai_guess_display.config(text="🎉 猜对啦！")
            self.feedback_entry.config(state="disabled")
            self.add_record(f"✅ AI共猜测{self.ai_guess_count}次，成功猜对！")
            messagebox.showinfo("AI猜数成功", f"AI总共猜测{self.ai_guess_count}次，成功猜对你的数字！")
            return

        # 3. 过滤候选池
        new_candidates = []
        for candidate in self.ai_guess_candidates:
            if check_guess(self.ai_current_guess, candidate) == feedback_num:
                new_candidates.append(candidate)
        self.ai_guess_candidates = new_candidates

        # 4. 检查候选池是否为空
        if len(self.ai_guess_candidates) == 0:
            self.ai_guess_display.config(text="⚠️ 候选池空")
            self.feedback_entry.config(state="disabled")
            self.add_record("❌ 候选池为空，大概率是你反馈的个数与实际不符！")
            messagebox.showwarning("猜测失败", "候选池为空，请检查反馈是否正确，或重置模式重新开始！")
            return

        # 5. AI下一轮猜测
        self.ai_current_guess = self.ai_guess_candidates[0]
        self.ai_guess_count += 1
        self.ai_guess_display.config(text=self.ai_current_guess)
        self.ai_guess_count_label.config(text=f"AI猜测次数：{self.ai_guess_count}")
        # 清空反馈输入框
        self.feedback_entry.delete(0, tk.END)
        # 添加下一轮猜测记录
        self.add_record(f"第{self.ai_guess_count}轮：AI猜测 → {self.ai_current_guess}，请你反馈正确个数")

    def reset_ai_guess_mode(self):
        """重置AI猜数模式"""
        self.ai_guess_count = 0
        self.ai_guess_candidates = self.generate_all_candidates()
        self.ai_current_guess = ""
        self.game_records = []
        # 重置界面
        self.ai_guess_display.config(text="未开始")
        self.feedback_entry.config(state="disabled")
        self.ai_guess_count_label.config(text=f"AI猜测次数：{self.ai_guess_count}")
        # 清空记录
        self.clear_record()
        self.add_record("🔄 AI猜数模式已重置，点击「开始AI第一轮猜测」重新开始")

    def clear_record(self):
        """清空游戏记录"""
        self.game_records = []
        self.record_text.config(state="normal")
        self.record_text.delete(1.0, tk.END)
        self.record_text.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = NumberGuessingGameGUI(root)
    root.mainloop()