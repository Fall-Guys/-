import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import math


class RSA:
    def __init__(self):
        self.public_key = None  # 公钥(e, n)
        self.private_key = None  # 私钥(d, n)

    def is_prime(self, n, k=5):
        """Miller-Rabin素性测试"""
        if n <= 1:
            return False
        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        if n in small_primes:
            return True
        for p in small_primes:
            if n % p == 0:
                return False

        d = n - 1
        s = 0
        while d % 2 == 0:
            d //= 2
            s += 1

        for _ in range(k):
            a = random.randint(2, min(n - 2, int(math.sqrt(n)) + 1))
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for __ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True

    def gcd(self, a, b):
        """计算最大公约数"""
        while b != 0:
            a, b = b, a % b
        return a

    def extended_gcd(self, a, b):
        """扩展欧几里得算法求模逆元"""
        if b == 0:
            return (a, 1, 0)
        else:
            g, x, y = self.extended_gcd(b, a % b)
            return (g, y, x - (a // b) * y)

    def generate_keys(self, p, q, e=None):
        """生成RSA密钥对"""
        # 验证素数输入
        if not (self.is_prime(p) and self.is_prime(q)):
            raise ValueError("p和q必须都是质数")
        if p == q:
            raise ValueError("p和q不能相同")

        n = p * q
        phi = (p - 1) * (q - 1)

        # 处理公钥指数e
        if e is not None:
            if e < 2 or e >= phi:
                raise ValueError("e必须在[2, φ(n))范围内")
            if self.gcd(e, phi) != 1:
                raise ValueError("e必须与φ(n)互质")
        else:
            # 优先尝试使用65537
            e = 65537
            if self.gcd(e, phi) != 1:
                # 随机选择合适的e
                e = random.randint(2, phi - 1)
                while self.gcd(e, phi) != 1:
                    e = random.randint(2, phi - 1)

        # 计算私钥指数d
        _, d, _ = self.extended_gcd(e, phi)
        d %= phi  # 保证d为正数

        self.public_key = (e, n)
        self.private_key = (d, n)
        return (e, n), (d, n)

    def encrypt(self, plaintext):
        """加密文本消息"""
        e, n = self.public_key
        byte_data = plaintext.encode('utf-8')
        m = int.from_bytes(byte_data, 'big')
        if m >= n:
            raise ValueError("明文过大，请使用更大密钥或分段加密")
        return pow(m, e, n)

    def encrypt_number(self, number):
        """加密数值消息"""
        e, n = self.public_key
        if number < 0:
            raise ValueError("加密数值不能为负数")
        if number >= n:
            raise ValueError(f"数值过大（必须 < {n}）")
        return pow(number, e, n)

    def decrypt(self, ciphertext):
        """解密密文"""
        d, n = self.private_key
        m = pow(ciphertext, d, n)
        byte_length = (m.bit_length() + 7) // 8
        return m.to_bytes(byte_length, 'big').decode('utf-8')


class RSAApp:
    def __init__(self, master):
        self.master = master
        master.title("RSA算法交互演示")
        self.rsa = RSA()

        # 界面布局
        main_frame = ttk.Frame(master, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 密钥生成区域
        key_frame = ttk.LabelFrame(main_frame, text="密钥生成", padding=10)
        key_frame.pack(fill=tk.X, pady=5)

        # 新增随机生成密钥对按钮
        ttk.Button(key_frame, text="随机生成密钥对", command=self.random_generate_keys).pack(side=tk.LEFT, pady=5, padx=5)
        ttk.Button(key_frame, text="手动生成密钥对", command=self.manual_generate_keys).pack(side=tk.LEFT, pady=5, padx=5)

        self.public_key_text = tk.Text(key_frame, height=3, width=60)
        self.public_key_text.pack(pady=5)
        self.private_key_text = tk.Text(key_frame, height=3, width=60)
        self.private_key_text.pack(pady=5)

        # 加解密操作区域
        operation_frame = ttk.Frame(main_frame)
        operation_frame.pack(fill=tk.BOTH, expand=True)

        # 加密区
        encrypt_frame = ttk.LabelFrame(operation_frame, text="加密", padding=10)
        encrypt_frame.grid(row=0, column=0, padx=5, sticky=tk.NSEW)

        # 输入类型选择
        self.input_type = tk.StringVar(value="auto")
        input_type_frame = ttk.Frame(encrypt_frame)
        input_type_frame.pack(pady=5)
        ttk.Label(input_type_frame, text="输入类型:").pack(side=tk.LEFT)
        ttk.Radiobutton(input_type_frame, text="自动", variable=self.input_type,
                        value="auto").pack(side=tk.LEFT)
        ttk.Radiobutton(input_type_frame, text="数值", variable=self.input_type,
                        value="number").pack(side=tk.LEFT)
        ttk.Radiobutton(input_type_frame, text="文本", variable=self.input_type,
                        value="text").pack(side=tk.LEFT)

        self.plaintext_entry = tk.Text(encrypt_frame, height=5, width=30)
        self.plaintext_entry.pack(pady=5)
        ttk.Button(encrypt_frame, text="加密", command=self.encrypt).pack()

        # 解密区
        decrypt_frame = ttk.LabelFrame(operation_frame, text="解密", padding=10)
        decrypt_frame.grid(row=0, column=1, padx=5, sticky=tk.NSEW)
        self.ciphertext_entry = tk.Text(decrypt_frame, height=5, width=30)
        self.ciphertext_entry.pack(pady=5)
        ttk.Button(decrypt_frame, text="解密", command=self.decrypt).pack()

        # 示例按钮
        ttk.Button(main_frame, text="显示示例", command=self.show_example).pack(pady=10)

    def random_generate_keys(self):
        """随机生成密钥对"""
        try:
            # 随机生成两个不同的素数
            while True:
                p = random.randint(100, 100000)
                if self.rsa.is_prime(p):
                    break
            while True:
                q = random.randint(100, 100000)
                if self.rsa.is_prime(q) and q != p:
                    break

            # 生成密钥对
            public, private = self.rsa.generate_keys(p, q)

            # 显示密钥
            self.public_key_text.delete('1.0', tk.END)
            self.public_key_text.insert(tk.END, f"公钥 (e, n):\n{public}")
            self.private_key_text.delete('1.0', tk.END)
            self.private_key_text.insert(tk.END, f"私钥 (d, n):\n{private}")

        except Exception as e:
            messagebox.showerror("生成错误", f"密钥生成失败: {str(e)}")

    def manual_generate_keys(self):
        """手动生成密钥对"""
        try:
            # 获取素数输入
            p = self.get_prime_input("请输入第一个大素数p")
            q = self.get_prime_input("请输入第二个大素数q")

            # 计算φ(n)用于提示
            phi = (p - 1) * (q - 1)
            hint = f"φ(n) = {phi}\n推荐选择与φ(n)互质的数（如65537）"

            # 获取公钥指数e
            e = self.get_e_input(phi)

            # 生成密钥对
            public, private = self.rsa.generate_keys(p, q, e)

            # 显示密钥
            self.public_key_text.delete('1.0', tk.END)
            self.public_key_text.insert(tk.END, f"公钥 (e, n):\n{public}")
            self.private_key_text.delete('1.0', tk.END)
            self.private_key_text.insert(tk.END, f"私钥 (d, n):\n{private}")

        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
        except Exception as e:
            messagebox.showerror("生成错误", f"密钥生成失败: {str(e)}")

    def get_prime_input(self, prompt):
        """获取并验证素数输入"""
        while True:
            value = simpledialog.askinteger("输入素数", prompt)
            if value is None:
                raise ValueError("输入已取消")

            if value < 2:
                messagebox.showerror("错误", "素数必须大于1")
                continue

            if not self.rsa.is_prime(value):
                if messagebox.askretrycancel("警告", "输入的不是质数，是否重试？"):
                    continue
                else:
                    raise ValueError("输入的不是质数")
            return value

    def get_e_input(self, phi):
        """获取公钥指数e输入"""
        hint = f"φ(n) = {phi}\n请输入与φ(n)互质的整数（留空使用默认值）"
        while True:
            value = simpledialog.askinteger(
                "输入公钥指数e",
                hint,
                minvalue=2,
                maxvalue=phi - 1
            )

            # 用户取消输入
            if value is None:
                return None  # 使用默认处理

            # 验证互质
            if math.gcd(value, phi) != 1:
                messagebox.showerror("错误", "e必须与φ(n)互质")
                continue

            return value

    def encrypt(self):
        """执行加密操作"""
        if not self.rsa.public_key:
            messagebox.showerror("错误", "请先生成密钥对！")
            return

        plaintext = self.plaintext_entry.get("1.0", tk.END).strip()
        if not plaintext:
            messagebox.showerror("错误", "请输入要加密的明文")
            return

        try:
            input_mode = self.input_type.get()
            if input_mode == "number":
                ciphertext = self.rsa.encrypt_number(int(plaintext))
            elif input_mode == "text":
                ciphertext = self.rsa.encrypt(plaintext)
            else:
                try:
                    ciphertext = self.rsa.encrypt_number(int(plaintext))
                except ValueError:
                    ciphertext = self.rsa.encrypt(plaintext)

            self.ciphertext_entry.delete('1.0', tk.END)
            self.ciphertext_entry.insert(tk.END, str(ciphertext))
        except Exception as e:
            messagebox.showerror("加密错误", str(e))

    def decrypt(self):
        """执行解密操作"""
        if not self.rsa.private_key:
            messagebox.showerror("错误", "没有可用的私钥")
            return

        ciphertext = self.ciphertext_entry.get("1.0", tk.END).strip()
        if not ciphertext:
            messagebox.showerror("错误", "请输入要解密的密文")
            return

        try:
            plaintext = self.rsa.decrypt(int(ciphertext))
            self.plaintext_entry.delete('1.0', tk.END)
            self.plaintext_entry.insert(tk.END, plaintext)
        except Exception as e:
            messagebox.showerror("解密错误", str(e))

    def show_example(self):
        """显示使用示例"""
        example_text = (
            "使用步骤：\n"
            "1. 可以选择点击'随机生成密钥对'或'手动生成密钥对'\n"
            "   手动生成：输入两个不同的质数（如101和103），输入公钥指数e（可选，留空使用默认值）\n"
            "2. 选择输入类型：\n"
            "   自动模式：自动识别数字/文本\n"
            "   数值模式：输入纯数字（如123）\n"
            "   文本模式：输入任意字符（如Hello）\n"
            "3. 加密/解密测试：\n"
            "   在明文区输入内容点击加密\n"
            "   复制密文到解密区点击解密"
        )
        messagebox.showinfo("示例说明", example_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = RSAApp(root)
    root.mainloop()