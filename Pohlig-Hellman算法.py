import tkinter as tk
from tkinter import ttk
from math import gcd
from sympy import factorint


class PohligHellmanSolver:
    def __init__(self):
        self.steps = []  # 记录计算步骤
        self.sub_problems = []  # 存储子问题结果

    def extended_gcd(self, a, b):
        """扩展欧几里得算法求逆元"""
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = self.extended_gcd(b % a, a)
            return (g, x - (b // a) * y, y)

    def mod_inverse(self, a, m):
        """计算模逆元"""
        g, x, y = self.extended_gcd(a, m)
        if g != 1:
            return None  # 逆元不存在
        else:
            return x % m

    def solve_subproblem(self, a, b, q, e, p):
        """求解单个q^e子问题"""
        self.steps.append(f"开始处理子问题 q={q}, e={e}")
        x = 0
        gamma = pow(a, (p - 1) // q, p)
        current = 1
        b_j = b

        for j in range(e):
            # 计算alpha
            exponent = (p - 1) // (q ** (j + 1))
            alpha = pow(a, exponent, p)

            # 计算beta
            beta = pow(b_j, exponent, p)

            # 求解离散对数d_j
            d_j = None
            for d in range(q):
                if pow(gamma, d, p) == beta:
                    d_j = d
                    break

            self.steps.append(f"步骤{j + 1}: 计算d_{j} = {d_j}")

            # 更新x
            x += d_j * (q ** j)

            # 更新b_j
            if j < e - 1:
                inv = self.mod_inverse(pow(a, x, p), p)
                b_j = (b_j * inv) % p

        return x % (q ** e)

    def crt(self, residues, moduli):
        """中国剩余定理合并结果"""
        self.steps.append("应用中国剩余定理合并结果")
        N = 1
        for m in moduli:
            N *= m

        result = 0
        for i in range(len(residues)):
            ni = N // moduli[i]
            inv = self.mod_inverse(ni, moduli[i])
            result += residues[i] * ni * inv
            self.steps.append(f"分量{moduli[i]}: {residues[i]} * {ni} * {inv} ≡ {residues[i] * ni * inv} mod {N}")

        return result % N

    def solve(self, a, b, p):
        """主求解函数"""
        self.steps = []
        self.sub_problems = []

        # 计算群的阶n = p-1
        n = p - 1
        self.steps.append(f"步骤1: 计算群的阶n = {p} - 1 = {n}")

        # 因子分解
        factors = factorint(n)
        self.steps.append("步骤2: 因子分解n = " + " * ".join([f"{q}^{e}" for q, e in factors.items()]))

        # 求解每个子问题
        residues = []
        moduli = []
        for q, e in factors.items():
            exp = q ** e
            self.steps.append(f"\n处理因子 {q}^{e}:")

            # 计算子问题
            x_i = self.solve_subproblem(a, b, q, e, p)
            self.sub_problems.append((q, e, x_i))

            residues.append(x_i)
            moduli.append(exp)
            self.steps.append(f"得到同余式: x ≡ {x_i} mod {exp}")

        # 中国剩余定理合并
        self.steps.append("\n步骤3: 合并同余式")
        x = self.crt(residues, moduli)
        return x


class PHGUI:
    def __init__(self, master):
        self.master = master
        master.title("Pohlig-Hellman算法求解器")

        # 输入区域
        input_frame = ttk.Frame(master, padding=10)
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="离散对数问题: a^x ≡ b mod p", font=('Arial', 12, 'bold')).grid(row=0, column=0,
                                                                                                    columnspan=3)

        # 输入项
        ttk.Label(input_frame, text="底数 a:").grid(row=1, column=0, sticky=tk.W)
        self.a_entry = ttk.Entry(input_frame, width=10)
        self.a_entry.grid(row=1, column=1)

        ttk.Label(input_frame, text="结果 b:").grid(row=2, column=0, sticky=tk.W)
        self.b_entry = ttk.Entry(input_frame, width=10)
        self.b_entry.grid(row=2, column=1)

        ttk.Label(input_frame, text="模数 p:").grid(row=3, column=0, sticky=tk.W)
        self.p_entry = ttk.Entry(input_frame, width=10)
        self.p_entry.grid(row=3, column=1)

        # 示例按钮
        example_btn = ttk.Button(input_frame, text="填入示例", command=self.fill_example)
        example_btn.grid(row=4, column=0, columnspan=2, pady=5)

        # 运行按钮
        run_btn = ttk.Button(input_frame, text="求解", command=self.run_solver)
        run_btn.grid(row=5, column=0, columnspan=2, pady=5)

        # 结果显示
        result_frame = ttk.Frame(master, padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)

        # 步骤显示
        self.steps_text = tk.Text(result_frame, height=20, width=70)
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.steps_text.yview)
        self.steps_text.configure(yscrollcommand=scrollbar.set)

        self.steps_text.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # 错误提示
        self.error_label = ttk.Label(result_frame, foreground="red")
        self.error_label.grid(row=1, column=0, sticky=tk.W)

    def fill_example(self):
        """填充示例数值"""
        self.a_entry.delete(0, tk.END)
        self.a_entry.insert(0, "2")
        self.b_entry.delete(0, tk.END)
        self.b_entry.insert(0, "18")
        self.p_entry.delete(0, tk.END)
        self.p_entry.insert(0, "29")

    def run_solver(self):
        """执行求解"""
        self.steps_text.delete(1.0, tk.END)
        self.error_label.config(text="")

        try:
            a = int(self.a_entry.get())
            b = int(self.b_entry.get())
            p = int(self.p_entry.get())

            if not self.is_prime(p):
                raise ValueError("p必须是质数")

            solver = PohligHellmanSolver()
            solution = solver.solve(a, b, p)

            # 显示结果
            self.steps_text.insert(tk.END, "\n".join(solver.steps))
            self.steps_text.insert(tk.END, f"\n\n最终解: x = {solution}")

            # 验证结果
            if pow(a, solution, p) != b % p:
                self.error_label.config(text="警告：计算结果验证失败！")

        except ValueError as e:
            self.error_label.config(text=f"错误: {str(e)}")
        except Exception as e:
            self.error_label.config(text=f"意外错误: {str(e)}")

    def is_prime(self, n):
        """简单质数检查"""
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
    app = PHGUI(root)
    root.mainloop()