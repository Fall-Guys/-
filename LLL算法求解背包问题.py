import numpy as np
import tkinter as tk
from tkinter import messagebox, scrolledtext
import time


class KnapsackLLLGUI:
    def __init__(self, master):
        self.master = master
        master.title("LLL算法求解背包问题")
        master.geometry("1000x700")
        self.swap_count = 0  # 新增交换次数计数器
        self.create_widgets()

    def create_widgets(self):
        # 输入区域：物品重量列表和目标重量
        input_frame = tk.LabelFrame(self.master, text="输入参数")
        input_frame.pack(pady=10, padx=10, fill=tk.X)

        # 物品重量列表输入
        tk.Label(input_frame, text="物品重量列表（空格分隔）:").pack(side=tk.LEFT, padx=5)
        self.weights_entry = tk.Entry(input_frame, width=50)
        self.weights_entry.pack(side=tk.LEFT, padx=5)

        # 目标重量输入
        tk.Label(input_frame, text="目标重量:").pack(side=tk.LEFT, padx=5)
        self.target_entry = tk.Entry(input_frame, width=10)
        self.target_entry.pack(side=tk.LEFT, padx=5)

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
        self.ratio_frame = tk.Frame(output_frame)
        self.ratio_frame.pack(fill=tk.X, pady=5)
        self.orig_h_label = tk.Label(self.ratio_frame, text="原始Hadamard比率: ")
        self.orig_h_label.pack(side=tk.LEFT, padx=10)
        self.reduced_h_label = tk.Label(self.ratio_frame, text="约减后Hadamard比率: ")
        self.reduced_h_label.pack(side=tk.LEFT, padx=10)
        self.time_label = tk.Label(self.ratio_frame, text="计算时间：")
        self.time_label.pack(side=tk.RIGHT, padx=10)

        # 新增交换次数标签
        self.swap_label = tk.Label(self.ratio_frame, text="交换次数: 0")
        self.swap_label.pack(side=tk.LEFT, padx=10)

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

    def lll_reduction(self, B, delta=0.99):
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
            self.result_text.insert(tk.END, f"迭代次数: {iter_count}, 当前 k: {k}\n")

            # 尺寸约减（带容错）
            for j in range(k - 1, -1, -1):
                denominator = np.dot(B_star[j], B_star[j])
                if abs(denominator) < 1e-10:
                    continue
                mu = np.dot(B[k], B_star[j]) / denominator
                if abs(mu) > 0.5 + 1e-6:  # 增加容错阈值
                    B[k] -= np.round(mu) * B[j]
                    B_star = self.gram_schmidt(B.copy())
                    self.result_text.insert(tk.END, f"尺寸约减: k={k}, j={j}, mu={mu:.6f}\n")

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
                self.result_text.insert(tk.END, f"Lovász条件满足: k={k}, mu={mu:.6f}, lhs={lhs:.6f}, rhs={rhs:.6f}\n")
            else:
                # 交换时增加计数
                B[[k, k - 1]] = B[[k - 1, k]]
                self.swap_count += 1  # 新增计数
                B_star = self.gram_schmidt(B.copy())
                k = max(k - 1, 1)
                self.result_text.insert(tk.END, f"交换操作: k={k}, mu={mu:.6f}, lhs={lhs:.6f}, rhs={rhs:.6f}\n")

            # 更新界面
            self.result_text.see(tk.END)
            self.master.update_idletasks()

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

    def parse_input(self):
        """解析输入的物品重量列表和目标重量"""
        weights_str = self.weights_entry.get().strip()
        target_str = self.target_entry.get().strip()

        if not weights_str or not target_str:
            raise ValueError("物品重量列表和目标重量不能为空")

        try:
            weights = [float(w) for w in weights_str.split()]
            target = float(target_str)
        except ValueError:
            raise ValueError("输入的物品重量或目标重量必须为数字")

        return weights, target

    def construct_lattice(self, weights, target):
        """构造用于求解子集和问题的格基矩阵"""
        n = len(weights)
        N = 2 * max(max(weights), target)  # 选择合适的N值
        B = np.zeros((n + 1, n + 1))
        for i in range(n):
            B[i, i] = 1
            B[i, -1] = N * weights[i]
        B[-1, :-1] = 0
        B[-1, -1] = -N * target
        return B

    def find_solution(self, reduced, weights):
        """从约减后的格基矩阵中寻找子集和问题的解"""
        n = len(weights)
        eps = 1e-6
        for row in reduced:
            solution = []
            valid = True
            for i in range(n):
                if abs(row[i]) < eps:
                    solution.append(0)
                elif abs(row[i] - 1) < eps:
                    solution.append(1)
                else:
                    valid = False
                    break
            if valid and abs(row[-1]) < eps:
                return solution
        return None

    def start_calculation(self):
        try:
            # 解析输入
            weights, target = self.parse_input()

            # 构造格基矩阵
            B = self.construct_lattice(weights, target)
            orig_h = self.hadamard_ratio(B)

            start_time = time.time()
            # 进行LLL约化
            reduced = self.lll_reduction(B)
            calc_time = time.time() - start_time

            # 后验验证
            if not self.is_lll_reduced(reduced):
                messagebox.showwarning("警告", "约减结果未完全满足LLL条件，可能存在数值误差")

            reduced_h = self.hadamard_ratio(reduced)

            # 寻找解
            solution = self.find_solution(reduced, weights)

            # 显示结果
            self.result_text.insert(tk.END, f"\nLLL约化完成\n")
            if solution is not None:
                selected_weights = [w for w, s in zip(weights, solution) if s]
                total_weight = sum(selected_weights)
                self.result_text.insert(tk.END, f"找到解：选择的物品重量为 {selected_weights}，总重量为 {total_weight}\n")
            else:
                self.result_text.insert(tk.END, "未找到满足条件的解。\n")

            # 更新显示
            self.orig_h_label.config(text=f"原始Hadamard比率: {orig_h:.6f}")
            self.reduced_h_label.config(text=f"约减后Hadamard比率: {reduced_h:.6f}")
            self.time_label.config(text=f"计算时间：{calc_time:.4f} 秒")
            self.swap_label.config(text=f"交换次数: {self.swap_count}")

        except Exception as e:
            messagebox.showerror("错误", f"计算错误: {str(e)}")

    def clear_input(self):
        """清空所有输入输出"""
        self.weights_entry.delete(0, tk.END)
        self.target_entry.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.orig_h_label.config(text="原始Hadamard比率: ")
        self.reduced_h_label.config(text="约减后Hadamard比率: ")
        self.time_label.config(text="计算时间：")
        self.swap_label.config(text="交换次数: 0")


if __name__ == "__main__":
    root = tk.Tk()
    app = KnapsackLLLGUI(root)
    root.mainloop()