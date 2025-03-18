# 1. 计算多项式逆元 #
### 运行ntru_inverse.py脚本，该脚本将使用 Wolfram Mathematica 计算多项式的逆元，并将结果保存到inverse_result.json文件中。

``` python ntru_inverse.py ```

# 2. 执行加密和解密操作 #
### 运行ntru_encrypt.py脚本，该脚本将加载逆元结果，生成公钥，对明文进行加密，并对密文进行解密。

```python ntru_encrypt.py```

# 代码结构 #
### ntru_inverse.py：使用 Wolfram Mathematica 计算多项式的逆元，并将结果保存到 JSON 文件中。

### ntru_encrypt.py：实现 NTRU 加密算法的主要功能，包括密钥生成、加密和解密。

### inverse_result.json：保存多项式逆元的计算结果。


## 注：
在 `PolynomialExtendedGCD` 的输出中：  
1. **第一个元素 ：表示在模 p(q) 条件下，输入的两个多项式 f(x)和 \( x^N - 1 \) 的最大公因式（GCD）**。  

2. #### 后面两个多项式 ：u(x)  和  v(x)  是贝祖等式（Bézout's identity）的系数多项式，即u(x)f(x)+v(x)(x^N-1)=1。  
  
