import time
import math

# Monitoreo básico de RAM sin librerías externas (psutil opcional)
try:
    import psutil
    PSUTIL_DISPONIBLE = True
except ImportError:
    PSUTIL_DISPONIBLE = False


class MotorAlgebra:
    """Operaciones de álgebra lineal, métricas de tiempo, RAM, conversiones y métodos numéricos."""

    @staticmethod
    def obtener_uso_ram():
        if PSUTIL_DISPONIBLE:
            mem = psutil.virtual_memory()
            proc = psutil.Process()
            ram_proceso = proc.memory_info().rss / (1024 * 1024)
            return f"RAM Proceso: {ram_proceso:.1f} MB | Sistema: {mem.percent}% ({mem.used / (1024**3):.2f} GB / {mem.total / (1024**3):.2f} GB)"
        else:
            return "RAM del Sistema: Monitoreo activo"

    @staticmethod
    def sumar_vectores(u, v):
        if len(u) != len(v):
            raise ValueError("Los vectores deben ser de la misma dimensión.")
        return [u[i] + v[i] for i in range(len(u))]

    @staticmethod
    def restar_vectores(u, v):
        if len(u) != len(v):
            raise ValueError("Los vectores deben ser de la misma dimensión.")
        return [u[i] - v[i] for i in range(len(u))]

    @staticmethod
    def escalar_vector(k, v):
        return [k * x for x in v]

    @staticmethod
    def sumar_matrices(A, B):
        f, c = len(A), len(A[0])
        if len(B) != f or len(B[0]) != c:
            raise ValueError("Las matrices deben tener dimensiones iguales (m x n).")
        return [[A[i][j] + B[i][j] for j in range(c)] for i in range(f)]

    @staticmethod
    def restar_matrices(A, B):
        f, c = len(A), len(A[0])
        if len(B) != f or len(B[0]) != c:
            raise ValueError("Las matrices deben tener dimensiones iguales (m x n).")
        return [[A[i][j] - B[i][j] for j in range(c)] for i in range(f)]

    @staticmethod
    def escalar_matriz(k, A):
        return [[k * A[i][j] for j in range(len(A[0]))] for i in range(len(A))]

    @staticmethod
    def multiplicar_matrices(A, B):
        f_a, c_a = len(A), len(A[0])
        f_b, c_b = len(B), len(B[0])
        if c_a != f_b:
            raise ValueError(f"No compatible: Columnas de A ({c_a}) != Filas de B ({f_b}).")

        C = [[0.0] * c_b for _ in range(f_a)]
        for i in range(f_a):
            for j in range(c_b):
                C[i][j] = sum(A[i][k] * B[k][j] for k in range(c_a))
        return C

    @staticmethod
    def gauss_jordan(A, b):
        filas, cols = len(A), len(A[0])
        matriz = [[float(val) for val in A[i]] + [float(b[i])] for i in range(filas)]

        log = ["╔════════════════════════════════════════════════════════════════════════╗",
               "║                      MATRIZ AUMENTADA INICIAL [A | b]                  ║",
               "╚════════════════════════════════════════════════════════════════════════╝\n"]
        for fila in matriz:
            log.append("   │ " + "  ".join(f"{v:8.2f}" for v in fila[:-1]) + f"  │  {fila[-1]:8.2f} │")

        log.append("\n" + "─"*72 + "\n ▶ OPERACIONES ELEMENTALES:\n")

        pivote_f = 0
        pivotes_c = []

        for j in range(cols):
            if pivote_f >= filas:
                break

            max_f = pivote_f
            for r in range(pivote_f + 1, filas):
                if abs(matriz[r][j]) > abs(matriz[max_f][j]):
                    max_f = r

            if abs(matriz[max_f][j]) < 1e-9:
                continue

            if max_f != pivote_f:
                matriz[pivote_f], matriz[max_f] = matriz[max_f], matriz[pivote_f]
                log.append(f"   • Interchange: Fila {pivote_f + 1} ↔ Fila {max_f + 1}")

            piv = matriz[pivote_f][j]
            for c in range(len(matriz[0])):
                matriz[pivote_f][c] /= piv

            for r in range(filas):
                if r != pivote_f:
                    f = matriz[r][j]
                    if abs(f) > 1e-9:
                        for c in range(len(matriz[0])):
                            matriz[r][c] -= f * matriz[pivote_f][c]

            pivotes_c.append(j)
            pivote_f += 1

        log.append("\n╔════════════════════════════════════════════════════════════════════════╗")
        log.append("║                   FORMA ESCALONADA REDUCIDA (RREF)                     ║")
        log.append("╚════════════════════════════════════════════════════════════════════════╝\n")
        for fila in matriz:
            log.append("   │ " + "  ".join(f"{v:8.2f}" for v in fila[:-1]) + f"  │  {fila[-1]:8.2f} │")

        for i in range(filas):
            casi_cero = all(abs(matriz[i][j]) < 1e-9 for j in range(cols))
            if casi_cero and abs(matriz[i][-1]) > 1e-9:
                return {"estado": "INCONSISTENTE", "sol": None, "log": "\n".join(log) + "\n\n❌ STATUS: Sistema Inconsistente (Sin solución)."}

        if len(pivotes_c) < cols:
            return {"estado": "INDETERMINADO", "sol": None, "log": "\n".join(log) + "\n\n⚠️ STATUS: Sistema Consistente Indeterminado (Infinitas soluciones)."}

        x = [0.0] * cols
        for i, col in enumerate(pivotes_c):
            x[col] = matriz[i][-1]

        return {"estado": "DETERMINADO", "sol": x, "log": "\n".join(log) + "\n\n✔ STATUS: Sistema Consistente Determinado."}

    @staticmethod
    def cramer(A, b):
        m, n = len(A), len(A[0])
        if m != n:
            raise ValueError(f"La Regla de Cramer solo aplica a sistemas cuadrados (m = n). El sistema es de {m}x{n}.")

        t_inicio = time.perf_counter()
        log = ["╔════════════════════════════════════════════════════════════════════════╗",
               f"║                  RESOLUCIÓN POR REGLA DE CRAMER ({n}x{n})              ║",
               "╚════════════════════════════════════════════════════════════════════════╝\n"]

        res_det_a = MotorAlgebra.determinante_lu(A, mostrar_pasos=False)
        det_A = res_det_a["determinante"]

        log.append(f"▶ PASO 1: Determinante de la Matriz del Sistema det(A):")
        log.append(f"   det(A) = {det_A:.4f}\n")

        if abs(det_A) < 1e-9:
            t_fin = time.perf_counter()
            tiempo = t_fin - t_inicio
            info_ram = MotorAlgebra.obtener_uso_ram()
            log.append("❌ NO SE PUEDE APLICAR CRAMER: det(A) = 0.")
            log.append("   El sistema no tiene solución única (es inconsistente o indeterminado).")
            log.append(f"\n ⏱ TIEMPO: {tiempo:.6f} s | 📊 {info_ram}")
            return {"estado": "NO_SINGULAR_REQUERIDO", "sol": None, "log": "\n".join(log)}

        sol = []
        log.append("▶ PASO 2: Cálculo de Determinantes Modificados det(Aᵢ) y Variables xᵢ:")

        for j in range(n):
            A_i = [[A[r][c] for c in range(n)] for r in range(n)]
            for r in range(n):
                A_i[r][j] = b[r]

            det_Ai = MotorAlgebra.determinante_lu(A_i, mostrar_pasos=False)["determinante"]
            x_i = det_Ai / det_A
            sol.append(x_i)

            log.append(f"\n   • Variable x{j+1}:")
            log.append(f"     det(A_{j+1}) = {det_Ai:.4f}")
            log.append(f"     x{j+1} = det(A_{j+1}) / det(A) = {det_Ai:.4f} / {det_A:.4f} = {x_i:.4f}")

        t_fin = time.perf_counter()
        tiempo_total = t_fin - t_inicio
        info_ram_fin = MotorAlgebra.obtener_uso_ram()

        log.append("\n╔════════════════════════════════════════════════════════════════════════╗")
        log.append("║                   SISTEMA RESUELTO CON ÉXITO                           ║")
        log.append("╚════════════════════════════════════════════════════════════════════════╝")
        log.append(f"\n ⏱ TIEMPO: {tiempo_total:.6f} s ({tiempo_total * 1000:.3f} ms) | 📊 {info_ram_fin}")

        return {"estado": "DETERMINADO", "sol": sol, "log": "\n".join(log)}

    @staticmethod
    def inversa_gauss_jordan(A, mostrar_pasos=True):
        n = len(A)
        if any(len(fila) != n for fila in A):
            raise ValueError("La matriz debe ser cuadrada (n x n) para calcular su inversa.")

        t_inicio = time.perf_counter()

        aug = []
        for i in range(n):
            identidad = [1.0 if i == j else 0.0 for j in range(n)]
            aug.append([float(x) for x in A[i]] + identidad)

        log = ["╔════════════════════════════════════════════════════════════════════════╗",
               f"║            MOTOR DE CÁLCULO GAUSS-JORDAN — MATRIZ INVERSA ({n}x{n})       ║",
               "╚════════════════════════════════════════════════════════════════════════╝"]

        if mostrar_pasos:
            log.append("\n▶ MATRIZ AUMENTADA INICIAL [A | I]:")
            log.append("┌" + "─"*68 + "┐")
            for fila in aug:
                izq = "  ".join(f"{v:7.2f}" for v in fila[:n])
                der = "  ".join(f"{v:7.2f}" for v in fila[n:])
                log.append(f"│  [ {izq}  │  {der} ]  │")
            log.append("└" + "─"*68 + "┘")
            log.append("\n▶ PASOS DE REDUCCIÓN GAUSSIANA:")

        for i in range(n):
            max_f = i
            for k in range(i + 1, n):
                if abs(aug[k][i]) > abs(aug[max_f][i]):
                    max_f = k

            if abs(aug[max_f][i]) < 1e-9:
                t_fin = time.perf_counter()
                tiempo = t_fin - t_inicio
                info_ram_fin = MotorAlgebra.obtener_uso_ram()
                
                razon = f" ❌ VALIDACIÓN METRIZ: NO INVERTIBLE / MATRIZ SINGULAR\n" \
                        f"    Razón: En la columna {i+1} no existe ningún pivote no nulo.\n" \
                        f"    Determinante = 0 | Filas/Columnas Linealmente Dependientes."
                
                log.append(f"\n{razon}")
                log.append("\n┌" + "─"*68 + "┐")
                log.append(f"│  ⏱  TIEMPO DE EJECUCIÓN: {tiempo:.6f} s ({tiempo * 1000:.3f} ms)")
                log.append(f"│  📊 {info_ram_fin}")
                log.append("└" + "─"*68 + "┘")

                return {
                    "existe": False,
                    "inversa": None,
                    "comprobacion": None,
                    "tiempo": tiempo,
                    "log": "\n".join(log)
                }

            if max_f != i:
                aug[i], aug[max_f] = aug[max_f], aug[i]
                if mostrar_pasos:
                    log.append(f"   • PIVOTEO: Intercambio Fila {i+1} ↔ Fila {max_f+1}")

            pivote = aug[i][i]
            for j in range(2 * n):
                aug[i][j] /= pivote
            
            if mostrar_pasos:
                log.append(f"   • NORMALIZAR: Fila {i+1} ÷ pivote ({pivote:.2f})")

            for k in range(n):
                if k != i:
                    factor = aug[k][i]
                    if abs(factor) > 1e-9:
                        for j in range(2 * n):
                            aug[k][j] -= factor * aug[i][j]
                        if mostrar_pasos:
                            log.append(f"   • REDUCCIÓN: Fila {k+1} = Fila {k+1} - ({factor:.2f}) × Fila {i+1}")

            if mostrar_pasos and (n <= 6):
                log.append("     Estado actual:")
                for fila in aug:
                    izq = "  ".join(f"{v:7.2f}" for v in fila[:n])
                    der = "  ".join(f"{v:7.2f}" for v in fila[n:])
                    log.append(f"      │ {izq}  │  {der} │")

        t_fin = time.perf_counter()
        tiempo_total = t_fin - t_inicio
        info_ram_fin = MotorAlgebra.obtener_uso_ram()

        inversa = [fila[n:] for fila in aug]
        comprobacion = MotorAlgebra.multiplicar_matrices(A, inversa)

        if mostrar_pasos:
            log.append("\n▶ MATRIZ REDUCIDA FINAL [I | A⁻¹]:")
            log.append("┌" + "─"*68 + "┐")
            for fila in aug:
                izq = "  ".join(f"{v:7.2f}" for v in fila[:n])
                der = "  ".join(f"{v:7.2f}" for v in fila[n:])
                log.append(f"│  [ {izq}  │  {der} ]  │")
            log.append("└" + "─"*68 + "┘")

        log.append(f"\n✔ VALIDACIÓN: LA MATRIZ ES INVERTIBLE (NO SINGULAR)\n" \
                   f"   Demostración: Transformación exitosa a Matriz Identidad [I | A⁻¹].\n" \
                   f"   Independencia lineal comprobada (det ≠ 0).")

        log.append("\n┌" + "─"*68 + "┐")
        log.append(f"│  ⏱  TIEMPO DE EJECUCIÓN: {tiempo_total:.6f} s ({tiempo_total * 1000:.3f} ms)")
        log.append(f"│  📊 {info_ram_fin}")
        log.append("└" + "─"*68 + "┘")

        return {
            "existe": True,
            "inversa": inversa,
            "comprobacion": comprobacion,
            "tiempo": tiempo_total,
            "log": "\n".join(log)
        }

    @staticmethod
    def determinante_lu(A, mostrar_pasos=True):
        n = len(A)
        t_inicio = time.perf_counter()
        U = [[float(val) for val in fila] for fila in A]
        L = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        
        det_signo = 1.0
        log = ["╔════════════════════════════════════════════════════════════════════════╗",
               f"║         DETERMINANTE POR DESCOMPOSICIÓN LU — DET(A) ({n}x{n})            ║",
               "╚════════════════════════════════════════════════════════════════════════╝"]

        for i in range(n):
            max_f = i
            for k in range(i + 1, n):
                if abs(U[k][i]) > abs(U[max_f][i]):
                    max_f = k

            if abs(U[max_f][i]) < 1e-9:
                t_fin = time.perf_counter()
                tiempo = t_fin - t_inicio
                info_ram = MotorAlgebra.obtener_uso_ram()
                log.append("\n⚠️ Pivote nulo encontrado en descomposición LU.")
                log.append("==================================================")
                log.append("RESULTADO: det(A) = 0.0000 (Matriz Singular)")
                log.append("==================================================")
                log.append(f" ⏱ TIEMPO: {tiempo:.6f} s | 📊 {info_ram}")
                return {"determinante": 0.0, "invertible": False, "log": "\n".join(log)}

            if max_f != i:
                U[i], U[max_f] = U[max_f], U[i]
                for c in range(i):
                    L[i][c], L[max_f][c] = L[max_f][c], L[i][c]
                det_signo *= -1.0
                if mostrar_pasos:
                    log.append(f"   • Pivoteo (P): Intercambio Fila {i+1} ↔ Fila {max_f+1} (Signo det × -1)")

            for k in range(i + 1, n):
                factor = U[k][i] / U[i][i]
                L[k][i] = factor
                for j in range(i, n):
                    U[k][j] -= factor * U[i][j]
                if mostrar_pasos and n <= 6:
                    log.append(f"   • Multiplicador L[{k+1}][{i+1}] = {factor:.2f}")

        det = det_signo
        elementos_diag = []
        for i in range(n):
            det *= U[i][i]
            elementos_diag.append(f"{U[i][i]:.2f}")

        t_fin = time.perf_counter()
        tiempo_total = t_fin - t_inicio
        info_ram_fin = MotorAlgebra.obtener_uso_ram()

        if mostrar_pasos and n <= 6:
            log.append("\n▶ MATRIZ TRIANGULAR INFERIOR (L):")
            for fila in L:
                log.append("   │ " + "  ".join(f"{v:8.2f}" for v in fila) + " │")
            log.append("\n▶ MATRIZ TRIANGULAR SUPERIOR (U):")
            for fila in U:
                log.append("   │ " + "  ".join(f"{v:8.2f}" for v in fila) + " │")

        log.append("\n▶ CÁLCULO: det(A) = det(P) × det(L) × det(U)")
        log.append(f"   det(L) = 1.0 (Diagonal de unos)")
        log.append(f"   det(U) = {' × '.join(elementos_diag)}")

        log.append("\n╔════════════════════════════════════════════════════════════════════════╗")
        log.append(f"║                   RESULTADO FINAL: det(A) = {det:10.4f}                 ║")
        log.append("╚════════════════════════════════════════════════════════════════════════╝")

        if abs(det) > 1e-9:
            log.append(" ✔ PROPIEDAD: Matriz NO SINGULAR (INVERTIBLE). Complejidad O(n³).")
        else:
            log.append(" ❌ PROPIEDAD: Matriz SINGULAR (NO INVERTIBLE).")

        log.append(f"\n ⏱ TIEMPO: {tiempo_total:.6f} s ({tiempo_total * 1000:.3f} ms) | 📊 {info_ram_fin}")
        return {"determinante": det, "invertible": abs(det) > 1e-9, "log": "\n".join(log)}

    @staticmethod
    def determinante_cofactores(A, mostrar_pasos=True):
        t_inicio = time.perf_counter()

        def submatriz(M, fila_elim, col_elim):
            return [[M[i][j] for j in range(len(M[0])) if j != col_elim] for i in range(len(M)) if i != fila_elim]

        def recur_det(M, nivel=0):
            n = len(M)
            if n == 1:
                return M[0][0]
            if n == 2:
                return M[0][0] * M[1][1] - M[0][1] * M[1][0]

            det_val = 0.0
            for j in range(n):
                sub = submatriz(M, 0, j)
                cofactor = ((-1) ** j) * recur_det(sub, nivel + 1)
                det_val += M[0][j] * cofactor
            return det_val

        n = len(A)
        log = ["╔════════════════════════════════════════════════════════════════════════╗",
               f"║       DETERMINANTE POR EXPANSIÓN DE COFACTORES — DET(A) ({n}x{n})         ║",
               "╚════════════════════════════════════════════════════════════════════════╝"]

        if n > 8:
            log.append("\n⚠️ ADVERTENCIA DE RENDIMIENTO:")
            log.append("   El método de cofactores tiene complejidad factorial O(n!).")
            log.append("   Procesar esta dimensión puede tomar tiempo prolongado de CPU.")

        if mostrar_pasos and n <= 4:
            log.append("\n▶ DESARROLLO POR LA FILA 1:")
            for j in range(n):
                sub = submatriz(A, 0, j)
                sub_det = recur_det(sub)
                signo_str = "+" if (j % 2 == 0) else "-"
                log.append(f"   • Elemento a₁,{j+1} = {A[0][j]:.2f} | Signo ({signo_str}) | Menor M₁,{j+1} = {sub_det:.4f}")

        det = recur_det(A)
        t_fin = time.perf_counter()
        tiempo_total = t_fin - t_inicio
        info_ram_fin = MotorAlgebra.obtener_uso_ram()

        log.append("\n╔════════════════════════════════════════════════════════════════════════╗")
        log.append(f"║                   RESULTADO FINAL: det(A) = {det:10.4f}                 ║")
        log.append("╚════════════════════════════════════════════════════════════════════════╝")

        if abs(det) > 1e-9:
            log.append(" ✔ PROPIEDAD: Matriz NO SINGULAR (INVERTIBLE).")
        else:
            log.append(" ❌ PROPIEDAD: Matriz SINGULAR (NO INVERTIBLE).")

        log.append(f"\n ⏱ TIEMPO: {tiempo_total:.6f} s ({tiempo_total * 1000:.3f} ms) | 📊 {info_ram_fin}")
        return {"determinante": det, "invertible": abs(det) > 1e-9, "log": "\n".join(log)}

    @staticmethod
    def determinante_sarrus(A, mostrar_pasos=True):
        n = len(A)
        if n not in (2, 3):
            raise ValueError(f"La Regla de Sarrus no es aplicable para dimensiones {n}x{n}. "
                             f"Solo aplica a matrices 2x2 y 3x3.")

        t_inicio = time.perf_counter()
        log = ["╔════════════════════════════════════════════════════════════════════════╗",
               f"║             DETERMINANTE POR REGLA DE SARRUS — DET(A) ({n}x{n})          ║",
               "╚════════════════════════════════════════════════════════════════════════╝"]

        if n == 2:
            p1 = A[0][0] * A[1][1]
            p2 = A[0][1] * A[1][0]
            det = p1 - p2

            if mostrar_pasos:
                log.append("\n▶ MATRIZ 2x2:")
                log.append(f"   │ {A[0][0]:8.2f}  {A[0][1]:8.2f} │")
                log.append(f"   │ {A[1][0]:8.2f}  {A[1][1]:8.2f} │")
                log.append("\n▶ DIAGONALES:")
                log.append(f"   • Diagonal Principal (+):  ({A[0][0]:.2f}) × ({A[1][1]:.2f}) = {p1:.4f}")
                log.append(f"   • Diagonal Secundaria (-): ({A[0][1]:.2f}) × ({A[1][0]:.2f}) = {p2:.4f}")
                log.append(f"\n▶ CÁLCULO: ({p1:.4f}) - ({p2:.4f})")

        elif n == 3:
            d1 = A[0][0] * A[1][1] * A[2][2]
            d2 = A[0][1] * A[1][2] * A[2][0]
            d3 = A[0][2] * A[1][0] * A[2][1]
            sum_pos = d1 + d2 + d3

            s1 = A[0][2] * A[1][1] * A[2][0]
            s2 = A[0][0] * A[1][2] * A[2][1]
            s3 = A[0][1] * A[1][0] * A[2][2]
            sum_neg = s1 + s2 + s3

            det = sum_pos - sum_neg

            if mostrar_pasos:
                log.append("\n▶ EXTENSIÓN DE MATRIZ (REGLA DE SARRUS):")
                ext = A + [A[0], A[1]]
                for fila in ext:
                    log.append("   │ " + "  ".join(f"{v:8.2f}" for v in fila) + " │")

                log.append("\n▶ DIAGONALES PRINCIPALES (Suma de Productos Positivos):")
                log.append(f"   • d₁ = ({A[0][0]:.2f}) × ({A[1][1]:.2f}) × ({A[2][2]:.2f}) = {d1:.4f}")
                log.append(f"   • d₂ = ({A[0][1]:.2f}) × ({A[1][2]:.2f}) × ({A[2][0]:.2f}) = {d2:.4f}")
                log.append(f"   • d₃ = ({A[0][2]:.2f}) × ({A[1][0]:.2f}) × ({A[2][1]:.2f}) = {d3:.4f}")
                log.append(f"   ➜ Σ(Diag Positivas) = {sum_pos:.4f}")

                log.append("\n▶ DIAGONALES SECUNDARIAS (Suma de Productos Negativos):")
                log.append(f"   • s₁ = ({A[0][2]:.2f}) × ({A[1][1]:.2f}) × ({A[2][0]:.2f}) = {s1:.4f}")
                log.append(f"   • s₂ = ({A[0][0]:.2f}) × ({A[1][2]:.2f}) × ({A[2][1]:.2f}) = {s2:.4f}")
                log.append(f"   • s₃ = ({A[0][1]:.2f}) × ({A[1][0]:.2f}) × ({A[2][2]:.2f}) = {s3:.4f}")
                log.append(f"   ➜ Σ(Diag Negativas) = {sum_neg:.4f}")

                log.append(f"\n▶ CÁLCULO FINAL: det(A) = Σ(Positivas) - Σ(Negativas)")
                log.append(f"   det(A) = ({sum_pos:.4f}) - ({sum_neg:.4f})")

        t_fin = time.perf_counter()
        tiempo_total = t_fin - t_inicio
        info_ram_fin = MotorAlgebra.obtener_uso_ram()

        log.append("\n╔════════════════════════════════════════════════════════════════════════╗")
        log.append(f"║                   RESULTADO FINAL: det(A) = {det:10.4f}                 ║")
        log.append("╚════════════════════════════════════════════════════════════════════════╝")

        if abs(det) > 1e-9:
            log.append(" ✔ PROPIEDAD: Matriz NO SINGULAR (INVERTIBLE).")
        else:
            log.append(" ❌ PROPIEDAD: Matriz SINGULAR (NO INVERTIBLE).")

        log.append(f"\n ⏱ TIEMPO: {tiempo_total:.6f} s ({tiempo_total * 1000:.3f} ms) | 📊 {info_ram_fin}")
        return {"determinante": det, "invertible": abs(det) > 1e-9, "log": "\n".join(log)}

    @staticmethod
    def metodo_biseccion(expr_str, a, b, tol, max_iter=100):
        t_inicio = time.perf_counter()
        
        def f(x_val):
            dic_contexto = {
                "x": x_val, "math": math, "sin": math.sin, "cos": math.cos,
                "tan": math.tan, "exp": math.exp, "log": math.log, "sqrt": math.sqrt,
                "pi": math.pi, "e": math.e
            }
            expr_eval = expr_str.replace("^", "**")
            return float(eval(expr_eval, {"__builtins__": None}, dic_contexto))

        try:
            fa = f(a)
            fb = f(b)
        except Exception as err:
            raise ValueError(f"Error al evaluar la función en el intervalo: {err}")

        log = ["╔════════════════════════════════════════════════════════════════════════╗",
               "║                   MÉTODO NUMÉRICO DE BISECCIÓN                         ║",
               "╚════════════════════════════════════════════════════════════════════════╝\n",
               f" ▶ Función: f(x) = {expr_str}",
               f" ▶ Intervalo Inicial: [{a}, {b}] | Tolerancia: {tol}\n"]

        if fa * fb >= 0:
            log.append("❌ TEOREMA DE BOLZANO NO CUMPLIDO: f(a) y f(b) deben tener signos opuestos.")
            log.append(f"   f({a}) = {fa:.6f} | f({b}) = {fb:.6f}")
            log.append("   No se garantiza la existencia de una raíz en este intervalo.")
            return {"exito": False, "filas": [], "raiz": None, "error": None, "iteraciones": 0, "log": "\n".join(log)}

        filas_tabla = []
        c = a
        error = abs(fb)

        for k in range(1, max_iter + 1):
            c = (a + b) / 2.0
            fc = f(c)
            error = abs(fc)

            filas_tabla.append({
                "iter": k, "a": a, "b": b, "c": c,
                "fa": fa, "fb": fb, "fc": fc, "error": error
            })

            log.append(f"   Iter {k:2d}: a={a:10.6f} | b={b:10.6f} | c={c:10.6f} | f(c)={fc:12.6f} | error={error:10.6f}")

            if error <= tol or abs(b - a) / 2.0 < tol:
                break

            if fa * fc < 0:
                b = c
                fb = fc
            else:
                a = c
                fa = fc

        t_fin = time.perf_counter()
        tiempo_total = t_fin - t_inicio
        info_ram_fin = MotorAlgebra.obtener_uso_ram()

        log.append("\n╔════════════════════════════════════════════════════════════════════════╗")
        log.append(f"║    RAÍZ APROXIMADA HALLADA: x ≈ {c:12.6f}                          ║")
        log.append(f"║    TOTAL ITERACIONES: {len(filas_tabla):2d} | ERROR FINAL: {error:10.6f}              ║")
        log.append("╚════════════════════════════════════════════════════════════════════════╝")
        log.append(f"\n ⏱ TIEMPO: {tiempo_total:.6f} s ({tiempo_total * 1000:.3f} ms) | 📊 {info_ram_fin}")

        return {
            "exito": True,
            "filas": filas_tabla,
            "raiz": c,
            "error": error,
            "iteraciones": len(filas_tabla),
            "log": "\n".join(log)
        }

    @classmethod
    def combinacion_lineal(cls, vectores, b):
        dim, num_vecs = len(b), len(vectores)
        for i, v in enumerate(vectores):
            if len(v) != dim:
                raise ValueError(f"Vector v{i+1} tiene dimensión {len(v)}, b requiere {dim}.")

        A = [[vectores[j][i] for j in range(num_vecs)] for i in range(dim)]
        return cls.gauss_jordan(A, b)

    @staticmethod
    def romano_a_arabico(cadena):
        m = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        cadena = cadena.upper().strip()
        if not cadena:
            raise ValueError("Ingrese un texto.")
        total = 0
        prev = 0
        for char in reversed(cadena):
            if char not in m:
                raise ValueError(f"Carácter inválido: '{char}'")
            val = m[char]
            if val < prev:
                total -= val
            else:
                total += val
                prev = val
        return total

    @staticmethod
    def arabico_a_romano(num):
        if not (0 < num < 4000):
            raise ValueError("Rango permitido: 1 a 3999.")
        tabla = [
            (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
            (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
            (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I')
        ]
        res = ""
        for val, sim in tabla:
            while num >= val:
                res += sim
                num -= val
        return res