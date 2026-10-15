import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import time
import random
import sys
import threading

# Monitoreo básico de RAM sin librerías externas (psutil opcional)
try:
    import psutil
    PSUTIL_DISPONIBLE = True
except ImportError:
    PSUTIL_DISPONIBLE = False
    import os


class MotorAlgebra:
    """Operaciones de álgebra lineal, métricas de tiempo, RAM y conversiones."""

    @staticmethod
    def obtener_uso_ram():
        """Retorna el consumo actual de RAM en MB y porcentaje (si está disponible)."""
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
    def inversa_gauss_jordan(A, mostrar_pasos=True):
        """Calcula la inversa por Gauss-Jordan con opción de mostrar paso a paso y comprobación A * A^-1 = I."""
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
        """Calcula el determinante por Descomposición LU (Factorización L*U)."""
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
        """Calcula el determinante por Expansión por Cofactores (Laplace)."""
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


class AplicacionLinearX(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LINEARX — Engine v1.0")
        self.geometry("960x820")

        self.modo_oscuro = True

        self.header_frame = tk.Frame(self)
        self.header_frame.pack(fill="x", padx=10, pady=5)

        self.lbl_titulo = tk.Label(self.header_frame, text="LINEARX Engine", font=("Segoe UI", 14, "bold"))
        self.lbl_titulo.pack(side="left")

        self.btn_tema = tk.Button(self.header_frame, text="🌙 Modo Oscuro", command=self.alternar_tema, font=("Segoe UI", 9, "bold"))
        self.btn_tema.pack(side="right")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 0))

        self.tab_vec = ttk.Frame(self.notebook)
        self.tab_mat = ttk.Frame(self.notebook)
        self.tab_inv = ttk.Frame(self.notebook)
        self.tab_det = ttk.Frame(self.notebook)
        self.tab_ec = ttk.Frame(self.notebook)
        self.tab_rom = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_vec, text="Vectores")
        self.notebook.add(self.tab_mat, text="Matrices")
        self.notebook.add(self.tab_inv, text="Inversa de Matriz")
        self.notebook.add(self.tab_det, text="Determinantes")
        self.notebook.add(self.tab_ec, text="Ecuaciones (Ax=b)")
        self.notebook.add(self.tab_rom, text="Números Romanos")

        self.bar_ram = tk.Label(self, text="Cargando estado de la RAM...", relief="sunken", anchor="w")
        self.bar_ram.pack(side="bottom", fill="x", padx=10, pady=5)

        self.lista_scrolled_texts = []
        self.lista_entries = []
        self.lista_canvases = []

        self.init_vectores()
        self.init_matrices()
        self.init_inversa()
        self.init_determinantes()
        self.init_ecuaciones()
        self.init_romanos()

        self.aplicar_tema()

        self.ejecutando = True
        self.hilo_ram = threading.Thread(target=self.actualizar_ram_loop, daemon=True)
        self.hilo_ram.start()

    def alternar_tema(self):
        self.modo_oscuro = not self.modo_oscuro
        self.aplicar_tema()

    def aplicar_tema(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        if self.modo_oscuro:
            BG = "#121212"
            PANEL = "#1e1e1e"
            TEXT = "#ffffff"
            ACCENT = "#0d47a1"
            ENTRY_BG = "#2b2b2b"
            BTN_BG = "#2d2d2d"
            self.btn_tema.config(text="🌙 Modo Oscuro", bg="#2d2d2d", fg="#ffffff")
        else:
            BG = "#f5f5f5"
            PANEL = "#ffffff"
            TEXT = "#000000"
            ACCENT = "#1976d2"
            ENTRY_BG = "#ffffff"
            BTN_BG = "#e0e0e0"
            self.btn_tema.config(text="☀️ Modo Claro", bg="#e0e0e0", fg="#000000")

        self.config(bg=BG)
        self.header_frame.config(bg=BG)
        self.lbl_titulo.config(bg=BG, fg=TEXT)
        self.bar_ram.config(bg=PANEL, fg=TEXT)

        style.configure(".", background=BG, foreground=TEXT, fieldbackground=PANEL, font=("Segoe UI", 9))
        style.configure("TFrame", background=BG)
        style.configure("TLabelframe", background=BG, foreground=TEXT, bordercolor="#888888")
        style.configure("TLabelframe.Label", background=BG, foreground=TEXT, font=("Segoe UI", 9, "bold"))
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("TButton", background=BTN_BG, foreground=TEXT, bordercolor="#888888", focuscolor=ACCENT)
        style.map("TButton", background=[("active", ACCENT)], foreground=[("active", "#ffffff")])
        style.configure("TCheckbutton", background=BG, foreground=TEXT)
        style.map("TCheckbutton", background=[("active", BG)], foreground=[("active", TEXT)])
        style.configure("TCombobox", fieldbackground=ENTRY_BG, background=BTN_BG, foreground=TEXT, arrowcolor=TEXT)
        style.map("TCombobox", fieldbackground=[("readonly", ENTRY_BG)], foreground=[("readonly", TEXT)])
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BTN_BG, foreground=TEXT, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", ACCENT)], foreground=[("selected", "#ffffff")])

        for txt in self.lista_scrolled_texts:
            txt.config(bg=PANEL, fg=TEXT, insertbackground=TEXT, selectbackground=ACCENT)

        for e in self.lista_entries:
            try:
                e.config(bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT)
            except Exception:
                pass

        for c in self.lista_canvases:
            try:
                c.config(bg=BG)
            except Exception:
                pass

    def crear_scrolled_text(self, parent, height=10):
        txt = scrolledtext.ScrolledText(parent, height=height, font=("Consolas", 10), borderwidth=1, relief="solid")
        self.lista_scrolled_texts.append(txt)
        return txt

    def crear_entry_adaptable(self, parent, width=6, default_text="0"):
        e = tk.Entry(parent, width=width, justify="center", borderwidth=1, relief="solid")
        e.insert(0, default_text)
        self.lista_entries.append(e)
        return e

    def copiar_al_portapapeles(self, widget_texto):
        contenido = widget_texto.get("1.0", tk.END).strip()
        if contenido:
            self.clipboard_clear()
            self.clipboard_append(contenido)
            messagebox.showinfo("Copiado", "Resultado copiado al portapapeles exitosamente.")

    def actualizar_ram_loop(self):
        while self.ejecutando:
            try:
                txt = MotorAlgebra.obtener_uso_ram()
                self.bar_ram.config(text=f" 📊 {txt}")
            except Exception:
                pass
            time.sleep(1.5)

    # --- PESTAÑA VECTORES ---
    def init_vectores(self):
        top = ttk.LabelFrame(self.tab_vec, text="Opciones")
        top.pack(fill="x", padx=5, pady=5)

        ttk.Label(top, text="Operación:").grid(row=0, column=0, padx=5, pady=5)
        self.op_vec = ttk.Combobox(top, values=["Suma (u + v)", "Resta (u - v)", "Escalar (k · v)", "Combinación Lineal"], state="readonly")
        self.op_vec.set("Suma (u + v)")
        self.op_vec.grid(row=0, column=1, padx=5, pady=5)
        self.op_vec.bind("<<ComboboxSelected>>", self.toggle_vec)

        ttk.Label(top, text="Dimensión (n):").grid(row=0, column=2, padx=5, pady=5)
        self.ent_dim_vec = self.crear_entry_adaptable(top, width=5, default_text="3")
        self.ent_dim_vec.grid(row=0, column=3, padx=5, pady=5)

        self.lbl_k_vec = ttk.Label(top, text="Cantidad vecs (k):")
        self.ent_k_vec = self.crear_entry_adaptable(top, width=5, default_text="3")

        ttk.Button(top, text="Generar", command=self.dibujar_vectores).grid(row=0, column=6, padx=10, pady=5)

        self.box_vec = ttk.Frame(self.tab_vec)
        self.box_vec.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Button(self.tab_vec, text="Calcular", command=self.calc_vectores).pack(fill="x", padx=5, pady=2)
        self.txt_vec = self.crear_scrolled_text(self.tab_vec, height=10)
        self.txt_vec.pack(fill="both", expand=True, padx=5, pady=5)

        self.dibujar_vectores()

    def toggle_vec(self, e=None):
        if self.op_vec.get() == "Combinación Lineal":
            self.lbl_k_vec.grid(row=0, column=4, padx=5, pady=5)
            self.ent_k_vec.grid(row=0, column=5, padx=5, pady=5)
        else:
            self.lbl_k_vec.grid_forget()
            self.ent_k_vec.grid_forget()

    def dibujar_vectores(self):
        for w in self.box_vec.winfo_children():
            w.destroy()

        try:
            n = int(self.ent_dim_vec.get())
        except ValueError:
            return

        op = self.op_vec.get()
        self.inputs_vec = {}

        if op in ["Suma (u + v)", "Resta (u - v)"]:
            for name, col in [("u", 0), ("v", 1)]:
                f = ttk.LabelFrame(self.box_vec, text=f"Vector {name}")
                f.grid(row=0, column=col, padx=10, pady=5)
                arr = []
                for i in range(n):
                    ttk.Label(f, text=f"x{i+1}:").grid(row=i, column=0)
                    e = self.crear_entry_adaptable(f, width=8, default_text="0")
                    e.grid(row=i, column=1, padx=2, pady=2)
                    arr.append(e)
                self.inputs_vec[name] = arr

        elif op == "Escalar (k · v)":
            f_k = ttk.Frame(self.box_vec)
            f_k.grid(row=0, column=0, columnspan=2)
            ttk.Label(f_k, text="Escalar k:").pack(side="left")
            self.inputs_vec["k"] = self.crear_entry_adaptable(f_k, width=8, default_text="2")
            self.inputs_vec["k"].pack(side="left", padx=5)

            f = ttk.LabelFrame(self.box_vec, text="Vector v")
            f.grid(row=1, column=0, pady=5)
            arr = []
            for i in range(n):
                ttk.Label(f, text=f"x{i+1}:").grid(row=i, column=0)
                e = self.crear_entry_adaptable(f, width=8, default_text="0")
                e.grid(row=i, column=1, padx=2, pady=2)
                arr.append(e)
            self.inputs_vec["v"] = arr

        elif op == "Combinación Lineal":
            try:
                k = int(self.ent_k_vec.get())
            except ValueError:
                return
            
            self.inputs_vec["vecs"] = []
            for j in range(k):
                f = ttk.LabelFrame(self.box_vec, text=f"v{j+1}")
                f.grid(row=0, column=j, padx=2)
                arr = []
                for i in range(n):
                    e = self.crear_entry_adaptable(f, width=6, default_text="0")
                    e.pack(pady=1)
                    arr.append(e)
                self.inputs_vec["vecs"].append(arr)

            f_b = ttk.LabelFrame(self.box_vec, text="b (Objetivo)")
            f_b.grid(row=0, column=k, padx=10)
            arr_b = []
            for i in range(n):
                e = self.crear_entry_adaptable(f_b, width=6, default_text="0")
                e.pack(pady=1)
                arr_b.append(e)
            self.inputs_vec["b"] = arr_b

        self.aplicar_tema()

    def calc_vectores(self):
        self.txt_vec.delete("1.0", tk.END)
        op = self.op_vec.get()

        try:
            if op in ["Suma (u + v)", "Resta (u - v)"]:
                u = [float(e.get()) for e in self.inputs_vec["u"]]
                v = [float(e.get()) for e in self.inputs_vec["v"]]
                res = MotorAlgebra.sumar_vectores(u, v) if op == "Suma (u + v)" else MotorAlgebra.restar_vectores(u, v)
                self.txt_vec.insert(tk.END, f"╔════════════════════════════════════════════════════════════════════════╗\n")
                self.txt_vec.insert(tk.END, f"║                           VECTOR RESULTANTE                            ║\n")
                self.txt_vec.insert(tk.END, f"╚════════════════════════════════════════════════════════════════════════╝\n\n")
                self.txt_vec.insert(tk.END, f"   ▶ v = [ " + ", ".join(f"{x:.4f}" for x in res) + " ]\n")

            elif op == "Escalar (k · v)":
                k = float(self.inputs_vec["k"].get())
                v = [float(e.get()) for e in self.inputs_vec["v"]]
                res = MotorAlgebra.escalar_vector(k, v)
                self.txt_vec.insert(tk.END, f"╔════════════════════════════════════════════════════════════════════════╗\n")
                self.txt_vec.insert(tk.END, f"║                      RESULTADO ESCALAR (k · v)                         ║\n")
                self.txt_vec.insert(tk.END, f"╚════════════════════════════════════════════════════════════════════════╝\n\n")
                self.txt_vec.insert(tk.END, f"   ▶ k · v = [ " + ", ".join(f"{x:.4f}" for x in res) + " ]\n")

            elif op == "Combinación Lineal":
                vecs = [[float(e.get()) for e in arr] for arr in self.inputs_vec["vecs"]]
                b = [float(e.get()) for e in self.inputs_vec["b"]]
                out = MotorAlgebra.combinacion_lineal(vecs, b)
                self.txt_vec.insert(tk.END, out["log"] + "\n")
                if out["estado"] == "DETERMINADO":
                    self.txt_vec.insert(tk.END, "\n▶ COEFICIENTES HALLADOS:\n")
                    for i, c in enumerate(out["sol"]):
                        self.txt_vec.insert(tk.END, f"   • c{i+1} = {c:.4f}\n")

        except Exception as err:
            messagebox.showerror("Error", str(err))

    # --- PESTAÑA MATRICES ---
    def init_matrices(self):
        top = ttk.LabelFrame(self.tab_mat, text="Configuración")
        top.pack(fill="x", padx=5, pady=5)

        ttk.Label(top, text="Operación:").grid(row=0, column=0, padx=5)
        self.op_mat = ttk.Combobox(top, values=["Suma (A + B)", "Resta (A - B)", "Escalar (k · A)", "Multiplicación (A · B)"], state="readonly")
        self.op_mat.set("Suma (A + B)")
        self.op_mat.grid(row=0, column=1)

        ttk.Label(top, text="A (m x n):").grid(row=0, column=2, padx=5)
        self.mat_a_m = self.crear_entry_adaptable(top, width=4, default_text="2"); self.mat_a_m.grid(row=0, column=3)
        self.mat_a_n = self.crear_entry_adaptable(top, width=4, default_text="2"); self.mat_a_n.grid(row=0, column=4)

        ttk.Label(top, text="B (r x p):").grid(row=0, column=5, padx=5)
        self.mat_b_r = self.crear_entry_adaptable(top, width=4, default_text="2"); self.mat_b_r.grid(row=0, column=6)
        self.mat_b_p = self.crear_entry_adaptable(top, width=4, default_text="2"); self.mat_b_p.grid(row=0, column=7)

        ttk.Button(top, text="Generar", command=self.dibujar_matrices).grid(row=0, column=8, padx=10)

        self.box_mat = ttk.Frame(self.tab_mat)
        self.box_mat.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Button(self.tab_mat, text="Calcular", command=self.calc_matrices).pack(fill="x", padx=5, pady=2)
        self.txt_mat = self.crear_scrolled_text(self.tab_mat, height=10)
        self.txt_mat.pack(fill="both", expand=True, padx=5, pady=5)

        self.dibujar_matrices()

    def dibujar_matrices(self):
        for w in self.box_mat.winfo_children():
            w.destroy()

        try:
            f1, c1 = int(self.mat_a_m.get()), int(self.mat_a_n.get())
            f2, c2 = int(self.mat_b_r.get()), int(self.mat_b_p.get())
        except ValueError:
            return

        self.inputs_mat = {}

        f_a = ttk.LabelFrame(self.box_mat, text="Matriz A")
        f_a.grid(row=0, column=0, padx=10)
        mat_a = []
        for i in range(f1):
            row = []
            for j in range(c1):
                e = self.crear_entry_adaptable(f_a, width=6, default_text="0")
                e.grid(row=i, column=j, padx=2, pady=2)
                row.append(e)
            mat_a.append(row)
        self.inputs_mat["A"] = mat_a

        f_k = ttk.Frame(self.box_mat)
        f_k.grid(row=0, column=1, padx=5)
        ttk.Label(f_k, text="k:").pack()
        self.inputs_mat["k"] = self.crear_entry_adaptable(f_k, width=5, default_text="1")
        self.inputs_mat["k"].pack()

        f_b = ttk.LabelFrame(self.box_mat, text="Matriz B")
        f_b.grid(row=0, column=2, padx=10)
        mat_b = []
        for i in range(f2):
            row = []
            for j in range(c2):
                e = self.crear_entry_adaptable(f_b, width=6, default_text="0")
                e.grid(row=i, column=j, padx=2, pady=2)
                row.append(e)
            mat_b.append(row)
        self.inputs_mat["B"] = mat_b

        self.aplicar_tema()

    def calc_matrices(self):
        self.txt_mat.delete("1.0", tk.END)
        op = self.op_mat.get()

        try:
            A = [[float(e.get()) for e in row] for row in self.inputs_mat["A"]]

            if op == "Escalar (k · A)":
                k = float(self.inputs_mat["k"].get())
                res = MotorAlgebra.escalar_matriz(k, A)
            else:
                B = [[float(e.get()) for e in row] for row in self.inputs_mat["B"]]
                if op == "Suma (A + B)":
                    res = MotorAlgebra.sumar_matrices(A, B)
                elif op == "Resta (A - B)":
                    res = MotorAlgebra.restar_matrices(A, B)
                else:
                    res = MotorAlgebra.multiplicar_matrices(A, B)

            self.txt_mat.insert(tk.END, "╔════════════════════════════════════════════════════════════════════════╗\n")
            self.txt_mat.insert(tk.END, "║                           MATRIZ RESULTANTE                            ║\n")
            self.txt_mat.insert(tk.END, "╚════════════════════════════════════════════════════════════════════════╝\n\n")
            for fila in res:
                self.txt_mat.insert(tk.END, "   │ " + "  ".join(f"{v:9.4f}" for v in fila) + " │\n")

        except Exception as err:
            messagebox.showerror("Error", str(err))

    # --- PESTAÑA INVERSA DE MATRIZ ---
    def init_inversa(self):
        top = ttk.LabelFrame(self.tab_inv, text="Matriz Cuadrada (n x n)")
        top.pack(fill="x", padx=5, pady=5)

        ttk.Label(top, text="Tamaño (n):").grid(row=0, column=0, padx=5, pady=5)
        self.ent_inv_n = self.crear_entry_adaptable(top, width=6, default_text="3")
        self.ent_inv_n.grid(row=0, column=1, padx=5, pady=5)

        self.var_pasos = tk.BooleanVar(value=True)
        self.chk_pasos = ttk.Checkbutton(top, text="Mostrar paso a paso detallado", variable=self.var_pasos)
        self.chk_pasos.grid(row=0, column=2, padx=10, pady=5)

        ttk.Button(top, text="Generar Campos", command=self.dibujar_inversa).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(top, text="Llenar Aleatorio", command=self.generar_aleatorio_inversa).grid(row=0, column=4, padx=5, pady=5)

        self.box_inv = ttk.Frame(self.tab_inv)
        self.box_inv.pack(fill="both", expand=True, padx=5, pady=5)

        sub_bar = ttk.Frame(self.tab_inv)
        sub_bar.pack(fill="x", padx=5, pady=2)

        ttk.Button(sub_bar, text="CALCULAR INVERSA (GAUSS-JORDAN)", command=self.calc_inversa).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(sub_bar, text="🧹 Limpiar Campos", command=self.limpiar_inversa).pack(side="left", padx=5)
        ttk.Button(sub_bar, text="📋 Copiar Resultado", command=lambda: self.copiar_al_portapapeles(self.txt_inv)).pack(side="right")

        self.txt_inv = self.crear_scrolled_text(self.tab_inv, height=12)
        self.txt_inv.pack(fill="both", expand=True, padx=5, pady=5)

        self.matriz_grande_cache = None
        self.dibujar_inversa()

    def limpiar_inversa(self):
        if self.inputs_inv:
            for row in self.inputs_inv:
                for e in row:
                    e.delete(0, tk.END)
                    e.insert(0, "0")
        self.txt_inv.delete("1.0", tk.END)

    def dibujar_inversa(self):
        for w in self.box_inv.winfo_children():
            w.destroy()

        self.matriz_grande_cache = None

        try:
            n = int(self.ent_inv_n.get())
            if n <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "El tamaño n debe ser un entero positivo.")
            return

        if n > 20:
            lbl = ttk.Label(
                self.box_inv, 
                text=f"Matriz de tamaño grande ({n}x{n}) detectada.\nSe generará automáticamente con valores aleatorios al presionar Calcular,\no puedes hacer clic en 'Llenar Aleatorio'.", 
                font=("Segoe UI", 10, "italic")
            )
            lbl.pack(pady=20)
            self.inputs_inv = None
            return

        canvas = tk.Canvas(self.box_inv, borderwidth=0, highlightthickness=0)
        self.lista_canvases.append(canvas)
        vbar = ttk.Scrollbar(self.box_inv, orient="vertical", command=canvas.yview)
        hbar = ttk.Scrollbar(self.box_inv, orient="horizontal", command=canvas.xview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        vbar.pack(side="right", fill="y")
        hbar.pack(side="bottom", fill="x")

        f = ttk.LabelFrame(scroll_frame, text=f" Matriz A ({n}x{n}) ")
        f.pack(padx=10, pady=5)

        self.inputs_inv = []
        for i in range(n):
            row = []
            for j in range(n):
                e = self.crear_entry_adaptable(f, width=6, default_text="0")
                e.grid(row=i, column=j, padx=2, pady=2)
                row.append(e)
            self.inputs_inv.append(row)

        self.aplicar_tema()

    def generar_aleatorio_inversa(self):
        try:
            n = int(self.ent_inv_n.get())
            if n <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Ingrese un tamaño n válido.")
            return

        self.matriz_grande_cache = [
            [round(random.uniform(-10, 10), 2) for _ in range(n)] for _ in range(n)
        ]

        if self.inputs_inv and n <= 20:
            for i in range(n):
                for j in range(n):
                    self.inputs_inv[i][j].delete(0, tk.END)
                    self.inputs_inv[i][j].insert(0, str(self.matriz_grande_cache[i][j]))

        messagebox.showinfo("Éxito", f"Se generó una matriz aleatoria de {n}x{n} lista para procesar.")

    def calc_inversa(self):
        self.txt_inv.delete("1.0", tk.END)

        try:
            n = int(self.ent_inv_n.get())

            if self.matriz_grande_cache and len(self.matriz_grande_cache) == n:
                A = self.matriz_grande_cache
            elif self.inputs_inv and n <= 20:
                A = [[float(e.get()) for e in row] for row in self.inputs_inv]
            else:
                A = [[round(random.uniform(-10, 10), 2) for _ in range(n)] for _ in range(n)]

            mostrar_pasos = self.var_pasos.get()
            res = MotorAlgebra.inversa_gauss_jordan(A, mostrar_pasos=mostrar_pasos)
            self.txt_inv.insert(tk.END, res["log"] + "\n\n")

            if res["existe"]:
                self.txt_inv.insert(tk.END, "╔════════════════════════════════════════════════════════════════════════╗\n")
                self.txt_inv.insert(tk.END, "║                     MATRIZ INVERSA RESULTANTE (A⁻¹)                    ║\n")
                self.txt_inv.insert(tk.END, "╚════════════════════════════════════════════════════════════════════════╝\n\n")
                for fila in res["inversa"]:
                    self.txt_inv.insert(tk.END, "   │ " + "  ".join(f"{v:9.4f}" for v in fila) + " │\n")

                self.txt_inv.insert(tk.END, "\n" + "═"*72 + "\n")
                self.txt_inv.insert(tk.END, " ▶ COMPROBACIÓN MATEMÁTICA: A · A⁻¹ = I (Identidad)\n")
                self.txt_inv.insert(tk.END, "═"*72 + "\n")
                for fila in res["comprobacion"]:
                    self.txt_inv.insert(tk.END, "   │ " + "  ".join(f"{v:8.4f}" for v in fila) + " │\n")

        except Exception as err:
            messagebox.showerror("Error", str(err))

    # --- PESTAÑA DETERMINANTES ---
    def init_determinantes(self):
        top = ttk.LabelFrame(self.tab_det, text="Matriz Cuadrada (n x n)")
        top.pack(fill="x", padx=5, pady=5)

        ttk.Label(top, text="Tamaño (n):").grid(row=0, column=0, padx=5, pady=5)
        self.ent_det_n = self.crear_entry_adaptable(top, width=6, default_text="3")
        self.ent_det_n.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(top, text="Método:").grid(row=0, column=2, padx=5, pady=5)
        self.op_metodo_det = ttk.Combobox(top, values=["Descomposición LU", "Expansión por Cofactores"], state="readonly", width=22)
        self.op_metodo_det.set("Descomposición LU")
        self.op_metodo_det.grid(row=0, column=3, padx=5, pady=5)

        self.var_pasos_det = tk.BooleanVar(value=True)
        self.chk_pasos_det = ttk.Checkbutton(top, text="Mostrar detalles", variable=self.var_pasos_det)
        self.chk_pasos_det.grid(row=0, column=4, padx=5, pady=5)

        ttk.Button(top, text="Generar Campos", command=self.dibujar_determinante).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(top, text="Llenar Aleatorio", command=self.generar_aleatorio_determinante).grid(row=0, column=6, padx=5, pady=5)

        # MARCO DE RECOMENDACIÓN DE EFICIENCIA
        self.lbl_recomendacion = ttk.Label(self.tab_det, text="", font=("Segoe UI", 9, "bold"))
        self.lbl_recomendacion.pack(fill="x", padx=10, pady=2)

        self.box_det = ttk.Frame(self.tab_det)
        self.box_det.pack(fill="both", expand=True, padx=5, pady=5)

        sub_bar = ttk.Frame(self.tab_det)
        sub_bar.pack(fill="x", padx=5, pady=2)

        ttk.Button(sub_bar, text="CALCULAR DETERMINANTE det(A)", command=self.calc_determinante).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(sub_bar, text="🧹 Limpiar Campos", command=self.limpiar_determinante).pack(side="left", padx=5)
        ttk.Button(sub_bar, text="📋 Copiar Resultado", command=lambda: self.copiar_al_portapapeles(self.txt_det)).pack(side="right")

        self.txt_det = self.crear_scrolled_text(self.tab_det, height=12)
        self.txt_det.pack(fill="both", expand=True, padx=5, pady=5)

        self.matriz_det_cache = None
        self.dibujar_determinante()

    def actualizar_recomendacion_eficiencia(self, n):
        """Calcula e informa al usuario cuál es el método más eficiente antes de seleccionar/ejecutar."""
        if n <= 3:
            rec = f"💡 RECOMENDACIÓN DE EFICIENCIA: Para dimensión {n}x{n}, ambos métodos son muy rápidos. " \
                  f"Cofactores es ideal para docencia; LU es óptimo estructuralmente."
        else:
            rec = f"⚡ RECOMENDACIÓN DE EFICIENCIA: Para dimensión {n}x{n}, la DESCOMPOSICIÓN LU es la más eficiente O(n³). " \
                  f"Evita Cofactores O(n!) para n ≥ 4 por alto costo computacional."
        self.lbl_recomendacion.config(text=rec)

    def limpiar_determinante(self):
        if self.inputs_det:
            for row in self.inputs_det:
                for e in row:
                    e.delete(0, tk.END)
                    e.insert(0, "0")
        self.txt_det.delete("1.0", tk.END)

    def dibujar_determinante(self):
        for w in self.box_det.winfo_children():
            w.destroy()

        self.matriz_det_cache = None

        try:
            n = int(self.ent_det_n.get())
            if n <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "El tamaño n debe ser un entero positivo.")
            return

        self.actualizar_recomendacion_eficiencia(n)

        if n > 20:
            lbl = ttk.Label(
                self.box_det, 
                text=f"Matriz de tamaño grande ({n}x{n}) detectada.\nSe generará automáticamente con valores aleatorios al presionar Calcular,\no puedes hacer clic en 'Llenar Aleatorio'.", 
                font=("Segoe UI", 10, "italic")
            )
            lbl.pack(pady=20)
            self.inputs_det = None
            return

        canvas = tk.Canvas(self.box_det, borderwidth=0, highlightthickness=0)
        self.lista_canvases.append(canvas)
        vbar = ttk.Scrollbar(self.box_det, orient="vertical", command=canvas.yview)
        hbar = ttk.Scrollbar(self.box_det, orient="horizontal", command=canvas.xview)
        scroll_frame = ttk.Frame(canvas)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        vbar.pack(side="right", fill="y")
        hbar.pack(side="bottom", fill="x")

        f = ttk.LabelFrame(scroll_frame, text=f" Matriz A ({n}x{n}) ")
        f.pack(padx=10, pady=5)

        self.inputs_det = []
        for i in range(n):
            row = []
            for j in range(n):
                e = self.crear_entry_adaptable(f, width=6, default_text="0")
                e.grid(row=i, column=j, padx=2, pady=2)
                row.append(e)
            self.inputs_det.append(row)

        self.aplicar_tema()

    def generar_aleatorio_determinante(self):
        try:
            n = int(self.ent_det_n.get())
            if n <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Ingrese un tamaño n válido.")
            return

        self.matriz_det_cache = [
            [round(random.uniform(-10, 10), 2) for _ in range(n)] for _ in range(n)
        ]

        if self.inputs_det and n <= 20:
            for i in range(n):
                for j in range(n):
                    self.inputs_det[i][j].delete(0, tk.END)
                    self.inputs_det[i][j].insert(0, str(self.matriz_det_cache[i][j]))

        messagebox.showinfo("Éxito", f"Se generó una matriz aleatoria de {n}x{n} lista para calcular el determinante.")

    def calc_determinante(self):
        self.txt_det.delete("1.0", tk.END)

        try:
            n = int(self.ent_det_n.get())

            if self.matriz_det_cache and len(self.matriz_det_cache) == n:
                A = self.matriz_det_cache
            elif self.inputs_det and n <= 20:
                A = [[float(e.get()) for e in row] for row in self.inputs_det]
            else:
                A = [[round(random.uniform(-10, 10), 2) for _ in range(n)] for _ in range(n)]

            metodo = self.op_metodo_det.get()
            mostrar_pasos = self.var_pasos_det.get()

            if metodo == "Descomposición LU":
                res = MotorAlgebra.determinante_lu(A, mostrar_pasos=mostrar_pasos)
            else:
                res = MotorAlgebra.determinante_cofactores(A, mostrar_pasos=mostrar_pasos)

            self.txt_det.insert(tk.END, res["log"] + "\n")

        except Exception as err:
            messagebox.showerror("Error", str(err))

    # --- PESTAÑA ECUACIONES ---
    def init_ecuaciones(self):
        top = ttk.LabelFrame(self.tab_ec, text="Dimensiones [A|b]")
        top.pack(fill="x", padx=5, pady=5)

        ttk.Label(top, text="Filas (m):").grid(row=0, column=0, padx=5)
        self.ec_m = self.crear_entry_adaptable(top, width=5, default_text="2"); self.ec_m.grid(row=0, column=1)

        ttk.Label(top, text="Columnas/Vars (n):").grid(row=0, column=2, padx=5)
        self.ec_n = self.crear_entry_adaptable(top, width=5, default_text="2"); self.ec_n.grid(row=0, column=3)

        ttk.Button(top, text="Generar", command=self.dibujar_ecuaciones).grid(row=0, column=4, padx=10)

        self.box_ec = ttk.Frame(self.tab_ec)
        self.box_ec.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Button(self.tab_ec, text="Resolver (Gauss-Jordan)", command=self.calc_ecuaciones).pack(fill="x", padx=5, pady=2)
        self.txt_ec = self.crear_scrolled_text(self.tab_ec, height=10)
        self.txt_ec.pack(fill="both", expand=True, padx=5, pady=5)

        self.dibujar_ecuaciones()

    def dibujar_ecuaciones(self):
        for w in self.box_ec.winfo_children():
            w.destroy()

        try:
            m, n = int(self.ec_m.get()), int(self.ec_n.get())
        except ValueError:
            return

        self.inputs_A = []
        self.inputs_b = []

        f = ttk.LabelFrame(self.box_ec, text=" Matriz Aumentada ")
        f.pack(padx=10, pady=5)

        for i in range(m):
            row = []
            for j in range(n):
                e = self.crear_entry_adaptable(f, width=7, default_text="0")
                e.grid(row=i, column=j, padx=2, pady=2)
                row.append(e)
            self.inputs_A.append(row)

            ttk.Label(f, text="|").grid(row=i, column=n, padx=5)

            eb = self.crear_entry_adaptable(f, width=7, default_text="0")
            eb.grid(row=i, column=n+1, padx=2, pady=2)
            self.inputs_b.append(eb)

        self.aplicar_tema()

    def calc_ecuaciones(self):
        self.txt_ec.delete("1.0", tk.END)

        try:
            A = [[float(e.get()) for e in row] for row in self.inputs_A]
            b = [float(e.get()) for e in self.inputs_b]

            res = MotorAlgebra.gauss_jordan(A, b)
            self.txt_ec.insert(tk.END, res["log"] + "\n")

            if res["estado"] == "DETERMINADO":
                self.txt_ec.insert(tk.END, "\n▶ VECTOR SOLUCIÓN:\n")
                for i, v in enumerate(res["sol"]):
                    self.txt_ec.insert(tk.END, f"   • x{i+1} = {v:.4f}\n")

        except Exception as err:
            messagebox.showerror("Error", str(err))

    # --- PESTAÑA ROMANOS ---
    def init_romanos(self):
        f = ttk.LabelFrame(self.tab_rom, text="Convertidor")
        f.pack(fill="x", padx=10, pady=10)

        ttk.Label(f, text="Modo:").grid(row=0, column=0, padx=5, pady=10)
        self.mode_rom = ttk.Combobox(f, values=["Romano a Arábigo", "Arábigo a Romano"], state="readonly")
        self.mode_rom.set("Romano a Arábigo")
        self.mode_rom.grid(row=0, column=1, padx=5, pady=10)

        ttk.Label(f, text="Valor:").grid(row=0, column=2, padx=5, pady=10)
        self.ent_rom = self.crear_entry_adaptable(f, width=15, default_text="")
        self.ent_rom.grid(row=0, column=3, padx=5, pady=10)

        ttk.Button(self.tab_rom, text="Convertir", command=self.calc_romanos).pack(fill="x", padx=10, pady=5)

        self.txt_rom = self.crear_scrolled_text(self.tab_rom, height=10)
        self.txt_rom.pack(fill="both", expand=True, padx=10, pady=10)

    def calc_romanos(self):
        self.txt_rom.delete("1.0", tk.END)
        modo = self.mode_rom.get()
        val = self.ent_rom.get().strip()

        try:
            if modo == "Romano a Arábigo":
                res = MotorAlgebra.romano_a_arabico(val)
                self.txt_rom.insert(tk.END, f"╔════════════════════════════════════════════════════════════════════════╗\n")
                self.txt_rom.insert(tk.END, f"║                     CONVERSIÓN DE ROMANO A ARÁBIGO                     ║\n")
                self.txt_rom.insert(tk.END, f"╚════════════════════════════════════════════════════════════════════════╝\n\n")
                self.txt_rom.insert(tk.END, f"   ▶ Numeral Romano: {val.upper()}\n")
                self.txt_rom.insert(tk.END, f"   ▶ Valor Decimal:  {res}\n")    
            else:
                num = int(val)
                res = MotorAlgebra.arabico_a_romano(num)
                self.txt_rom.insert(tk.END, f"╔════════════════════════════════════════════════════════════════════════╗\n")
                self.txt_rom.insert(tk.END, f"║                     CONVERSIÓN DE ARÁBIGO A ROMANO                     ║\n")
                self.txt_rom.insert(tk.END, f"╚════════════════════════════════════════════════════════════════════════╝\n\n")
                self.txt_rom.insert(tk.END, f"   ▶ Valor Decimal:  {num}\n")
                self.txt_rom.insert(tk.END, f"   ▶ Numeral Romano: {res}\n")

        except Exception as err:
            messagebox.showerror("Error", str(err))


if __name__ == "__main__":
    app = AplicacionLinearX()
    app.mainloop()