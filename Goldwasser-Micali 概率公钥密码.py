import tkinter as tk
from tkinter import messagebox
import random

# 生成大素数的简单函数，这里简单模拟，实际应用中需要更复杂的素性测试
def generate_prime():
    while True:
        num = random.randint(100, 1000)  # 简单范围，实际应用中需要更大的数
        if all(num % i != 0 for i in range(2, int(num**0.5) + 1)):
            return num

# 计算勒让德符号
def legendre_symbol(a, p):
    ls = pow(a, (p - 1) // 2, p)
    return -1 if ls == p - 1 else ls

# 密钥生成函数
def key_generation():
    # 生成两个不同的大素数 p 和 q
    p = generate_prime()
    while True:
        q = generate_prime()
        if q != p:
            break
    N = p * q
    # 选择一个非二次剩余 a
    while True:
        a = random.randint(2, N - 1)
        if legendre_symbol(a, p) == -1 and legendre_symbol(a, q) == -1:
            break
    public_key = (N, a)
    private_key = (p, q)
    process_text = f"生成素数 p = {p} 和 q = {q}\n计算 N = p * q = {N}\n"
    process_text += f"寻找非二次剩余 a，最终选择 a = {a}，因为 (a/p) = {legendre_symbol(a, p)} 且 (a/q) = {legendre_symbol(a, q)}\n"
    return public_key, private_key, process_text

# 加密函数
def encrypt(public_key, m):
    N, a = public_key
    r = random.randint(1, N - 1)
    if m == 0:
        c = pow(r, 2, N)
        process_text = f"明文 m = {m}，随机选择 r = {r}\n计算密文 c = r^2 mod N = {r}^2 mod {N} = {c}\n"
    else:
        c = (a * pow(r, 2)) % N
        process_text = f"明文 m = {m}，随机选择 r = {r}\n计算密文 c = a * r^2 mod N = {a} * {r}^2 mod {N} = {c}\n"
    return c, process_text

# 解密函数
def decrypt(private_key, c):
    p, q = private_key
    # 计算勒让德符号
    ls = legendre_symbol(c, p)
    m = 0 if ls == 1 else 1
    process_text = f"私钥 (p, q) = ({p}, {q})\n计算勒让德符号 (c/p) = ({c}/{p}) = {ls}\n"
    process_text += f"由于 (c/p) = {ls}，所以解密后的明文 m = {m}\n"
    return m, process_text

# 处理加密按钮点击事件
def encrypt_button_click():
    try:
        # 获取用户输入的明文（0 或 1）
        m = int(entry_plaintext.get())
        if m not in [0, 1]:
            messagebox.showerror("输入错误", "明文必须是 0 或 1")
            return
        # 生成密钥
        public_key, private_key, key_process = key_generation()
        # 加密明文
        c, encrypt_process = encrypt(public_key, m)
        # 显示加密结果和公钥
        label_public_key.config(text=f"公钥 (N, a): {public_key}")
        label_ciphertext.config(text=f"密文: {c}")
        # 显示计算过程
        process_text = key_process + encrypt_process
        text_encryption_process.delete(1.0, tk.END)
        text_encryption_process.insert(tk.END, process_text)
        # 保存私钥用于解密
        global saved_private_key
        saved_private_key = private_key
    except ValueError:
        messagebox.showerror("输入错误", "请输入有效的整数 0 或 1")

# 处理解密按钮点击事件
def decrypt_button_click():
    try:
        if 'saved_private_key' not in globals():
            messagebox.showerror("错误", "请先进行加密操作")
            return
        # 获取用户输入的密文
        c = int(entry_ciphertext.get())
        # 解密密文
        m, decrypt_process = decrypt(saved_private_key, c)
        # 显示解密结果
        label_decrypted_text.config(text=f"解密后的明文: {m}")
        # 显示计算过程
        text_decryption_process.delete(1.0, tk.END)
        text_decryption_process.insert(tk.END, decrypt_process)
    except ValueError:
        messagebox.showerror("输入错误", "请输入有效的整数密文")

# 创建主窗口
root = tk.Tk()
root.title("Goldwasser - Micali 密码算法")

# 创建标签和输入框用于输入明文
label_plaintext = tk.Label(root, text="请输入明文 (0 或 1):")
label_plaintext.pack()
entry_plaintext = tk.Entry(root)
entry_plaintext.pack()

# 创建加密按钮
button_encrypt = tk.Button(root, text="加密", command=encrypt_button_click)
button_encrypt.pack()

# 创建标签用于显示公钥
label_public_key = tk.Label(root, text="公钥: 未生成")
label_public_key.pack()

# 创建标签用于显示密文
label_ciphertext = tk.Label(root, text="密文: 未生成")
label_ciphertext.pack()

# 创建文本框用于显示加密过程
label_encryption_process = tk.Label(root, text="加密计算过程:")
label_encryption_process.pack()
text_encryption_process = tk.Text(root, height=10, width=50)
text_encryption_process.pack()

# 创建标签和输入框用于输入密文进行解密
label_decrypt_ciphertext = tk.Label(root, text="请输入要解密的密文:")
label_decrypt_ciphertext.pack()
entry_ciphertext = tk.Entry(root)
entry_ciphertext.pack()

# 创建解密按钮
button_decrypt = tk.Button(root, text="解密", command=decrypt_button_click)
button_decrypt.pack()

# 创建标签用于显示解密后的明文
label_decrypted_text = tk.Label(root, text="解密后的明文: 未解密")
label_decrypted_text.pack()

# 创建文本框用于显示解密过程
label_decryption_process = tk.Label(root, text="解密计算过程:")
label_decryption_process.pack()
text_decryption_process = tk.Text(root, height=10, width=50)
text_decryption_process.pack()

# 保存私钥的全局变量
saved_private_key = None

# 运行主循环
root.mainloop()