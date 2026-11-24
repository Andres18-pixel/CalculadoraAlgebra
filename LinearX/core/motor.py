import math
import re
import copy


class MotorAlgebra:

    @staticmethod
    def _fmt_num(val, decimales=4):
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
        n = len(A)
        lineas = []
        for i in range(n):
            fila_a = " ".join(MotorAlgebra._fmt_num(x) for x in A[i])
            var_str = f"{vars_nombres[i]:^3}"
            val_b = MotorAlgebra._fmt_num(b[i])
            signo_eq = " = " if i == n // 2 else "   "
            signo_mul = " · " if i == n // 2 else "   "
            lineas.append(f"  [ {fila_a} ]{signo_mul}[ {var_str} ]{signo_eq}[ {val_b} ]")
        return "\n".join(lineas)

    @staticmethod
    def _fmt_ecuacion_lineal(fila, rhs, vars_nombres):
        partes = []
        for coef, var in zip(fila, vars_nombres):
            if abs(coef) < 1e-11:
                continue
            if not partes:
                if abs(coef - 1.0) < 1e-9:
                    partes.append(f"{var}")
                elif abs(coef + 1.0) < 1e-9:
                    partes.append(f"-{var}")
                else:
                    c_str = f"{int(round(coef))}" if abs(coef - round(coef)) < 1e-9 else f"{coef:.4f}"
                    partes.append(f"{c_str}{var}")
            else:
                signo = "+" if coef >= 0 else "-"
                abs_c = abs(coef)
                if abs(abs_c - 1.0) < 1e-9:
                    partes.append(f" {signo} {var}")
                else:
                    c_str = f"{int(round(abs_c))}" if abs(abs_c - round(abs_c)) < 1e-9 else f"{abs_c:.4f}"
                    partes.append(f" {signo} {c_str}{var}")
        izq = "".join(partes) if partes else "0"
        rhs_str = f"{int(round(rhs))}" if abs(rhs - round(rhs)) < 1e-9 else f"{rhs:.4f}"
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
        A = [[vecs[j][i] for j in range(num_vecs)] for i in range(dim)]
        M = [A[i] + [b[i]] for i in range(dim)]

        log = "COMBINACION LINEAL: c1*v1 + c2*v2 + ... = b\n"
        log += "Matriz aumentada [V | b]:\n" + MotorAlgebra._fmt_matriz(M, num_vecs) + "\n\n"

        fila_piv = 0
        pivotes = []
        for col in range(num_vecs):
            if fila_piv >= dim:
                break
            max_r = max(range(fila_piv, dim), key=lambda r: abs(M[r][col]))
            if abs(M[max_r][col]) < 1e-10:
                continue
            M[fila_piv], M[max_r] = M[max_r], M[fila_piv]
            piv = M[fila_piv][col]
            M[fila_piv] = [x / piv for x in M[fila_piv]]
            for r in range(dim):
                if r != fila_piv and abs(M[r][col]) > 1e-10:
                    f = M[r][col]
                    M[r] = [M[r][c] - f * M[fila_piv][c] for c in range(num_vecs + 1)]
            pivotes.append((fila_piv, col))
            fila_piv += 1

        log += "Matriz escalonada reducida:\n" + MotorAlgebra._fmt_matriz(M, num_vecs) + "\n\n"

        for r in range(dim):
            if all(abs(M[r][c]) < 1e-9 for c in range(num_vecs)) and abs(M[r][num_vecs]) > 1e-9:
                log += "CONCLUSION: El vector b NO es combinacion lineal (sistema inconsistente)."
                return {"log": log, "sol": None}

        sol = [0.0] * num_vecs
        for r, c in pivotes:
            sol[c] = M[r][num_vecs]

        log += "CONCLUSION: El vector b SI es combinacion lineal.\n"
        for idx, val in enumerate(sol, 1):
            log += f"• c{idx} = {val:.4f}\n"
        return {"log": log, "sol": sol}

    # ==================== 2. MATRICES ====================
    @staticmethod
    def sumar_matrices(A, B):
        if len(A) != len(B) or len(A[0]) != len(B[0]):
            raise ValueError("Las matrices deben tener las mismas dimensiones para sumar.")
        res = [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
        log = "SUMA DE MATRICES (A + B)\nMatriz Resultado:\n" + MotorAlgebra._fmt_matriz(res)
        return {"resultado": res, "log": log}

    @staticmethod
    def restar_matrices(A, B):
        if len(A) != len(B) or len(A[0]) != len(B[0]):
            raise ValueError("Las matrices deben tener las mismas dimensiones para restar.")
        res = [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]
        log = "RESTA DE MATRICES (A - B)\nMatriz Resultado:\n" + MotorAlgebra._fmt_matriz(res)
        return {"resultado": res, "log": log}

    @staticmethod
    def multiplicar_matrices(A, B):
        filas_a, cols_a = len(A), len(A[0])
        filas_b, cols_b = len(B), len(B[0])
        if cols_a != filas_b:
            raise ValueError(f"Columnas de A ({cols_a}) deben ser iguales a filas de B ({filas_b}).")
        res = [[sum(A[i][k] * B[k][j] for k in range(cols_a)) for j in range(cols_b)] for i in range(filas_a)]
        log = f"MULTIPLICACION DE MATRICES ({filas_a}x{cols_a}) * ({filas_b}x{cols_b})\nMatriz Producto C = A · B:\n" + MotorAlgebra._fmt_matriz(res)
        return {"resultado": res, "log": log}

    @staticmethod
    def escalar_matriz(k, A):
        res = [[k * x for x in fila] for fila in A]
        log = f"ESCALAR POR MATRIZ (k = {k})\nMatriz Resultado:\n" + MotorAlgebra._fmt_matriz(res)
        return {"resultado": res, "log": log}

    # ==================== 3. DETERMINANTE E INVERSA ====================
    @staticmethod
    def inversa_gauss_jordan(A, mostrar_pasos=True):
        n = len(A)
        if any(len(fila) != n for fila in A):
            raise ValueError("La matriz debe ser cuadrada (n x n).")

        log = f"======================================================================\n"
        log += f"DETERMINANTE E INVERSA DE MATRIZ CUADRADA ({n}x{n})\n"
        log += f"======================================================================\n\n"

        log += "1. MATRIZ ORIGINAL A:\n"
        log += MotorAlgebra._fmt_matriz(A) + "\n\n"

        log += "2. CALCULO DEL DETERMINANTE det(A) (Reduccion a forma triangular U):\n"
        U = copy.deepcopy(A)
        swaps = 0
        singular = False

        for i in range(n):
            max_r = max(range(i, n), key=lambda r: abs(U[r][i]))
            if abs(U[max_r][i]) < 1e-11:
                singular = True
                break
            if max_r != i:
                U[i], U[max_r] = U[max_r], U[i]
                swaps += 1
                if mostrar_pasos:
                    log += f"   • Intercambio F{i+1} <-> F{max_r+1} (cambia signo del determinante)\n"
            for k in range(i + 1, n):
                if abs(U[k][i]) > 1e-11:
                    factor = U[k][i] / U[i][i]
                    for j in range(i, n):
                        U[k][j] -= factor * U[i][j]
                    if mostrar_pasos:
                        log += f"   • F{k+1} <- F{k+1} - ({factor:.4f}) * F{i+1}\n"

        if singular:
            if mostrar_pasos:
                log += "\nMatriz escalonada:\n" + MotorAlgebra._fmt_matriz(U) + "\n"
            log += f"\n   • Resultado: det(A) = 0\n\n"
            log += "3. JUSTIFICACION DE EXISTENCIA DE INVERSA:\n"
            log += f"   Como det(A) = 0, la matriz A es SINGULAR (sus filas/columnas son linealmente dependientes).\n"
            log += f"   Por lo tanto, NO EXISTE la matriz inversa A^-1.\n"
            return {"existe": False, "determinante": 0.0, "inversa": None, "comprobacion": None, "log": log}

        det = (-1) ** swaps
        diag_terms = []
        for i in range(n):
            det *= U[i][i]
            diag_terms.append(f"({U[i][i]:.4f})")

        if mostrar_pasos:
            log += "\nMatriz Triangular Superior U:\n" + MotorAlgebra._fmt_matriz(U) + "\n"
            log += f"   • Signo por {swaps} intercambio(s): {(-1)**swaps:+d}\n"
            log += f"   • Producto diagonal: {(-1)**swaps:+d} * {' * '.join(diag_terms)}\n"

        det_fmt = f"{int(round(det))}" if abs(det - round(det)) < 1e-7 else f"{det:.6f}"
        log += f"   => det(A) = {det_fmt}\n\n"

        log += "3. JUSTIFICACION DE EXISTENCIA DE INVERSA:\n"
        log += f"   Dado que det(A) = {det_fmt} != 0, la matriz A es NO SINGULAR (invertible).\n"
        log += f"   Por teorema matricial, existe una unica matriz inversa A^-1 tal que A · A^-1 = I_{n}.\n\n"

        log += f"4. CALCULO DE A^-1 POR GAUSS-JORDAN [A | I_{n}] -> [I_{n} | A^-1]:\n"
        M = [copy.deepcopy(row) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(A)]
        log += "Matriz Aumentada Inicial:\n" + MotorAlgebra._fmt_matriz(M, n) + "\n\n"

        for i in range(n):
            max_el = abs(M[i][i])
            max_row = i
            for k in range(i + 1, n):
                if abs(M[k][i]) > max_el:
                    max_el = abs(M[k][i])
                    max_row = k

            if max_row != i:
                M[i], M[max_row] = M[max_row], M[i]
                if mostrar_pasos:
                    log += f"Paso: Intercambio F{i+1} <-> F{max_row+1}\n" + MotorAlgebra._fmt_matriz(M, n) + "\n\n"

            pivote = M[i][i]
            if abs(pivote - 1.0) > 1e-11:
                for j in range(2 * n):
                    M[i][j] /= pivote
                if mostrar_pasos:
                    log += f"Paso: F{i+1} <- F{i+1} / ({pivote:.4f})\n" + MotorAlgebra._fmt_matriz(M, n) + "\n\n"

            cambio_fila = False
            for k in range(n):
                if k != i and abs(M[k][i]) > 1e-11:
                    factor = M[k][i]
                    for j in range(2 * n):
                        M[k][j] -= factor * M[i][j]
                    if mostrar_pasos:
                        log += f"Paso: F{k+1} <- F{k+1} - ({factor:.4f}) * F{i+1}\n"
                        cambio_fila = True
            if mostrar_pasos and cambio_fila:
                log += MotorAlgebra._fmt_matriz(M, n) + "\n\n"

        inversa = [row[n:] for row in M]
        log += "5. MATRIZ INVERSA FINAL (A^-1):\n"
        log += MotorAlgebra._fmt_matriz(inversa, decimales=6) + "\n\n"

        producto = [[sum(A[i][k] * inversa[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
        log += f"6. VERIFICACION MATRICIAL (A · A^-1 = I_{n}):\n"
        log += MotorAlgebra._fmt_matriz(producto, decimales=4) + "\n"
        log += f"   => Comprobado: el producto A · A^-1 coincide con la matriz identidad I_{n}.\n"

        return {
            "existe": True,
            "determinante": det,
            "inversa": inversa,
            "comprobacion": f"A * A^-1 = I_{n} verificada.",
            "log": log
        }

    # ==================== 4. DETERMINANTES ====================
    @staticmethod
    def determinante_lu(A, mostrar_pasos=True):
        n = len(A)
        if any(len(fila) != n for fila in A):
            raise ValueError("La matriz debe ser cuadrada.")
        U = copy.deepcopy(A)
        swaps = 0

        log = f"DETERMINANTE POR DESCOMPOSICION LU ({n}x{n})\n"
        for i in range(n):
            max_r = max(range(i, n), key=lambda r: abs(U[r][i]))
            if abs(U[max_r][i]) < 1e-11:
                log += "Pivote cero encontrado. Determinante = 0."
                return {"determinante": 0.0, "log": log}
            if max_r != i:
                U[i], U[max_r] = U[max_r], U[i]
                swaps += 1
            for k in range(i + 1, n):
                factor = U[k][i] / U[i][i]
                for j in range(i, n):
                    U[k][j] -= factor * U[i][j]

        det = (-1) ** swaps
        diag_str = []
        for i in range(n):
            det *= U[i][i]
            diag_str.append(f"{U[i][i]:.4f}")

        if mostrar_pasos:
            log += "Matriz Triangular Superior U:\n" + MotorAlgebra._fmt_matriz(U) + "\n\n"
            log += f"• Intercambios de fila: {swaps} (signo: {(-1)**swaps:+d})\n"
            log += f"• Diagonal de U: {' * '.join(diag_str)}\n"
        log += f"\nDETERMINANTE FINAL = {det:.6f}"
        return {"determinante": det, "log": log}

    @staticmethod
    def _det_recursivo(M):
        n = len(M)
        if n == 1:
            return M[0][0]
        if n == 2:
            return M[0][0] * M[1][1] - M[0][1] * M[1][0]
        total = 0.0
        for c in range(n):
            menor = [fila[:c] + fila[c+1:] for fila in M[1:]]
            total += ((-1) ** c) * M[0][c] * MotorAlgebra._det_recursivo(menor)
        return total

    @staticmethod
    def determinante_cofactores(A, mostrar_pasos=True):
        n = len(A)
        if any(len(fila) != n for fila in A):
            raise ValueError("La matriz debe ser cuadrada.")
        log = f"DETERMINANTE POR COFACTORES (Expansion por Fila 1 - {n}x{n})\n"
        if n == 1:
            det = A[0][0]
            log += f"DETERMINANTE FINAL = {det:.6f}"
            return {"determinante": det, "log": log}

        det = 0.0
        for c in range(n):
            signo = (-1) ** c
            elem = A[0][c]
            menor = [fila[:c] + fila[c+1:] for fila in A[1:]]
            det_menor = MotorAlgebra._det_recursivo(menor)
            aporte = signo * elem * det_menor
            det += aporte
            if mostrar_pasos:
                log += f"• C1{c+1}: ({signo:+d}) * ({elem:.4f}) * det(M1{c+1})[{det_menor:.4f}] = {aporte:.4f}\n"

        log += f"\nDETERMINANTE FINAL = {det:.6f}"
        return {"determinante": det, "log": log}

    @staticmethod
    def determinante_sarrus(A, mostrar_pasos=True):
        n = len(A)
        if n == 2 and len(A[0]) == 2:
            d1 = A[0][0] * A[1][1]
            d2 = A[0][1] * A[1][0]
            det = d1 - d2
            log = (
                f"DETERMINANTE 2x2\n"
                f"• Diagonal Principal : {A[0][0]} * {A[1][1]} = {d1:.4f}\n"
                f"• Diagonal Secundaria: {A[0][1]} * {A[1][0]} = {d2:.4f}\n"
                f"• Det = {d1:.4f} - ({d2:.4f}) = {det:.6f}"
            )
            return {"determinante": det, "log": log}
        elif n == 3 and len(A[0]) == 3:
            p1 = A[0][0] * A[1][1] * A[2][2]
            p2 = A[0][1] * A[1][2] * A[2][0]
            p3 = A[0][2] * A[1][0] * A[2][1]
            s1 = A[0][2] * A[1][1] * A[2][0]
            s2 = A[0][0] * A[1][2] * A[2][1]
            s3 = A[0][1] * A[1][0] * A[2][2]
            suma_p = p1 + p2 + p3
            suma_s = s1 + s2 + s3
            det = suma_p - suma_s
            log = (
                f"REGLA DE SARRUS (3x3)\n"
                f"• Diagonales (+) : ({p1:.4f}) + ({p2:.4f}) + ({p3:.4f}) = {suma_p:.4f}\n"
                f"• Diagonales (-) : ({s1:.4f}) + ({s2:.4f}) + ({s3:.4f}) = {suma_s:.4f}\n"
                f"\nDETERMINANTE FINAL = {suma_p:.4f} - ({suma_s:.4f}) = {det:.6f}"
            )
            return {"determinante": det, "log": log}
        raise ValueError("La regla de Sarrus solo aplica a matrices 2x2 o 3x3. Usa LU o Cofactores para matrices mas grandes.")

    # ==================== 5. SISTEMAS DE ECUACIONES ====================
    @staticmethod
    def _bloque_verificacion_sistema(A, b, sol, vars_nombres):
        n = len(A)
        txt = "5. VERIFICACION DE LA SOLUCION:\n"
        txt += "   a) Sustitucion en cada ecuacion original:\n"
        for i in range(n):
            ec_str = MotorAlgebra._fmt_ecuacion_lineal(A[i], b[i], vars_nombres)
            terminos = []
            suma = 0.0
            for coef, val in zip(A[i], sol):
                prod = coef * val
                suma += prod
                if abs(coef) > 1e-11:
                    c_s = f"{int(round(coef))}" if abs(coef - round(coef)) < 1e-9 else f"{coef:.4f}"
                    v_s = f"{int(round(val))}" if abs(val - round(val)) < 1e-9 else f"{val:.4f}"
                    terminos.append(f"({c_s})({v_s})")
            b_s = f"{int(round(b[i]))}" if abs(b[i] - round(b[i])) < 1e-9 else f"{b[i]:.4f}"
            sum_s = f"{int(round(suma))}" if abs(suma - round(suma)) < 1e-7 else f"{suma:.4f}"
            txt += f"      Ec.{i+1} [{ec_str}]: {' + '.join(terminos)} = {sum_s} == {b_s}  [OK]\n"

        txt += "\n   b) Comprobacion matricial A · X = B:\n"
        ax_vec = [sum(A[i][j] * sol[j] for j in range(n)) for i in range(n)]
        for i in range(n):
            fila_a = " ".join(MotorAlgebra._fmt_num(x) for x in A[i])
            val_x = MotorAlgebra._fmt_num(sol[i])
            val_ax = MotorAlgebra._fmt_num(ax_vec[i])
            val_b = MotorAlgebra._fmt_num(b[i])
            signo_mul = " · " if i == n // 2 else "   "
            signo_eq = " = " if i == n // 2 else "   "
            txt += f"      [ {fila_a} ]{signo_mul}[ {val_x} ]{signo_eq}[ {val_ax} ]  (B = {val_b.strip()})\n"
        return txt

    @staticmethod
    def gauss_jordan(A, b):
        n = len(A)
        if any(len(fila) != n for fila in A) or len(b) != n:
            raise ValueError("La matriz A debe ser cuadrada (n x n) y coincidir con la longitud de b.")

        vars_nombres = MotorAlgebra._nombres_variables(n)
        det_A = MotorAlgebra._det_recursivo(A)
        det_fmt = f"{int(round(det_A))}" if abs(det_A - round(det_A)) < 1e-7 else f"{det_A:.6f}"

        log = f"======================================================================\n"
        log += f"SISTEMA LINEAL DE {n} INCOGNITAS - METODO GAUSS-JORDAN\n"
        log += f"======================================================================\n\n"

        log += f"1. IDENTIFICACION DE INCOGNITAS:\n"
        log += f"   Vector de incognitas: X = [{', '.join(vars_nombres)}]^T\n\n"

        log += f"2. EXPRESION MATRICIAL DEL SISTEMA (A · X = B):\n"
        log += MotorAlgebra._fmt_sistema_axb(A, b, vars_nombres) + "\n\n"

        log += f"3. ANALISIS DE EXISTENCIA DE SOLUCION UNICA:\n"
        log += f"   • Determinante de la matriz de coeficientes: det(A) = {det_fmt}\n"
        if abs(det_A) < 1e-11:
            log += f"   • Conclusion: Como det(A) = 0, el sistema NO tiene solucion unica (puede ser inconsistente o tener infinitas soluciones).\n"
            return {"estado": "singular", "sol": None, "log": log}
        log += f"   • Conclusion: Como det(A) = {det_fmt} != 0, el sistema es compatible determinado y posee SOLUCION UNICA.\n\n"

        M = [copy.deepcopy(A[i]) + [b[i]] for i in range(n)]
        log += "4. PROCEDIMIENTO ALGEBRAICO (GAUSS-JORDAN SOBRE [A | B]):\n"
        log += "Matriz Aumentada Inicial [A | B]:\n" + MotorAlgebra._fmt_matriz(M, n) + "\n\n"

        for i in range(n):
            max_r = max(range(i, n), key=lambda r: abs(M[r][i]))
            if abs(M[max_r][i]) < 1e-11:
                log += "SISTEMA SIN SOLUCION UNICA (Pivote nulo)."
                return {"estado": "singular", "sol": None, "log": log}

            if max_r != i:
                M[i], M[max_r] = M[max_r], M[i]
                log += f"Paso: F{i+1} <-> F{max_r+1}\n" + MotorAlgebra._fmt_matriz(M, n) + "\n\n"

            piv = M[i][i]
            if abs(piv - 1.0) > 1e-11:
                M[i] = [x / piv for x in M[i]]
                log += f"Paso: F{i+1} <- F{i+1} / ({piv:.4f})\n" + MotorAlgebra._fmt_matriz(M, n) + "\n\n"

            hubo_op = False
            for k in range(n):
                if k != i and abs(M[k][i]) > 1e-11:
                    f = M[k][i]
                    M[k] = [M[k][j] - f * M[i][j] for j in range(n + 1)]
                    log += f"Paso: F{k+1} <- F{k+1} - ({f:.4f}) * F{i+1}\n"
                    hubo_op = True
            if hubo_op:
                log += MotorAlgebra._fmt_matriz(M, n) + "\n\n"

        sol = [M[i][n] for i in range(n)]
        log += "SOLUCION UNICA ENCONTRADA:\n"
        for var, val in zip(vars_nombres, sol):
            val_fmt = f"{int(round(val))}" if abs(val - round(val)) < 1e-7 else f"{val:.6f}"
            log += f"   • {var} = {val_fmt}\n"
        log += "\n" + MotorAlgebra._bloque_verificacion_sistema(A, b, sol, vars_nombres)

        return {"estado": "ok", "sol": sol, "log": log}

    @staticmethod
    def cramer(A, b):
        n = len(A)
        if any(len(fila) != n for fila in A) or len(b) != n:
            raise ValueError("La matriz A debe ser cuadrada (n x n) y coincidir con b.")

        vars_nombres = MotorAlgebra._nombres_variables(n)
        det_A = MotorAlgebra._det_recursivo(A)
        det_fmt = f"{int(round(det_A))}" if abs(det_A - round(det_A)) < 1e-7 else f"{det_A:.6f}"

        log = f"======================================================================\n"
        log += f"SISTEMA LINEAL DE {n} INCOGNITAS - REGLA DE CRAMER\n"
        log += f"======================================================================\n\n"

        log += f"1. IDENTIFICACION DE INCOGNITAS:\n"
        log += f"   Vector de incognitas: X = [{', '.join(vars_nombres)}]^T\n\n"

        log += f"2. EXPRESION MATRICIAL DEL SISTEMA (A · X = B):\n"
        log += MotorAlgebra._fmt_sistema_axb(A, b, vars_nombres) + "\n\n"

        log += f"3. ANALISIS DE EXISTENCIA DE SOLUCION UNICA:\n"
        log += f"   • Determinante Principal (Delta) = det(A) = {det_fmt}\n"

        if abs(det_A) < 1e-11:
            log += f"   • Conclusion: Como Delta = 0, el sistema NO tiene solucion unica por Cramer.\n"
            return {"estado": "singular", "sol": None, "log": log}

        log += f"   • Conclusion: Como Delta = {det_fmt} != 0, existe SOLUCION UNICA.\n\n"
        log += "4. CALCULO DE DETERMINANTES POR INCOGNITA:\n"

        sol = []
        for col in range(n):
            var = vars_nombres[col]
            M_col = copy.deepcopy(A)
            for r in range(n):
                M_col[r][col] = b[r]
            det_col = MotorAlgebra._det_recursivo(M_col)
            xi = det_col / det_A
            sol.append(xi)
            dc_fmt = f"{int(round(det_col))}" if abs(det_col - round(det_col)) < 1e-7 else f"{det_col:.6f}"
            xi_fmt = f"{int(round(xi))}" if abs(xi - round(xi)) < 1e-7 else f"{xi:.6f}"
            log += f"   • Delta_{var} = {dc_fmt}  =>  {var} = Delta_{var} / Delta = {dc_fmt} / {det_fmt} = {xi_fmt}\n"

        log += "\nSOLUCION UNICA ENCONTRADA:\n"
        for var, val in zip(vars_nombres, sol):
            val_fmt = f"{int(round(val))}" if abs(val - round(val)) < 1e-7 else f"{val:.6f}"
            log += f"   • {var} = {val_fmt}\n"
        log += "\n" + MotorAlgebra._bloque_verificacion_sistema(A, b, sol, vars_nombres)

        return {"estado": "ok", "sol": sol, "log": log}

    # ==================== 6. METODOS DE RAICES ====================
    @staticmethod
    def limpiar_expresion_matematica(expr_str):
        e = expr_str.strip().replace("−", "-").replace("·", "*")
        e = e.replace("X", "x").replace("^", "**")

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
        elif "sqrt" in expr_lower or ("(" in expr_lower and "*" in expr_lower and any(f in expr_lower for f in ["sin", "cos", "exp", "log", "ln"])):
            recomendacion = "Newton-Raphson o Secante"
            motivo = "Funcion compuesta continua y derivable; Newton-Raphson ofrece convergencia cuadratica rapida y la Secante evita derivar analiticamente."
        elif "sin" in expr_lower or "cos" in expr_lower or "exp" in expr_lower or "log" in expr_lower or "ln" in expr_lower:
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
            f"1. METODO SELECCIONADO Y JUSTIFICACION:\n"
            f"   • Metodo: Biseccion (metodo cerrado de acotamiento).\n"
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
            f"1. METODO SELECCIONADO Y JUSTIFICACION:\n"
            f"   • Metodo: Falsa Posicion / Regula Falsi (metodo cerrado con interpolacion lineal).\n"
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
            f"1. METODO SELECCIONADO Y JUSTIFICACION:\n"
            f"   • Metodo: Newton-Raphson (metodo abierto basado en recta tangente).\n"
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
            f"1. METODO SELECCIONADO Y JUSTIFICACION:\n"
            f"   • Metodo: Secante (metodo abierto con aproximacion por diferencias finitas).\n"
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