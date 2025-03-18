import numpy as np
import json
import os


class NTRUCrypt:
    def __init__(self, N=7, p=3, q=41, d=2):
        self.N = N  # 多项式阶数
        self.p = p  # 小模数
        self.q = q  # 大模数
        self.d = d  # 参数 d

    def parse_polynomial(self, poly_str):
        """将多项式字符串解析为系数列表"""
        poly_str = poly_str.replace("{", "").replace("}", "")
        terms = poly_str.split(", ")
        coeffs = np.zeros(self.N, dtype=int)
        for term in terms:
            if "+" in term:
                parts = term.split("+")
                for part in parts:
                    self._parse_term(part, coeffs)
            else:
                self._parse_term(term, coeffs)
        return coeffs

    def _parse_term(self, term, coeffs):
        term = term.strip()
        if term.isdigit():
            coeffs[0] = int(term)
        elif "x" in term:
            if "^" in term:
                if "*" in term:
                    power_part, power = term.split("x^")
                    coeff_part, _ = power_part.split("*")
                    power = int(power)
                    coeff = int(coeff_part)
                else:
                    power_part, power = term.split("x^")
                    power = int(power)
                    if power_part:
                        coeff = int(power_part)
                    else:
                        coeff = 1
                coeffs[power] = coeff
            else:
                if term == "x":
                    coeffs[1] = 1
                elif "*" in term:
                    coeff_part, _ = term.split("*")
                    coeffs[1] = int(coeff_part)
                else:
                    coeff_part, _ = term.split("x")
                    coeffs[1] = int(coeff_part)

    def load_inverse_from_mathematica(self, filename="inverse_result.json"):
        """加载 Mathematica 计算的逆元"""
        if not os.path.exists(filename):
            print(f"错误: 文件 {filename} 不存在。请先运行 ntru_inverse.py 生成该文件。")
            return
        with open(filename, "r") as f:
            data = json.load(f)
        try:
            mod_3_str = data["result"]["mod_3"]
            mod_41_str = data["result"]["mod_41"]
            # 提取 u(x) 的系数
            mod_3_poly_str = mod_3_str.split(", {")[1].split(", ")[0].replace("}", "")
            mod_41_poly_str = mod_41_str.split(", {")[1].split(", ")[0].replace("}", "")
            self.f = np.array([-1, 0, 1, 1, -1, 0, 1])  # f(x)=-1+x^2+x^3-x^4+x^6
            self.F_p = self.parse_polynomial(mod_3_poly_str)
            self.F_q = self.parse_polynomial(mod_41_poly_str)
            print("F_p(x) 的系数:", self.F_p)
            print("F_q(x) 的系数:", self.F_q)
        except (KeyError, ValueError) as e:
            print(f"解析 JSON 文件时出错: {e}")
            print(f"JSON 文件内容: {data}")

    def poly_mult(self, a, b, mod=None):
        """多项式乘法（循环卷积）"""
        conv = np.convolve(a, b)
        result = np.zeros(self.N, dtype=int)
        for i in range(self.N):
            result[i] = conv[i] + (conv[i + self.N] if i + self.N < len(conv) else 0)
        if mod is None:
            mod = self.q
        return result % mod

    def generate_keys(self):
        """生成公钥 h = F_q * g mod q"""
        self.g = np.array([0, -1, -1, 0, 1, 0, 1])  # g(x)=-x-x^2+x^4+x^6
        self.h = self.poly_mod(self.poly_mult(self.F_q, self.g), self.q)
        print("生成的公钥 h(x) 系数:", self.h)
        return self.h

    def encrypt(self, m, h, r):
        """加密: e = p * r * h + m mod q"""
        e = self.poly_mod(self.p * self.poly_mult(r, h), self.q) + m
        return self.poly_mod(e, self.q)

    def decrypt(self, e):
        # 计算 f(x) * e(x) 并对 q 取模
        fe_product = self.poly_mult(self.f, e, mod=self.q)
        fe_mod_q = self.poly_mod(fe_product, self.q)

        # 第一次中心提升（模 q）
        center_lifted_q = np.where(fe_mod_q > self.q / 2, fe_mod_q - self.q, fe_mod_q)
        # print("第一次中心提升（模 q）结果:", center_lifted_q)

        # 对中心提升后的结果模 p
        a_mod_p = self.poly_mod(center_lifted_q, self.p)

        # 计算 F_p(x) * a(x) 模 p
        fp_a_product = self.poly_mult(self.F_p, a_mod_p, mod=self.p)
        # print("F_p(x) 乘 a(x) 模 p 结果:", fp_a_product)

        # 第二次中心提升（模 p）
        center_lifted_p = np.where(fp_a_product > self.p / 2, fp_a_product - self.p, fp_a_product)
        # print("第二次中心提升（模 p）结果:", center_lifted_p)

        return center_lifted_p

    def poly_mod(self, poly, modulus):
        """多项式模约简"""
        return np.mod(poly, modulus)


if __name__ == "__main__":
    ntru = NTRUCrypt()
    ntru.load_inverse_from_mathematica()
    if hasattr(ntru, 'f') and hasattr(ntru, 'F_p') and hasattr(ntru, 'F_q'):
        public_key = ntru.generate_keys()
        m = np.array([1, -1, 1, 1, 0, -1, 0])  # m(x)=-x^5 + x^3 + x^2 - x + 1
        r = np.array([-1, 1, 0, 0, 0, -1, 1])  # r(x)=-1 + x- x^5 + x^6
        ciphertext = ntru.encrypt(m, public_key, r)
        decrypted = ntru.decrypt(ciphertext)
        print("原始明文:", m)
        print("密文:", ciphertext)
        print("解密结果（最终明文）:", decrypted)
        print("解密是否成功:", np.array_equal(m, decrypted))
    else:
        print("无法继续执行，因为未成功加载逆元。")