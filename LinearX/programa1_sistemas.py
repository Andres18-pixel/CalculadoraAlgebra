"""
=============================================================================
PROGRAMA 1: SISTEMAS DE ECUACIONES LINEALES (GAUSS-JORDAN)
=============================================================================
Este módulo resuelve sistemas de ecuaciones lineales Ax = b mediante el 
algoritmo de Eliminación de Gauss-Jordan hasta obtener la forma escalonada 
reducida por filas (RREF).

Procedimiento Algebraico Equivalente:
1. Pivoteo Parcial: Intercambia filas de la matriz aumentada [A|b] si la 
   entrada diagonal es cero, seleccionando la fila con el valor absoluto máximo.
2. Normalización del Pivote: Se divide toda la fila k entre A[k][k] para 
   convertir la entrada diagonal principal en 1.
3. Reducción por Filas (Hacia adelante y hacia atrás): Para toda fila i != k,
   F_i = F_i - (A[i][k] * F_k), eliminando las variables en las columnas de pivote.
4. Evaluación del Rango y Consistencia:
   - Inconsistente: Si existe una fila de ceros en A con b[i] != 0 (0 = k).
   - Consistente Determinado: Si Rango(A) = Rango([A|b]) = Número de variables.
   - Consistente Indeterminado: Si Rango(A) = Rango([A|b]) < Número de variables.
=============================================================================
"""

import copy
from utilidades import (
    limpiar_pantalla, 
    pausar, 
    pedir_entero, 
    pedir_flotante, 
    imprimir_matriz_aumentada, 
    formatear_numero
)

def resolver_gauss_jordan(A_orig, b_orig, mostrar_pasos=True):
    """
    Aplica el algoritmo completo de Gauss-Jordan para la matriz [A|b].
    
    Parámetros:
      - A_orig (list): Matriz m x n de coeficientes.
      - b_orig (list): Vector de términos independientes (m elementos).
      - mostrar_pasos (bool): Muestra en pantalla el desarrollo paso a paso.
      
    Devuelve:
      - dict: Conteniendo la matriz A RREF, vector b RREF, tipo de sistema,
              soluciones numéricas (si aplica) y variables libres.
    """
    m = len(A_orig)
    n = len(A_orig[0])
    
    # Trabajar con copias para conservar los originales intactos
    A = [row[:] for row in A_orig]
    b = list(b_orig)
    
    if mostrar_pasos:
        print("\n" + "="*60)
        print(" MATRIZ AUMENTADA INICIAL [A|b]:")
        print("="*60)
        imprimir_matriz_aumentada(A, b)
        print("="*60 + "\n")
    
    fila_pivote = 0
    pivotes_columnas = []
    
    for j in range(n):
        if fila_pivote >= m:
            break
            
        # Buscar el pivote máximo en la columna j a partir de la fila_pivote
        max_fila = fila_pivote
        max_val = abs(A[fila_pivote][j])
        for k in range(fila_pivote + 1, m):
            if abs(A[k][j]) > max_val:
                max_val = abs(A[k][j])
                max_fila = k
                
        if abs(A[max_fila][j]) < 1e-9:
            # Columna sin pivote (columna nula en las filas restantes)
            continue
            
        # Intercambiar filas si el mayor pivote no está en la fila actual
        if max_fila != fila_pivote:
            A[fila_pivote], A[max_fila] = A[max_fila], A[fila_pivote]
            b[fila_pivote], b[max_fila] = b[max_fila], b[fila_pivote]
            if mostrar_pasos:
                print(f"──> Intercambio de Filas: F{fila_pivote+1} <──> F{max_fila+1}")
                imprimir_matriz_aumentada(A, b)
                print()

        # Normalizar el pivote a 1
        pivote = A[fila_pivote][j]
        if abs(pivote - 1.0) > 1e-9:
            factor = pivote
            for col in range(j, n):
                A[fila_pivote][col] /= factor
            b[fila_pivote] /= factor
            if mostrar_pasos:
                print(f"──> Normalizar Pivote: F{fila_pivote+1} = F{fila_pivote+1} / ({formatear_numero(factor)})")
                imprimir_matriz_aumentada(A, b)
                print()

        # Hacer ceros en toda la columna j (arriba y abajo del pivote)
        for i in range(m):
            if i != fila_pivote:
                factor = A[i][j]
                if abs(factor) > 1e-9:
                    for col in range(j, n):
                        A[i][col] -= factor * A[fila_pivote][col]
                    b[i] -= factor * b[fila_pivote]
                    if mostrar_pasos:
                        print(f"──> Reducción por Fila: F{i+1} = F{i+1} - ({formatear_numero(factor)}) * F{fila_pivote+1}")
                        imprimir_matriz_aumentada(A, b)
                        print()
                        
        pivotes_columnas.append(j)
        fila_pivote += 1

    # Limpiar imprecisiones flotantes extremadamente pequeñas
    for i in range(m):
        for j in range(n):
            if abs(A[i][j]) < 1e-9:
                A[i][j] = 0.0
        if abs(b[i]) < 1e-9:
            b[i] = 0.0

    # CLASIFICACIÓN DEL SISTEMA
    es_inconsistente = False
    for i in range(m):
        es_fila_ceros = all(abs(A[i][j]) < 1e-9 for j in range(n))
        if es_fila_ceros and abs(b[i]) > 1e-9:
            es_inconsistente = True
            break
            
    if es_inconsistente:
        tipo = "INCONSISTENTE"
        solucion = None
    elif len(pivotes_columnas) == n:
        tipo = "CONSISTENTE_DETERMINADO"
        solucion = [0.0] * n
        for i, col in enumerate(pivotes_columnas):
            solucion[col] = b[i]
    else:
        tipo = "CONSISTENTE_INDETERMINADO"
        solucion = None

    return {
        "A_rref": A,
        "b_rref": b,
        "tipo": tipo,
        "solucion": solucion,
        "pivotes": pivotes_columnas,
        "n_vars": n,
        "m_eqs": m
    }

