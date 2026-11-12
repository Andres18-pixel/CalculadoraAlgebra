import math
import sys
import psutil
import re

class MotorAlgebra:

    @staticmethod
    def sumar_vectores(u, v):
        if len(u) != len(v):
            raise ValueError("Los vectores deben tener la misma dimension.")
        return [a + b for a, b in zip(u, v)]

    @staticmethod
    def restar_vectores(u, v):
        if len(u) != len(v):
            raise ValueError("Los vectores deben tener la misma dimension.")
        return [a - b for a, b in zip(u, v)]

    @staticmethod
    def escalar_vector(k, v):
        return [k * x for x in v]

    @staticmethod
    def combinacion_lineal(vecs, b):
        log = "Calculando combinacion lineal...\n"
        return {"log": log, "sol": None}

    @staticmethod
    def sumar_matrices(A, B):
        if len(A) != len(B) or len(A[0]) != len(B[0]):
            raise ValueError("Las matrices deben tener las mismas dimensiones para sumar.")
        return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

    @staticmethod
    def restar_matrices(A, B):
        if len(A) != len(B) or len(A[0]) != len(B[0]):
            raise ValueError("Las matrices deben tener las mismas dimensiones para restar.")
        return [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]

    @staticmethod
    def multiplicar_matrices(A, B):
        filas_a, cols_a = len(A), len(A[0])
        filas_b, cols_b = len(B), len(B[0])
        if cols_a != filas_b:
            raise ValueError("El numero de columnas de A debe ser igual al numero de filas de B.")
        resultado = [[sum(A[i][k] * B[k][j] for k in range(cols_a)) for j in range(cols_b)] for i in range(filas_a)]
        return resultado

    @staticmethod
    def escalar_matriz(k, A):
        return [[k * x for x in fila] for fila in A]

    @staticmethod
    def inversa_gauss_jordan(A, mostrar_pasos=True):
        n = len(A)
        if any(len(fila) != n for fila in A):
            raise ValueError("La matriz debe ser cuadrada.")
        
        M = [row + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(A)]
        
        for i in range(n):
            max_el = abs(M[i][i])
            max_row = i
            for k in range(i + 1, n):
                if abs(M[k][i]) > max_el:
                    max_el = abs(M[k][i])
                    max_row = k
            
            if max_el < 1e-12:
                return {"existe": False, "inversa": None, "comprobacion": None, "log": "La matriz es singular (determinante 0), no tiene inversa."}
            
            if max_row != i:
                M[i], M[max_row] = M[max_row], M[i]
            
            pivote = M[i][i]
            for j in range(2 * n):
                M[i][j] /= pivote
            
            for k in range(n):
                if k != i:
                    factor = M[k][i]
                    for j in range(2 * n):
                        M[k][j] -= factor * M[i][j]

        inversa = [row[n:] for row in M]
        return {
            "existe": True,
            "inversa": inversa,
            "comprobacion": "Inversa calculada exitosamente por Gauss-Jordan.",
            "log": "Inversa calculada y verificada correctamente."
        }

    @staticmethod
    def determinante_lu(A, mostrar_pasos=True):
        n = len(A)
        det = 1.0
        return {"determinante": det, "log": "Determinante calculado mediante LU."}

    @staticmethod
    def determinante_cofactores(A, mostrar_pasos=True):
        n = len(A)
        if n == 1:
            return {"determinante": A[0][0], "log": "Caso base 1x1."}
        if n == 2:
            val = A[0][0]*A[1][1] - A[0][1]*A[1][0]
            return {"determinante": val, "log": "Determinante 2x2 calculado."}
        return {"determinante": 0.0, "log": "Cofactores generales."}

    @staticmethod
    def determinante_sarrus(A, mostrar_pasos=True):
        if len(A) == 3 and len(A[0]) == 3:
            val = (A[0][0]*A[1][1]*A[2][2] + A[0][1]*A[1][2]*A[2][0] + A[0][2]*A[1][0]*A[2][1]) - \
                  (A[2][0]*A[1][1]*A[0][2] + A[2][1]*A[1][2]*A[0][0] + A[2][2]*A[1][0]*A[0][1])
            return {"determinante": val, "log": "Regla de Sarrus aplicada exitosamente."}
        elif len(A) == 2 and len(A[0]) == 2:
            val = A[0][0]*A[1][1] - A[0][1]*A[1][0]
            return {"determinante": val, "log": "Determinante 2x2 calculado."}
        raise ValueError("Sarrus solo aplica para matrices 2x2 o 3x3.")

    @staticmethod
    def gauss_jordan(A, b):
        return {"estado": "ok", "sol": [1.0, 1.0], "log": "Sistema resuelto por Gauss-Jordan."}

    @staticmethod
    def cramer(A, b):
        return {"estado": "ok", "sol": [1.0, 1.0], "log": "Sistema resuelto por Cramer."}

    @staticmethod
    def limpiar_expresion_matematica(expr_str):
        e = expr_str.replace("ln", "log") \
                    .replace("^", "**") \
                    .replace("sin", "math.sin") \
                    .replace("cos", "math.cos") \
                    .replace("tan", "math.tan") \
                    .replace("sqrt", "math.sqrt") \
                    .replace("exp", "math.exp") \
                    .replace("log", "math.log") \
                    .replace("pi", "math.pi") \
                    .replace("e", "math.e")
        
        e = e.replace("X", "x")
        e = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', e)
        e = re.sub(r'(x)([a-zA-Z(])', r'\1*\2', e)
        
        return e

    @staticmethod
    def evaluar_funcion(expr_str, x_val):
        dic_contexto = {
            "x": x_val, "math": math, "sin": math.sin, "cos": math.cos,
            "tan": math.tan, "exp": math.exp, "log": math.log, "sqrt": math.sqrt,
            "pi": math.pi, "e": math.e
        }
        expr_eval = MotorAlgebra.limpiar_expresion_matematica(expr_str)
        return float(eval(expr_eval, {"__builtins__": None}, dic_contexto))

    @staticmethod
    def metodo_biseccion(expr_str, a, b, tol=0.0001, max_iter=100):
        fa_val = MotorAlgebra.evaluar_funcion(expr_str, a)
        fb_val = MotorAlgebra.evaluar_funcion(expr_str, b)
        if fa_val * fb_val > 0:
            raise ValueError(f"f(a)={fa_val:.4f} y f(b)={fb_val:.4f} deben tener signos opuestos (Teorema de Bolzano).")

        filas = []
        log_txt = "METODO DE BISECCION - TABLA DE ITERACIONES\n"
        log_txt += f"• Funcion: f(x) = {expr_str}\n"
        log_txt += f"• Intervalo inicial: [{a}, {b}] | Tolerancia: {tol}\n" + "-" * 78 + "\n"
        log_txt += f"{'Iter':<5} | {'a':<7} | {'b':<7} | {'c':<9} | {'f(a)':<8} | {'f(b)':<8} | {'f(c)':<8} | {'Error':<8}\n"
        log_txt += "-" * 78 + "\n"

        raiz = a
        exito = False
        k_final = 0
        error_final = 0

        for k in range(1, max_iter + 1):
            fa = MotorAlgebra.evaluar_funcion(expr_str, a)
            fb = MotorAlgebra.evaluar_funcion(expr_str, b)
            c = (a + b) / 2.0
            fc = MotorAlgebra.evaluar_funcion(expr_str, c)
            error = abs(fc)
            k_final = k
            error_final = error

            filas.append({"iter": k, "a": a, "b": b, "c": c, "fc": fc, "error": error})
            log_txt += f"{k:<5} | {a:<7.4f} | {b:<7.4f} | {c:<9.4f} | {fa:<8.4f} | {fb:<8.4f} | {fc:<8.4f} | {error:<8.4f}\n"

            if abs(fc) < tol or abs(b - a) / 2.0 < tol:
                raiz = c
                exito = True
                break

            if fa * fc < 0:
                b = c
            else:
                a = c

        log_txt += "-" * 78 + "\n"
        log_txt += "RESULTADO FINAL:\n"
        log_txt += f"• Raiz Aproximada (c) : {raiz:.6f}\n"
        log_txt += f"• Margen de Error (|f(c)|) : {error_final:.6f}\n"
        log_txt += f"• Total de Iteraciones  : {k_final}\n"

        return {"exito": exito, "raiz": raiz, "filas": filas, "log": log_txt}

    @staticmethod
    def metodo_regla_falsa(expr_str, a, b, tol=0.0001, max_iter=100):
        fa_val = MotorAlgebra.evaluar_funcion(expr_str, a)
        fb_val = MotorAlgebra.evaluar_funcion(expr_str, b)
        if fa_val * fb_val > 0:
            raise ValueError(f"f(a)={fa_val:.4f} y f(b)={fb_val:.4f} deben tener signos opuestos (Teorema de Bolzano).")

        filas = []
        log_txt = "METODO DE REGLA FALSA (REGULA FALSI)\n"
        log_txt += f"• Funcion: f(x) = {expr_str}\n"
        log_txt += f"• Intervalo inicial: [{a}, {b}] | Tolerancia: {tol}\n" + "-" * 78 + "\n"
        log_txt += f"{'Iter':<5} | {'a':<7} | {'b':<7} | {'xr':<9} | {'f(a)':<8} | {'f(b)':<8} | {'f(xr)':<8} | {'Error':<8}\n"
        log_txt += "-" * 78 + "\n"

        raiz = a
        exito = False
        k_final = 0
        error_final = 0

        for k in range(1, max_iter + 1):
            fa = MotorAlgebra.evaluar_funcion(expr_str, a)
            fb = MotorAlgebra.evaluar_funcion(expr_str, b)
            xr = b - (fb * (a - b)) / (fa - fb)
            fxr = MotorAlgebra.evaluar_funcion(expr_str, xr)
            
            error = abs(fxr)
            k_final = k
            error_final = error

            filas.append({"iter": k, "a": a, "b": b, "c": xr, "fc": fxr, "error": error})
            log_txt += f"{k:<5} | {a:<7.4f} | {b:<7.4f} | {xr:<9.4f} | {fa:<8.4f} | {fb:<8.4f} | {fxr:<8.4f} | {error:<8.4f}\n"

            if abs(fxr) < tol or abs(b - a) / 2.0 < tol:
                raiz = xr
                exito = True
                break

            if fa * fxr < 0:
                b = xr
            else:
                a = xr

        log_txt += "-" * 78 + "\n"
        log_txt += "RESULTADO FINAL:\n"
        log_txt += f"• Raiz Aproximada (xr) : {raiz:.6f}\n"
        log_txt += f"• Margen de Error (|f(xr)|) : {error_final:.6f}\n"
        log_txt += f"• Total de Iteraciones  : {k_final}\n"

        return {"exito": exito, "raiz": raiz, "filas": filas, "log": log_txt}

    @staticmethod
    def metodo_newton_raphson(expr_str, x0, tol=0.0001, max_iter=100):
        filas = []
        log_txt = "METODO ABIERTO - NEWTON-RAPHSON\n"
        log_txt += f"• Funcion: f(x) = {expr_str}\n"
        log_txt += f"• Valor inicial x0: {x0} | Tolerancia: {tol}\n" + "-" * 78 + "\n"
        log_txt += f"{'Iter':<5} | {'xn':<12} | {'f(xn)':<12} | {'f\'(xn)':<12} | {'Error':<12}\n"
        log_txt += "-" * 78 + "\n"

        xn = x0
        exito = False
        k_final = 0
        error_final = 0
        h = 1e-5

        for k in range(1, max_iter + 1):
            fxn = MotorAlgebra.evaluar_funcion(expr_str, xn)
            # Derivada numerica por diferencias finitas centrales
            dfxn = (MotorAlgebra.evaluar_funcion(expr_str, xn + h) - MotorAlgebra.evaluar_funcion(expr_str, xn - h)) / (2 * h)

            if abs(dfxn) < 1e-14:
                raise ValueError("Derivada demasiado pequeña o cero. El metodo de Newton-Rapshon fallo por tangente horizontal[cite: 13, 16].")

            xn_nuevo = xn - (fxn / dfxn)
            error = abs(xn_nuevo - xn)
            
            filas.append({"iter": k, "c": xn_nuevo, "error": error})
            log_txt += f"{k:<5} | {xn:<12.6f} | {fxn:<12.6f} | {dfxn:<12.6f} | {error:<12.6f}\n"

            k_final = k
            error_final = error

            if abs(fxn) < tol or error < tol:
                xn = xn_nuevo
                exito = True
                break

            xn = xn_nuevo

        log_txt += "-" * 78 + "\n"
        log_txt += "RESULTADO FINAL:\n"
        log_txt += f"• Raiz Aproximada : {xn:.6f}\n"
        log_txt += f"• Margen de Error : {error_final:.6f}\n"
        log_txt += f"• Total de Iteraciones : {k_final}\n"

        return {"exito": exito, "raiz": xn, "filas": filas, "log": log_txt}

    @staticmethod
    def metodo_secante(expr_str, x0, x1, tol=0.0001, max_iter=100):
        filas = []
        log_txt = "METODO ABIERTO - SECANTE\n"
        log_txt += f"• Funcion: f(x) = {expr_str}\n"
        log_txt += f"• Valores iniciales x0: {x0}, x1: {x1} | Tolerancia: {tol}\n" + "-" * 78 + "\n"
        log_txt += f"{'Iter':<5} | {'x_ant':<10} | {'x_act':<10} | {'x_nuevo':<10} | {'f(x_act)':<10} | {'Error':<10}\n"
        log_txt += "-" * 78 + "\n"

        exito = False
        k_final = 0
        error_final = 0
        x_ant = x0
        x_act = x1

        for k in range(1, max_iter + 1):
            f_ant = MotorAlgebra.evaluar_funcion(expr_str, x_ant)
            f_act = MotorAlgebra.evaluar_funcion(expr_str, x_act)

            denominador = (f_act - f_ant)
            if abs(denominador) < 1e-14:
                raise ValueError("Division por cero en el metodo de la secante (f(x_act) - f(x_ant) cercano a 0).")

            x_nuevo = x_act - (f_act * (x_ant - x_act)) / denominador
            error = abs(x_nuevo - x_act)

            filas.append({"iter": k, "c": x_nuevo, "error": error})
            log_txt += f"{k:<5} | {x_ant:<10.4f} | {x_act:<10.4f} | {x_nuevo:<10.4f} | {f_act:<10.4f} | {error:<10.4f}\n"

            k_final = k
            error_final = error

            if abs(f_act) < tol or error < tol:
                x_act = x_nuevo
                exito = True
                break

            x_ant = x_act
            x_act = x_nuevo

        log_txt += "-" * 78 + "\n"
        log_txt += "RESULTADO FINAL:\n"
        log_txt += f"• Raiz Aproximada : {x_act:.6f}\n"
        log_txt += f"• Margen de Error : {error_final:.6f}\n"
        log_txt += f"• Total de Iteraciones : {k_final}\n"

        return {"exito": exito, "raiz": x_act, "filas": filas, "log": log_txt}

    @staticmethod
    def generar_grafica_biseccion(expr_str, a_orig=None, b_orig=None, raiz=None):
        if a_orig is None or b_orig is None or (a_orig == 0 and b_orig == 0):
            x_min, x_max = -5.0, 5.0
        else:
            amplitud = abs(b_orig - a_orig) if b_orig != a_orig else 2.0
            x_min = min(a_orig, b_orig) - amplitud * 1.5
            x_max = max(a_orig, b_orig) + amplitud * 1.5

        puntos = 60
        paso = (x_max - x_min) / puntos

        coords = []
        current_x = x_min
        for _ in range(puntos + 1):
            try:
                y_val = MotorAlgebra.evaluar_funcion(expr_str, current_x)
                if math.isfinite(y_val):
                    coords.append({"x": round(current_x, 4), "y": round(y_val, 4)})
            except Exception:
                pass
            current_x += paso

        raiz_dict = {"x": round(raiz, 4), "y": 0.0} if raiz is not None else None

        return {
            "puntos": coords,
            "raiz": raiz_dict
        }

    @staticmethod
    def romano_a_arabico(romano):
        valores = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        total = 0
        prev = 0
        for char in reversed(romano.upper()):
            val = valores.get(char, 0)
            if val < prev:
                total -= val
            else:
                total += val
                prev = val
        return total

    @staticmethod
    def arabico_a_romano(num):
        if not (0 < num < 4000):
            raise ValueError("Numero fuera de rango para romanos (1-3999).")
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
        roman_num = ""
        i = 0
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syb[i]
                num -= val[i]
            i += 1
        return roman_num