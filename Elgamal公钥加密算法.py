import secrets
from math import gcd
import tkinter as tk
from tkinter import messagebox, scrolledtext

# 定义 Miller-Rabin 素性测试函数
def is_prime(n, k=5):
    """
    Miller-Rabin 素性测试，用于判断一个数是否可能为素数。
    该算法通过多次随机测试来提高判断的准确性，但仍存在一定的误判概率。
    :param n: 要测试的数
    :param k: 测试的迭代次数，迭代次数越多，判断结果越准确
    :return: 如果 n 可能是素数，返回 True；否则返回 False
    """
    log_text.insert(tk.END, f"开始对 {n} 进行 Miller-Rabin 素性测试...\n")
    # 小于等于 1 的数不是素数
    if n <= 1:
        log_text.insert(tk.END, f"{n} 小于等于 1，不是素数。\n")
        return False
    # 先检查 n 是否为 2 到 31 之间的素数
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        if n % p == 0:
            result = n == p
            log_text.insert(tk.END, f"{n} 能被 {p} 整除，{'是' if result else '不是'}素数。\n")
            return result
    # 将 n - 1 分解为 2^s * d 的形式
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    log_text.insert(tk.END, f"n - 1 分解为 2^{s} * {d}\n")
    # 进行 k 次随机测试
    for i in range(k):
        # 随机选择一个 2 到 n - 2 之间的数 a
        a = secrets.randbelow(n - 4) + 2
        log_text.insert(tk.END, f"第 {i + 1} 次测试，随机选择 a = {a}\n")
        # 计算 x = a^d mod n
        x = pow(a, d, n)
        log_text.insert(tk.END, f"计算 x = a^d mod n = {x}\n")
        # 如果 x 等于 1 或 n - 1，继续下一次测试
        if x == 1 or x == n - 1:
            log_text.insert(tk.END, f"x 等于 1 或 n - 1，继续下一次测试。\n")
            continue
        # 进行 s - 1 次平方运算
        for j in range(s - 1):
            x = pow(x, 2, n)
            log_text.insert(tk.END, f"第 {j + 1} 次平方运算，x = {x}\n")
            # 如果 x 等于 n - 1，跳出循环
            if x == n - 1:
                log_text.insert(tk.END, f"x 等于 n - 1，跳出循环。\n")
                break
        else:
            # 如果没有找到 n - 1，说明 n 是合数
            log_text.insert(tk.END, f"经过 {k} 次测试，未找到 n - 1，{n} 是合数。\n")
            return False
    # 经过 k 次测试后，认为 n 可能是素数
    log_text.insert(tk.END, f"经过 {k} 次测试，{n} 可能是素数。\n")
    return True

# 定义生成大素数的函数
def generate_large_prime(bits=512):
    """
    生成指定位数的大素数。
    该函数通过随机生成指定位数的数，并使用 Miller-Rabin 素性测试来判断是否为素数。
    :param bits: 素数的位数
    :return: 生成的大素数
    """
    log_text.insert(tk.END, f"开始生成 {bits} 位的大素数...\n")
    while True:
        # 随机生成一个指定位数的数
        p = secrets.randbits(bits)
        # 确保最高位为 1，且是奇数
        p |= (1 << (bits - 1)) | 1
        log_text.insert(tk.END, f"随机生成数 p = {p}，开始进行素性测试...\n")
        # 使用 Miller-Rabin 素性测试判断 p 是否为素数
        if is_prime(p):
            log_text.insert(tk.END, f"找到大素数 p = {p}\n")
            return p

