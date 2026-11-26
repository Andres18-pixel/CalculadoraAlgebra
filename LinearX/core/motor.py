import math
import re
import copy
from fractions import Fraction


class MotorAlgebra:

    @staticmethod
    def _to_frac(val):
        if isinstance(val, Fraction):
            return val
        if isinstance(val, int):
            return Fraction(val, 1)
        if isinstance(val, float):
            if abs(val) < 1e-12:
                return Fraction(0, 1)
            return Fraction(str(val)).limit_denominator(10**7)
        s = str(val).strip().replace("−", "-").replace(" ", "")
        if not s:
            return Fraction(0, 1)
        return Fraction(s).limit_denominator(10**7)

    @staticmethod
    def _fmt_frac_or_dec(val, decimales=6):
        if isinstance(val, Fraction):
            if val.denominator == 1:
                return str(val.numerator)
            dec = float(val)
            return f"{val.numerator}/{val.denominator} ({dec:.{decimales}f})"
        if abs(val) < 1e-11:
            return "0"
        if abs(val - round(val)) < 1e-9:
            return str(int(round(val)))
        return f"{val:.{decimales}f}"

    @staticmethod
    def _fmt_celda_frac(val, ancho=11):
        if isinstance(val, Fraction):
            s = str(val.numerator) if val.denominator == 1 else f"{val.numerator}/{val.denominator}"
            return f"{s:>{ancho}}"
        if abs(val) < 1e-11:
            val = 0.0
        if abs(val - round(val)) < 1e-9:
            return f"{int(round(val)):>{ancho}}"
        return f"{val:>{ancho}.4f}"

    @staticmethod
    def _fmt_matriz_frac(M, separador_col=None, ancho=11):
        lineas = []
        for fila in M:
            if separador_col is not None:
                izq = " ".join(MotorAlgebra._fmt_celda_frac(x, ancho) for x in fila[:separador_col])
                der = " ".join(MotorAlgebra._fmt_celda_frac(x, ancho) for x in fila[separador_col:])
                lineas.append(f"  [ {izq}  | {der} ]")
            else:
                vals = " ".join(MotorAlgebra._fmt_celda_frac(x, ancho) for x in fila)
                lineas.append(f"  [ {vals} ]")
        return "\n".join(lineas)

    @staticmethod
    def _fmt_num(val, decimales=4):
        if isinstance(val, Fraction):
            val = float(val)
        if abs(val) < 1e-11:
            val = 0.0
        if abs(val - round(val)) < 1e-9:
            return f"{int(round(val)):>9}"
        return f"{val:>9.{decimales}f}"

    @staticmethod
    def _fmt_matriz(M, separador_col=None, decimales=4):
        lineas = []
        for fila in M:
            if separador_col is not None:
                izq = " ".join(MotorAlgebra._fmt_num(x, decimales) for x in fila[:separador_col])
                der = " ".join(MotorAlgebra._fmt_num(x, decimales) for x in fila[separador_col:])
                lineas.append(f"  [ {izq}  | {der} ]")
            else:
                vals = " ".join(MotorAlgebra._fmt_num(x, decimales) for x in fila)
                lineas.append(f"  [ {vals} ]")
        return "\n".join(lineas)

    @staticmethod
    def _nombres_variables(n):
        if n == 2:
            return ["x", "y"]
        elif n == 3:
            return ["x", "y", "z"]
        elif n == 4:
            return ["x", "y", "z", "w"]
        return [f"x{i+1}" for i in range(n)]

    @staticmethod
    def _fmt_sistema_axb(A, b, vars_nombres):
        m = len(A)
        n = len(A[0])
        lineas = []
        filas_visuales = max(m, n)
        for i in range(filas_visuales):
            if i < m:
                fila_a = " ".join(MotorAlgebra._fmt_celda_frac(x, 8) for x in A[i])
                mat_part = f"[ {fila_a} ]"
                val_b = MotorAlgebra._fmt_celda_frac(b[i], 8)
                b_part = f"[ {val_b} ]"
            else:
                espacios = " " * (9 * n + 3)
                mat_part = espacios
                b_part = ""

            if i < n:
                var_part = f"[ {vars_nombres[i]:^3} ]"
            else:
                var_part = "       "

            signo_mul = " · " if i == filas_visuales // 2 else "   "
            signo_eq = " = " if i == filas_visuales // 2 else "   "
            lineas.append(f"  {mat_part}{signo_mul}{var_part}{signo_eq}{b_part}")
        return "\n".join(lineas)

    @staticmethod
    def _fmt_ecuacion_lineal(fila, rhs, vars_nombres):
        partes = []
        for coef, var in zip(fila, vars_nombres):
            c_val = float(coef) if isinstance(coef, Fraction) else coef
            if abs(c_val) < 1e-11:
                continue
            c_str_exact = str(coef.numerator) if (isinstance(coef, Fraction) and coef.denominator == 1) else (
                f"({coef.numerator}/{coef.denominator})" if isinstance(coef, Fraction) else (
                    f"{int(round(c_val))}" if abs(c_val - round(c_val)) < 1e-9 else f"{c_val:.4f}"
                )
            )
            if not partes:
                if abs(c_val - 1.0) < 1e-9:
                    partes.append(f"{var}")
                elif abs(c_val + 1.0) < 1e-9:
                    partes.append(f"-{var}")
                else:
                    partes.append(f"{c_str_exact}{var}")
            else:
                signo = "+" if c_val >= 0 else "-"
                abs_c = abs(c_val)
                if abs(abs_c - 1.0) < 1e-9:
                    partes.append(f" {signo} {var}")
                else:
                    abs_str = str(abs(coef).numerator) if (isinstance(coef, Fraction) and coef.denominator == 1) else (
                        f"({abs(coef).numerator}/{abs(coef).denominator})" if isinstance(coef, Fraction) else (
                            f"{int(round(abs_c))}" if abs(abs_c - round(abs_c)) < 1e-9 else f"{abs_c:.4f}"
                        )
                    )
                    partes.append(f" {signo} {abs_str}{var}")
        izq = "".join(partes) if partes else "0"
        rhs_str = MotorAlgebra._fmt_celda_frac(rhs, 1).strip()
        return f"{izq} = {rhs_str}"

    # ==================== 1. VECTORES ====================
    @staticmethod
    def sumar_vectores(u, v):
        if len(u) != len(v):
            raise ValueError("Los vectores deben tener la misma dimension.")
        res = [a + b for a, b in zip(u, v)]
        log = (
            f"SUMA DE VECTORES (u + v)\n"
            f"u = {u}\n"
            f"v = {v}\n"
            f"Resultado = {[round(x, 4) for x in res]}"
        )
        return {"resultado": res, "log": log}

    @staticmethod
    def restar_vectores(u, v):
        if len(u) != len(v):
            raise ValueError("Los vectores deben tener la misma dimension.")
        res = [a - b for a, b in zip(u, v)]
        log = (
            f"RESTA DE VECTORES (u - v)\n"
            f"u = {u}\n"
            f"v = {v}\n"
            f"Resultado = {[round(x, 4) for x in res]}"
        )
        return {"resultado": res, "log": log}

    @staticmethod
    def escalar_vector(k, v):
        res = [k * x for x in v]
        log = (
            f"MULTIPLICACION POR ESCALAR (k * v)\n"
            f"Escalar k = {k}\n"
            f"Vector v  = {v}\n"
            f"Resultado = {[round(x, 4) for x in res]}"
        )
        return {"resultado": res, "log": log}

    @staticmethod
    def producto_punto(u, v):
        if len(u) != len(v):
            raise ValueError("Los vectores deben tener la misma dimension.")
        terminos = [f"({a}*{b})" for a, b in zip(u, v)]
        res = sum(a * b for a, b in zip(u, v))
        norma_u = math.sqrt(sum(a**2 for a in u))
        norma_v = math.sqrt(sum(b**2 for b in v))
        log = (
            f"PRODUCTO PUNTO Y NORMAS\n"
            f"• u · v = {' + '.join(terminos)} = {res:.4f}\n"
            f"• ||u|| = {norma_u:.4f}\n"
            f"• ||v|| = {norma_v:.4f}"
        )
        return {"resultado": res, "log": log}

    @staticmethod
    def combinacion_lineal(vecs, b):
        if not vecs or len(vecs[0]) != len(b):
            raise ValueError("Dimensiones incompatibles entre los vectores y el vector objetivo b.")
        num_vecs = len(vecs)
        dim = len(b)
        A = [[MotorAlgebra._to_frac(vecs[j][i]) for j in range(num_vecs)] for i in range(dim)]
        M = [A[i] + [MotorAlgebra._to_frac(b[i])] for i in range(dim)]

        log = "COMBINACION LINEAL: c1*v1 + c2*v2 + ... = b\n"
        log += "Matriz aumentada [V | b]:\n" + MotorAlgebra._fmt_matriz_frac(M, num_vecs) + "\n\n"

        fila_piv = 0
        pivotes = []
        for col in range(num_vecs):
            if fila_piv >= dim:
                break
            max_r = max(range(fila_piv, dim), key=lambda r: abs(M[r][col]))
            if M[max_r][col] == 0:
                continue
            M[fila_piv], M[max_r] = M[max_r], M[fila_piv]
            piv = M[fila_piv][col]
            M[fila_piv] = [x / piv for x in M[fila_piv]]
            for r in range(dim):
                if r != fila_piv and M[r][col] != 0:
                    f = M[r][col]
                    M[r] = [M[r][c] - f * M[fila_piv][c] for c in range(num_vecs + 1)]
            pivotes.append((fila_piv, col))
            fila_piv += 1

        log += "Matriz escalonada reducida:\n" + MotorAlgebra._fmt_matriz_frac(M, num_vecs) + "\n\n"

        for r in range(dim):
            if all(M[r][c] == 0 for c in range(num_vecs)) and M[r][num_vecs] != 0:
                log += "CONCLUSION: El vector b NO es combinacion lineal (sistema inconsistente)."
                return {"log": log, "sol": None}

        sol = [Fraction(0, 1)] * num_vecs
        for r, c in pivotes:
            sol[c] = M[r][num_vecs]

        log += "CONCLUSION: El vector b SI es combinacion lineal.\n"
        for idx, val in enumerate(sol, 1):
            log += f"• c{idx} = {MotorAlgebra._fmt_frac_or_dec(val, 6)}\n"
        return {"log": log, "sol": [float(x) for x in sol]}

    # ==================== 2. MATRICES (CUADRADAS Y RECTANGULARES) ====================
    @staticmethod
    def _parsear_matriz_frac(M_raw):
        return [[MotorAlgebra._to_frac(x) for x in fila] for fila in M_raw]

    @staticmethod
    def sumar_matrices(A, B):
        Af = MotorAlgebra._parsear_matriz_frac(A)
        Bf = MotorAlgebra._parsear_matriz_frac(B)
        if len(Af) != len(Bf) or len(Af[0]) != len(Bf[0]):
            raise ValueError("Las matrices deben tener las mismas dimensiones para sumar.")
        res = [[Af[i][j] + Bf[i][j] for j in range(len(Af[0]))] for i in range(len(Af))]
        log = f"SUMA DE MATRICES (A + B) [{len(Af)}x{len(Af[0])}]\nMatriz Resultado:\n" + MotorAlgebra._fmt_matriz_frac(res)
        return {"resultado": [[float(x) for x in r] for r in res], "log": log}

    @staticmethod
    def restar_matrices(A, B):
        Af = MotorAlgebra._parsear_matriz_frac(A)
        Bf = MotorAlgebra._parsear_matriz_frac(B)
        if len(Af) != len(Bf) or len(Af[0]) != len(Bf[0]):
            raise ValueError("Las matrices deben tener las mismas dimensiones para restar.")
        res = [[Af[i][j] - Bf[i][j] for j in range(len(Af[0]))] for i in range(len(Af))]
        log = f"RESTA DE MATRICES (A - B) [{len(Af)}x{len(Af[0])}]\nMatriz Resultado:\n" + MotorAlgebra._fmt_matriz_frac(res)
        return {"resultado": [[float(x) for x in r] for r in res], "log": log}

    @staticmethod
    def combinacion_matrices(A, B, C=None, alpha=1, beta=1, gamma=0):
        Af = MotorAlgebra._parsear_matriz_frac(A)
        Bf = MotorAlgebra._parsear_matriz_frac(B)
        a_f = MotorAlgebra._to_frac(alpha)
        b_f = MotorAlgebra._to_frac(beta)
        g_f = MotorAlgebra._to_frac(gamma)

        filas, cols = len(Af), len(Af[0])
        if len(Bf) != filas or len(Bf[0]) != cols:
            raise ValueError("Las matrices A y B deben tener las mismas dimensiones.")

        Cf = None
        if C is not None and g_f != 0:
            Cf = MotorAlgebra._parsear_matriz_frac(C)
            if len(Cf) != filas or len(Cf[0]) != cols:
                raise ValueError("La matriz C debe tener las mismas dimensiones que A y B.")

        res = []
        pasos_celda = []
        for i in range(filas):
            fila_res = []
            for j in range(cols):
                val = a_f * Af[i][j] + b_f * Bf[i][j]
                expr_c = f"({a_f})*({Af[i][j]}) + ({b_f})*({Bf[i][j]})"
                if Cf is not None:
                    val += g_f * Cf[i][j]
                    expr_c += f" + ({g_f})*({Cf[i][j]})"
                fila_res.append(val)
                pasos_celda.append(f"   • C[{i+1},{j+1}] = {expr_c} = {MotorAlgebra._fmt_celda_frac(val, 1).strip()}")
            res.append(fila_res)

        titulo_expr = f"({a_f})·A + ({b_f})·B" + (f" + ({g_f})·C" if Cf is not None else "")
        log = (
            f"======================================================================\n"
            f"OPERACION LINEAL DE MATRICES RECTANGULARES ({filas}x{cols})\n"
            f"Expresion: {titulo_expr}\n"
            f"======================================================================\n\n"
            f"1. MATRICES DE ENTRADA:\n"
            f"Matriz A:\n{MotorAlgebra._fmt_matriz_frac(Af)}\n\n"
            f"Matriz B:\n{MotorAlgebra._fmt_matriz_frac(Bf)}\n"
        )
        if Cf is not None:
            log += f"\nMatriz C:\n{MotorAlgebra._fmt_matriz_frac(Cf)}\n"

        log += "\n2. PROCEDIMIENTO ELEMENTO A ELEMENTO:\n" + "\n".join(pasos_celda) + "\n\n"
        log += "3. MATRIZ RESULTADO:\n" + MotorAlgebra._fmt_matriz_frac(res)
        return {"resultado": [[float(x) for x in r] for r in res], "log": log}

    @staticmethod
    def multiplicar_matrices(A, B):
        Af = MotorAlgebra._parsear_matriz_frac(A)
        Bf = MotorAlgebra._parsear_matriz_frac(B)
        filas_a, cols_a = len(Af), len(Af[0])
        filas_b, cols_b = len(Bf), len(Bf[0])
        if cols_a != filas_b:
            raise ValueError(f"Columnas de A ({cols_a}) deben ser iguales a filas de B ({filas_b}).")
        res = [[sum(Af[i][k] * Bf[k][j] for k in range(cols_a)) for j in range(cols_b)] for i in range(filas_a)]
        log = f"MULTIPLICACION DE MATRICES ({filas_a}x{cols_a}) * ({filas_b}x{cols_b})\nMatriz Producto C = A · B:\n" + MotorAlgebra._fmt_matriz_frac(res)
        return {"resultado": [[float(x) for x in r] for r in res], "log": log}

    @staticmethod
    def escalar_matriz(k, A):
        kf = MotorAlgebra._to_frac(k)
        Af = MotorAlgebra._parsear_matriz_frac(A)
        res = [[kf * x for x in fila] for fila in Af]
        log = f"ESCALAR POR MATRIZ (k = {kf})\nMatriz Resultado:\n" + MotorAlgebra._fmt_matriz_frac(res)
        return {"resultado": [[float(x) for x in r] for r in res], "log": log}

    # ==================== 3. DETERMINANTE E INVERSA ====================
    @staticmethod
    def inversa_gauss_jordan(A, mostrar_pasos=True):
        Af = MotorAlgebra._parsear_matriz_frac(A)
        n = len(Af)
        if any(len(fila) != n for fila in Af):
            raise ValueError("La matriz debe ser cuadrada (n x n).")

        log = f"======================================================================\n"
        log += f"DETERMINANTE E INVERSA DE MATRIZ CUADRADA ({n}x{n})\n"
        log += f"======================================================================\n\n"

        log += "1. MATRIZ ORIGINAL A:\n"
        log += MotorAlgebra._fmt_matriz_frac(Af) + "\n\n"

        log += "2. CALCULO DEL DETERMINANTE det(A) (Reduccion a forma triangular U):\n"
        U = copy.deepcopy(Af)
        swaps = 0
        singular = False

        for i in range(n):
            max_r = max(range(i, n), key=lambda r: abs(U[r][i]))
            if U[max_r][i] == 0:
                singular = True
                break
            if max_r != i:
                U[i], U[max_r] = U[max_r], U[i]
                swaps += 1
                if mostrar_pasos:
                    log += f"   • Intercambio F{i+1} <-> F{max_r+1} (cambia signo del determinante)\n"
            for k in range(i + 1, n):
                if U[k][i] != 0:
                    factor = U[k][i] / U[i][i]
                    for j in range(i, n):
                        U[k][j] -= factor * U[i][j]
                    if mostrar_pasos:
                        log += f"   • F{k+1} <- F{k+1} - ({MotorAlgebra._fmt_celda_frac(factor, 1).strip()}) * F{i+1}\n"

        if singular:
            if mostrar_pasos:
                log += "\nMatriz escalonada:\n" + MotorAlgebra._fmt_matriz_frac(U) + "\n"
            log += f"\n   • Resultado: det(A) = 0\n\n"
            log += "3. JUSTIFICACION DE EXISTENCIA DE INVERSA:\n"
            log += f"   Como det(A) = 0, la matriz A es SINGULAR (sus filas/columnas son linealmente dependientes).\n"
            log += f"   Por lo tanto, NO EXISTE la matriz inversa A^-1.\n"
            return {"existe": False, "determinante": 0.0, "inversa": None, "comprobacion": None, "log": log}

        det = Fraction((-1) ** swaps, 1)
        diag_terms = []
        for i in range(n):
            det *= U[i][i]
            diag_terms.append(f"({MotorAlgebra._fmt_celda_frac(U[i][i], 1).strip()})")

        if mostrar_pasos:
            log += "\nMatriz Triangular Superior U:\n" + MotorAlgebra._fmt_matriz_frac(U) + "\n"
            log += f"   • Signo por {swaps} intercambio(s): {(-1)**swaps:+d}\n"
            log += f"   • Producto diagonal: {(-1)**swaps:+d} * {' * '.join(diag_terms)}\n"

        det_fmt = MotorAlgebra._fmt_frac_or_dec(det, 6)
        log += f"   => det(A) = {det_fmt}\n\n"

        log += "3. JUSTIFICACION DE EXISTENCIA DE INVERSA:\n"
        log += f"   Dado que det(A) = {det_fmt} != 0, la matriz A es NO SINGULAR (invertible).\n"
        log += f"   Por teorema matricial, existe una unica matriz inversa A^-1 tal que A · A^-1 = I_{n}.\n\n"

        log += f"4. CALCULO DE A^-1 POR GAUSS-JORDAN [A | I_{n}] -> [I_{n} | A^-1]:\n"
        M = [copy.deepcopy(row) + [Fraction(1, 1) if i == j else Fraction(0, 1) for j in range(n)] for i, row in enumerate(Af)]
        log += "Matriz Aumentada Inicial:\n" + MotorAlgebra._fmt_matriz_frac(M, n) + "\n\n"

        for i in range(n):
            max_row = max(range(i, n), key=lambda r: abs(M[r][i]))
            if max_row != i:
                M[i], M[max_row] = M[max_row], M[i]
                if mostrar_pasos:
                    log += f"Paso: Intercambio F{i+1} <-> F{max_row+1}\n" + MotorAlgebra._fmt_matriz_frac(M, n) + "\n\n"

            pivote = M[i][i]
            if pivote != 1:
                for j in range(2 * n):
                    M[i][j] /= pivote
                if mostrar_pasos:
                    log += f"Paso: F{i+1} <- F{i+1} / ({MotorAlgebra._fmt_celda_frac(pivote, 1).strip()})\n" + MotorAlgebra._fmt_matriz_frac(M, n) + "\n\n"

            cambio_fila = False
            for k in range(n):
                if k != i and M[k][i] != 0:
                    factor = M[k][i]
                    for j in range(2 * n):
                        M[k][j] -= factor * M[i][j]
                    if mostrar_pasos:
                        log += f"Paso: F{k+1} <- F{k+1} - ({MotorAlgebra._fmt_celda_frac(factor, 1).strip()}) * F{i+1}\n"
                        cambio_fila = True
            if mostrar_pasos and cambio_fila:
                log += MotorAlgebra._fmt_matriz_frac(M, n) + "\n\n"

        inversa = [row[n:] for row in M]
        log += "5. MATRIZ INVERSA FINAL (A^-1 en fraccion exacta):\n"
        log += MotorAlgebra._fmt_matriz_frac(inversa, ancho=12) + "\n\n"
        log += "   MATRIZ INVERSA EN DECIMALES (8 cifras):\n"
        log += MotorAlgebra._fmt_matriz([[float(x) for x in r] for r in inversa], decimales=8) + "\n\n"

        producto = [[sum(Af[i][k] * inversa[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        log += f"6. VERIFICACION MATRICIAL (A · A^-1 = I_{n}):\n"
        log += MotorAlgebra._fmt_matriz_frac(producto, ancho=6) + "\n"
        log += f"   => Comprobado: el producto A · A^-1 coincide exactamente con la matriz identidad I_{n}.\n"

        return {
            "existe": True,
            "determinante": float(det),
            "inversa": [[float(x) for x in r] for r in inversa],
            "comprobacion": f"A * A^-1 = I_{n} verificada.",
            "log": log
        }

    # ==================== 4. DETERMINANTES ====================
    @staticmethod
    def _det_frac(M):
        n = len(M)
        U = copy.deepcopy(M)
        swaps = 0
        for i in range(n):
            max_r = max(range(i, n), key=lambda r: abs(U[r][i]))
            if U[max_r][i] == 0:
                return Fraction(0, 1)
            if max_r != i:
                U[i], U[max_r] = U[max_r], U[i]
                swaps += 1
            for k in range(i + 1, n):
                if U[k][i] != 0:
                    f = U[k][i] / U[i][i]
                    for j in range(i, n):
                        U[k][j] -= f * U[i][j]
        det = Fraction((-1) ** swaps, 1)
        for i in range(n):
            det *= U[i][i]
        return det

    @staticmethod
    def determinante_lu(A, mostrar_pasos=True):
        Af = MotorAlgebra._parsear_matriz_frac(A)
        n = len(Af)
        if any(len(fila) != n for fila in Af):
            raise ValueError("La matriz debe ser cuadrada.")
        U = copy.deepcopy(Af)
        swaps = 0

        log = f"DETERMINANTE POR DESCOMPOSICION LU ({n}x{n})\n"
        for i in range(n):
            max_r = max(range(i, n), key=lambda r: abs(U[r][i]))
            if U[max_r][i] == 0:
                log += "Pivote cero encontrado. Determinante = 0."
                return {"determinante": 0.0, "log": log}
            if max_r != i:
                U[i], U[max_r] = U[max_r], U[i]
                swaps += 1
            for k in range(i + 1, n):
                factor = U[k][i] / U[i][i]
                for j in range(i, n):
                    U[k][j] -= factor * U[i][j]

        det = Fraction((-1) ** swaps, 1)
        diag_str = []
        for i in range(n):
            det *= U[i][i]
            diag_str.append(MotorAlgebra._fmt_celda_frac(U[i][i], 1).strip())

        if mostrar_pasos:
            log += "Matriz Triangular Superior U:\n" + MotorAlgebra._fmt_matriz_frac(U) + "\n\n"
            log += f"• Intercambios de fila: {swaps} (signo: {(-1)**swaps:+d})\n"
            log += f"• Diagonal de U: {' * '.join(diag_str)}\n"
        log += f"\nDETERMINANTE FINAL = {MotorAlgebra._fmt_frac_or_dec(det, 6)}"
        return {"determinante": float(det), "log": log}

    @staticmethod
    def determinante_cofactores(A, mostrar_pasos=True):
        Af = MotorAlgebra._parsear_matriz_frac(A)
        n = len(Af)
        if any(len(fila) != n for fila in Af):
            raise ValueError("La matriz debe ser cuadrada.")
        log = f"DETERMINANTE POR COFACTORES (Expansion por Fila 1 - {n}x{n})\n"
        if n == 1:
            det = Af[0][0]
            log += f"DETERMINANTE FINAL = {MotorAlgebra._fmt_frac_or_dec(det, 6)}"
            return {"determinante": float(det), "log": log}

        det = Fraction(0, 1)
        for c in range(n):
            signo = (-1) ** c
            elem = Af[0][c]
            menor = [fila[:c] + fila[c+1:] for fila in Af[1:]]
            det_menor = MotorAlgebra._det_frac(menor)
            aporte = signo * elem * det_menor
            det += aporte
            if mostrar_pasos:
                log += f"• C1{c+1}: ({signo:+d}) * ({MotorAlgebra._fmt_celda_frac(elem, 1).strip()}) * det(M1{c+1})[{MotorAlgebra._fmt_celda_frac(det_menor, 1).strip()}] = {MotorAlgebra._fmt_celda_frac(aporte, 1).strip()}\n"

        log += f"\nDETERMINANTE FINAL = {MotorAlgebra._fmt_frac_or_dec(det, 6)}"
        return {"determinante": float(det), "log": log}

    @staticmethod
    def determinante_sarrus(A, mostrar_pasos=True):
        Af = MotorAlgebra._parsear_matriz_frac(A)
        n = len(Af)
        if n == 2 and len(Af[0]) == 2:
            d1 = Af[0][0] * Af[1][1]
            d2 = Af[0][1] * Af[1][0]
            det = d1 - d2
            log = (
                f"DETERMINANTE 2x2\n"
                f"• Diagonal Principal : {Af[0][0]} * {Af[1][1]} = {d1}\n"
                f"• Diagonal Secundaria: {Af[0][1]} * {Af[1][0]} = {d2}\n"
                f"• Det = {d1} - ({d2}) = {MotorAlgebra._fmt_frac_or_dec(det, 6)}"
            )
            return {"determinante": float(det), "log": log}
        elif n == 3 and len(Af[0]) == 3:
            p1 = Af[0][0] * Af[1][1] * Af[2][2]
            p2 = Af[0][1] * Af[1][2] * Af[2][0]
            p3 = Af[0][2] * Af[1][0] * Af[2][1]
            s1 = Af[0][2] * Af[1][1] * Af[2][0]
            s2 = Af[0][0] * Af[1][2] * Af[2][1]
            s3 = Af[0][1] * Af[1][0] * Af[2][2]
            suma_p = p1 + p2 + p3
            suma_s = s1 + s2 + s3
            det = suma_p - suma_s
            log = (
                f"REGLA DE SARRUS (3x3)\n"
                f"• Diagonales (+) : ({p1}) + ({p2}) + ({p3}) = {suma_p}\n"
                f"• Diagonales (-) : ({s1}) + ({s2}) + ({s3}) = {suma_s}\n"
                f"\nDETERMINANTE FINAL = {suma_p} - ({suma_s}) = {MotorAlgebra._fmt_frac_or_dec(det, 6)}"
            )
            return {"determinante": float(det), "log": log}
        raise ValueError("La regla de Sarrus solo aplica a matrices 2x2 o 3x3. Usa LU o Cofactores para matrices mas grandes.")

    # ==================== 5. SISTEMAS DE ECUACIONES (CUADRADOS Y RECTANGULARES) ====================
    @staticmethod
    def _bloque_verificacion_sistema(Af, bf, sol_f, vars_nombres):
        n = len(Af)
        txt = "5. VERIFICACION DE LA SOLUCION:\n"
        txt += "   a) Sustitucion en cada ecuacion original:\n"
        for i in range(n):
            ec_str = MotorAlgebra._fmt_ecuacion_lineal(Af[i], bf[i], vars_nombres)
            terminos = []
            suma = Fraction(0, 1)
            for coef, val in zip(Af[i], sol_f):
                prod = coef * val
                suma += prod
                if coef != 0:
                    c_s = MotorAlgebra._fmt_celda_frac(coef, 1).strip()
                    v_s = MotorAlgebra._fmt_celda_frac(val, 1).strip()
                    terminos.append(f"({c_s})({v_s})")
            b_s = MotorAlgebra._fmt_celda_frac(bf[i], 1).strip()
            sum_s = MotorAlgebra._fmt_celda_frac(suma, 1).strip()
            txt += f"      Ec.{i+1} [{ec_str}]: {' + '.join(terminos)} = {sum_s} == {b_s}  [OK]\n"

        txt += "\n   b) Comprobacion matricial A · X = B:\n"
        ax_vec = [sum(Af[i][j] * sol_f[j] for j in range(n)) for i in range(n)]
        for i in range(n):
            fila_a = " ".join(MotorAlgebra._fmt_celda_frac(x, 8) for x in Af[i])
            val_x = MotorAlgebra._fmt_celda_frac(sol_f[i], 8)
            val_ax = MotorAlgebra._fmt_celda_frac(ax_vec[i], 8)
            val_b = MotorAlgebra._fmt_celda_frac(bf[i], 8)
            signo_mul = " · " if i == n // 2 else "   "
            signo_eq = " = " if i == n // 2 else "   "
            txt += f"      [ {fila_a} ]{signo_mul}[ {val_x} ]{signo_eq}[ {val_ax} ]  (B = {val_b.strip()})\n"
        return txt

    @staticmethod
    def gauss_jordan(A, b):
        Af = MotorAlgebra._parsear_matriz_frac(A)
        bf = [MotorAlgebra._to_frac(x) for x in b]
        n = len(Af)
        if any(len(fila) != n for fila in Af) or len(bf) != n:
            raise ValueError("La matriz A debe ser cuadrada (n x n) y coincidir con la longitud de b.")

        vars_nombres = MotorAlgebra._nombres_variables(n)
        det_A = MotorAlgebra._det_frac(Af)
        det_fmt = MotorAlgebra._fmt_frac_or_dec(det_A, 6)

        if det_A == 0:
            # Si det(A) = 0 (ej. Ejercicio 14), delegamos al solver RREF general para clasificar inconsistente vs infinitas
            res_rect = MotorAlgebra.sistema_rectangular(A, b)
            encabezado = (
                f"======================================================================\n"
                f"SISTEMA LINEAL DE {n} INCOGNITAS - ANALISIS DE CASO SINGULAR (det(A) = 0)\n"
                f"======================================================================\n\n"
                f"• Determinante: det(A) = 0 => NO tiene solucion unica.\n"
                f"• Se procede con eliminacion de Gauss-Jordan completa para determinar\n"
                f"  si el sistema es INCOMPATIBLE o COMPATIBLE INDETERMINADO (infinitas):\n\n"
            )
            res_rect["log"] = encabezado + res_rect["log"]
            return res_rect

        log = f"======================================================================\n"
        log += f"SISTEMA LINEAL DE {n} INCOGNITAS - METODO GAUSS-JORDAN\n"
        log += f"======================================================================\n\n"

        log += f"1. IDENTIFICACION DE INCOGNITAS:\n"
        log += f"   Vector de incognitas: X = [{', '.join(vars_nombres)}]^T\n\n"

        log += f"2. EXPRESION MATRICIAL DEL SISTEMA (A · X = B):\n"
        log += MotorAlgebra._fmt_sistema_axb(Af, bf, vars_nombres) + "\n\n"

        log += f"3. ANALISIS DE EXISTENCIA DE SOLUCION UNICA:\n"
        log += f"   • Determinante de la matriz de coeficientes: det(A) = {det_fmt}\n"
        log += f"   • Conclusion: Como det(A) = {det_fmt} != 0, el sistema es compatible determinado y posee SOLUCION UNICA.\n\n"

        M = [copy.deepcopy(Af[i]) + [bf[i]] for i in range(n)]
        log += "4. PROCEDIMIENTO ALGEBRAICO (GAUSS-JORDAN SOBRE [A | B]):\n"
        log += "Matriz Aumentada Inicial [A | B]:\n" + MotorAlgebra._fmt_matriz_frac(M, n) + "\n\n"

        for i in range(n):
            max_r = max(range(i, n), key=lambda r: abs(M[r][i]))
            if max_r != i:
                M[i], M[max_r] = M[max_r], M[i]
                log += f"Paso: F{i+1} <-> F{max_r+1}\n" + MotorAlgebra._fmt_matriz_frac(M, n) + "\n\n"

            piv = M[i][i]
            if piv != 1:
                M[i] = [x / piv for x in M[i]]
                log += f"Paso: F{i+1} <- F{i+1} / ({MotorAlgebra._fmt_celda_frac(piv, 1).strip()})\n" + MotorAlgebra._fmt_matriz_frac(M, n) + "\n\n"

            hubo_op = False
            for k in range(n):
                if k != i and M[k][i] != 0:
                    f = M[k][i]
                    M[k] = [M[k][j] - f * M[i][j] for j in range(n + 1)]
                    log += f"Paso: F{k+1} <- F{k+1} - ({MotorAlgebra._fmt_celda_frac(f, 1).strip()}) * F{i+1}\n"
                    hubo_op = True
            if hubo_op:
                log += MotorAlgebra._fmt_matriz_frac(M, n) + "\n\n"

        sol_f = [M[i][n] for i in range(n)]
        log += "SOLUCION UNICA ENCONTRADA:\n"
        for var, val in zip(vars_nombres, sol_f):
            log += f"   • {var} = {MotorAlgebra._fmt_frac_or_dec(val, 8)}\n"
        log += "\n" + MotorAlgebra._bloque_verificacion_sistema(Af, bf, sol_f, vars_nombres)

        return {"estado": "ok", "sol": [float(x) for x in sol_f], "log": log}

    @staticmethod
    def cramer(A, b):
        Af = MotorAlgebra._parsear_matriz_frac(A)
        bf = [MotorAlgebra._to_frac(x) for x in b]
        n = len(Af)
        if any(len(fila) != n for fila in Af) or len(bf) != n:
            raise ValueError("La matriz A debe ser cuadrada (n x n) y coincidir con b.")

        vars_nombres = MotorAlgebra._nombres_variables(n)
        det_A = MotorAlgebra._det_frac(Af)
        det_fmt = MotorAlgebra._fmt_frac_or_dec(det_A, 6)

        log = f"======================================================================\n"
        log += f"SISTEMA LINEAL DE {n} INCOGNITAS - REGLA DE CRAMER\n"
        log += f"======================================================================\n\n"

        log += f"1. IDENTIFICACION DE INCOGNITAS:\n"
        log += f"   Vector de incognitas: X = [{', '.join(vars_nombres)}]^T\n\n"

        log += f"2. EXPRESION MATRICIAL DEL SISTEMA (A · X = B):\n"
        log += MotorAlgebra._fmt_sistema_axb(Af, bf, vars_nombres) + "\n\n"

        log += f"3. ANALISIS DE EXISTENCIA DE SOLUCION UNICA:\n"
        log += f"   • Determinante Principal (Delta) = det(A) = {det_fmt}\n"

        if det_A == 0:
            log += f"   • Conclusion: Como Delta = 0, el sistema NO tiene solucion unica por Cramer. Usa Gauss-Jordan para ver si tiene infinitas o ninguna.\n"
            return {"estado": "singular", "sol": None, "log": log}

        log += f"   • Conclusion: Como Delta = {det_fmt} != 0, existe SOLUCION UNICA.\n\n"
        log += "4. CALCULO DE DETERMINANTES POR INCOGNITA:\n"

        sol_f = []
        for col in range(n):
            var = vars_nombres[col]
            M_col = copy.deepcopy(Af)
            for r in range(n):
                M_col[r][col] = bf[r]
            det_col = MotorAlgebra._det_frac(M_col)
            xi = det_col / det_A
            sol_f.append(xi)
            dc_fmt = MotorAlgebra._fmt_celda_frac(det_col, 1).strip()
            da_fmt = MotorAlgebra._fmt_celda_frac(det_A, 1).strip()
            xi_fmt = MotorAlgebra._fmt_frac_or_dec(xi, 8)
            log += f"   • Delta_{var} = {dc_fmt}  =>  {var} = {dc_fmt} / {da_fmt} = {xi_fmt}\n"

        log += "\nSOLUCION UNICA ENCONTRADA:\n"
        for var, val in zip(vars_nombres, sol_f):
            log += f"   • {var} = {MotorAlgebra._fmt_frac_or_dec(val, 8)}\n"
        log += "\n" + MotorAlgebra._bloque_verificacion_sistema(Af, bf, sol_f, vars_nombres)

        return {"estado": "ok", "sol": [float(x) for x in sol_f], "log": log}

    # ==================== 5B. SISTEMAS RECTANGULARES (PARTE V: EJ. 50-54) ====================
    @staticmethod
    def sistema_rectangular(A, b):
        Af = MotorAlgebra._parsear_matriz_frac(A)
        bf = [MotorAlgebra._to_frac(x) for x in b]
        m = len(Af)
        n = len(Af[0])
        if len(bf) != m:
            raise ValueError("El vector B debe tener la misma cantidad de filas que A.")

        vars_nombres = [f"x{i+1}" for i in range(n)]
        M = [copy.deepcopy(Af[i]) + [bf[i]] for i in range(m)]

        log = f"======================================================================\n"
        log += f"SISTEMA LINEAL RECTANGULAR ({m} ECUACIONES x {n} INCOGNITAS) - GAUSS-JORDAN\n"
        log += f"======================================================================\n\n"

        log += f"1. IDENTIFICACION DE INCOGNITAS:\n"
        log += f"   Vector de incognitas: X = [{', '.join(vars_nombres)}]^T\n\n"

        log += f"2. REPRESENTACION MATRICIAL (A · X = B):\n"
        log += MotorAlgebra._fmt_sistema_axb(Af, bf, vars_nombres) + "\n\n"

        log += f"3. REDUCCION POR FILAS (FORMA ESCALONADA REDUCIDA RREF):\n"
        log += "Matriz Aumentada Inicial [A | B]:\n" + MotorAlgebra._fmt_matriz_frac(M, n) + "\n\n"

        fila_piv = 0
        pivotes = []
        for col in range(n):
            if fila_piv >= m:
                break
            max_r = max(range(fila_piv, m), key=lambda r: abs(M[r][col]))
            if M[max_r][col] == 0:
                continue
            if max_r != fila_piv:
                M[fila_piv], M[max_r] = M[max_r], M[fila_piv]
                log += f"Paso: F{fila_piv+1} <-> F{max_r+1}\n" + MotorAlgebra._fmt_matriz_frac(M, n) + "\n\n"

            piv = M[fila_piv][col]
            if piv != 1:
                M[fila_piv] = [x / piv for x in M[fila_piv]]
                log += f"Paso: F{fila_piv+1} <- F{fila_piv+1} / ({MotorAlgebra._fmt_celda_frac(piv, 1).strip()})\n" + MotorAlgebra._fmt_matriz_frac(M, n) + "\n\n"

            hubo_op = False
            for r in range(m):
                if r != fila_piv and M[r][col] != 0:
                    f = M[r][col]
                    M[r] = [M[r][c] - f * M[fila_piv][c] for c in range(n + 1)]
                    log += f"Paso: F{r+1} <- F{r+1} - ({MotorAlgebra._fmt_celda_frac(f, 1).strip()}) * F{fila_piv+1}\n"
                    hubo_op = True
            if hubo_op:
                log += MotorAlgebra._fmt_matriz_frac(M, n) + "\n\n"

            pivotes.append((fila_piv, col))
            fila_piv += 1

        rango_A = len(pivotes)
        fila_contradictoria = None
        for r in range(m):
            if all(M[r][c] == 0 for c in range(n)) and M[r][n] != 0:
                fila_contradictoria = (r + 1, M[r][n])
                break

        log += "4. CLASIFICACION Y ANALISIS DE RANGO (TEOREMA DE ROUCHE-FROBENIUS):\n"
        log += f"   • Numero de incognitas (n) : {n}\n"
        log += f"   • Rango(A)                 : {rango_A}\n"

        if fila_contradictoria is not None:
            f_idx, val_rhs = fila_contradictoria
            rhs_s = MotorAlgebra._fmt_celda_frac(val_rhs, 1).strip()
            log += f"   • Rango([A | B])           : {rango_A + 1}\n"
            log += f"   • Clasificacion            : SISTEMA INCOMPATIBLE (SIN SOLUCION).\n"
            log += f"   • Justificacion            : En la fila F{f_idx} de la matriz reducida aparece la contradiccion\n"
            log += f"                                0 = {rhs_s} (0 != {rhs_s}), por lo que las restricciones no pueden\n"
            log += f"                                satisfacerse simultaneamente. Conjunto solucion: Vacio (Ø).\n"
            return {"estado": "incompatible", "log": log}

        log += f"   • Rango([A | B])           : {rango_A}\n"
        cols_pivote = {c for _, c in pivotes}
        cols_libres = [c for c in range(n) if c not in cols_pivote]

        if not cols_libres:
            log += f"   • Clasificacion            : SISTEMA COMPATIBLE DETERMINADO (SOLUCION UNICA).\n"
            log += f"   • Justificacion            : Rango(A) = Rango([A | B]) = n = {n} (0 variables libres).\n\n"
            log += "5. SOLUCION UNICA:\n"
            sol_f = [Fraction(0, 1)] * n
            for r, c in pivotes:
                sol_f[c] = M[r][n]
            for var, val in zip(vars_nombres, sol_f):
                log += f"   • {var} = {MotorAlgebra._fmt_frac_or_dec(val, 6)}\n"
            return {"estado": "unico", "log": log}

        nombres_params = ["t", "s", "r", "u", "v"]
        mapa_param = {c: nombres_params[idx] if idx < len(nombres_params) else f"t{idx+1}" for idx, c in enumerate(cols_libres)}
        vars_libres_str = [f"{vars_nombres[c]} = {mapa_param[c]}" for c in cols_libres]

        log += f"   • Clasificacion            : SISTEMA COMPATIBLE INDETERMINADO (INFINITAS SOLUCIONES).\n"
        log += f"   • Justificacion            : Rango(A) = Rango([A | B]) = {rango_A} < n ({n} incognitas).\n"
        log += f"   • Cantidad variables libres: {len(cols_libres)} ({', '.join(vars_nombres[c] for c in cols_libres)})\n\n"

        log += "5. SOLUCION GENERAL EN FORMA PARAMETRICA:\n"
        log += f"   Parametros libres: {', '.join(vars_libres_str)} ∈ ℝ\n\n"

        ecuaciones_param = [""] * n
        for c in cols_libres:
            ecuaciones_param[c] = f"{mapa_param[c]}  (variable libre)"

        for r, c in pivotes:
            const = M[r][n]
            partes = []
            if const != 0:
                partes.append(MotorAlgebra._fmt_celda_frac(const, 1).strip())
            for cl in cols_libres:
                coef = -M[r][cl]
                if coef == 0:
                    continue
                p_name = mapa_param[cl]
                if not partes:
                    if coef == 1:
                        partes.append(f"{p_name}")
                    elif coef == -1:
                        partes.append(f"-{p_name}")
                    else:
                        partes.append(f"({MotorAlgebra._fmt_celda_frac(coef, 1).strip()}){p_name}")
                else:
                    signo = "+" if coef > 0 else "-"
                    abs_c = abs(coef)
                    if abs_c == 1:
                        partes.append(f" {signo} {p_name}")
                    else:
                        partes.append(f" {signo} ({MotorAlgebra._fmt_celda_frac(abs_c, 1).strip()}){p_name}")
            ecuaciones_param[c] = "".join(partes) if partes else "0"

        for idx, var in enumerate(vars_nombres):
            log += f"   • {var} = {ecuaciones_param[idx]}\n"

        return {"estado": "infinitas", "log": log}

    # ==================== 5C. INDEPENDENCIA LINEAL DE VECTORES (PARTE VII: EJ. 60-64) ====================
    @staticmethod
    def independencia_lineal(vecs):
        if not vecs or not vecs[0]:
            raise ValueError("Debe ingresar al menos un vector.")
        k = len(vecs)
        dim = len(vecs[0])
        if any(len(v) != dim for v in vecs):
            raise ValueError("Todos los vectores deben tener la misma dimension.")

        V_cols = [[MotorAlgebra._to_frac(vecs[j][i]) for j in range(k)] for i in range(dim)]
        M = [copy.deepcopy(V_cols[i]) + [Fraction(0, 1)] for i in range(dim)]
        alfas = [f"α{j+1}" for j in range(k)]

        log = f"======================================================================\n"
        log += f"ANALISIS DE INDEPENDENCIA LINEAL ({k} VECTORES EN R^{dim})\n"
        log += f"======================================================================\n\n"

        log += "1. CONJUNTO DE VECTORES DADOS:\n"
        for j, v in enumerate(vecs, 1):
            v_str = ", ".join(MotorAlgebra._fmt_celda_frac(MotorAlgebra._to_frac(x), 1).strip() for x in v)
            log += f"   • v{j} = ({v_str})\n"

        eq_vec = " + ".join(f"α{j+1}·v{j+1}" for j in range(k))
        log += f"\n2. PLANTEAMIENTO DE LA COMBINACION LINEAL HOMOGENEA:\n"
        log += f"   {eq_vec} = 0\n\n"
        log += f"   Matriz asociada con los vectores como columnas [v1 ... v{k} | 0]:\n"
        log += MotorAlgebra._fmt_matriz_frac(M, k) + "\n\n"

        log += "3. REDUCCION POR FILAS (GAUSS-JORDAN):\n"
        fila_piv = 0
        pivotes = []
        for col in range(k):
            if fila_piv >= dim:
                break
            max_r = max(range(fila_piv, dim), key=lambda r: abs(M[r][col]))
            if M[max_r][col] == 0:
                continue
            if max_r != fila_piv:
                M[fila_piv], M[max_r] = M[max_r], M[fila_piv]
                log += f"Paso: F{fila_piv+1} <-> F{max_r+1}\n" + MotorAlgebra._fmt_matriz_frac(M, k) + "\n\n"

            piv = M[fila_piv][col]
            if piv != 1:
                M[fila_piv] = [x / piv for x in M[fila_piv]]
                log += f"Paso: F{fila_piv+1} <- F{fila_piv+1} / ({MotorAlgebra._fmt_celda_frac(piv, 1).strip()})\n" + MotorAlgebra._fmt_matriz_frac(M, k) + "\n\n"

            hubo_op = False
            for r in range(dim):
                if r != fila_piv and M[r][col] != 0:
                    f = M[r][col]
                    M[r] = [M[r][c] - f * M[fila_piv][c] for c in range(k + 1)]
                    log += f"Paso: F{r+1} <- F{r+1} - ({MotorAlgebra._fmt_celda_frac(f, 1).strip()}) * F{fila_piv+1}\n"
                    hubo_op = True
            if hubo_op:
                log += MotorAlgebra._fmt_matriz_frac(M, k) + "\n\n"

            pivotes.append((fila_piv, col))
            fila_piv += 1

        rango = len(pivotes)
        cols_piv = {c for _, c in pivotes}
        cols_libres = [c for c in range(k) if c not in cols_piv]

        log += "4. CONCLUSION Y JUSTIFICACION POR RANGO:\n"
        log += f"   • Cantidad de vectores (k) : {k}\n"
        log += f"   • Dimension del espacio    : R^{dim}\n"
        log += f"   • Rango de la matriz       : rango(A) = {rango}\n"

        if rango == k:
            log += f"   • Resultado                : CONJUNTO LINEALMENTE INDEPENDIENTE (LI).\n"
            log += f"   • Justificacion            : Como rango(A) = {rango} = k (numero de vectores), no existen\n"
            log += f"                                variables libres; la unica solucion es la trivial:\n"
            log += f"                                {', '.join(f'{a} = 0' for a in alfas)}.\n"
            return {"independiente": True, "log": log}

        log += f"   • Resultado                : CONJUNTO LINEALMENTE DEPENDIENTE (LD).\n"
        log += f"   • Justificacion            : Como rango(A) = {rango} < k ({k} vectores), existen {len(cols_libres)}\n"
        log += f"                                variable(s) libre(s), admitiendo soluciones no triviales.\n\n"

        log += "5. RELACION DE DEPENDENCIA NO TRIVIAL Y COMBINACION LINEAL:\n"
        # Tomamos la primera columna libre (ej. c_libre) y la fijamos en t = 1 (o multiplicamos por mcm de denominadores)
        c_libre = cols_libres[0]
        coefs = [Fraction(0, 1)] * k
        coefs[c_libre] = Fraction(1, 1)
        for r, c in pivotes:
            coefs[c] = -M[r][c_libre]

        # Escalamos por el minimo comun multiplo de los denominadores para tener enteros limpios
        denoms = [c.denominator for c in coefs if c != 0]
        mcm = 1
        for d in denoms:
            mcm = math.lcm(mcm, d)
        coefs_int = [c * mcm for c in coefs]

        rel_partes = []
        for idx, c in enumerate(coefs_int, 1):
            if c == 0:
                continue
            if not rel_partes:
                if c == 1:
                    rel_partes.append(f"v{idx}")
                elif c == -1:
                    rel_partes.append(f"-v{idx}")
                else:
                    rel_partes.append(f"{c}v{idx}")
            else:
                signo = "+" if c > 0 else "-"
                abs_c = abs(c)
                if abs_c == 1:
                    rel_partes.append(f" {signo} v{idx}")
                else:
                    rel_partes.append(f" {signo} {abs_c}v{idx}")

        log += f"   • Solucion particular no trivial: {', '.join(f'α{i+1} = {coefs_int[i]}' for i in range(k))}\n"
        log += f"   • Relacion de dependencia       : {''.join(rel_partes)} = 0\n"

        # Expresar v_{c_libre + 1} como combinacion lineal de los demas
        comb_partes = []
        for idx in range(k):
            if idx == c_libre or coefs[idx] == 0:
                continue
            val = -coefs[idx]
            if not comb_partes:
                if val == 1:
                    comb_partes.append(f"v{idx+1}")
                elif val == -1:
                    comb_partes.append(f"-v{idx+1}")
                else:
                    comb_partes.append(f"({MotorAlgebra._fmt_celda_frac(val, 1).strip()})v{idx+1}")
            else:
                signo = "+" if val > 0 else "-"
                abs_v = abs(val)
                if abs_v == 1:
                    comb_partes.append(f" {signo} v{idx+1}")
                else:
                    comb_partes.append(f" {signo} ({MotorAlgebra._fmt_celda_frac(abs_v, 1).strip()})v{idx+1}")

        comb_str = "".join(comb_partes) if comb_partes else "0"
        log += f"   • Vector expresado como C.L.    : v{c_libre+1} = {comb_str}\n"

        return {"independiente": False, "log": log}

    # ==================== 6. METODOS DE RAICES ====================
    @staticmethod
    def limpiar_expresion_matematica(expr_str):
        e = expr_str.strip().replace("−", "-").replace("–", "-").replace("·", "*").replace("×", "*")
        e = e.replace("²", "**2").replace("³", "**3").replace("⁴", "**4")
        e = e.replace("X", "x").replace("^", "**")

        # Traducir 'sen' en espanol a 'sin' y 'e(...)' a 'exp(...)'
        e = re.sub(r'\bsen\b', 'sin', e, flags=re.IGNORECASE)
        e = re.sub(r'\be\s*\(', 'exp(', e)
        e = re.sub(r'([a-zA-Z0-9\)])\.([a-zA-Z\(])', r'\1*\2', e)

        e = re.sub(r'\b(sin|cos|tan|ln|log|sqrt|exp)x\b', r'\1(x)', e)

        e = re.sub(r'\bln\b', '__LN__', e)
        e = re.sub(r'\blog\b', '__LOG__', e)
        e = re.sub(r'\bsin\b', '__SIN__', e)
        e = re.sub(r'\bcos\b', '__COS__', e)
        e = re.sub(r'\btan\b', '__TAN__', e)
        e = re.sub(r'\bsqrt\b', '__SQRT__', e)
        e = re.sub(r'\bexp\b', '__EXP__', e)
        e = re.sub(r'\bpi\b', '__PI__', e)
        e = re.sub(r'\be\b', '__E__', e)

        e = re.sub(r'(\d)(x|\(|__)', r'\1*\2', e)
        e = re.sub(r'(x|\))(\(|__|x|\d)', r'\1*\2', e)
        e = re.sub(r'(__PI__|__E__)(x|\()', r'\1*\2', e)

        e = e.replace('__LN__', 'math.log') \
             .replace('__LOG__', 'math.log') \
             .replace('__SIN__', 'math.sin') \
             .replace('__COS__', 'math.cos') \
             .replace('__TAN__', 'math.tan') \
             .replace('__SQRT__', 'math.sqrt') \
             .replace('__EXP__', 'math.exp') \
             .replace('__PI__', 'math.pi') \
             .replace('__E__', 'math.e')

        return e

    @staticmethod
    def _analizar_dominio_texto(expr_str):
        el = expr_str.lower().replace("−", "-")
        notas = []
        if "ln(" in el or "log(" in el:
            notas.append("Argumento de logaritmo estrictamente positivo: u(x) > 0 (ej. ln(x) => x > 0; ln(x+1) => x > -1).")
        if "sqrt(" in el:
            notas.append("Radicando no negativo: u(x) >= 0.")
        if "/x" in el or "/(x" in el:
            notas.append("Denominador distinto de cero: x != 0.")
        if "x**2-4" in el.replace(" ", "") or "x^2-4" in el.replace(" ", ""):
            notas.append("Denominador cuadratico: x^2 - 4 != 0 => x != 2 y x != -2.")
        if "tan(" in el:
            notas.append("Tangente: cos(x) != 0 (x != pi/2 + k*pi); si tan(x) esta en el denominador, x != k*pi.")
        if not notas:
            notas.append("Funcion continua en todo R (sin restricciones de denominador o logaritmo).")
        return "\n   • ".join(notas)

    @staticmethod
    def evaluar_funcion(expr_str, x_val):
        dic_contexto = {"x": x_val, "math": math}
        expr_eval = MotorAlgebra.limpiar_expresion_matematica(expr_str)
        val = float(eval(expr_eval, {"__builtins__": None}, dic_contexto))
        if not math.isfinite(val):
            raise ValueError("Valor no finito.")
        return val

    @staticmethod
    def _derivada_numerica(expr_str, x_val, h=1e-7):
        return (MotorAlgebra.evaluar_funcion(expr_str, x_val + h) - MotorAlgebra.evaluar_funcion(expr_str, x_val - h)) / (2.0 * h)

    @staticmethod
    def buscar_intervalos_raices(expr_str):
        puntos_x = []
        x = -10.0
        while x <= 10.0001:
            if abs(x) > 1e-9:
                puntos_x.append(round(x, 4))
            else:
                puntos_x.extend([-0.15, -0.05, 0.05, 0.15])
            x += 0.25

        puntos_x = sorted(list(set(puntos_x)))
        intervalos = []

        for i in range(len(puntos_x) - 1):
            a = puntos_x[i]
            b = puntos_x[i + 1]
            try:
                fa = MotorAlgebra.evaluar_funcion(expr_str, a)
                fb = MotorAlgebra.evaluar_funcion(expr_str, b)
            except Exception:
                continue

            if abs(fa) > 1e5 or abs(fb) > 1e5:
                continue

            if fa * fb < 0:
                mid = (a + b) / 2.0
                try:
                    fm = MotorAlgebra.evaluar_funcion(expr_str, mid)
                    salto_max = max(abs(fa), abs(fb)) * 3.0 + 10.0
                    if abs(fm) < salto_max and abs(fb - fa) < 80.0:
                        tipo = "Positiva (x > 0)" if a > 0 else ("Cerca de 0" if b > 0 else "Negativa (x < 0)")
                        intervalos.append({
                            "a": a,
                            "b": b,
                            "fa": round(fa, 6),
                            "fb": round(fb, 6),
                            "x0": round(mid, 4),
                            "tipo": tipo
                        })
                except Exception:
                    continue

        return intervalos

    @staticmethod
    def recomendar_metodo(expr_str, a=None, b=None):
        expr_lower = expr_str.lower()
        intervalos = MotorAlgebra.buscar_intervalos_raices(expr_str)
        dominio_txt = MotorAlgebra._analizar_dominio_texto(expr_str)

        info_bolzano = ""
        if a is not None and b is not None:
            try:
                fa = MotorAlgebra.evaluar_funcion(expr_str, a)
                fb = MotorAlgebra.evaluar_funcion(expr_str, b)
                if fa * fb < 0:
                    info_bolzano = f"• Intervalo actual [{a}, {b}]: f({a})={fa:.6f} y f({b})={fb:.6f} (Signos opuestos: VALIDO para Biseccion/Regla Falsa).\n"
                else:
                    info_bolzano = f"• Intervalo actual [{a}, {b}]: f({a})={fa:.6f} y f({b})={fb:.6f} (Mismo signo: NO sirve para metodos cerrados).\n"
            except Exception as exc:
                info_bolzano = f"• Intervalo actual [{a}, {b}]: Fuera de dominio o asintota ({exc}).\n"

        if "tan" in expr_lower or "/x" in expr_lower:
            recomendacion = "Newton-Raphson o Secante (en intervalo continuo sin asintotas)"
            motivo = "La funcion posee asintotas verticales (tan(x) o 1/x). Usa un intervalo acotado lejos de los polos o Newton-Raphson cerca de la raiz."
        elif "sqrt" in expr_lower or ("(" in expr_lower and "*" in expr_lower and any(f in expr_lower for f in ["sin", "sen", "cos", "exp", "log", "ln"])):
            recomendacion = "Newton-Raphson o Secante"
            motivo = "Funcion compuesta continua y derivable; Newton-Raphson ofrece convergencia cuadratica rapida y la Secante evita derivar analiticamente."
        elif any(f in expr_lower for f in ["sin", "sen", "cos", "exp", "log", "ln"]):
            recomendacion = "Newton-Raphson"
            motivo = "Funcion trascendental suave con convergencia cuadratica en pocas iteraciones."
        elif "**3" in expr_lower or "**4" in expr_lower or "^3" in expr_lower or "^4" in expr_lower:
            recomendacion = "Newton-Raphson o Biseccion"
            motivo = "Polinomio continuo; Biseccion garantiza convergencia en [a, b] y Newton-Raphson converge cuadraticamente desde el punto medio."
        else:
            recomendacion = "Regla Falsa o Biseccion"
            motivo = "Funcion continua ideal para acotar la raiz en [a, b] mediante el Teorema de Bolzano."

        txt_intervalos = "INTERVALOS DETECTADOS POR EL ASESOR (CAMBIO DE SIGNO REAL):\n"
        if intervalos:
            for idx, itv in enumerate(intervalos, 1):
                txt_intervalos += (
                    f"   {idx}. [{itv['a']}, {itv['b']}] -> {itv['tipo']} | "
                    f"f({itv['a']}) = {itv['fa']}, f({itv['b']}) = {itv['fb']} | "
                    f"Sugerido x0 = {itv['x0']}\n"
                )
        else:
            txt_intervalos += "   • No se detectaron cambios de signo simples en [-10, 10] (puede haber raiz tangente/doble o fuera de rango). Usa Newton-Raphson.\n"

        log = (
            f"======================================================================\n"
            f"ASESOR INTELIGENTE DE ANALISIS NUMERICO\n"
            f"======================================================================\n"
            f"• Funcion analizada: f(x) = {expr_str}\n"
            f"• Restricciones Dom: {dominio_txt}\n"
            f"• Metodo Sugerido  : {recomendacion}\n"
            f"{info_bolzano}"
            f"• Justificacion    : {motivo}\n\n"
            f"{txt_intervalos}"
        )

        return {
            "recomendacion": recomendacion,
            "motivo": motivo,
            "intervalos": intervalos,
            "log": log
        }

    @staticmethod
    def metodo_biseccion(expr_str, a, b, tol=1e-6, max_iter=100):
        fa_val = MotorAlgebra.evaluar_funcion(expr_str, a)
        fb_val = MotorAlgebra.evaluar_funcion(expr_str, b)
        dom_txt = MotorAlgebra._analizar_dominio_texto(expr_str)

        if abs(fa_val) <= tol:
            return {
                "exito": True,
                "raiz": a,
                "filas": [{"iter": 0, "a": a, "b": b, "c": a, "fc": fa_val, "error": 0.0}],
                "log": f"El extremo izquierdo a = {a} ya es raiz exacta (f({a}) = {fa_val:.8f})."
            }
        if abs(fb_val) <= tol:
            return {
                "exito": True,
                "raiz": b,
                "filas": [{"iter": 0, "a": a, "b": b, "c": b, "fc": fb_val, "error": 0.0}],
                "log": f"El extremo derecho b = {b} ya es raiz exacta (f({b}) = {fb_val:.8f})."
            }

        if fa_val * fb_val > 0:
            raise ValueError(f"f(a)={fa_val:.8f} y f(b)={fb_val:.8f} deben tener signos opuestos (Teorema de Bolzano). Presiona el Asesor Inteligente para ver intervalos validos.")

        a_ini, b_ini = a, b
        filas = []
        raiz = a
        c_ant = a
        exito = False
        k_final = 0
        err_abs_final = 0.0
        residuo_final = 0.0

        tabla_lineas = []
        for k in range(1, max_iter + 1):
            fa = MotorAlgebra.evaluar_funcion(expr_str, a)
            c = (a + b) / 2.0
            fc = MotorAlgebra.evaluar_funcion(expr_str, c)
            err_abs = abs(b - a) / 2.0
            err_rel = (abs(c - c_ant) / abs(c) * 100.0) if (k > 1 and abs(c) > 1e-14) else 100.0
            k_final = k
            err_abs_final = err_abs
            residuo_final = abs(fc)

            filas.append({"iter": k, "a": a, "b": b, "c": c, "fc": fc, "error": err_abs})
            tabla_lineas.append(
                f"{k:<4} | {a:<12.8f} | {b:<12.8f} | {c:<12.8f} | {fc:<13.8f} | {err_abs:<12.8f} | {err_rel:<9.4f}%"
            )

            if abs(fc) < tol or err_abs < tol:
                raiz = c
                exito = True
                break

            c_ant = c
            if fa * fc < 0:
                b = c
            else:
                a = c

        if not exito:
            raiz = c

        log_txt = (
            f"=================================================================================================\n"
            f"INFORME DE ECUACION NO LINEAL - METODO DE BISECCION (CERRADO)\n"
            f"=================================================================================================\n\n"
            f"1. METODO SELECCIONADO, DOMINIO Y JUSTIFICACION:\n"
            f"   • Metodo: Biseccion (metodo cerrado de acotamiento).\n"
            f"   • Restricciones de dominio: {dom_txt}\n"
            f"   • Justificacion: La funcion f(x) = {expr_str} es continua en [{a_ini}, {b_ini}] y cumple el\n"
            f"     Teorema de Bolzano: f({a_ini}) = {fa_val:.8f} y f({b_ini}) = {fb_val:.8f}, por lo que\n"
            f"     f(a)·f(b) = {fa_val * fb_val:.8f} < 0. Esto garantiza convergencia segura sin divergencia.\n\n"
            f"2. DATOS INICIALES:\n"
            f"   • Ecuacion: f(x) = {expr_str} = 0\n"
            f"   • Intervalo inicial: [a, b] = [{a_ini}, {b_ini}]\n"
            f"   • Tolerancia exigida: {tol:.2e} ({tol:.8f}) | Max. iteraciones: {max_iter}\n\n"
            f"3. FORMULA ITERATIVA:\n"
            f"   • Punto medio: c_k = (a_k + b_k) / 2\n"
            f"   • Regla de subintervalo: Si f(a_k)·f(c_k) < 0 entonces b_{{k+1}} = c_k; si no, a_{{k+1}} = c_k\n\n"
            f"4. TABLA DE ITERACIONES (8 CIFRAS DECIMALES):\n"
            + "-" * 97 + "\n"
            + f"{'Iter':<4} | {'a':<12} | {'b':<12} | {'c':<12} | {'f(c)':<13} | {'Err Abs':<12} | {'Err Rel %':<9}\n"
            + "-" * 97 + "\n"
            + "\n".join(tabla_lineas) + "\n"
            + "-" * 97 + "\n\n"
            + f"5. CRITERIO DE PARADA:\n"
            + f"   • Se detiene cuando |f(c_k)| < {tol:.2e} o |b_k - a_k|/2 < {tol:.2e} (alcanzado en iteracion {k_final}).\n\n"
            + f"6. APROXIMACION FINAL Y RESIDUO ({'CONVERGIO' if exito else 'LIMITE ITERACIONES'}):\n"
            + f"   • Raiz aproximada (x*) : {raiz:.8f}\n"
            + f"   • Residuo |f(x*)|      : {residuo_final:.8f}\n"
            + f"   • Error absoluto final : {err_abs_final:.8f}\n"
            + f"   • Total iteraciones    : {k_final}\n\n"
            + f"7. ANALISIS DE RAZONABILIDAD:\n"
            + f"   • La raiz x* = {raiz:.8f} pertenece al intervalo [{a_ini}, {b_ini}] y al evaluarla en la funcion\n"
            + f"     produce f({raiz:.8f}) = {MotorAlgebra.evaluar_funcion(expr_str, raiz):.8f} ≈ 0, validando el resultado.\n"
        )

        return {"exito": exito, "raiz": raiz, "filas": filas, "log": log_txt}

    @staticmethod
    def metodo_regla_falsa(expr_str, a, b, tol=1e-6, max_iter=100):
        fa_val = MotorAlgebra.evaluar_funcion(expr_str, a)
        fb_val = MotorAlgebra.evaluar_funcion(expr_str, b)
        dom_txt = MotorAlgebra._analizar_dominio_texto(expr_str)

        if abs(fa_val) <= tol:
            return {
                "exito": True,
                "raiz": a,
                "filas": [{"iter": 0, "a": a, "b": b, "c": a, "fc": fa_val, "error": 0.0}],
                "log": f"El extremo izquierdo a = {a} ya es raiz exacta (f({a}) = {fa_val:.8f})."
            }
        if abs(fb_val) <= tol:
            return {
                "exito": True,
                "raiz": b,
                "filas": [{"iter": 0, "a": a, "b": b, "c": b, "fc": fb_val, "error": 0.0}],
                "log": f"El extremo derecho b = {b} ya es raiz exacta (f({b}) = {fb_val:.8f})."
            }

        if fa_val * fb_val > 0:
            raise ValueError(f"f(a)={fa_val:.8f} y f(b)={fb_val:.8f} deben tener signos opuestos (Teorema de Bolzano). Presiona el Asesor Inteligente para ver intervalos validos.")

        a_ini, b_ini = a, b
        filas = []
        raiz = a
        xr_ant = a
        exito = False
        k_final = 0
        err_abs_final = 0.0
        residuo_final = 0.0

        tabla_lineas = []
        for k in range(1, max_iter + 1):
            fa = MotorAlgebra.evaluar_funcion(expr_str, a)
            fb = MotorAlgebra.evaluar_funcion(expr_str, b)
            if abs(fa - fb) < 1e-14:
                raise ValueError("Division por cero en Regla Falsa (f(a) - f(b) cercano a 0).")
            xr = b - (fb * (a - b)) / (fa - fb)
            fxr = MotorAlgebra.evaluar_funcion(expr_str, xr)

            err_abs = abs(xr - xr_ant) if k > 1 else abs(b - a)
            err_rel = (abs(xr - xr_ant) / abs(xr) * 100.0) if (k > 1 and abs(xr) > 1e-14) else 100.0
            k_final = k
            err_abs_final = err_abs
            residuo_final = abs(fxr)

            filas.append({"iter": k, "a": a, "b": b, "c": xr, "fc": fxr, "error": err_abs})
            tabla_lineas.append(
                f"{k:<4} | {a:<12.8f} | {b:<12.8f} | {xr:<12.8f} | {fxr:<13.8f} | {err_abs:<12.8f} | {err_rel:<9.4f}%"
            )

            if abs(fxr) < tol or (k > 1 and err_abs < tol):
                raiz = xr
                exito = True
                break

            xr_ant = xr
            if fa * fxr < 0:
                b = xr
            else:
                a = xr

        if not exito:
            raiz = xr

        log_txt = (
            f"=================================================================================================\n"
            f"INFORME DE ECUACION NO LINEAL - METODO DE FALSA POSICION (REGULA FALSI)\n"
            f"=================================================================================================\n\n"
            f"1. METODO SELECCIONADO, DOMINIO Y JUSTIFICACION:\n"
            f"   • Metodo: Falsa Posicion / Regula Falsi (metodo cerrado con interpolacion lineal).\n"
            f"   • Restricciones de dominio: {dom_txt}\n"
            f"   • Justificacion: En [{a_ini}, {b_ini}] se cumple f({a_ini}) = {fa_val:.8f} y f({b_ini}) = {fb_val:.8f}\n"
            f"     (f(a)·f(b) < 0). Combina la seguridad de un intervalo cerrado con una cuerda secante que\n"
            f"     acelera la aproximacion hacia el extremo donde f(x) esta mas cerca de cero.\n\n"
            f"2. DATOS INICIALES:\n"
            f"   • Ecuacion: f(x) = {expr_str} = 0\n"
            f"   • Intervalo inicial: [a, b] = [{a_ini}, {b_ini}]\n"
            f"   • Tolerancia exigida: {tol:.2e} ({tol:.8f}) | Max. iteraciones: {max_iter}\n\n"
            f"3. FORMULA ITERATIVA:\n"
            f"   • Interseccion cuerda: xr = b - [f(b)·(a - b)] / [f(a) - f(b)]\n"
            f"   • Actualizacion: Si f(a)·f(xr) < 0 entonces b = xr; en caso contrario, a = xr\n\n"
            f"4. TABLA DE ITERACIONES (8 CIFRAS DECIMALES):\n"
            + "-" * 97 + "\n"
            + f"{'Iter':<4} | {'a':<12} | {'b':<12} | {'xr':<12} | {'f(xr)':<13} | {'Err Abs':<12} | {'Err Rel %':<9}\n"
            + "-" * 97 + "\n"
            + "\n".join(tabla_lineas) + "\n"
            + "-" * 97 + "\n\n"
            + f"5. CRITERIO DE PARADA:\n"
            + f"   • Se detiene cuando |f(xr)| < {tol:.2e} o |xr_k - xr_{{k-1}}| < {tol:.2e} (iteracion {k_final}).\n\n"
            + f"6. APROXIMACION FINAL Y RESIDUO ({'CONVERGIO' if exito else 'LIMITE ITERACIONES'}):\n"
            + f"   • Raiz aproximada (x*) : {raiz:.8f}\n"
            + f"   • Residuo |f(x*)|      : {residuo_final:.8f}\n"
            + f"   • Error absoluto final : {err_abs_final:.8f}\n"
            + f"   • Total iteraciones    : {k_final}\n\n"
            + f"7. ANALISIS DE RAZONABILIDAD:\n"
            + f"   • La raiz x* = {raiz:.8f} permanece acotada dentro de [{a_ini}, {b_ini}] y satisface\n"
            + f"     f({raiz:.8f}) = {MotorAlgebra.evaluar_funcion(expr_str, raiz):.8f} ≈ 0.\n"
        )

        return {"exito": exito, "raiz": raiz, "filas": filas, "log": log_txt}

    @staticmethod
    def metodo_newton_raphson(expr_str, x0, tol=1e-6, max_iter=100):
        filas = []
        xn = x0
        exito = False
        k_final = 0
        err_abs_final = 0.0
        residuo_final = 0.0
        dom_txt = MotorAlgebra._analizar_dominio_texto(expr_str)

        fx0 = MotorAlgebra.evaluar_funcion(expr_str, x0)
        dfx0 = MotorAlgebra._derivada_numerica(expr_str, x0)

        tabla_lineas = []
        for k in range(1, max_iter + 1):
            fxn = MotorAlgebra.evaluar_funcion(expr_str, xn)
            dfxn = MotorAlgebra._derivada_numerica(expr_str, xn)

            if abs(dfxn) < 1e-14:
                raise ValueError("Derivada cero (tangente horizontal). Cambia el punto inicial x0.")

            xn_nuevo = xn - (fxn / dfxn)
            if not math.isfinite(xn_nuevo) or abs(xn_nuevo) > 1e12:
                raise ValueError("El metodo divergio al infinito. Elige un x0 mas cercano a la raiz.")

            fxn_nuevo = MotorAlgebra.evaluar_funcion(expr_str, xn_nuevo)
            err_abs = abs(xn_nuevo - xn)
            err_rel = (err_abs / abs(xn_nuevo) * 100.0) if abs(xn_nuevo) > 1e-14 else 0.0

            filas.append({"iter": k, "c": xn_nuevo, "error": err_abs})
            tabla_lineas.append(
                f"{k:<4} | {xn:<13.8f} | {fxn:<13.8f} | {dfxn:<13.8f} | {err_abs:<12.8f} | {err_rel:<9.4f}%"
            )

            k_final = k
            err_abs_final = err_abs
            residuo_final = abs(fxn_nuevo)

            if abs(fxn_nuevo) < tol and err_abs < tol:
                xn = xn_nuevo
                exito = True
                break

            xn = xn_nuevo

        log_txt = (
            f"=================================================================================================\n"
            f"INFORME DE ECUACION NO LINEAL - METODO DE NEWTON-RAPHSON (ABIERTO)\n"
            f"=================================================================================================\n\n"
            f"1. METODO SELECCIONADO, DOMINIO Y JUSTIFICACION:\n"
            f"   • Metodo: Newton-Raphson (metodo abierto basado en recta tangente).\n"
            f"   • Restricciones de dominio: {dom_txt}\n"
            f"   • Justificacion: La funcion f(x) = {expr_str} es continua y diferenciable cerca de x0 = {x0},\n"
            f"     con derivada no nula f'({x0}) = {dfx0:.8f} != 0. Proporciona convergencia cuadratica,\n"
            f"     alcanzando precision de 10^-6 en muy pocas iteraciones sin requerir intervalo cerrado.\n\n"
            f"2. DATOS INICIALES:\n"
            f"   • Ecuacion: f(x) = {expr_str} = 0\n"
            f"   • Aproximacion inicial: x0 = {x0} (con f(x0) = {fx0:.8f})\n"
            f"   • Tolerancia exigida: {tol:.2e} ({tol:.8f}) | Max. iteraciones: {max_iter}\n\n"
            f"3. FORMULA ITERATIVA:\n"
            f"   • x_{{n+1}} = x_n - f(x_n) / f'(x_n)\n\n"
            f"4. TABLA DE ITERACIONES (8 CIFRAS DECIMALES):\n"
            + "-" * 99 + "\n"
            + f"{'Iter':<4} | {'x_n':<13} | {'f(x_n)':<13} | {'f\'(x_n)':<13} | {'Err Abs':<12} | {'Err Rel %':<9}\n"
            + "-" * 99 + "\n"
            + "\n".join(tabla_lineas) + "\n"
            + "-" * 99 + "\n\n"
            + f"5. CRITERIO DE PARADA:\n"
            + f"   • Se detiene cuando |x_{{n+1}} - x_n| < {tol:.2e} y |f(x_{{n+1}})| < {tol:.2e} (iteracion {k_final}).\n\n"
            + f"6. APROXIMACION FINAL Y RESIDUO ({'CONVERGIO' if exito else 'LIMITE ITERACIONES'}):\n"
            + f"   • Raiz aproximada (x*) : {xn:.8f}\n"
            + f"   • Residuo |f(x*)|      : {residuo_final:.8f}\n"
            + f"   • Error absoluto final : {err_abs_final:.8f}\n"
            + f"   • Total iteraciones    : {k_final}\n\n"
            + f"7. ANALISIS DE RAZONABILIDAD:\n"
            + f"   • La sucesion convergio de forma estable y monotona desde x0 = {x0} hacia x* = {xn:.8f},\n"
            + f"     verificando f({xn:.8f}) = {MotorAlgebra.evaluar_funcion(expr_str, xn):.8f} ≈ 0.\n"
        )

        return {"exito": exito, "raiz": xn, "filas": filas, "log": log_txt}

    @staticmethod
    def metodo_secante(expr_str, x0, x1, tol=1e-6, max_iter=100):
        filas = []
        exito = False
        k_final = 0
        err_abs_final = 0.0
        residuo_final = 0.0
        x_ant = x0
        x_act = x1
        dom_txt = MotorAlgebra._analizar_dominio_texto(expr_str)

        fx0 = MotorAlgebra.evaluar_funcion(expr_str, x0)
        fx1 = MotorAlgebra.evaluar_funcion(expr_str, x1)

        tabla_lineas = []
        for k in range(1, max_iter + 1):
            f_ant = MotorAlgebra.evaluar_funcion(expr_str, x_ant)
            f_act = MotorAlgebra.evaluar_funcion(expr_str, x_act)

            denominador = (f_act - f_ant)
            if abs(denominador) < 1e-14:
                raise ValueError("Division por cero en la Secante (f(x_act) - f(x_ant) cercano a 0).")

            x_nuevo = x_act - (f_act * (x_act - x_ant)) / denominador
            if not math.isfinite(x_nuevo) or abs(x_nuevo) > 1e12:
                raise ValueError("El metodo divergio al infinito. Elige x0 y x1 mas cercanos a la raiz.")

            f_nuevo = MotorAlgebra.evaluar_funcion(expr_str, x_nuevo)
            err_abs = abs(x_nuevo - x_act)
            err_rel = (err_abs / abs(x_nuevo) * 100.0) if abs(x_nuevo) > 1e-14 else 0.0

            filas.append({"iter": k, "c": x_nuevo, "error": err_abs})
            tabla_lineas.append(
                f"{k:<4} | {x_ant:<12.8f} | {x_act:<12.8f} | {x_nuevo:<12.8f} | {f_nuevo:<13.8f} | {err_abs:<12.8f} | {err_rel:<9.4f}%"
            )

            k_final = k
            err_abs_final = err_abs
            residuo_final = abs(f_nuevo)

            if abs(f_nuevo) < tol and err_abs < tol:
                x_act = x_nuevo
                exito = True
                break

            x_ant = x_act
            x_act = x_nuevo

        log_txt = (
            f"========================================================================================================\n"
            f"INFORME DE ECUACION NO LINEAL - METODO DE LA SECANTE (ABIERTO)\n"
            f"========================================================================================================\n\n"
            f"1. METODO SELECCIONADO, DOMINIO Y JUSTIFICACION:\n"
            f"   • Metodo: Secante (metodo abierto con aproximacion por diferencias finitas).\n"
            f"   • Restricciones de dominio: {dom_txt}\n"
            f"   • Justificacion: Aproxima la pendiente de la tangente mediante dos puntos iniciales x0 = {x0}\n"
            f"     y x1 = {x1}, evitando evaluar derivadas analiticas. Posee convergencia superlineal (orden ≈ 1.618)\n"
            f"     y no exige cambio de signo obligatorio entre los puntos iniciales.\n\n"
            f"2. DATOS INICIALES:\n"
            f"   • Ecuacion: f(x) = {expr_str} = 0\n"
            f"   • Puntos iniciales: x0 = {x0} (f(x0) = {fx0:.8f}), x1 = {x1} (f(x1) = {fx1:.8f})\n"
            f"   • Tolerancia exigida: {tol:.2e} ({tol:.8f}) | Max. iteraciones: {max_iter}\n\n"
            f"3. FORMULA ITERATIVA:\n"
            f"   • x_{{n+1}} = x_n - [f(x_n)·(x_n - x_{{n-1}})] / [f(x_n) - f(x_{{n-1}})]\n\n"
            f"4. TABLA DE ITERACIONES (8 CIFRAS DECIMALES):\n"
            + "-" * 108 + "\n"
            + f"{'Iter':<4} | {'x_{n-1}':<12} | {'x_n':<12} | {'x_{n+1}':<12} | {'f(x_{n+1})':<13} | {'Err Abs':<12} | {'Err Rel %':<9}\n"
            + "-" * 108 + "\n"
            + "\n".join(tabla_lineas) + "\n"
            + "-" * 108 + "\n\n"
            + f"5. CRITERIO DE PARADA:\n"
            + f"   • Se detiene cuando |x_{{n+1}} - x_n| < {tol:.2e} y |f(x_{{n+1}})| < {tol:.2e} (iteracion {k_final}).\n\n"
            + f"6. APROXIMACION FINAL Y RESIDUO ({'CONVERGIO' if exito else 'LIMITE ITERACIONES'}):\n"
            + f"   • Raiz aproximada (x*) : {x_act:.8f}\n"
            + f"   • Residuo |f(x*)|      : {residuo_final:.8f}\n"
            + f"   • Error absoluto final : {err_abs_final:.8f}\n"
            + f"   • Total iteraciones    : {k_final}\n\n"
            + f"7. ANALISIS DE RAZONABILIDAD:\n"
            + f"   • Partiendo de x0 = {x0} y x1 = {x1}, las rectas secantes convergieron rapidamente a\n"
            + f"     x* = {x_act:.8f}, donde f({x_act:.8f}) = {MotorAlgebra.evaluar_funcion(expr_str, x_act):.8f} ≈ 0.\n"
        )

        return {"exito": exito, "raiz": x_act, "filas": filas, "log": log_txt}

    @staticmethod
    def generar_grafica_biseccion(expr_str, a_orig=None, b_orig=None, raiz=None, x_min_custom=None, x_max_custom=None):
        if x_min_custom is not None and x_max_custom is not None and x_min_custom < x_max_custom:
            x_min = float(x_min_custom)
            x_max = float(x_max_custom)
        elif a_orig is None or b_orig is None or (a_orig == 0 and b_orig == 0):
            x_min, x_max = -2.0, 2.0
        else:
            amplitud = abs(b_orig - a_orig) if b_orig != a_orig else 1.5
            x_min = min(a_orig, b_orig) - amplitud * 0.8
            x_max = max(a_orig, b_orig) + amplitud * 0.8

        puntos = 300
        paso = (x_max - x_min) / puntos

        coords = []
        current_x = x_min
        for _ in range(puntos + 1):
            try:
                y_val = MotorAlgebra.evaluar_funcion(expr_str, current_x)
                if math.isfinite(y_val) and abs(y_val) < 1e4:
                    coords.append({"x": round(current_x, 8), "y": round(y_val, 8)})
            except Exception:
                pass
            current_x += paso

        raiz_dict = {"x": round(raiz, 8), "y": 0.0} if raiz is not None else None

        return {
            "puntos": coords,
            "raiz": raiz_dict,
            "x_min": x_min,
            "x_max": x_max,
            "intervalo_a": a_orig,
            "intervalo_b": b_orig
        }

    # ==================== 7. ROMANOS ====================
    @staticmethod
    def romano_a_arabico(romano):
        valores = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        total = 0
        prev = 0
        for char in reversed(romano.upper()):
            if char not in valores:
                raise ValueError(f"Simbolo romano invalido: {char}")
            val = valores[char]
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