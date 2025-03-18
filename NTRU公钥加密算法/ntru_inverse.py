from wolframclient.evaluation import WolframLanguageSession
from wolframclient.language import wlexpr
import json

KERNEL_PATH = r"D:\Mathematica\11.3\MathKernel.exe"


def compute_poly_inverse():
    session = WolframLanguageSession(KERNEL_PATH)
    try:
        moduli = [3, 41]
        results = {}
        for modulus in moduli:
            full_code = f"""
            Block[{{
                $OutputSizeLimit = Infinity,
                PageWidth = Infinity,
                $DisplayFunction = Identity,
                $NestLimit = Infinity,
                $RecursionLimit = Infinity
            }},
            ToString[
                PolynomialExtendedGCD[
                    x^6 - x^4 + x^3 + x^2 - 1, 
                    x^7 - 1, 
                    x, 
                    Modulus -> {modulus}
                ], 
                InputForm
            ]
            ]
            """
            res_str = session.evaluate(wlexpr(full_code))
            results[f"mod_{modulus}"] = res_str

        inverse_data = {"result": results}
        with open("inverse_result.json", "w") as f:
            json.dump(inverse_data, f)
        print("逆元结果已保存到 inverse_result.json")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        session.stop()


if __name__ == "__main__":
    compute_poly_inverse()
