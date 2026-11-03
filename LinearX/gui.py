import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import threading
import time

# Importamos la lógica matemática del backend empaquetado en core/
from core.motor import MotorAlgebra


class AplicacionLinearX(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LINEARX — Engine v1.0")
        self.geometry("980x850")

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
        self.tab_bis = ttk.Frame(self.notebook)
        self.tab_rom = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_vec, text="Vectores")
        self.notebook.add(self.tab_mat, text="Matrices")
        self.notebook.add(self.tab_inv, text="Inversa de Matriz")
        self.notebook.add(self.tab_det, text="Determinantes")
        self.notebook.add(self.tab_ec, text="Ecuaciones (Ax=b)")
        self.notebook.add(self.tab_bis, text="Bisección")
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
        self.init_biseccion()
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

        style.configure("Treeview", background=PANEL, foreground=TEXT, fieldbackground=PANEL, rowheight=24)
        style.configure("Treeview.Heading", background=BTN_BG, foreground=TEXT, font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "#ffffff")])

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
                b = [float(e.get()) for e in self.inputs_b]
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
        self.op_metodo_det = ttk.Combobox(top, values=["Descomposición LU", "Expansión por Cofactores", "Regla de Sarrus"], state="readonly", width=22)
        self.op_metodo_det.set("Descomposición LU")
        self.op_metodo_det.grid(row=0, column=3, padx=5, pady=5)

        self.var_pasos_det = tk.BooleanVar(value=True)
        self.chk_pasos_det = ttk.Checkbutton(top, text="Mostrar detalles", variable=self.var_pasos_det)
        self.chk_pasos_det.grid(row=0, column=4, padx=5, pady=5)

        ttk.Button(top, text="Generar Campos", command=self.dibujar_determinante).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(top, text="Llenar Aleatorio", command=self.generar_aleatorio_determinante).grid(row=0, column=6, padx=5, pady=5)

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
        if n in (2, 3):
            rec = f"💡 RECOMENDACIÓN DE EFICIENCIA: Para dimensión {n}x{n}, la Regla de Sarrus y Cofactores son " \
                  f"los métodos manuales más intuitivos. LU es óptimo a nivel computacional."
        else:
            rec = f"⚡ RECOMENDACIÓN DE EFICIENCIA: Para dimensión {n}x{n}, la DESCOMPOSICIÓN LU es la más eficiente O(n³). " \
                  f"Nota: Sarrus NO aplica para n ≥ 4, y Cofactores es muy lento O(n!)."
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

            metodo = self.op_metodo_det.get()
            if metodo == "Regla de Sarrus" and n not in (2, 3):
                messagebox.showwarning(
                    "Método No Aplicable", 
                    f"La Regla de Sarrus solo se puede aplicar a matrices 2x2 y 3x3.\n"
                    f"Para dimensión {n}x{n}, por favor seleccione Descomposición LU o Cofactores."
                )
                return

            if self.matriz_det_cache and len(self.matriz_det_cache) == n:
                A = self.matriz_det_cache
            elif self.inputs_det and n <= 20:
                A = [[float(e.get()) for e in row] for row in self.inputs_det]
            else:
                A = [[round(random.uniform(-10, 10), 2) for _ in range(n)] for _ in range(n)]

            mostrar_pasos = self.var_pasos_det.get()

            if metodo == "Descomposición LU":
                res = MotorAlgebra.determinante_lu(A, mostrar_pasos=mostrar_pasos)
            elif metodo == "Expansión por Cofactores":
                res = MotorAlgebra.determinante_cofactores(A, mostrar_pasos=mostrar_pasos)
            elif metodo == "Regla de Sarrus":
                res = MotorAlgebra.determinante_sarrus(A, mostrar_pasos=mostrar_pasos)

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

        ttk.Label(top, text="Método:").grid(row=0, column=4, padx=5)
        self.op_metodo_ec = ttk.Combobox(top, values=["Gauss-Jordan", "Regla de Cramer"], state="readonly", width=18)
        self.op_metodo_ec.set("Gauss-Jordan")
        self.op_metodo_ec.grid(row=0, column=5, padx=5)

        ttk.Button(top, text="Generar", command=self.dibujar_ecuaciones).grid(row=0, column=6, padx=10)

        self.box_ec = ttk.Frame(self.tab_ec)
        self.box_ec.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Button(self.tab_ec, text="Resolver Sistema", command=self.calc_ecuaciones).pack(fill="x", padx=5, pady=2)
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

            metodo = self.op_metodo_ec.get()

            if metodo == "Gauss-Jordan":
                res = MotorAlgebra.gauss_jordan(A, b)
            else:
                res = MotorAlgebra.cramer(A, b)

            self.txt_ec.insert(tk.END, res["log"] + "\n")

            if res["estado"] == "DETERMINADO" and res["sol"] is not None:
                self.txt_ec.insert(tk.END, "\n▶ VECTOR SOLUCIÓN FINAL:\n")
                for i, v in enumerate(res["sol"]):
                    self.txt_ec.insert(tk.END, f"   • x{i+1} = {v:.4f}\n")

        except Exception as err:
            messagebox.showerror("Error", str(err))

    # --- PESTAÑA BISECCIÓN ---
    def init_biseccion(self):
        top = ttk.LabelFrame(self.tab_bis, text="Parámetros de Bisección")
        top.pack(fill="x", padx=5, pady=5)

        ttk.Label(top, text="Ejercicio Predefinido:").grid(row=0, column=0, padx=5, pady=5)
        self.combo_ej_bis = ttk.Combobox(
            top, 
            values=[
                "Ejercicio Excel 1: f(x) = x^4 - 5x^3 + 0.5x^2 - 11x + 10",
                "Ejercicio Excel 2: f(x) = x^3 - 4x - 9",
                "Función Personalizada"
            ], 
            state="readonly", 
            width=48
        )
        self.combo_ej_bis.set("Ejercicio Excel 1: f(x) = x^4 - 5x^3 + 0.5x^2 - 11x + 10")
        self.combo_ej_bis.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="w")
        self.combo_ej_bis.bind("<<ComboboxSelected>>", self.cargar_preset_biseccion)

        ttk.Label(top, text="f(x):").grid(row=1, column=0, padx=5, pady=5)
        self.ent_fx_bis = self.crear_entry_adaptable(top, width=35, default_text="x**4 - 5*x**3 + 0.5*x**2 - 11*x + 10")
        self.ent_fx_bis.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(top, text="a inicial:").grid(row=1, column=2, padx=5, pady=5)
        self.ent_a_bis = self.crear_entry_adaptable(top, width=8, default_text="5.0")
        self.ent_a_bis.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(top, text="b inicial:").grid(row=1, column=4, padx=5, pady=5)
        self.ent_b_bis = self.crear_entry_adaptable(top, width=8, default_text="5.4")
        self.ent_b_bis.grid(row=1, column=5, padx=5, pady=5)

        ttk.Label(top, text="Tolerancia (e):").grid(row=1, column=6, padx=5, pady=5)
        self.ent_tol_bis = self.crear_entry_adaptable(top, width=10, default_text="0.0001")
        self.ent_tol_bis.grid(row=1, column=7, padx=5, pady=5)

        sub_bar = ttk.Frame(self.tab_bis)
        sub_bar.pack(fill="x", padx=5, pady=2)

        ttk.Button(sub_bar, text="CALCULAR BISECCIÓN", command=self.calc_biseccion).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(sub_bar, text="📋 Copiar Resultado (Texto)", command=lambda: self.copiar_al_portapapeles(self.txt_bis)).pack(side="right")

        frame_tabla = ttk.Frame(self.tab_bis)
        frame_tabla.pack(fill="both", expand=True, padx=5, pady=5)

        columnas = ("iter", "a", "b", "c", "fa", "fb", "fc", "error")
        self.tree_bis = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=8)

        self.tree_bis.heading("iter", text="Iter (k)")
        self.tree_bis.heading("a", text="a")
        self.tree_bis.heading("b", text="b")
        self.tree_bis.heading("c", text="c (Medio)")
        self.tree_bis.heading("fa", text="f(a)")
        self.tree_bis.heading("fb", text="f(b)")
        self.tree_bis.heading("fc", text="f(c)")
        self.tree_bis.heading("error", text="Error |f(c)|")

        for col in columnas:
            w_col = 65 if col == "iter" else 110
            self.tree_bis.column(col, width=w_col, anchor="center")

        v_scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree_bis.yview)
        h_scroll = ttk.Scrollbar(frame_tabla, orient="horizontal", command=self.tree_bis.xview)
        self.tree_bis.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree_bis.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        frame_tabla.grid_rowconfigure(0, weight=1)
        frame_tabla.grid_columnconfigure(0, weight=1)

        self.txt_bis = self.crear_scrolled_text(self.tab_bis, height=8)
        self.txt_bis.pack(fill="both", expand=True, padx=5, pady=5)

    def cargar_preset_biseccion(self, event=None):
        opcion = self.combo_ej_bis.get()
        if "Ejercicio Excel 1" in opcion:
            self.ent_fx_bis.delete(0, tk.END); self.ent_fx_bis.insert(0, "x**4 - 5*x**3 + 0.5*x**2 - 11*x + 10")
            self.ent_a_bis.delete(0, tk.END); self.ent_a_bis.insert(0, "5.0")
            self.ent_b_bis.delete(0, tk.END); self.ent_b_bis.insert(0, "5.4")
            self.ent_tol_bis.delete(0, tk.END); self.ent_tol_bis.insert(0, "0.0001")
        elif "Ejercicio Excel 2" in opcion:
            self.ent_fx_bis.delete(0, tk.END); self.ent_fx_bis.insert(0, "x**3 - 4*x - 9")
            self.ent_a_bis.delete(0, tk.END); self.ent_a_bis.insert(0, "2.0")
            self.ent_b_bis.delete(0, tk.END); self.ent_b_bis.insert(0, "3.0")
            self.ent_tol_bis.delete(0, tk.END); self.ent_tol_bis.insert(0, "0.0001")

    def calc_biseccion(self):
        self.txt_bis.delete("1.0", tk.END)
        for row in self.tree_bis.get_children():
            self.tree_bis.delete(row)

        try:
            expr = self.ent_fx_bis.get().strip()
            a = float(self.ent_a_bis.get())
            b = float(self.ent_b_bis.get())
            tol = float(self.ent_tol_bis.get())

            res = MotorAlgebra.metodo_biseccion(expr, a, b, tol)
            self.txt_bis.insert(tk.END, res["log"] + "\n")

            if res["exito"]:
                for fila in res["filas"]:
                    self.tree_bis.insert("", "end", values=(
                        fila["iter"],
                        f"{fila['a']:.6f}",
                        f"{fila['b']:.6f}",
                        f"{fila['c']:.6f}",
                        f"{fila['fa']:.6f}",
                        f"{fila['fb']:.6f}",
                        f"{fila['fc']:.6f}",
                        f"{fila['error']:.6f}"
                    ))
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