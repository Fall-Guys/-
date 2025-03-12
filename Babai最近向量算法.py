import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# 设置 matplotlib 支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体字体，根据系统情况可更换
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题



class Vector:
    def __init__(self, data):
        self.data = np.array(data, dtype=float)

    def __add__(self, other):
        return Vector(self.data + other.data)

    def __sub__(self, other):
        return Vector(self.data - other.data)

    def __mul__(self, scalar):
        return Vector(self.data * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def dot(self, other):
        return np.dot(self.data, other.data)

    def norm(self):
        return np.linalg.norm(self.data)

    def __repr__(self):
        return f"Vector({self.data.round(4).tolist()})"


def gram_schmidt(basis):
    ortho_basis = []
    mu = np.zeros((len(basis), len(basis)))

    for i in range(len(basis)):
        v_i = basis[i].data.copy()
        for j in range(i):
            mu[i][j] = basis[i].dot(ortho_basis[j]) / ortho_basis[j].dot(ortho_basis[j])
            v_i -= mu[i][j] * ortho_basis[j].data
        ortho_basis.append(Vector(v_i))
    return ortho_basis, mu


def babai_closest_vector(basis, target):
    ortho_basis, mu = gram_schmidt(basis)
    n = len(basis)
    t = target.data.copy()
    a = np.zeros(n, dtype=float)

    for i in reversed(range(n)):
        a[i] = round(t.dot(ortho_basis[i].data) / ortho_basis[i].dot(ortho_basis[i]))
        for j in range(i):
            t[j] -= a[i] * mu[i][j]

    closest = Vector(np.zeros_like(target.data))
    for i in range(n):
        closest += a[i] * basis[i]
    return closest


class BabaiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Babai最近向量算法可视化")

        # 初始化图形属性
        self.fig = Figure(figsize=(6, 6))#程序界面的大小
        self.ax = self.fig.add_subplot(111)

        # 初始化其他参数
        self.dimension = 2
        self.basis_vectors = []
        self.target_vector = None
        self.closest_vector = None

        # 按正确顺序初始化组件
        self.create_visualization()
        self.create_controls()  # 确保这个方法存在
        self.create_result_panel()

    # 新增缺失的三个核心方法
    def create_controls(self):
        """创建左侧控制面板"""
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # 维度选择组件
        ttk.Label(control_frame, text="选择维度:").grid(row=0, column=0)
        self.dim_var = tk.IntVar(value=2)
        ttk.Combobox(control_frame, textvariable=self.dim_var, values=[2, 3], width=5).grid(row=0, column=1)
        ttk.Button(control_frame, text="应用", command=self.update_dimension).grid(row=0, column=2)

        # 基向量输入
        self.basis_frame = ttk.LabelFrame(control_frame, text="基向量输入")
        self.basis_frame.grid(row=1, column=0, columnspan=3, pady=5)

        # 目标向量输入
        ttk.Label(control_frame, text="目标向量:").grid(row=2, column=0)
        self.target_entries = []
        self.target_frame = ttk.Frame(control_frame)
        self.target_frame.grid(row=2, column=1, columnspan=2)

        # 操作按钮
        ttk.Button(control_frame, text="计算最近向量", command=self.calculate).grid(row=3, column=0, pady=10)
        ttk.Button(control_frame, text="重置", command=self.reset).grid(row=3, column=1)

        self.update_dimension()

    def create_visualization(self):
        """创建可视化区域"""
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def create_result_panel(self):
        """创建结果面板"""
        result_frame = ttk.Frame(self.root)
        result_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.result_text = tk.Text(result_frame, height=8, width=40)
        self.result_text.pack(pady=5)

    def update_dimension(self):
        """更新维度时重置输入控件"""
        self.dimension = self.dim_var.get()

        # 更新基向量输入
        for widget in self.basis_frame.winfo_children():
            widget.destroy()

        self.basis_entries = []
        for i in range(self.dimension):
            frame = ttk.Frame(self.basis_frame)
            frame.pack(pady=2)
            ttk.Label(frame, text=f"基向量{i + 1}:").pack(side=tk.LEFT)
            entries = []
            for _ in range(self.dimension):
                entry = ttk.Entry(frame, width=5)
                entry.pack(side=tk.LEFT)
                entries.append(entry)
            self.basis_entries.append(entries)

        # 更新目标向量输入
        for widget in self.target_frame.winfo_children():
            widget.destroy()

        self.target_entries = []
        for i in range(self.dimension):
            entry = ttk.Entry(self.target_frame, width=5)
            entry.pack(side=tk.LEFT)
            self.target_entries.append(entry)

        self.update_visualization()

    def update_visualization(self):
        """更新可视化图形"""
        self.fig.clf()
        if self.dimension == 2:
            self.ax = self.fig.add_subplot(111)
            self.draw_2d()
        else:
            self.ax = self.fig.add_subplot(111, projection='3d')
            self.draw_3d()

        self.canvas.draw()

    def draw_2d(self):
        """最终修正版2D绘图方法"""
        self.ax.clear()

        # 收集所有向量数据（包含原始基向量、目标和最近向量）
        all_vectors = []
        max_component = 0  # 记录所有分量的最大绝对值

        # 解析基向量
        basis_vectors = []
        for entries in self.basis_entries:
            try:
                vec = [float(e.get()) for e in entries]
                basis_vectors.append(vec)
                all_vectors.append(vec)
                max_component = max(max_component, np.max(np.abs(vec)))
            except:
                pass

        # 解析目标向量
        target_vector = None
        try:
            target_vector = [float(e.get()) for e in self.target_entries]
            all_vectors.append(target_vector)
            max_component = max(max_component, np.max(np.abs(target_vector)))
        except:
            pass

        # 包含最近向量
        if self.closest_vector is not None:
            cv = self.closest_vector.data.tolist()
            all_vectors.append(cv)
            max_component = max(max_component, np.max(np.abs(cv)))

        # 动态计算可视化参数
        axis_padding = max(2.0, max_component * 0.2)  # 最小留白2单位
        axis_limit = max(5, max_component + axis_padding)

        # 智能网格步长
        grid_step = 1 if axis_limit <= 10 else 2 if axis_limit <= 20 else 5

        # 绘制网格背景
        self.ax.set_axisbelow(True)
        self.ax.grid(True, color='#DDDDDD', linestyle='--', linewidth=0.5)
        self.ax.set_xticks(np.arange(-axis_limit, axis_limit + grid_step, grid_step))
        self.ax.set_yticks(np.arange(-axis_limit, axis_limit + grid_step, grid_step))

        # 核心箭头参数计算（物理尺寸固定）
        base_arrow_width = 0.3  # 基础线宽（屏幕坐标）
        base_head_width = 4.0  # 箭头头部宽度（点）
        base_head_length = 5.0  # 箭头头部长度（点）
        min_arrow_length = 0.1  # 最小显示长度（数据单位）

        # 统一箭头样式参数
        arrow_style = {
            'angles': 'xy',
            'scale_units': 'xy',
            'scale': 1,  # 统一缩放比例
            'width': 0.003,  # 固定箭头杆宽度（相对坐标比例）
            'headwidth': 3.0,  # 统一箭头头部宽度
            'headlength': 5.0,  # 统一箭头头部长度
            'headaxislength': 4.5,
            'minshaft': 1.5  # 箭头杆最小长度比例
        }

        # 绘制基向量（蓝色系）
        for i, vec in enumerate(basis_vectors):
            self.ax.quiver(0, 0, vec[0], vec[1],
                           color=f'C{i}',  # 自动渐变色
                           label=f'Basis {i + 1}',
                           **arrow_style)  # 统一应用样式

        # 绘制目标向量（红色虚线）
        if target_vector is not None:
            self.ax.quiver(0, 0, target_vector[0], target_vector[1],
                           color='red',
                           linestyle=':',
                           linewidth=1.5,
                           label='Target',
                           **arrow_style)

            # 绘制最近向量（绿色且不加粗）
            if self.closest_vector is not None:
                cv = self.closest_vector.data
                self.ax.quiver(0, 0, cv[0], cv[1],
                               color='#2ca02c',  # 保持与基向量相同的样式参数
                               label='Closest',
                               **arrow_style)  # 关键点：使用相同的样式字典

        # 设置坐标轴属性
        self.ax.set_xlim(-axis_limit, axis_limit)
        self.ax.set_ylim(-axis_limit, axis_limit)
        self.ax.set_aspect('equal')
        self.ax.legend(loc='best', fontsize=8)

        # 添加调试信息
        debug_info = [
            f"坐标范围: ±{axis_limit:.1f}",
            f"最大分量: {max_component:.2f}",
            f"最近向量: {cv.tolist() if self.closest_vector else 'None'}"
        ]
        self.ax.text(0.02, 0.98, '\n'.join(debug_info),
                     transform=self.ax.transAxes,
                     verticalalignment='top',
                     fontsize=8,
                     bbox=dict(facecolor='white', alpha=0.8))

    def draw_3d(self):
        """最终稳定版3D绘图方法"""
        self.ax.clear()

        # 动态计算坐标范围
        max_val = 0
        valid_vectors = []

        # 基向量处理（增强容错）
        for i, entries in enumerate(self.basis_entries):
            try:
                # 跳过空输入并过滤无效字符
                vec = [float(e.get()) for e in entries if e.get().strip() != '']
                if len(vec) == 3:
                    valid_vectors.append(vec)
                    max_val = max(max_val, np.max(np.abs(vec)))
            except (ValueError, TypeError) as e:
                print(f"基向量{i + 1}输入异常: {str(e)}")
                continue

        # 目标向量处理（增强类型检查）
        target_vector = []
        try:
            target_vector = [float(e.get()) for e in self.target_entries if e.get().strip() != '']
            if len(target_vector) == 3:
                valid_vectors.append(target_vector)
                max_val = max(max_val, np.max(np.abs(target_vector)))
        except Exception as e:
            print(f"目标向量异常: {str(e)}")

        # 最近向量处理
        closest_vector = []
        if self.closest_vector and hasattr(self.closest_vector, 'data'):
            try:
                closest_vector = self.closest_vector.data.tolist()
                if len(closest_vector) == 3:
                    valid_vectors.append(closest_vector)
                    max_val = max(max_val, np.max(np.abs(closest_vector)))
            except Exception as e:
                print(f"最近向量异常: {str(e)}")

        # 设置动态坐标范围
        axis_limit = max(5, max_val * 1.2) if valid_vectors else 5

        # 统一箭头参数（移除非颜色相关参数）
        base_arrow_params = {
            'arrow_length_ratio': 0.2,
            'linewidths': 1.5,
            'alpha': 0.9,
            'length': 1.0  # 新增长度控制参数
        }

        # 绘制基向量（使用独立颜色参数）
        for i, entries in enumerate(self.basis_entries):
            try:
                vec = [float(e.get()) for e in entries if e.get().strip()]
                if len(vec) == 3:
                    # 显式设置颜色参数
                    self.ax.quiver(0, 0, 0, *vec,
                                   color=f'C{i}',  # 使用matplotlib默认颜色循环
                                   **base_arrow_params)
                    # 手动添加图例项
                    self.ax.plot([], [], color=f'C{i}',
                                 label=f'Basis {i + 1}')

            except Exception as e:
                print(f"基向量{i + 1}错误: {str(e)}")

        # 绘制目标向量（蓝色实线）
        if len(target_vector) == 3:
            self.ax.quiver(0, 0, 0, *target_vector,
                           color='#000080',
                           **base_arrow_params)
            self.ax.plot([], [], color='#000080',
                         label='Target')

        # 绘制最近向量（红色虚线）
        if len(closest_vector) == 3:
            self.ax.quiver(0, 0, 0, *closest_vector,
                           color='red',  # 使用更鲜明的绿色
                           linestyles=':',
                           **base_arrow_params)
            self.ax.plot([], [], color='red', linestyle=':',
                         label='Closest')

        # 创建图例（独立绘制空线段）
        if self.ax.get_legend_handles_labels()[1]:
            self.ax.legend(loc='upper left',
                           bbox_to_anchor=(1.05, 1),
                           fontsize=8)

        # 坐标轴设置
        self.ax.set_xlim([-axis_limit, axis_limit])
        self.ax.set_ylim([-axis_limit, axis_limit])
        self.ax.set_zlim([-axis_limit, axis_limit])
        self.ax.set_box_aspect([1, 1, 1])

        # 添加标签和视角优化
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.view_init(elev=25, azim=45)  # 初始视角
        self.ax.legend(loc='upper right', fontsize=8)

        # 保持比例一致
        self.ax.set_box_aspect([1, 1, 1])  # 关键！保持三维坐标比例一致

    def calculate(self):
        """执行Babai算法计算"""
        try:
            # 解析输入
            basis = []
            for entries in self.basis_entries:
                vec = [float(entry.get()) for entry in entries]
                basis.append(Vector(vec))

            target = Vector([float(entry.get()) for entry in self.target_entries])

            # 执行算法
            self.closest_vector = babai_closest_vector(basis, target)
            self.target_vector = target.data

            # 更新结果展示
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"目标向量: {target.data}\n")
            self.result_text.insert(tk.END, f"最近格向量: {self.closest_vector.data}\n")
            self.result_text.insert(tk.END, f"欧氏距离: {np.linalg.norm(target.data - self.closest_vector.data):.4f}")

            # 更新可视化
            self.update_visualization()

        except ValueError as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "输入错误！请检查数值格式")

    def reset(self):
        """重置所有输入和可视化"""
        for entries in self.basis_entries:
            for entry in entries:
                entry.delete(0, tk.END)

        for entry in self.target_entries:
            entry.delete(0, tk.END)

        self.closest_vector = None
        self.target_vector = None
        self.update_visualization()
        self.result_text.delete(1.0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = BabaiGUI(root)
    root.mainloop()