def verificar_solucion(A, b, solucion):
    """
    Sustituye la solución en las ecuaciones originales A*x para verificar b.
    
    Parámetros:
      - A (list): Matriz original de m x n.
      - b (list): Vector término independiente original.
      - solucion (list): Valores numéricos de x.
      
    Devuelve: Ninguno (Imprime la verificación).
    """
    print("\n" + "="*60)
    print(" VERIFICACIÓN DE LA SOLUCIÓN OBTENIDA:")
    print("="*60)
    
    m = len(A)
    n = len(A[0])
    
    for i in range(m):
        linea = " "
        suma_lhs = 0.0
        terminos = []
        for j in range(n):
            coef = A[i][j]
            val_x = solucion[j]
            suma_lhs += coef * val_x
            terminos.append(f"{formatear_numero(coef)}({formatear_numero(val_x)})")
            
        linea += " + ".join(terminos)
        linea += f" = {formatear_numero(suma_lhs)}"
        cumple = abs(suma_lhs - b[i]) < 1e-5
        simbolo = "✓" if cumple else "✗"
        print(f" Ecuación {i+1}: {linea} (Esperado: {formatear_numero(b[i])}) [{simbolo}]")
    print("="*60)

def mostrar_solucion_parametrica(A_rref, b_rref, pivotes, n_vars):
    """
    Muestra la solución general de un sistema indeterminado parametrizando 
    las variables libres.
    
    Parámetros:
      - A_rref (list): Matriz RREF de coeficientes.
      - b_rref (list): Vector RREF de términos independientes.
      - pivotes (list): Índices de columnas que contienen pivotes.
      - n_vars (int): Cantidad total de variables del sistema.
      
    Devuelve: Ninguno.
    """
    vars_libres = [j for j in range(n_vars) if j not in pivotes]
    nombres_parametros = {}
    
    print("\n Soluciones Paramétricas:")
    for idx, var_f in enumerate(vars_libres):
        param = f"t{idx+1}"
        nombres_parametros[var_f] = param
        print(f"   x{var_f+1} = {param}  (Variable libre, {param} ∈ ℝ)")
        
    for i, col_piv in enumerate(pivotes):
        expr = f"{formatear_numero(b_rref[i])}"
        for var_f in vars_libres:
            coef = A_rref[i][var_f]
            if abs(coef) > 1e-9:
                signo = " - " if coef > 0 else " + "
                val_abs = abs(coef)
                str_coef = "" if abs(val_abs - 1.0) < 1e-9 else f"{formatear_numero(val_abs)}·"
                expr += f"{signo}{str_coef}{nombres_parametros[var_f]}"
        print(f"   x{col_piv+1} = {expr}")

