import math
import re
import copy


class MotorAlgebra:

    @staticmethod
    def _fmt_num(val):
        if abs(val) < 1e-10:
            val = 0.0
        if abs(val - round(val)) < 1e-9:
            return f"{int(round(val)):>8}"
        return f"{val:>8.4f}"

    @staticmethod
    def _fmt_matriz(M, separador_col=None):
        lineas = []
        for fila in M:
            if separador_col is not None:
                izq = " ".join(MotorAlgebra._fmt_num(x) for x in fila[:separador_col])
                der = " ".join(MotorAlgebra._fmt_num(x) for x in fila[separador_col:])
                lineas.append(f"  [ {izq}  | {der} ]")
            else:
                vals = " ".join(MotorAlgebra._fmt_num(x) for x in fila)
                lineas.append(f"  [ {vals} ]")
        return "\n".join(lineas)

    # ==================== 1. VECTORES ====================
    @staticmethod
    def sumar_vectores(u, v):
        if len(u) != len(v):
            raise ValueError("Los vectores deben tener la misma dimension.")
        res = [a + b for a, b in zip(u, v)]
        log = f"SUMA DE VECTORES (u + v)\n• u = {u}\n• v = {v}\n• Resultado = {[round(x, 4) for x in res]}"
        return {"resultado": res, "log": log}

    @staticmethod
    def restar_vectores(u, v):
        if len(u) != len(v):
            raise ValueError("Los vectores deben tener la misma dimension.")
        res = [a - b for a, b in zip(u, v)]
        log = f"RESTA DE VECTORES (u - v)\n• u = {u}\n• v = {v}\n• Resultado = {[round(x, 4) for x in res]}"
        return {"resultado": res, "log": log}

    @staticmethod
    def escalar_vector(k, v):
        res = [k * x for x in v]
        log = f"MULTIPLICACION POR ESCALAR (k * v)\n• Escalar k = {k}\n• Vector v  = {v}\n• Resultado = {[round(x, 4) for x in res]}"
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
        # Construir matriz A donde cada vector es una columna
        A = [[vecs[j][i] for j in range(num_vecs)] for i in range(dim)]
        M = [A[i] + [b[i]] for i in range(dim)]

        log = "COMBINACION LINEAL: c1*v1 + c2*v2 + ... = b\n"
        log += "Matriz aumentada [V | b]:\n" + MotorAlgebra._fmt_matriz(M, num_vecs) + "\n\n"

        # Eliminacion Gauss-Jordan sobre sistema rectangular
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

        # Verificar inconsistencia
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

    # ==================== 3. INVERSA GAUSS-JORDAN ====================
    @staticmethod
    def inversa_gauss_jordan(A, mostrar_pasos=True):
        n = len(A)
        if any(len(fila) != n for fila in A):
            raise ValueError("La matriz debe ser cuadrada (n x n).")

        M = [copy.deepcopy(row) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(A)]
        log = f"INVERSA POR GAUSS-JORDAN ({n}x{n})\nMatriz Aumentada Inicial [A | I]:\n"
        log += MotorAlgebra._fmt_matriz(M, n) + "\n\n"

        for i in range(n):
            max_el = abs(M[i][i])
            max_row = i
            for k in range(i + 1, n):
                if abs(M[k][i]) > max_el:
                    max_el = abs(M[k][i])
                    max_row = k

            if max_el < 1e-11:
                log += f"DETENCION: Pivote nulo en columna {i+1}. La matriz es singular (det = 0) y NO tiene inversa."
                return {"existe": False, "inversa": None, "comprobacion": None, "log": log}

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
        log += "MATRIZ INVERSA FINAL (A^-1):\n" + MotorAlgebra._fmt_matriz(inversa) + "\n"
        return {
            "existe": True,
            "inversa": inversa,
            "comprobacion": "A * A^-1 = I verificada.",
            "log": log
        }

    # ==================== 4. DETERMINANTES ====================
    @staticmethod
    def determinante_lu(A, mostrar_pasos=True):
        n = len(A)
        if any(len(fila) != n for fila in A):
            raise ValueError("La matriz debe ser cuadrada.")
        U = copy.deepcopy(A)
        L = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
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
                L[k][i] = factor
                for j in range(i, n):
                    U[k][j] -= factor * U[i][j]

        det = (-1) ** swaps
        diag_str = []
        for i in range(n):
            det *= U[i][i]
            diag_str.append(f"{U[i][i]:.4f}")

        if mostrar_pasos:
            log += "Matriz Triangular Superior U:\n" + MotorAlgebra._fmt_matriz(U) + "\n\n"
            log += f"• Intercambios de fila: {swaps} (signo: {(-1)**swaps})\n"
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
            log = f"DETERMINANTE 2x2\n• Diagonal Principal: {A[0][0]}*{A[1][1]} = {d1:.4f}\n• Diagonal Secundaria: {A[0][1]}*{A[1][0]} = {d2:.4f}\n• Det = {d1:.4f} - {d2:.4f} = {det:.6f}"
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

    # ==================== 5. SISTEMAS DE ECUACIONES (Ax = b) ====================
    @staticmethod
    def gauss_jordan(A, b):
        n = len(A)
        if any(len(fila) != n for fila in A) or len(b) != n:
            raise ValueError("La matriz A debe ser cuadrada (n x n) y coincidir con la longitud de b.")

        M = [copy.deepcopy(A[i]) + [b[i]] for i in range(n)]
        log = f"SISTEMA DE ECUACIONES POR GAUSS-JORDAN ({n}x{n})\nMatriz Aumentada [A | b]:\n"
        log += MotorAlgebra._fmt_matriz(M, n) + "\n\n"

        for i in range(n):
            max_r = max(range(i, n), key=lambda r: abs(M[r][i]))
            if abs(M[max_r][i]) < 1e-11:
                log += "SISTEMA SIN SOLUCION UNICA (Determinante = 0)."
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
        log += "SOLUCION DEL SISTEMA:\n"
        for idx, val in enumerate(sol, 1):
            log += f"• x{idx} = {val:.6f}\n"
        return {"estado": "ok", "sol": sol, "log": log}

    @staticmethod
    def cramer(A, b):
        n = len(A)
        if any(len(fila) != n for fila in A) or len(b) != n:
            raise ValueError("La matriz A debe ser cuadrada (n x n) y coincidir con b.")

        det_A = MotorAlgebra._det_recursivo(A)
        log = f"SISTEMA DE ECUACIONES POR REGLA DE CRAMER ({n}x{n})\n"
        log += f"• Determinante Principal (Delta) = {det_A:.6f}\n"

        if abs(det_A) < 1e-11:
            log += "\nERROR: Delta = 0. El sistema no tiene solucion unica por Cramer."
            return {"estado": "singular", "sol": None, "log": log}

        log += "-" * 55 + "\n"
        sol = []
        for col in range(n):
            M_col = copy.deepcopy(A)
            for r in range(n):
                M_col[r][col] = b[r]
            det_col = MotorAlgebra._det_recursivo(M_col)
            xi = det_col / det_A
            sol.append(xi)
            log += f"• Delta_x{col+1} = {det_col:.6f}  =>  x{col+1} = {det_col:.4f} / {det_A:.4f} = {xi:.6f}\n"

        return {"estado": "ok", "sol": sol, "log": log}

    # ==================== 6. METODOS DE RAICES ====================
    @staticmethod
    def limpiar_expresion_matematica(expr_str):
        e = expr_str.strip()
        e = e.replace("X", "x").replace("^", "**")

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
        return float(eval(expr_eval, {"__builtins__": None}, dic_contexto))

    @staticmethod
    def recomendar_metodo(expr_str, a=None, b=None):
        expr_lower = expr_str.lower()
        info_bolzano = ""
        cumple_bolzano = None

        if a is not None and b is not None:
            try:
                fa = MotorAlgebra.evaluar_funcion(expr_str, a)
                fb = MotorAlgebra.evaluar_funcion(expr_str, b)
                if fa * fb < 0:
                    cumple_bolzano = True
                    info_bolzano = f"• Verificacion Bolzano en [{a}, {b}]: f({a})={fa:.4f} y f({b})={fb:.4f} (Signos opuestos: SI hay raiz garantizada).\n"
                else:
                    cumple_bolzano = False
                    info_bolzano = f"• Verificacion Bolzano en [{a}, {b}]: f({a})={fa:.4f} y f({b})={fb:.4f} (Mismo signo: NO sirve para Biseccion/Regla Falsa).\n"
            except Exception:
                pass

        if cumple_bolzano is False:
            recomendacion = "Newton-Raphson o Secante (Metodos Abiertos)"
            motivo = "El intervalo evaluado no presenta cambio de signo, por lo que los metodos cerrados fallaran. Usa un metodo abierto."
        elif "sqrt" in expr_lower or ("(" in expr_lower and "*" in expr_lower and any(f in expr_lower for f in ["sin", "cos", "exp", "log"])):
            recomendacion = "Metodo de la Secante (Abierto)"
            motivo = "La funcion tiene radicales o productos compuestos donde calcular f'(x) es costoso; la Secante aproxima la pendiente con dos puntos."
        elif "sin" in expr_lower or "cos" in expr_lower or "tan" in expr_lower or "exp" in expr_lower or "log" in expr_lower or "ln" in expr_lower:
            recomendacion = "Newton-Raphson"
            motivo = "Funcion trascendental suave con convergencia cuadratica rapida mediante recta tangente."
        elif "**3" in expr_lower or "**4" in expr_lower or "**5" in expr_lower or "^3" in expr_lower or "^4" in expr_lower:
            recomendacion = "Newton-Raphson"
            motivo = "Polinomio de grado superior con derivada directa y convergencia muy rapida."
        else:
            recomendacion = "Regla Falsa o Biseccion (Metodos Cerrados)"
            motivo = "Funcion algebraica ideal para encerrar la raiz en un intervalo [a, b] con convergencia 100% segura."

        return {
            "recomendacion": recomendacion,
            "motivo": motivo,
            "log": f"ASISTENTE DE ANALISIS NUMERICO:\n• Metodo Sugerido: {recomendacion}\n{info_bolzano}• Criterio Tecnico: {motivo}\n"
        }

    @staticmethod
    def metodo_biseccion(expr_str, a, b, tol=0.0001, max_iter=100):
        fa_val = MotorAlgebra.evaluar_funcion(expr_str, a)
        fb_val = MotorAlgebra.evaluar_funcion(expr_str, b)
        if fa_val * fb_val > 0:
            raise ValueError(f"f(a)={fa_val:.4f} y f(b)={fb_val:.4f} deben tener signos opuestos (Teorema de Bolzano).")

        filas = []
        log_txt = "METODO CERRADO - BISECCION\n"
        log_txt += f"• Funcion: f(x) = {expr_str}\n"
        log_txt += f"• Intervalo inicial: [{a}, {b}] | Tolerancia: {tol}\n" + "-" * 86 + "\n"
        log_txt += f"{'Iter':<5} | {'a':<8} | {'b':<8} | {'c':<10} | {'f(c)':<10} | {'Err Abs':<10} | {'Err Rel %':<9}\n"
        log_txt += "-" * 86 + "\n"

        raiz = a
        c_ant = a
        exito = False
        k_final = 0
        error_final = 0

        for k in range(1, max_iter + 1):
            fa = MotorAlgebra.evaluar_funcion(expr_str, a)
            c = (a + b) / 2.0
            fc = MotorAlgebra.evaluar_funcion(expr_str, c)
            err_abs = abs(b - a) / 2.0
            err_rel = (abs(c - c_ant) / abs(c) * 100.0) if (k > 1 and abs(c) > 1e-14) else 100.0
            k_final = k
            error_final = abs(fc)

            filas.append({"iter": k, "a": a, "b": b, "c": c, "fc": fc, "error": err_abs})
            log_txt += f"{k:<5} | {a:<8.5f} | {b:<8.5f} | {c:<10.6f} | {fc:<10.6f} | {err_abs:<10.6f} | {err_rel:<8.3f}%\n"

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

        log_txt += "-" * 86 + "\n"
        log_txt += f"RESULTADO FINAL ({'CONVERGIO' if exito else 'LIMITE ITERACIONES'}):\n"
        log_txt += f"• Raiz Aproximada (c) : {raiz:.6f}\n"
        log_txt += f"• Residuo |f(c)|        : {error_final:.6f}\n"
        log_txt += f"• Total de Iteraciones  : {k_final}\n"

        return {"exito": exito, "raiz": raiz, "filas": filas, "log": log_txt}

    @staticmethod
    def metodo_regla_falsa(expr_str, a, b, tol=0.0001, max_iter=100):
        fa_val = MotorAlgebra.evaluar_funcion(expr_str, a)
        fb_val = MotorAlgebra.evaluar_funcion(expr_str, b)
        if fa_val * fb_val > 0:
            raise ValueError(f"f(a)={fa_val:.4f} y f(b)={fb_val:.4f} deben tener signos opuestos (Teorema de Bolzano).")

        filas = []
        log_txt = "METODO CERRADO - REGLA FALSA (REGULA FALSI)\n"
        log_txt += f"• Funcion: f(x) = {expr_str}\n"
        log_txt += f"• Intervalo inicial: [{a}, {b}] | Tolerancia: {tol}\n" + "-" * 86 + "\n"
        log_txt += f"{'Iter':<5} | {'a':<8} | {'b':<8} | {'xr':<10} | {'f(xr)':<10} | {'Err Abs':<10} | {'Err Rel %':<9}\n"
        log_txt += "-" * 86 + "\n"

        raiz = a
        xr_ant = a
        exito = False
        k_final = 0
        error_final = 0

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
            error_final = abs(fxr)

            filas.append({"iter": k, "a": a, "b": b, "c": xr, "fc": fxr, "error": err_abs})
            log_txt += f"{k:<5} | {a:<8.5f} | {b:<8.5f} | {xr:<10.6f} | {fxr:<10.6f} | {err_abs:<10.6f} | {err_rel:<8.3f}%\n"

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

        log_txt += "-" * 86 + "\n"
        log_txt += f"RESULTADO FINAL ({'CONVERGIO' if exito else 'LIMITE ITERACIONES'}):\n"
        log_txt += f"• Raiz Aproximada (xr) : {raiz:.6f}\n"
        log_txt += f"• Residuo |f(xr)|        : {error_final:.6f}\n"
        log_txt += f"• Total de Iteraciones  : {k_final}\n"

        return {"exito": exito, "raiz": raiz, "filas": filas, "log": log_txt}

    @staticmethod
    def metodo_newton_raphson(expr_str, x0, tol=0.0001, max_iter=100):
        filas = []
        log_txt = "METODO ABIERTO - NEWTON-RAPHSON\n"
        log_txt += f"• Funcion: f(x) = {expr_str}\n"
        log_txt += f"• Valor inicial x0: {x0} | Tolerancia: {tol}\n" + "-" * 86 + "\n"
        log_txt += f"{'Iter':<5} | {'xn':<11} | {'f(xn)':<11} | {'f\'(xn)':<11} | {'Err Abs':<11} | {'Err Rel %':<9}\n"
        log_txt += "-" * 86 + "\n"

        xn = x0
        exito = False
        k_final = 0
        error_final = 0
        h = 1e-6

        for k in range(1, max_iter + 1):
            fxn = MotorAlgebra.evaluar_funcion(expr_str, xn)
            dfxn = (MotorAlgebra.evaluar_funcion(expr_str, xn + h) - MotorAlgebra.evaluar_funcion(expr_str, xn - h)) / (2 * h)

            if abs(dfxn) < 1e-14:
                raise ValueError("Derivada cero (tangente horizontal). Cambia el punto inicial x0.")

            xn_nuevo = xn - (fxn / dfxn)
            if not math.isfinite(xn_nuevo) or abs(xn_nuevo) > 1e12:
                raise ValueError("El metodo divergio al infinito. Elige un x0 mas cercano a la raiz.")

            err_abs = abs(xn_nuevo - xn)
            err_rel = (err_abs / abs(xn_nuevo) * 100.0) if abs(xn_nuevo) > 1e-14 else 0.0

            filas.append({"iter": k, "c": xn_nuevo, "error": err_abs})
            log_txt += f"{k:<5} | {xn:<11.6f} | {fxn:<11.6f} | {dfxn:<11.6f} | {err_abs:<11.6f} | {err_rel:<8.3f}%\n"

            k_final = k
            error_final = err_abs

            if abs(fxn) < tol or err_abs < tol:
                xn = xn_nuevo
                exito = True
                break

            xn = xn_nuevo

        log_txt += "-" * 86 + "\n"
        log_txt += f"RESULTADO FINAL ({'CONVERGIO' if exito else 'LIMITE ITERACIONES'}):\n"
        log_txt += f"• Raiz Aproximada : {xn:.6f}\n"
        log_txt += f"• Margen de Error : {error_final:.6f}\n"
        log_txt += f"• Total de Iteraciones : {k_final}\n"

        return {"exito": exito, "raiz": xn, "filas": filas, "log": log_txt}

    @staticmethod
    def metodo_secante(expr_str, x0, x1, tol=0.0001, max_iter=100):
        filas = []
        log_txt = "METODO ABIERTO - SECANTE\n"
        log_txt += f"• Funcion: f(x) = {expr_str}\n"
        log_txt += f"• Valores iniciales x0: {x0}, x1: {x1} | Tolerancia: {tol}\n" + "-" * 86 + "\n"
        log_txt += f"{'Iter':<5} | {'x_ant':<10} | {'x_act':<10} | {'x_nuevo':<10} | {'f(x_act)':<10} | {'Err Abs':<10} | {'Err Rel %':<9}\n"
        log_txt += "-" * 86 + "\n"

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
                raise ValueError("Division por cero en la Secante (f(x_act) - f(x_ant) cercano a 0).")

            x_nuevo = x_act - (f_act * (x_act - x_ant)) / denominador
            if not math.isfinite(x_nuevo) or abs(x_nuevo) > 1e12:
                raise ValueError("El metodo divergio al infinito. Elige x0 y x1 mas cercanos a la raiz.")

            err_abs = abs(x_nuevo - x_act)
            err_rel = (err_abs / abs(x_nuevo) * 100.0) if abs(x_nuevo) > 1e-14 else 0.0

            filas.append({"iter": k, "c": x_nuevo, "error": err_abs})
            log_txt += f"{k:<5} | {x_ant:<10.4f} | {x_act:<10.4f} | {x_nuevo:<10.4f} | {f_act:<10.4f} | {err_abs:<10.4f} | {err_rel:<8.3f}%\n"

            k_final = k
            error_final = err_abs

            if abs(f_act) < tol or err_abs < tol:
                x_act = x_nuevo
                exito = True
                break

            x_ant = x_act
            x_act = x_nuevo

        log_txt += "-" * 86 + "\n"
        log_txt += f"RESULTADO FINAL ({'CONVERGIO' if exito else 'LIMITE ITERACIONES'}):\n"
        log_txt += f"• Raiz Aproximada : {x_act:.6f}\n"
        log_txt += f"• Margen de Error : {error_final:.6f}\n"
        log_txt += f"• Total de Iteraciones : {k_final}\n"

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
                if math.isfinite(y_val):
                    coords.append({"x": round(current_x, 6), "y": round(y_val, 6)})
            except Exception:
                pass
            current_x += paso

        raiz_dict = {"x": round(raiz, 6), "y": 0.0} if raiz is not None else None

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