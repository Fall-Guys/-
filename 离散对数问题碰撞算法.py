import tkinter as tk
from tkinter import ttk
import math


def bsgs_with_steps(a, b, p):
    if a % p == 0:
        if b % p == 0:
            return 1, [], []  # 示例，可能需要更严谨的处理
        else:
            raise ValueError("无解")
    m = int(math.ceil(math.sqrt(p)))

    # Baby Steps
    baby_steps = []
    current = 1
    table = {}
    for j in range(m):
        baby_steps.append((j, current))
        table[current] = j
        current = (current * a) % p

    # 计算a^-m mod p
    c = pow(a, m, p)
    c_inv = pow(c, p - 2, p)

    # Giant Steps
    current = b % p
    giant_steps = []
    found = False
    x = None
    for k in range(m):
        j = table.get(current, None)
        if j is not None:
            giant_steps.append({'k': k, 'current': current, 'found': True, 'j': j})
            x = k * m + j
            found = True
            break
        else:
            giant_steps.append({'k': k, 'current': current, 'found': False})
        current = (current * c_inv) % p
    if not found:
        raise ValueError("无解")
    return x, baby_steps, giant_steps


class BSGSApp:
    def __init__(self, master):
        self.master = master
        master.title("Baby-Step Giant-Step ")

        # 公式展示
        formula_frame = ttk.Frame(master, padding="10")
        formula_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        formula_label = ttk.Label(
            formula_frame,
            text="求解离散对数问题：a^x ≡ b (mod p)",
            font=('Arial', 12, 'bold'),
            foreground="blue"
        )
        formula_label.pack()

        input_frame = ttk.Frame(master, padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # a输入行
        a_row = ttk.Frame(input_frame)
        a_row.pack(fill=tk.X, pady=2)
        ttk.Label(a_row, text="a (底数):").pack(side=tk.LEFT)
        self.a_entry = ttk.Entry(a_row, width=15)
        self.a_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(a_row, text="在方程 a^x ≡ b mod p 中的基数", foreground="gray").pack(side=tk.LEFT)

        # b输入行
        b_row = ttk.Frame(input_frame)
        b_row.pack(fill=tk.X, pady=2)
        ttk.Label(b_row, text="b (结果):").pack(side=tk.LEFT)
        self.b_entry = ttk.Entry(b_row, width=15)
        self.b_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(b_row, text="期望达到的模p结果", foreground="gray").pack(side=tk.LEFT)

        # p输入行
        p_row = ttk.Frame(input_frame)
        p_row.pack(fill=tk.X, pady=2)
        ttk.Label(p_row, text="p (模数):").pack(side=tk.LEFT)
        self.p_entry = ttk.Entry(p_row, width=15)
        self.p_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(p_row, text="必须是质数", foreground="red").pack(side=tk.LEFT)

        # 示例按钮
        example_frame = ttk.Frame(input_frame)
        example_frame.pack(pady=5)
        ttk.Button(
            example_frame,
            text="填入示例",
            command=self.fill_example
        ).pack(side=tk.LEFT)
        ttk.Label(
            example_frame,
            text="示例：3^x ≡ 13 mod 17 → x=4",
            foreground="green"
        ).pack(side=tk.LEFT, padx=10)

        # 运行按钮
        self.run_button = ttk.Button(input_frame, text="运行", command=self.run_bsgs)
        self.run_button.pack(pady=5)  # 关键修改点

        # 结果区域
        result_frame = ttk.Frame(master, padding="10")
        result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))  # 注意修改行号从1改为2

        self.result_label = ttk.Label(result_frame, text="结果: ")
        self.result_label.grid(row=0, column=0, sticky=tk.W)

        # Baby Steps显示
        self.baby_steps_text = tk.Text(result_frame, height=10, width=30)
        self.baby_steps_text.grid(row=1, column=0, padx=5, pady=5)

        # Giant Steps显示
        self.giant_steps_text = tk.Text(result_frame, height=10, width=40)
        self.giant_steps_text.grid(row=1, column=1, padx=5, pady=5)

        # 错误信息标签
        self.error_label = ttk.Label(result_frame, text="", foreground="red")
        self.error_label.grid(row=2, column=0, columnspan=2, sticky=tk.W)

    def fill_example(self):
        """填充示例数值"""
        self.a_entry.delete(0, tk.END)
        self.a_entry.insert(0, "3")
        self.b_entry.delete(0, tk.END)
        self.b_entry.insert(0, "13")
        self.p_entry.delete(0, tk.END)
        self.p_entry.insert(0, "17")


    def run_bsgs(self):
        # 清空错误信息
        self.error_label.config(text="")
        self.baby_steps_text.delete('1.0', tk.END)
        self.giant_steps_text.delete('1.0', tk.END)

        # 获取输入
        try:
            a = int(self.a_entry.get())
            b = int(self.b_entry.get())
            p = int(self.p_entry.get())
        except ValueError:
            self.error_label.config(text="请输入有效的整数。")
            return

        # 检查p是否为质数
        if not self.is_prime(p):
            self.error_label.config(text="p必须是质数。")
            return

        # 运行算法
        try:
            x, baby_steps, giant_steps = bsgs_with_steps(a, b, p)
        except ValueError as e:
            self.result_label.config(text=f"结果: {str(e)}")
            return

        # 显示结果
        self.result_label.config(text=f"结果: x = {x}")

        # 显示Baby Steps
        baby_text = "Baby Steps:\nj | a^j mod p\n"
        for j, val in baby_steps:
            baby_text += f"{j} | {val}\n"
        self.baby_steps_text.insert(tk.END, baby_text)

        # 显示Giant Steps
        giant_text = "Giant Steps:\nk | 当前值 | 是否找到\n"
        for step in giant_steps:
            k = step['k']
            current = step['current']
            found = step['found']
            if found:
                j = step['j']
                giant_text += f"{k} | {current} | 是 (j={j})\n"
            else:
                giant_text += f"{k} | {current} | 否\n"
        self.giant_steps_text.insert(tk.END, giant_text)

    def is_prime(self, n):
        if n <= 1:
            return False
        if n <= 3:
            return True
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        w = 2
        while i * i <= n:
            if n % i == 0:
                return False
            i += w
            w = 6 - w
        return True


if __name__ == "__main__":
    root = tk.Tk()
    app = BSGSApp(root)
    root.mainloop()