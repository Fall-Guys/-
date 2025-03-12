import numpy as np
import tkinter as tk
from tkinter import messagebox, scrolledtext #tkinter 的子模块，分别用于显示消息框和滚动文本框
import time


class LLLGUI:
    def __init__(self, master):
        self.master = master
        master.title("LLL格基约简计算器")
        master.geometry("1000x700")
        self.swap_count = 0  # 新增交换次数计数器
        self.input_entries = []  # 用于存储输入框
        self.create_widgets()

    def create_widgets(self):
        # 维数输入区域
        dim_frame = tk.LabelFrame(self.master, text="输入方阵维数")
        dim_frame.pack(pady=10, padx=10, fill=tk.X)
        self.dim_entry = tk.Entry(dim_frame)
        self.dim_entry.pack(side=tk.LEFT, padx=5)
        self.generate_btn = tk.Button(dim_frame, text="生成矩阵", command=self.generate_matrix)
        self.generate_btn.pack(side=tk.LEFT, padx=5)

        # 输入区域
        self.input_frame = tk.LabelFrame(self.master, text="输入矩阵")
        self.input_frame.pack(pady=10, padx=10, fill=tk.X)

        # 按钮区域
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=5)
        self.calc_btn = tk.Button(button_frame, text="开始计算", command=self.start_calculation)
        self.calc_btn.pack(side=tk.LEFT, padx=5)
        self.clear_btn = tk.Button(button_frame, text="清空输入", command=self.clear_input)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # 输出区域
        output_frame = tk.LabelFrame(self.master, text="计算结果")
        output_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # 统一的比率显示框架
        self.ratio_frame = tk.Frame(output_frame)
        self.ratio_frame.pack(fill=tk.X, pady=5)
        self.orig_h_label = tk.Label(self.ratio_frame, text="原始Hadamard比率: ")
        self.orig_h_label.pack(side=tk.LEFT, padx=10)
        self.reduced_h_label = tk.Label(self.ratio_frame, text="约减后Hadamard比率: ")
        self.reduced_h_label.pack(side=tk.LEFT, padx=10)
        self.swap_label = tk.Label(self.ratio_frame, text="交换次数: 0")
        self.swap_label.pack(side=tk.LEFT, padx=10)
        self.time_label = tk.Label(self.ratio_frame, text="计算时间：")
        self.time_label.pack(side=tk.RIGHT, padx=10)

        self.result_text = scrolledtext.ScrolledText(output_frame, height=15)
        self.result_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

    def hadamard_ratio(self, B):
        """计算格的Hadamard比率（改进稳定性）"""
        B_star = self.gram_schmidt(B.copy())
        norms = [max(np.linalg.norm(v), 1e-10) for v in B_star]  # 防止零向量
        det = np.prod(norms)
        denominator = np.prod([max(np.linalg.norm(v), 1e-10) for v in B])
        n = len(B)
        return (abs(det) / denominator) ** (1 / n)

    def gram_schmidt(self, B):
        """Gram-Schmidt正交化（带数值稳定性改进）"""
        B = np.array(B, dtype=np.float64)  # 使用双精度浮点
        n = len(B)
        B_star = B.copy()

        for i in range(1, n):
            for j in range(i):
                denominator = np.dot(B_star[j], B_star[j])
                if abs(denominator) < 1e-12:  # 调整阈值
                    print(f"跳过正交化: i={i}, j={j}, denominator={denominator}")
                    continue
                mu = np.dot(B[i], B_star[j]) / denominator
                B_star[i] -= mu * B_star[j]
        return B_star

    def lll_reduction(self, B, delta=0.99):  # Lovász参数设置
        """LLL算法实现（带稳定性改进和终止保护）"""
        self.swap_count = 0  # 重置计数器
        B = np.array(B, dtype=np.float64)
        n = len(B)
        B_star = self.gram_schmidt(B.copy())

        k = 1
        max_iter = 10 ** n  # 最大迭代次数
        iter_count = 0

        while k < n and iter_count < max_iter:
            iter_count += 1

            # 尺寸约减（带容错）
            for j in range(k - 1, -1, -1):
                denominator = np.dot(B_star[j], B_star[j])
                if abs(denominator) < 1e-10:
                    continue
                mu = np.dot(B[k], B_star[j]) / denominator
                if abs(mu) > 0.5 + 1e-6:  # 增加容错阈值
                    B[k] -= np.round(mu) * B[j]
                    B_star = self.gram_schmidt(B.copy())

            # Lovász条件检查
            denominator = np.dot(B_star[k - 1], B_star[k - 1])
            if denominator < 1e-10:  # 处理零向量
                k += 1
                continue

            mu = np.dot(B[k], B_star[k - 1]) / denominator
            lhs = np.dot(B_star[k], B_star[k])
            rhs = (delta - mu ** 2) * np.dot(B_star[k - 1], B_star[k - 1])

            if lhs >= rhs - 1e-6:  # 增加容错
                k += 1
            else:
                # 交换时增加计数
                B[[k, k - 1]] = B[[k - 1, k]]
                self.swap_count += 1  # 新增计数
                B_star = self.gram_schmidt(B.copy())
                k = max(k - 1, 1)

        return B

    def is_lll_reduced(self, B, delta=0.75):
        """后验验证函数（新增）"""
        try:
            B = np.array(B, dtype=np.float64)
            B_star = self.gram_schmidt(B)

            for k in range(1, len(B)):
                # 检查尺寸约减
                for j in range(k):
                    denominator = np.dot(B_star[j], B_star[j])
                    if denominator < 1e-10:
                        continue
                    mu = np.dot(B[k], B_star[j]) / denominator
                    if abs(mu) > 0.5:
                        return False

                # 检查Lovász条件
                denominator = np.dot(B_star[k - 1], B_star[k - 1])
                if denominator < 1e-10:
                    continue
                mu = np.dot(B[k], B_star[k - 1]) / denominator
                lhs = np.dot(B_star[k], B_star[k])
                rhs = (delta - mu ** 2) * denominator
                if lhs < rhs - 1e-6:
                    return False
            return True
        except:
            return False

    def generate_matrix(self):
        try:
            n = int(self.dim_entry.get())
            # 清空之前的输入框
            for row in self.input_entries:
                for entry in row:
                    entry.destroy()
            self.input_entries = []

            # 生成新的输入框矩阵
            for i in range(n):
                row_entries = []
                for j in range(n):
                    entry = tk.Entry(self.input_frame, width=10)
                    entry.grid(row=i, column=j, padx=2, pady=2)
                    row_entries.append(entry)
                self.input_entries.append(row_entries)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的整数维数")

    def parse_matrix(self):
        """解析输入矩阵（增加错误处理）"""
        rows = []
        for row_entries in self.input_entries:
            row = []
            for entry in row_entries:
                try:
                    value = float(entry.get())
                    row.append(value)
                except ValueError:
                    raise ValueError(f"非法元素: {entry.get()}")
            rows.append(row)

        # 验证矩阵维度
        lens = set(len(row) for row in rows)
        if len(lens) != 1 or len(rows) != len(rows[0]):
            raise ValueError("必须输入方阵且行列数一致")

        return np.array(rows)

    def start_calculation(self):
        try:
            B = self.parse_matrix()
            orig_h = self.hadamard_ratio(B)

            start_time = time.time()
            reduced = self.lll_reduction(B)
            calc_time = time.time() - start_time

            # 后验验证
            if not self.is_lll_reduced(reduced):
                messagebox.showwarning("警告", "约减结果未完全满足LLL条件，可能存在数值误差")

            reduced_h = self.hadamard_ratio(reduced)

            # 显示结果（优化精度显示）
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "约简后的格基:\n")
            for row in reduced:
                formatted_row = [f"{x:8.4f}" if abs(x) > 1e-4 else f"{0:8.4f}" for x in row]  # 过滤微小值
                self.result_text.insert(tk.END, "[ " + "  ".join(formatted_row) + " ]\n")

            # 更新显示
            self.orig_h_label.config(text=f"原始Hadamard比率: {orig_h:.6f}")
            self.reduced_h_label.config(text=f"约减后Hadamard比率: {reduced_h:.6f}")
            self.time_label.config(text=f"计算时间：{calc_time:.4f} 秒")

            # 更新交换次数显示
            self.swap_label.config(text=f"交换次数: {self.swap_count}")

        except Exception as e:
            messagebox.showerror("错误", f"计算错误: {str(e)}")

    def clear_input(self):
        """清空所有输入输出"""
        self.dim_entry.delete(0, tk.END)
        for row in self.input_entries:
            for entry in row:
                entry.destroy()
        self.input_entries = []
        self.result_text.delete(1.0, tk.END)
        self.orig_h_label.config(text="原始Hadamard比率: ")
        self.reduced_h_label.config(text="约减后Hadamard比率: ")
        self.time_label.config(text="计算时间：")
        self.swap_label.config(text="交换次数: 0")  # 新增清空


if __name__ == "__main__":
    root = tk.Tk()
    app = LLLGUI(root)
    root.mainloop()