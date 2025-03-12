import tkinter as tk
from tkinter import messagebox, simpledialog
import math
import random


class MerkleHellman:
    def __init__(self):
        self.r = []  # 超递增序列
        self.A = 0
        self.B = 0
        self.M = []  # 公钥

    def generate_super_increasing(self, n=5):
        """生成超递增序列"""
        if n < 2:
            return []
        sequence = [random.randint(1, 100)]
        for _ in range(n - 1):
            next_num = sum(sequence) + random.randint(1, 50)
            sequence.append(next_num)
        return sequence

    def generate_A_B(self, r):
        """生成A和B"""
        max_r = r[-1]
        while True:
            self.B = random.randint(2 * max_r, 2 * max_r + 100)
            self.A = random.randint(1, self.B - 1)
            if math.gcd(self.A, self.B) == 1:
                break

    def create_public_key(self):
        """生成公钥M"""
        self.M = [(self.A * ri) % self.B for ri in self.r]

    def encrypt(self, plaintext):
        """加密"""
        if not all(c in '01' for c in plaintext):
            raise ValueError("明文必须是二进制字符串")
        if len(plaintext) > len(self.M):
            raise ValueError(f"明文长度不能超过{len(self.M)}位")
        return sum(int(bit) * mi for bit, mi in zip(plaintext, self.M))

    def decrypt(self, ciphertext):
        """解密"""
        # 计算S' = A^-1 * S mod B
        A_inv = self.mod_inverse(self.A, self.B)
        s_prime = (A_inv * ciphertext) % self.B

        # 解子集和问题
        plaintext = []
        for ri in reversed(self.r):
            if s_prime >= ri:
                plaintext.append('1')
                s_prime -= ri
            else:
                plaintext.append('0')
        return ''.join(reversed(plaintext))

    def mod_inverse(self, a, m):
        """求模逆元"""
        if math.gcd(a, m) != 1:
            raise ValueError("模逆元不存在")
        return pow(a, -1, m)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Merkle-Hellman密码算法演示")
        self.mh = MerkleHellman()

        # 界面组件
        self.create_widgets()

    def create_widgets(self):
        # 超递增序列长度输入
        tk.Label(self.root, text="超递增序列长度:").grid(row=0, column=0, sticky=tk.W)
        self.entry_r_length = tk.Entry(self.root, width=5)
        self.entry_r_length.grid(row=0, column=1)
        self.entry_r_length.insert(0, "5")  # 默认长度

        # 超递增序列部分
        tk.Label(self.root, text="超递增序列:").grid(row=1, column=0, sticky=tk.W)
        self.btn_gen_r_random = tk.Button(self.root, text="随机生成超递增序列", command=self.gen_r_random)
        self.btn_gen_r_random.grid(row=1, column=1)
        self.btn_gen_r_manual = tk.Button(self.root, text="手动输入超递增序列", command=self.gen_r_manual)
        self.btn_gen_r_manual.grid(row=1, column=2)

        # A和B部分
        tk.Label(self.root, text="A和B:").grid(row=2, column=0, sticky=tk.W)
        self.btn_gen_AB_random = tk.Button(self.root, text="随机生成A,B", command=self.gen_AB_random)
        self.btn_gen_AB_random.grid(row=2, column=1)
        self.btn_gen_AB_manual = tk.Button(self.root, text="手动输入A,B", command=self.gen_AB_manual)
        self.btn_gen_AB_manual.grid(row=2, column=2)

        # 清空功能
        self.btn_clear = tk.Button(self.root, text="清空所有", command=self.clear_all)
        self.btn_clear.grid(row=2, column=3)

        # 公钥显示
        tk.Label(self.root, text="公钥M:").grid(row=3, column=0, sticky=tk.W)
        self.txt_M = tk.Text(self.root, height=1, width=50)
        self.txt_M.grid(row=3, column=1, columnspan=2)

        # 加密解密部分
        tk.Label(self.root, text="二进制明文:").grid(row=4, column=0, sticky=tk.W)
        self.entry_plaintext = tk.Entry(self.root)
        self.entry_plaintext.grid(row=4, column=1)
        self.btn_encrypt = tk.Button(self.root, text="加密", command=self.do_encrypt)
        self.btn_encrypt.grid(row=4, column=2)

        tk.Label(self.root, text="密文:").grid(row=5, column=0, sticky=tk.W)
        self.entry_ciphertext = tk.Entry(self.root)
        self.entry_ciphertext.grid(row=5, column=1)
        self.btn_decrypt = tk.Button(self.root, text="解密", command=self.do_decrypt)
        self.btn_decrypt.grid(row=5, column=2)

        # 结果显示
        self.txt_result = tk.Text(self.root, height=10, width=60)
        self.txt_result.grid(row=6, column=0, columnspan=3)

    def gen_r_random(self):
        """随机生成超递增序列"""
        try:
            length = int(self.entry_r_length.get())
            self.mh.r = self.mh.generate_super_increasing(length)
            self.txt_result.insert(tk.END, f"随机生成超递增序列: {self.mh.r}\n")
        except:
            messagebox.showerror("错误", "请输入有效的长度数字")

    def gen_r_manual(self):
        """手动输入超递增序列"""
        input_str = simpledialog.askstring("输入", "请输入超递增序列（逗号分隔）")
        if input_str:
            try:
                self.mh.r = [int(x.strip()) for x in input_str.split(',')]
                self.txt_result.insert(tk.END, f"手动输入超递增序列: {self.mh.r}\n")
            except:
                messagebox.showerror("错误", "输入格式错误")

    def gen_AB_random(self):
        """随机生成A,B"""
        if not self.mh.r:
            messagebox.showerror("错误", "请先生成超递增序列")
            return
        self.mh.generate_A_B(self.mh.r)
        self.txt_result.insert(tk.END, f"随机生成A={self.mh.A}, B={self.mh.B}\n")
        self.mh.create_public_key()
        self.txt_M.delete(1.0, tk.END)
        self.txt_M.insert(tk.END, self.mh.M)

    def gen_AB_manual(self):
        """手动输入A,B"""
        if not self.mh.r:
            messagebox.showerror("错误", "请先生成超递增序列")
            return
        A = simpledialog.askinteger("输入", "请输入A")
        B = simpledialog.askinteger("输入", "请输入B")
        if A and B:
            if B > 2 * self.mh.r[-1] and math.gcd(A, B) == 1:
                self.mh.A = A
                self.mh.B = B
                self.txt_result.insert(tk.END, f"手动输入A={self.mh.A}, B={self.mh.B}\n")
                self.mh.create_public_key()
                self.txt_M.delete(1.0, tk.END)
                self.txt_M.insert(tk.END, self.mh.M)
            else:
                messagebox.showerror("错误", "不满足B>2*r[-1]或gcd(A,B)!=1")

    def do_encrypt(self):
        """执行加密"""
        if not self.mh.M:
            messagebox.showerror("错误", "请先生成公钥")
            return
        plaintext = self.entry_plaintext.get()
        try:
            ciphertext = self.mh.encrypt(plaintext)
            self.entry_ciphertext.delete(0, tk.END)
            self.entry_ciphertext.insert(0, ciphertext)
            self.txt_result.insert(tk.END, f"加密过程：明文{plaintext} → 密文{ciphertext}\n")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def do_decrypt(self):
        """执行解密"""
        if not self.mh.r or not self.mh.A or not self.mh.B:
            messagebox.showerror("错误", "请先完成密钥生成")
            return
        try:
            ciphertext = int(self.entry_ciphertext.get())
            plaintext = self.mh.decrypt(ciphertext)
            self.txt_result.insert(tk.END, f"解密过程：密文{ciphertext} → 明文{plaintext}\n")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def clear_all(self):
        """清空所有内容"""
        self.mh.r = []
        self.mh.A = 0
        self.mh.B = 0
        self.mh.M = []
        self.txt_result.delete(1.0, tk.END)
        self.txt_M.delete(1.0, tk.END)
        self.entry_plaintext.delete(0, tk.END)
        self.entry_ciphertext.delete(0, tk.END)
        self.entry_r_length.delete(0, tk.END)
        self.entry_r_length.insert(0, "5")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()