# 定义寻找模 p 的原根的函数
def find_primitive_root(p):
    """
    寻找模 p 的原根（生成元）。
    原根是指一个数 g，使得 g 的幂次可以生成模 p 的所有非零元素。
    :param p: 大素数
    :return: 模 p 的一个原根
    """
    log_text.insert(tk.END, f"开始寻找模 {p} 的原根...\n")
    # 当 p 为 2 时，原根为 1
    if p == 2:
        log_text.insert(tk.END, f"p 为 2，原根为 1。\n")
        return 1
    # 分解 p - 1 为 2^s * d 的形式
    p1 = p - 1
    factors = []
    d = p1
    while d % 2 == 0:
        factors.append(2)
        d //= 2
    log_text.insert(tk.END, f"p - 1 分解为 2^{len(factors)} * {d}\n")
    # 测试随机数 g 直到找到原根
    while True:
        # 随机选择一个 2 到 p - 1 之间的数 g
        g = secrets.randbelow(p - 2) + 2
        log_text.insert(tk.END, f"随机选择 g = {g}，开始检查是否为原根...\n")
        # 检查 g 是否为原根
        for factor in factors:
            result = pow(g, (p - 1) // factor, p)
            log_text.insert(tk.END, f"计算 g^((p - 1) / {factor}) mod p = {result}\n")
            if result == 1:
                log_text.insert(tk.END, f"g 不是原根，继续寻找。\n")
                break
        else:
            # 如果 g 满足条件，返回 g
            log_text.insert(tk.END, f"找到原根 g = {g}\n")
            return g

# 定义生成 ElGamal 密钥对的函数
def generate_keys(bits=512):
    """
    生成 ElGamal 的公钥和私钥。
    ElGamal 是一种基于离散对数问题的公钥加密算法。
    :param bits: 素数的位数
    :return: 公钥 (p, g, h) 和私钥 (p, x)
    """
    log_text.insert(tk.END, f"开始生成 ElGamal 密钥对，素数位数为 {bits}...\n")
    # 生成大素数 p
    p = generate_large_prime(bits)
    # 寻找 p 的原根 g
    g = find_primitive_root(p)
    # 生成私钥 x，1 <= x <= p - 2
    x = secrets.randbelow(p - 2) + 1
    log_text.insert(tk.END, f"生成私钥 x = {x}\n")
    # 计算公钥 h = g^x mod p
    h = pow(g, x, p)
    log_text.insert(tk.END, f"计算公钥 h = g^x mod p = {h}\n")
    public_key = (p, g, h)
    private_key = (p, x)
    log_text.insert(tk.END, f"生成公钥 (p, g, h) = {public_key}，私钥 (p, x) = {private_key}\n")
    return public_key, private_key

# 定义将字节转换为整数的函数
def bytes_to_int(b):
    """
    将字节转换为整数。
    :param b: 字节对象
    :return: 转换后的整数
    """
    return int.from_bytes(b, byteorder='big')

# 定义将整数转换为字节的函数
def int_to_bytes(i):
    """
    将整数转换为字节。
    :param i: 整数
    :return: 转换后的字节对象
    """
    return i.to_bytes((i.bit_length() + 7) // 8, byteorder='big')

# 定义使用公钥加密明文的函数
def encrypt(public_key, plaintext):
    """
    使用公钥加密明文。
    :param public_key: 公钥元组 (p, g, h)
    :param plaintext: 明文字符串
    :return: 密文元组 (c1, c2)
    """
    p, g, h = public_key
    log_text.insert(tk.END, f"开始使用公钥 (p, g, h) = {public_key} 加密明文 '{plaintext}'...\n")
    # 将明文转换为整数 m
    m = bytes_to_int(plaintext.encode('utf-8'))
    log_text.insert(tk.END, f"将明文转换为整数 m = {m}\n")
    # 检查明文是否过大
    if m >= p:
        log_text.insert(tk.END, f"明文过大，m = {m} >= p = {p}，加密失败。\n")
        raise ValueError("明文过大，请缩短明文或使用更大的素数位数")
    # 生成随机数 y，1 <= y <= p - 2
    y = secrets.randbelow(p - 2) + 1
    log_text.insert(tk.END, f"生成随机数 y = {y}\n")
    # 计算 c1 = g^y mod p
    c1 = pow(g, y, p)
    log_text.insert(tk.END, f"计算 c1 = g^y mod p = {c1}\n")
    # 计算共享密钥 s = h^y mod p
    s = pow(h, y, p)
    log_text.insert(tk.END, f"计算共享密钥 s = h^y mod p = {s}\n")
    # 计算 c2 = m * s mod p
    c2 = (m * s) % p
    log_text.insert(tk.END, f"计算 c2 = m * s mod p = {c2}\n")
    log_text.insert(tk.END, f"加密完成，密文 (c1, c2) = ({c1}, {c2})\n")
    return (c1, c2)

# 定义使用私钥解密密文的函数
def decrypt(private_key, ciphertext):
    """
    使用私钥解密密文。
    :param private_key: 私钥元组 (p, x)
    :param ciphertext: 密文元组 (c1, c2)
    :return: 解密后的明文字符串
    """
    p, x = private_key
    c1, c2 = ciphertext
    log_text.insert(tk.END, f"开始使用私钥 (p, x) = {private_key} 解密密文 (c1, c2) = {ciphertext}...\n")
    # 计算共享密钥 s = c1^x mod p
    s = pow(c1, x, p)
    log_text.insert(tk.END, f"计算共享密钥 s = c1^x mod p = {s}\n")
    # 计算 s 的模逆元
    s_inv = pow(s, p - 2, p)
    log_text.insert(tk.END, f"计算 s 的模逆元 s_inv = {s_inv}\n")
    # 计算原始消息 m = c2 * s_inv mod p
    m = (c2 * s_inv) % p
    log_text.insert(tk.END, f"计算原始消息 m = c2 * s_inv mod p = {m}\n")
    # 将整数转换为字节，再解码为字符串
    decrypted = int_to_bytes(m).decode('utf-8', errors='replace')
    log_text.insert(tk.END, f"解密完成，解密后的消息为 '{decrypted}'\n")
    return decrypted

def generate_and_encrypt():
    try:
        bits = int(bits_entry.get())
        if bits < 512:
            messagebox.showwarning("警告", "素数位数建议至少为 512 位，以确保安全性。请重新输入。")
            return
        # 清空日志
        log_text.delete(1.0, tk.END)
        # 生成密钥对
        status_label.config(text="正在生成密钥对，请稍候...")
        root.update()
        public_key, private_key = generate_keys(bits)
        status_label.config(text=f"生成成功！公钥(p, g, h) = {public_key}，私钥中 x = {private_key[1]}")

        plaintext = plaintext_entry.get()
        try:
            # 加密过程
            ciphertext = encrypt(public_key, plaintext)
            ciphertext_label.config(text=f"加密后的密文(c1, c2) = {ciphertext}")

            # 解密过程
            decrypted = decrypt(private_key, ciphertext)
            decrypted_label.config(text=f"解密后的消息：{decrypted}")
        except ValueError as e:
            messagebox.showerror("加密失败", f"{e}\n请缩短明文或重新输入素数位数。")
    except ValueError:
        messagebox.showerror("输入错误", "请输入有效的素数位数（整数）。")


# 创建主窗口
root = tk.Tk()
root.title("ElGamal 公钥加密算法演示")

# 创建标签和输入框
bits_label = tk.Label(root, text="请输入素数位数（推荐至少 512 位）：")
bits_label.pack(pady=10)
bits_entry = tk.Entry(root)
bits_entry.pack(pady=5)

plaintext_label = tk.Label(root, text="请输入要加密的消息：")
plaintext_label.pack(pady=10)
plaintext_entry = tk.Entry(root, width=50)
plaintext_entry.pack(pady=5)

# 创建按钮
encrypt_button = tk.Button(root, text="生成密钥并加密", command=generate_and_encrypt)
encrypt_button.pack(pady=20)

# 创建状态标签
status_label = tk.Label(root, text="")
status_label.pack(pady=10)

# 创建密文和明文显示标签
ciphertext_label = tk.Label(root, text="")
ciphertext_label.pack(pady=10)
decrypted_label = tk.Label(root, text="")
decrypted_label.pack(pady=10)

# 创建日志文本框
log_text = scrolledtext.ScrolledText(root, height=20, width=80)
log_text.pack(pady=20)

# 运行主循环
root.mainloop()