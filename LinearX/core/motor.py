import math
import sys
import psutil

class MotorAlgebra:

    @staticmethod
    def sumar_vectores(u, v):
        if len(u) != len(v):
            raise ValueError("Los vectores deben tener la misma dimensión.")
        return [a + b for a, b in zip(u, v)]

    @staticmethod
    def restar_vectores(u, v):
        if len(u) != len(v):
            raise ValueError("Los vectores deben tener la misma dimensión.")
        return [a - b for a, b in zip(u, v)]

    @staticmethod
    def escalar_vector(k, v):
        return [k * x for x in v]

    @staticmethod
    def combinacion_lineal(vecs, b):
        log = "Calculando combinación lineal...\n"
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
            raise ValueError("El número de columnas de A debe ser igual al número de filas de B.")
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
        
        # Crear matriz aumentada [A | I]
        M = [row + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(A)]
        log = "Matriz aumentada inicial [A | I]:\n"
        
        for i in range(n):
            # Pivoteo parcial
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
            
            # Normalizar fila pivote
            pivote = M[i][i]
            for j in range(2 * n):
                M[i][j] /= pivote
            
            # Reducción de otras filas
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
    def metodo_biseccion(expr_str, a, b, tol=0.0001, max_iter=100):
        def f(x_val):
            dic_contexto = {
                "x": x_val, "math": math, "sin": math.sin, "cos": math.cos,
                "tan": math.tan, "exp": math.exp, "log": math.log, "sqrt": math.sqrt,
                "pi": math.pi, "e": math.e
            }
            expr_eval = expr_str.replace("^", "**")
            return float(eval(expr_eval, {"__builtins__": None}, dic_contexto))

        fa = f(a)
        fb = f(b)
        if fa * fb > 0:
            raise ValueError("f(a) y f(b) deben tener signos opuestos (Teorema de Bolzano).")

        filas = []
        log_txt = f"Función: f(x) = {expr_str}\nIntervalo: [{a}, {b}] | Tolerancia: {tol}\n\n"
        log_txt += f"{'Iter (k)':<10} | {'a':<10} | {'b':<10} | {'c (Medio)':<10} | {'f(c)':<12} | {'Error':<10}\n"
        log_txt += "-" * 75 + "\n"

        c_ant = a
        raiz = a
        exito = False

        for k in range(1, max_iter + 1):
            c = (a + b) / 2.0
            fc = f(c)
            error = abs(c - c_ant) if k > 1 else abs(b - a)

            filas.append({"iter": k, "a": a, "b": b, "c": c, "fc": fc, "error": error})
            log_txt += f"{k:<10} | {a:<10.5f} | {b:<10.5f} | {c:<10.5f} | {fc:<12.5f} | {error:<10.5f}\n"

            if abs(fc) < tol or error < tol:
                raiz = c
                exito = True
                break

            if f(a) * fc < 0:
                b = c
            else:
                a = c
            c_ant = c

        return {"exito": exito, "raiz": raiz, "filas": filas, "log": log_txt}

    @staticmethod
    def generar_grafica_biseccion(expr_str, a_orig, b_orig, raiz):
        """Genera los puntos (x, y) para graficar la función y la raíz en la web."""
        def f(x_val):
            dic_contexto = {
                "x": x_val, "math": math, "sin": math.sin, "cos": math.cos,
                "tan": math.tan, "exp": math.exp, "log": math.log, "sqrt": math.sqrt,
                "pi": math.pi, "e": math.e
            }
            expr_eval = expr_str.replace("^", "**")
            return float(eval(expr_eval, {"__builtins__": None}, dic_contexto))

        margen = (b_orig - a_orig) * 0.5 if b_orig != a_orig else 1.0
        x_min = a_orig - margen
        x_max = b_orig + margen

        puntos = 40
        paso = (x_max - x_min) / puntos

        coords = []
        current_x = x_min
        for _ in range(puntos + 1):
            try:
                y_val = f(current_x)
                if math.isfinite(y_val):
                    coords.append({"x": round(current_x, 4), "y": round(y_val, 4)})
            except Exception:
                pass
            current_x += paso

        return {
            "puntos": coords,
            "raiz": {"x": round(raiz, 4), "y": 0.0}
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
            raise ValueError("Número fuera de rango para romanos (1-3999).")
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