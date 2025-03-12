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
        # 生成q
        q = random.randint(10000000, 100000000)  # 简单模拟，实际应更大
        process += f"生成模数 q = {q}\n"

        # 生成f和g
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

    # 计算h
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
            if r < 1 or r >= math.sqrt(q / 2):  # 注意r的范围
                raise ValueError("输入的 r 不在有效范围内")
            process += f"使用输入的 r = {r}\n"
        except ValueError as e:
            raise ValueError(f"输入无效: {e}")

    e = (r * h + m) % q
    # 边界检查
    if e < 0 or e >= q:
        raise ValueError(f"加密结果 e 不在有效范围内，e = {e}, q = {q}")
    process += f"计算密文 e = r*h + m mod q = {r}*{h} + {m} mod {q} = {e}\n"
    return e, process

def decrypt(private_key, public_key, e):
    f, g = private_key
    q, _ = public_key
    process = "解密过程：\n"

    a = (f * e) % q
    # 边界检查
    if a < 0 or a >= q:
        raise ValueError(f"中间结果 a 不在有效范围内，a = {a}, q = {q}")
    process += f"计算 a = f*e mod q = {f}*{e} mod {q} = {a}\n"

    a_inverse = mod_inverse(f, g)
    b = (a_inverse * a) % g
    # 边界检查
    if b < 0 or b >= g:
        raise ValueError(f"解密结果 b 不在有效范围内，b = {b}, g = {g}")
    process += f"计算 b = f⁻¹*a mod g = {a_inverse}*{a} mod {g} = {b}\n"

    return b, process

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
        btn_decrypt.config(state=tk.NORMAL)
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
        global encrypted_e
        encrypted_e = e
    except Exception as e:
        messagebox.showerror("错误", str(e))

def do_decrypt():
    try:
        if not saved_private_key:
            raise ValueError("请先生成密钥")
        global encrypted_e
        m, process = decrypt(saved_private_key, saved_public_key, encrypted_e)
        txt_decrypt_process.delete(1.0, tk.END)
        txt_decrypt_process.insert(tk.END, process)
        entry_decrypted_m.delete(0, tk.END)
        entry_decrypted_m.insert(0, str(m))
    except Exception as e:
        messagebox.showerror("错误", str(e))

# 创建主窗口
root = tk.Tk()
root.title("同余公钥密码系统")

# 密钥生成部分
tk.Label(root, text="密钥生成").pack()
key_generate_var = tk.StringVar()
key_generate_var.set("随机生成")

# 创建一个Frame来放置单选按钮
radio_frame = tk.Frame(root)
radio_frame.pack()
tk.Radiobutton(radio_frame, text="随机生成", variable=key_generate_var, value="随机生成").pack(side=tk.LEFT)
tk.Radiobutton(radio_frame, text="手动生成", variable=key_generate_var, value="手动生成").pack(side=tk.LEFT)

# 创建一个Frame来放置输入框
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

# 解密部分
tk.Label(root, text="解密").pack()
btn_decrypt = tk.Button(root, text="解密", command=do_decrypt, state=tk.DISABLED)
btn_decrypt.pack()
txt_decrypt_process = tk.Text(root, height=5, width=80)
txt_decrypt_process.pack()
entry_decrypted_m = tk.Entry(root)
entry_decrypted_m.pack()
tk.Label(root, text="解密后的明文 m").pack()

saved_public_key = None
saved_private_key = None
encrypted_e = None

root.mainloop()