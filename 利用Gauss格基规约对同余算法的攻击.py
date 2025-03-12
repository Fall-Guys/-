import tkinter as tk
from tkinter import messagebox
import math
import random


# 扩展欧几里得算法求逆元
def extended_gcd(a, b):
    if b == 0:
        return a, 1, 0
    gcd, x1, y1 = extended_gcd(b, a % b)
    x, y = y1, x1 - (a // b) * y1
    return gcd, x, y


def mod_inverse(a, m):
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError("逆元不存在")
    return x % m


# 密钥生成
def key_generation(generate_type, q_input, f_input, g_input):
    process = "密钥生成过程：\n"
    if generate_type == "随机生成":
        q = random.randint(10000000, 100000000000)  # 简单模拟，实际应更大
        process += f"生成模数 q = {q}\n"

        while True:
            f = random.randint(1, int(math.sqrt(q / 2)))
            g_lower = int(math.sqrt(q / 4))
            g_upper = int(math.sqrt(q / 2))
            g = random.randint(g_lower, g_upper)
            if math.gcd(f, q) == 1:
                break
        process += f"选择秘密整数 f = {f}（满足 f < √(q/2)）\n"
        process += f"选择秘密整数 g = {g}（满足 √(q/4) < g < √(q/2)）\n"
    else:
        try:
            q = int(q_input)
            f = int(f_input)
            g = int(g_input)
            if f >= math.sqrt(q / 2) or g < math.sqrt(q / 4) or g > math.sqrt(q / 2) or math.gcd(f, q) != 1:
                raise ValueError("输入的 f、g 不满足条件")
            process += f"使用输入的模数 q = {q}\n"
            process += f"使用输入的秘密整数 f = {f}\n"
            process += f"使用输入的秘密整数 g = {g}\n"
        except ValueError as e:
            raise ValueError(f"输入无效: {e}")

    f_inverse = mod_inverse(f, q)
    h = (f_inverse * g) % q
    process += f"计算 f⁻¹ = {f_inverse} mod {q}\n"
    process += f"计算 h = f⁻¹ * g mod q = {f_inverse}*{g} mod {q} = {h}\n"

    public_key = (q, h)
    private_key = (f, g)
    return public_key, private_key, process


# 加密
def encrypt(public_key, m, r_generate_type, r_input):
    q, h = public_key
    process = "加密过程：\n"
    if m >= math.sqrt(q / 4):
        raise ValueError("m 不满足 m < √(q/4)")

    if r_generate_type == "随机生成":
        r_upper = int(math.sqrt(q / 2))
        r = random.randint(1, r_upper)
        process += f"随机选择 r = {r}\n"
    else:
        try:
            r = int(r_input)
            if r < 1 or r >= math.sqrt(q / 2):
                raise ValueError("输入的 r 不在有效范围内")
            process += f"使用输入的 r = {r}\n"
        except ValueError as e:
            raise ValueError(f"输入无效: {e}")

    e = (r * h + m) % q
    if e < 0 or e >= q:
        raise ValueError(f"加密结果 e 不在有效范围内，e = {e}, q = {q}")
    process += f"计算密文 e = r*h + m mod q = {r}*{h} + {m} mod {q} = {e}\n"
    return e, process


# 向量类
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


# Gauss格基规约算法
def Gauss(x, y):
    steps = []
    v1, v2 = x, y
    steps.append((v1, v2))
    finished = False
    while not finished:
        m = round(v2.dot_product(v1) / v1.dot_product(v1))
        v2 = v2 - m * v1
        steps.append((v1, v2))
        if v1.norm() <= v2.norm():
            finished = True
        else:
            v1, v2 = v2, v1
            steps.append((v1, v2))
    return steps


# 攻击函数
def attack(public_key):
    q, h = public_key
    v1 = Vector([1, h])
    v2 = Vector([0, q])
    steps = Gauss(v1, v2)
    reduced_v1, reduced_v2 = steps[-1]

    if abs(reduced_v1.data[0]) < math.sqrt(q / 2) and math.gcd(reduced_v1.data[0], q) == 1:
        f = reduced_v1.data[0]#将 reduced_v1 的第一个元素赋值给 f
        g = reduced_v1.data[1]
        return (f, g), steps
    elif abs(reduced_v2.data[0]) < math.sqrt(q / 2) and math.gcd(reduced_v2.data[0], q) == 1:
        #如果 reduced_v1 不满足条件，则检查 reduced_v2 是否满足相同的条件。如果满足，则使用 reduced_v2 的第一个元素恢复私钥 (f, g) 并返回
        f = reduced_v2.data[0]
        g = reduced_v2.data[1]
        return (f, g), steps
    else:
        return None, steps


# 界面交互函数
def generate_keys():
    try:
        generate_type = key_generate_var.get()
        if generate_type == "手动生成":
            q = entry_q.get()
            f = entry_f.get()
            g = entry_g.get()
        else:
            q = f = g = None
        public_key, private_key, process = key_generation(generate_type, q, f, g)
        txt_process.delete(1.0, tk.END)
        txt_process.insert(tk.END, process)
        global saved_public_key, saved_private_key
        saved_public_key = public_key
        saved_private_key = private_key
        btn_encrypt.config(state=tk.NORMAL)
        btn_attack.config(state=tk.NORMAL)
    except Exception as e:
        messagebox.showerror("错误", str(e))


def do_encrypt():
    try:
        if not saved_public_key:
            raise ValueError("请先生成密钥")
        m = int(entry_m.get())
        r_generate_type = r_generate_var.get()
        if r_generate_type == "手动生成":
            r = entry_r.get()
        else:
            r = None
        e, process = encrypt(saved_public_key, m, r_generate_type, r)
        txt_encrypt_process.delete(1.0, tk.END)
        txt_encrypt_process.insert(tk.END, process)
        entry_e_encrypt.delete(0, tk.END)
        entry_e_encrypt.insert(0, str(e))
    except Exception as e:
        messagebox.showerror("错误", str(e))


def do_attack():
    try:
        if not saved_public_key:
            raise ValueError("请先生成密钥")
        attacked_private_key, attack_steps = attack(saved_public_key)
        txt_attack_process.delete(1.0, tk.END)
        for idx, (v1, v2) in enumerate(attack_steps):
            txt_attack_process.insert(tk.END, f"Step {idx}: v1 = {v1}, v2 = {v2}\n")
        if attacked_private_key:
            f, g = attacked_private_key
            messagebox.showinfo("攻击成功", f"恢复的私钥: f = {f}, g = {g}")
        else:
            messagebox.showinfo("攻击失败", "未能恢复私钥")
    except Exception as e:
        messagebox.showerror("错误", str(e))


# 创建主窗口
root = tk.Tk()
root.title("同余公钥密码系统（含Gauss格基规约攻击）")

# 密钥生成部分
tk.Label(root, text="密钥生成").pack()
key_generate_var = tk.StringVar()
key_generate_var.set("随机生成")

radio_frame = tk.Frame(root)
radio_frame.pack()
tk.Radiobutton(radio_frame, text="随机生成", variable=key_generate_var, value="随机生成").pack(side=tk.LEFT)
tk.Radiobutton(radio_frame, text="手动生成", variable=key_generate_var, value="手动生成").pack(side=tk.LEFT)

input_frame = tk.Frame(root)
input_frame.pack()
tk.Label(input_frame, text="输入 q:").pack(side=tk.LEFT)
entry_q = tk.Entry(input_frame)
entry_q.pack(side=tk.LEFT)
tk.Label(input_frame, text="输入 f:").pack(side=tk.LEFT)
entry_f = tk.Entry(input_frame)
entry_f.pack(side=tk.LEFT)
tk.Label(input_frame, text="输入 g:").pack(side=tk.LEFT)
entry_g = tk.Entry(input_frame)
entry_g.pack(side=tk.LEFT)

btn_generate = tk.Button(root, text="生成密钥", command=generate_keys)
btn_generate.pack()
txt_process = tk.Text(root, height=10, width=80)
txt_process.pack()

# 加密部分
tk.Label(root, text="加密").pack()
entry_m = tk.Entry(root)
entry_m.pack()
tk.Label(root, text="输入明文 m（满足 m < √(q/4)）").pack()

r_generate_var = tk.StringVar()
r_generate_var.set("随机生成")
tk.Radiobutton(root, text="随机生成 r", variable=r_generate_var, value="随机生成").pack()
tk.Radiobutton(root, text="手动生成 r", variable=r_generate_var, value="手动生成").pack()

entry_r = tk.Entry(root)
tk.Label(root, text="输入 r（满足 r < √(q/2)）:").pack()
entry_r.pack()

btn_encrypt = tk.Button(root, text="加密", command=do_encrypt, state=tk.DISABLED)
btn_encrypt.pack()
txt_encrypt_process = tk.Text(root, height=5, width=80)
txt_encrypt_process.pack()
entry_e_encrypt = tk.Entry(root)
entry_e_encrypt.pack()
tk.Label(root, text="生成的密文 e").pack()

# 攻击部分
tk.Label(root, text="使用Gauss格基规约攻击").pack()
btn_attack = tk.Button(root, text="发起攻击", command=do_attack, state=tk.DISABLED)
btn_attack.pack()
txt_attack_process = tk.Text(root, height=10, width=80)
txt_attack_process.pack()

saved_public_key = None
saved_private_key = None

root.mainloop()