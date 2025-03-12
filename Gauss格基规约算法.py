import tkinter as tk
from tkinter import ttk
import math
import time


class Vector:
    def __init__(self, data):
        self.data = data

    def dot_product(self, other):
        return sum(a * b for a, b in zip(self.data, other.data))

    def norm(self):
        return sum(x ** 2 for x in self.data) ** 0.5

    def __sub__(self, other):
        return Vector([a - b for a, b in zip(self.data, other.data)])

    def __mul__(self, scalar):
        return Vector([x * scalar for x in self.data])

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __repr__(self):
        return f"Vector({self.data})"

    def angle_with(self, other):
        """计算与另一向量之间的夹角（单位：度）"""
        dot = self.dot_product(other)
        norm_product = self.norm() * other.norm()
        if norm_product < 1e-9:  # 防止除以零
            return 0.0
        cos_theta = dot / norm_product
        cos_theta = max(min(cos_theta, 1.0), -1.0)  # 处理浮点误差
        return math.degrees(math.acos(cos_theta))


def Gauss(x, y):
    steps = []
    v1, v2 = x, y
    finished = False
    while not finished:
        steps.append((Vector(v1.data), Vector(v2.data)))
        m = round(v2.dot_product(v1) / v1.dot_product(v1))# dot_product点积、round四舍五入
        v2 = v2 - m * v1
        if v1.norm() <= v2.norm():#比较v1、v2范数
            finished = True
        else:
            v1, v2 = v2, v1
    steps.append((v1, v2))
    return steps


class GaussGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("高斯格基规约工具")
        self.canvas_size = 400
        self.scale_factor = 1.0
        self.dragging_vector = None
        self.animation_steps = []
        self.current_step = 0
        self.current_projection = 'XY'
        self.create_widgets()
        self.create_projection_controls()

    def create_widgets(self):
        # 左侧控制面板
        left_frame = ttk.Frame(self.root)
        left_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        # 维度设置
        frame_dim = ttk.LabelFrame(left_frame, text="设置向量维度")
        frame_dim.pack(pady=5, fill="x")

        self.dim_entry = ttk.Entry(frame_dim)
        self.dim_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(
            frame_dim,
            text="确认维度",
            command=self.create_vector_inputs
        ).pack(side=tk.LEFT, padx=5)

        # 向量输入区
        self.vector_frame = ttk.Frame(left_frame)
        self.vector_frame.pack(pady=5, fill="x")

        # 缩放控制
        frame_scale = ttk.LabelFrame(left_frame, text="缩放控制")
        frame_scale.pack(pady=5, fill="x")
        self.scale_slider = ttk.Scale(
            frame_scale,
            from_=0.5,
            to=5,
            value=1.0,
            command=lambda v: self.update_scale(float(v))
        )
        self.scale_slider.pack(padx=5, fill="x")

        # 时间显示标签
        self.time_label = ttk.Label(left_frame, text="执行时间：未测量", foreground="gray")
        self.time_label.pack(pady=(0, 5))

        # 操作按钮
        ttk.Button(
            left_frame,
            text="执行规约",
            command=self.start_animation
        ).pack(pady=5)
        ttk.Button(
            left_frame,
            text="重置",
            command=self.reset_interface
        ).pack(pady=5)

        # 结果展示区
        self.result_text = tk.Text(left_frame, height=8, width=40)
        self.result_text.pack(pady=5, fill=tk.X)

        # 右侧画布
        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        self.canvas = tk.Canvas(
            self.canvas_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="white"
        )
        self.canvas.pack()
        self.bind_events()
        self.draw_coordinate_system()

    def create_projection_controls(self):
        """创建投影模式选择控件"""
        proj_frame = ttk.LabelFrame(self.root, text="投影模式")
        proj_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.proj_var = tk.StringVar(value='XY')
        ttk.Radiobutton(proj_frame, text="XY平面", variable=self.proj_var,
                        value='XY', command=self.update_projection).pack(side=tk.LEFT)
        ttk.Radiobutton(proj_frame, text="XZ平面", variable=self.proj_var,
                        value='XZ', command=self.update_projection).pack(side=tk.LEFT)
        ttk.Radiobutton(proj_frame, text="YZ平面", variable=self.proj_var,
                        value='YZ', command=self.update_projection).pack(side=tk.LEFT)

    def update_projection(self):
        """更新投影模式"""
        self.current_projection = self.proj_var.get()
        self.redraw_vectors()

    def format_time(self, seconds):
        """格式化时间显示"""
        if seconds < 1e-6:
            return f"{seconds * 1e9:.2f} ns"
        elif seconds < 1e-3:
            return f"{seconds * 1e6:.2f} μs"
        elif seconds < 1:
            return f"{seconds * 1e3:.2f} ms"
        else:
            return f"{seconds:.4f} s"

    def start_animation(self):
        """执行规约并启动动画"""
        try:
            v1_data = [float(e.get()) for e in self.v1_entries]
            v2_data = [float(e.get()) for e in self.v2_entries]
            v1 = Vector(v1_data)
            v2 = Vector(v2_data)

            start_time = time.perf_counter()
            self.animation_steps = Gauss(v1, v2)
            elapsed = time.perf_counter() - start_time
            final_result = self.animation_steps[-1]

            self.run_calculation(final_result, elapsed)
            self.current_step = 0
            self.animate_next_step()

        except ValueError:
            self.time_label.config(text="执行时间：测量失败")
            self.canvas.delete("all")
            self.canvas.create_text(
                self.canvas_size // 2, self.canvas_size // 2,
                text="输入错误！", fill="red"
            )

    def bind_events(self):
        """绑定鼠标事件"""
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag_vector)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)

    def start_drag(self, event):
        """检测是否点击在向量箭头上"""
        x, y = event.x, event.y
        tolerance = 10

        if hasattr(self, 'current_v1'):
            end = self.vector_to_screen(self.current_v1)
            if math.hypot(x - end[0], y - end[1]) < tolerance:
                self.dragging_vector = 'v1'
        if hasattr(self, 'current_v2'):
            end = self.vector_to_screen(self.current_v2)
            if math.hypot(x - end[0], y - end[1]) < tolerance:
                self.dragging_vector = 'v2'

    def drag_vector(self, event):
        """拖动更新向量数据"""
        if not self.dragging_vector:
            return

        math_x = (event.x - self.origin[0]) / (self.scale_factor * (self.canvas_size // 2 - 20))
        math_y = (self.origin[1] - event.y) / (self.scale_factor * (self.canvas_size // 2 - 20))

        if self.dragging_vector == 'v1':
            entries = self.v1_entries
        else:
            entries = self.v2_entries

        for i, entry in enumerate(entries):
            entry.delete(0, tk.END)
            value = math_x if i == 0 else math_y
            entry.insert(0, f"{value:.2f}")

        self.run_calculation(update_animation=False)

    def end_drag(self, event):
        self.dragging_vector = None

    def update_scale(self, factor):
        """缩放画布"""
        self.scale_factor = factor
        self.draw_coordinate_system()
        if hasattr(self, 'current_v1'):
            self.redraw_vectors()

    def redraw_vectors(self):
        """重新绘制所有向量"""
        self.draw_coordinate_system()
        if hasattr(self, 'current_v1'):
            self.draw_vector(self.current_v1, "red", "Original v1")
        if hasattr(self, 'current_v2'):
            self.draw_vector(self.current_v2, "orange", "Original v2")
        if hasattr(self, 'result_v1'):
            self.draw_vector(self.result_v1, "blue", "Reduced v1")
        if hasattr(self, 'result_v2'):
            self.draw_vector(self.result_v2, "green", "Reduced v2")

    def create_vector_inputs(self):
        for widget in self.vector_frame.winfo_children():
            widget.destroy()

        try:
            dim = int(self.dim_entry.get())
            if dim < 1:
                raise ValueError
        except:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "错误：请输入正整数维度")
            return

        # 创建向量输入组件
        ttk.Label(self.vector_frame, text="向量1分量：").grid(row=0, column=0, sticky="w")
        self.v1_entries = []
        for i in range(dim):
            entry = ttk.Entry(self.vector_frame, width=6)
            entry.grid(row=0, column=i + 1, padx=2)
            self.v1_entries.append(entry)

        ttk.Label(self.vector_frame, text="向量2分量：").grid(row=1, column=0, sticky="w")
        self.v2_entries = []
        for i in range(dim):
            entry = ttk.Entry(self.vector_frame, width=6)
            entry.grid(row=1, column=i + 1, padx=2)
            self.v2_entries.append(entry)

    def draw_coordinate_system(self):
        """绘制坐标系"""
        self.canvas.delete("all")
        self.origin = (self.canvas_size // 2, self.canvas_size // 2)

        if self.current_projection == 'XY':
            self._draw_xy_axes()
        elif self.current_projection == 'XZ':
            self._draw_xz_axes()
        elif self.current_projection == 'YZ':
            self._draw_yz_axes()

    def _draw_xy_axes(self):
        """XY投影坐标轴"""
        self.canvas.create_line(0, self.origin[1], self.canvas_size, self.origin[1],
                                fill="gray", arrow=tk.LAST)
        self.canvas.create_line(self.origin[0], 0, self.origin[0], self.canvas_size,
                                fill="gray", arrow=tk.LAST)
        self.canvas.create_text(self.canvas_size - 10, self.origin[1] - 10, text="X", fill="gray")
        self.canvas.create_text(self.origin[0] + 10, 10, text="Y", fill="gray")

    def _draw_xz_axes(self):
        """XZ投影坐标轴"""
        self.canvas.create_line(0, self.origin[1], self.canvas_size, self.origin[1],
                                fill="gray", arrow=tk.LAST)
        self.canvas.create_line(self.origin[0], self.origin[1],
                                self.origin[0] + 50, self.origin[1] - 50,
                                fill="gray", arrow=tk.LAST)
        self.canvas.create_text(self.canvas_size - 10, self.origin[1] - 10, text="X", fill="gray")
        self.canvas.create_text(self.origin[0] + 60, self.origin[1] - 60, text="Z", fill="gray")

    def _draw_yz_axes(self):
        """YZ投影坐标轴"""
        self.canvas.create_line(self.origin[0], 0, self.origin[0], self.canvas_size,
                                fill="gray", arrow=tk.LAST)
        self.canvas.create_line(self.origin[0], self.origin[1],
                                self.origin[0] + 50, self.origin[1] - 50,
                                fill="gray", arrow=tk.LAST)
        self.canvas.create_text(self.origin[0] + 10, 10, text="Y", fill="gray")
        self.canvas.create_text(self.origin[0] + 60, self.origin[1] - 60, text="Z", fill="gray")

    def vector_to_screen(self, vector):
        """坐标转换"""
        if self.current_projection == 'XY':
            x, y = vector.data[0], vector.data[1] if len(vector.data) > 1 else 0
        elif self.current_projection == 'XZ':
            x, z = vector.data[0], vector.data[2] if len(vector.data) > 2 else 0
            x, y = x, z
        elif self.current_projection == 'YZ':
            y = vector.data[1] if len(vector.data) > 1 else 0
            z = vector.data[2] if len(vector.data) > 2 else 0
            x, y = y, z

        max_dim = max(abs(x), abs(y))
        scale = (self.canvas_size // 2 - 20) * self.scale_factor / (max_dim + 1e-6)
        return (
            self.origin[0] + x * scale,
            self.origin[1] - y * scale
        )

    def draw_vector(self, vector, color, label):
        """绘制向量"""
        if len(vector.data) < 2 and self.current_projection != 'XZ':
            return

        end = self.vector_to_screen(vector)

        self.canvas.create_line(
            self.origin[0], self.origin[1], end[0], end[1],
            fill=color, width=2, arrow=tk.LAST, tags="vector"
        )

        labels = []
        if self.current_projection == 'XY' and len(vector.data) > 2:
            labels.append(f"z={vector.data[2]:.1f}")
        elif self.current_projection == 'XZ' and len(vector.data) > 1:
            labels.append(f"y={vector.data[1]:.1f}")
        elif self.current_projection == 'YZ' and len(vector.data) > 0:
            labels.append(f"x={vector.data[0]:.1f}")

        full_label = f"{label} ({', '.join(labels)})" if labels else label

        label_pos = (
            (self.origin[0] + end[0]) / 2 + 10,
            (self.origin[1] + end[1]) / 2
        )
        self.canvas.create_text(*label_pos, text=full_label, fill=color, tags="label")

    def animate_next_step(self):
        """动画演示"""
        if self.current_step < len(self.animation_steps):
            self.canvas.delete("vector")
            self.canvas.delete("label")

            v1, v2 = self.animation_steps[self.current_step]
            self.draw_vector(v1, "blue", f"Step{self.current_step}v1")
            self.draw_vector(v2, "green", f"Step{self.current_step}v2")

            self.current_step += 1
            self.root.after(1000, self.animate_next_step)

    def reset_interface(self):
        """重置界面"""
        self.dim_entry.delete(0, tk.END)
        for entry in self.v1_entries + self.v2_entries:
            entry.delete(0, tk.END)
        self.canvas.delete("all")
        self.draw_coordinate_system()
        self.animation_steps = []
        self.current_step = 0

    def run_calculation(self, final_result, elapsed_time=None):
        """计算结果展示（新增角度计算）"""
        try:
            self.result_text.delete(1.0, tk.END)

            # 获取原始向量和规约后向量
            original_v1 = Vector([float(e.get()) for e in self.v1_entries])
            original_v2 = Vector([float(e.get()) for e in self.v2_entries])
            reduced_v1, reduced_v2 = final_result[0], final_result[1]

            # 计算角度
            original_angle = original_v1.angle_with(original_v2)
            reduced_angle = reduced_v1.angle_with(reduced_v2)

            # 显示结果
            self.result_text.insert(tk.END, "原始向量：\n")
            self.result_text.insert(tk.END, f"v1 = {original_v1}\n")
            self.result_text.insert(tk.END, f"v2 = {original_v2}\n")
            self.result_text.insert(tk.END, f"夹角: {original_angle:.2f}°\n\n")

            self.result_text.insert(tk.END, "规约结果：\n")
            self.result_text.insert(tk.END, f"新v1 = {reduced_v1} (范数: {reduced_v1.norm():.2f})\n")
            self.result_text.insert(tk.END, f"新v2 = {reduced_v2} (范数: {reduced_v2.norm():.2f})\n")
            self.result_text.insert(tk.END, f"夹角: {reduced_angle:.2f}°")

            # 绘制向量（原有代码不变）
            self.draw_coordinate_system()
            if len(reduced_v1.data) >= 2 and len(reduced_v2.data) >= 2:
                self.draw_vector(reduced_v1, "red", "Reduced v1")
                self.draw_vector(reduced_v2, "green", "Reduced v2")

            if elapsed_time is not None:
                self.time_label.config(text=f"执行时间：{self.format_time(elapsed_time)}")

        except ValueError as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "错误：请输入有效的数字")
            self.time_label.config(text="执行时间：测量失败")

if __name__ == "__main__":
    root = tk.Tk()
    app = GaussGUI(root)
    root.mainloop()