def ejecutar_modulo_sistemas():
    """
    Submenú principal para la gestión y resolución de sistemas lineales.
    
    Parámetros: Ninguno.
    Devuelve: Ninguno.
    """
    while True:
        limpiar_pantalla()
        print("╔══════════════════════════════════════════════════════════╗")
        print("║          MÓDULO 1: SISTEMAS DE ECUACIONES LINEALES       ║")
        print("║                     (GAUSS-JORDAN)                       ║")
        print("╠══════════════════════════════════════════════════════════╣")
        print("║                                                          ║")
        print("║   1. Resolver Sistema de Ecuaciones (Ax = b)             ║")
        print("║   2. Volver al Menú Principal                            ║")
        print("║                                                          ║")
        print("╚══════════════════════════════════════════════════════════╝")
        
        opc = pedir_entero("Seleccione una opción: ", minimo=1, maximo=2)
        
        if opc == 2:
            break
            
        limpiar_pantalla()
        print("┌──────────────────────────────────────────────────────────┐")
        print("│      CONFIGURACIÓN DEL SISTEMA DE ECUACIONES [A|b]       │")
        print("└──────────────────────────────────────────────────────────┘\n")
        
        m = pedir_entero(" Ingrese el número de ecuaciones (m): ", minimo=1)
        n = pedir_entero(" Ingrese el número de variables (n): ", minimo=1)
        
        print(f"\n--- Coeficientes de la Matriz A ({m} x {n}) ---")
        A = []
        for i in range(m):
            fila = []
            print(f" Filas de Ecuación {i+1}:")
            for j in range(n):
                val = pedir_flotante(f"  Coeficiente de x{j+1}: ")
                fila.append(val)
            A.append(fila)
            
        print("\n--- Términos Independientes del Vector b ---")
        b = []
        for i in range(m):
            val = pedir_flotante(f"  Término independiente de Ecuación {i+1} (b[{i+1}]): ")
            b.append(val)
            
        limpiar_pantalla()
        res = resolver_gauss_jordan(A, b, mostrar_pasos=True)
        
        print("\n" + "="*60)
        print(" CLASIFICACIÓN FINAL DEL SISTEMA DE ECUACIONES")
        print("="*60)
        
        if res["tipo"] == "CONSISTENTE_DETERMINADO":
            print(" SISTEMA CONSISTENTE DETERMINADO: Presenta Solución Única.\n")
            print(" Valores de las Variables:")
            for idx, val in enumerate(res["solucion"]):
                print(f"   x{idx+1} = {formatear_numero(val)}")
            verificar_solucion(A, b, res["solucion"])
            
        elif res["tipo"] == "CONSISTENTE_INDETERMINADO":
            print(" SISTEMA CONSISTENTE INDETERMINADO: Presenta Infinitas Soluciones.\n")
            mostrar_solucion_parametrica(res["A_rref"], res["b_rref"], res["pivotes"], res["n_vars"])
            
        elif res["tipo"] == "INCONSISTENTE":
            print(" SISTEMA INCONSISTENTE: Sin Solución.")
            print(" Explicación: Se detectó una incoherencia de tipo [ 0 0 ... 0 | k ] con k ≠ 0.")
            
        pausar()