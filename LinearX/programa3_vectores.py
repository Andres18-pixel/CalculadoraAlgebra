"""
=============================================================================
PROGRAMA 3: VECTORES, OPERACIONES MATRICIALES Y ECUACIONES MATRICIALES
=============================================================================
Este módulo maneja sub-módulos para:
  3.1 Vectores en Rⁿ (Suma, resta, escalar, combinación lineal).
  3.2 Operaciones Matriciales Básicas (Suma, resta, escalar, multiplicación).
  3.3 Ecuaciones Matriciales (Ax = b) integrando el módulo de Gauss-Jordan.

Procedimiento Algebraico Equivalente:
1. Operaciones Vectoriales/Matriciales: Elemento a elemento.
2. Combinación Lineal: Se construye el sistema [v1 v2 ... vk | b] y se aplica
   Gauss-Jordan. Si el sistema es consistente, los valores de las variables 
   corresponden a los escalares c1, c2, ..., ck de la combinación.
=============================================================================
"""

from utilidades import (
    limpiar_pantalla, 
    pausar, 
    pedir_entero, 
    pedir_flotante, 
    pedir_vector, 
    pedir_matriz, 
    imprimir_matriz, 
    formatear_numero
)
from programa1_sistemas import resolver_gauss_jordan

# =============================================================================
# SUB-MÓDULO 3.1: VECTORES EN Rⁿ
# =============================================================================

def suma_vectores():
    """Suma componente a componente dos vectores v1, v2 de dimensión n."""
    print("─── SUMA DE VECTORES (u + v) ───\n")
    n = pedir_entero("Ingrese la dimensión n de los vectores: ", minimo=1)
    u = pedir_vector(n, nombre="u")
    v = pedir_vector(n, nombre="v")
    
    res = [u[i] + v[i] for i in range(n)]
    
    print("\n Resultado de u + v:")
    for i in range(n):
        print(f"  [{i+1}]: {formatear_numero(u[i])} + {formatear_numero(v[i])} = {formatear_numero(res[i])}")

def resta_vectores():
    """Resta componente a componente dos vectores u - v de dimensión n."""
    print("─── RESTA DE VECTORES (u - v) ───\n")
    n = pedir_entero("Ingrese la dimensión n de los vectores: ", minimo=1)
    u = pedir_vector(n, nombre="u")
    v = pedir_vector(n, nombre="v")
    
    res = [u[i] - v[i] for i in range(n)]
    
    print("\n Resultado de u - v:")
    for i in range(n):
        print(f"  [{i+1}]: {formatear_numero(u[i])} - {formatear_numero(v[i])} = {formatear_numero(res[i])}")

def escalar_por_vector():
    """Multiplica un escalar k por un vector v de dimensión n."""
    print("─── MULTIPLICACIÓN POR UN ESCALAR (k · v) ───\n")
    n = pedir_entero("Ingrese la dimensión n del vector: ", minimo=1)
    v = pedir_vector(n, nombre="v")
    k = pedir_flotante("\nIngrese el número escalar k: ")
    
    res = [k * v[i] for i in range(n)]
    
    print(f"\n Resultado de {formatear_numero(k)} · v:")
    for i in range(n):
        print(f"  [{i+1}]: {formatear_numero(k)} · {formatear_numero(v[i])} = {formatear_numero(res[i])}")

def evaluar_combinacion_lineal():
    """
    Evalúa si un vector b es combinación lineal de un conjunto de k vectores {v1, ..., vk}.
    Arma una matriz A cuya columna j es el vector vj y resuelve A * c = b.
    """
    print("─── COMBINACIÓN LINEAL DE VECTORES ───\n")
    n = pedir_entero("Ingrese la dimensión n de los vectores: ", minimo=1)
    k = pedir_entero("Ingrese la cantidad k de vectores en el conjunto: ", minimo=1)
    
    vectores = []
    for i in range(k):
        v = pedir_vector(n, nombre=f"v{i+1}")
        vectores.append(v)
        
    b = pedir_vector(n, nombre="b (vector objetivo)")
    
    # Construir la matriz A de dimensiones n x k donde la columna j es el vector vj
    A = [[0.0] * k for _ in range(n)]
    for j in range(k):
        for i in range(n):
            A[i][j] = vectores[j][i]
            
    print("\n Se formula el sistema lineal [v1 v2 ... vk | b] para calcular los coeficientes (c1, ..., ck):")
    res = resolver_gauss_jordan(A, b, mostrar_pasos=False)
    
    if res["tipo"] == "CONSISTENTE_DETERMINADO":
        print("\n ¡ÉXITO! El vector b SÍ es COMBINACIÓN LINEAL del conjunto de vectores.")
        print(" Coeficientes únicos encontrados:")
        for idx, val in enumerate(res["solucion"]):
            print(f"   c{idx+1} = {formatear_numero(val)}")
        
        # Mostrar ecuación
        eq_str = " + ".join([f"{formatear_numero(res['solucion'][i])}·v{i+1}" for i in range(k)])
        print(f"\n Expresión: b = {eq_str}")

    elif res["tipo"] == "CONSISTENTE_INDETERMINADO":
        print("\n ¡ÉXITO! El vector b SÍ es COMBINACIÓN LINEAL (existen infinitas combinaciones posibles).")

    else:
        print("\n NO ES COMBINACIÓN LINEAL. El vector b no puede expresarse como combinación del conjunto de vectores dados.")

def menu_vectores():
    """Menú secundario para operaciones con vectores."""
    while True:
        limpiar_pantalla()
        print("╔══════════════════════════════════════════════════════════╗")
        print("║              SUB-MÓDULO: VECTORES EN Rⁿ                  ║")
        print("╠══════════════════════════════════════════════════════════╣")
        print("║   1. Suma de Vectores (u + v)                            ║")
        print("║   2. Resta de Vectores (u - v)                           ║")
        print("║   3. Multiplicación por un Escalar (k · v)               ║")
        print("║   4. Evaluar Combinación Lineal                          ║")
        print("║   5. Volver al Menú Anterior                             ║")
        print("╚══════════════════════════════════════════════════════════╝")
        
        opc = pedir_entero("Seleccione una opción: ", minimo=1, maximo=5)
        if opc == 5:
            break
        limpiar_pantalla()
        if opc == 1:
            suma_vectores()
        elif opc == 2:
            resta_vectores()
        elif opc == 3:
            escalar_por_vector()
        elif opc == 4:
            evaluar_combinacion_lineal()
        pausar()

# =============================================================================
# SUB-MÓDULO 3.2: OPERACIONES MATRICIALES BÁSICAS
# =============================================================================

def suma_matrices():
    """Suma elemento a elemento dos matrices A, B de m x n."""
    print("─── SUMA DE MATRICES (A + B) ───\n")
    m = pedir_entero("Ingrese número de filas (m): ", minimo=1)
    n = pedir_entero("Ingrese número de columnas (n): ", minimo=1)
    
    A = pedir_matriz(m, n, nombre="A")
    B = pedir_matriz(m, n, nombre="B")
    
    C = [[A[i][j] + B[i][j] for j in range(n)] for i in range(m)]
    
    print("\n Matriz Resultante C = A + B:")
    imprimir_matriz(C)

def resta_matrices():
    """Resta elemento a elemento dos matrices A, B de m x n."""
    print("─── RESTA DE MATRICES (A - B) ───\n")
    m = pedir_entero("Ingrese número de filas (m): ", minimo=1)
    n = pedir_entero("Ingrese número de columnas (n): ", minimo=1)
    
    A = pedir_matriz(m, n, nombre="A")
    B = pedir_matriz(m, n, nombre="B")
    
    C = [[A[i][j] - B[i][j] for j in range(n)] for i in range(m)]
    
    print("\n Matriz Resultante C = A - B:")
    imprimir_matriz(C)

def escalar_por_matriz():
    """Multiplica una matriz de m x n por un escalar k."""
    print("─── MULTIPLICACIÓN DE MATRIZ POR UN ESCALAR (k · A) ───\n")
    m = pedir_entero("Ingrese número de filas (m): ", minimo=1)
    n = pedir_entero("Ingrese número de columnas (n): ", minimo=1)
    
    A = pedir_matriz(m, n, nombre="A")
    k = pedir_flotante("\nIngrese el número escalar k: ")
    
    C = [[k * A[i][j] for j in range(n)] for i in range(m)]
    
    print(f"\n Matriz Resultante C = {formatear_numero(k)} · A:")
    imprimir_matriz(C)

def multiplicacion_matrices():
    """
    Multiplica dos matrices A(m x n) y B(n x p), validando la compatibilidad.
    C[i][j] = Σ A[i][k] * B[k][j]
    """
    print("─── MULTIPLICACIÓN DE MATRICES (A · B) ───\n")
    mA = pedir_entero("Ingrese filas de Matriz A (m): ", minimo=1)
    nA = pedir_entero("Ingrese columnas de Matriz A (n): ", minimo=1)
    
    print(f"\n NOTA: Para multiplicar A · B, las filas de B deben ser iguales a {nA}.")
    mB = nA
    pB = pedir_entero("Ingrese columnas de Matriz B (p): ", minimo=1)
    
    A = pedir_matriz(mA, nA, nombre="A")
    B = pedir_matriz(mB, pB, nombre="B")
    
    # Algoritmo de multiplicación de matrices
    C = [[0.0] * pB for _ in range(mA)]
    for i in range(mA):
        for j in range(pB):
            suma = 0.0
            for k in range(nA):
                suma += A[i][k] * B[k][j]
            C[i][j] = suma
            
    print(f"\n Matriz Resultante C = A · B ({mA} x {pB}):")
    imprimir_matriz(C)

def menu_matrices():
    """Menú secundario para operaciones con matrices."""
    while True:
        limpiar_pantalla()
        print("╔══════════════════════════════════════════════════════════╗")
        print("║         SUB-MÓDULO: OPERACIONES MATRICIALES              ║")
        print("╠══════════════════════════════════════════════════════════╣")
        print("║   1. Suma de Matrices (A + B)                            ║")
        print("║   2. Resta de Matrices (A - B)                           ║")
        print("║   3. Multiplicación por un Escalar (k · A)               ║")
        print("║   4. Multiplicación de Matrices (A · B)                  ║")
        print("║   5. Volver al Menú Anterior                             ║")
        print("╚══════════════════════════════════════════════════════════╝")
        
        opc = pedir_entero("Seleccione una opción: ", minimo=1, maximo=5)
        if opc == 5:
            break
        limpiar_pantalla()
        if opc == 1:
            suma_matrices()
        elif opc == 2:
            resta_matrices()
        elif opc == 3:
            escalar_por_matriz()
        elif opc == 4:
            multiplicacion_matrices()
        pausar()

# =============================================================================
# SUB-MÓDULO 3.3: ECUACIONES MATRICIALES (Ax = b)
# =============================================================================

def resolver_ecuacion_matricial():
    """
    Resuelve la ecuación matricial Ax = b importando y reutilizando el 
    algoritmo del Módulo 1 (Gauss-Jordan).
    """
    print("─── RESOLUCIÓN DE ECUACIÓN MATRICIAL (Ax = b) ───\n")
    m = pedir_entero("Ingrese número de filas de A (m): ", minimo=1)
    n = pedir_entero("Ingrese número de columnas de A (n): ", minimo=1)
    
    A = pedir_matriz(m, n, nombre="A")
    b = pedir_vector(m, nombre="b")
    
    limpiar_pantalla()
    print(" Importando y ejecutando motor de Gauss-Jordan de programa1_sistemas.py...\n")
    res = resolver_gauss_jordan(A, b, mostrar_pasos=True)
    
    print("\n" + "="*60)
    print(" RESULTADO DE LA ECUACIÓN MATRICIAL")
    print("="*60)
    if res["tipo"] == "CONSISTENTE_DETERMINADO":
        print(" SISTEMA CONSISTENTE DETERMINADO: Solución Única Vectorial x.\n")
        print(" Vector Incógnita x:")
        for idx, val in enumerate(res["solucion"]):
            print(f"   x[{idx+1}] = {formatear_numero(val)}")
    elif res["tipo"] == "CONSISTENTE_INDETERMINADO":
        print(" SISTEMA CONSISTENTE INDETERMINADO: Infinitos Vectores x satisfacen Ax = b.")
    else:
        print(" SISTEMA INCONSISTENTE: No existe un vector x tal que Ax = b.")

def ejecutar_modulo_vectores():
    """
    Menú principal del Módulo 3.
    
    Parámetros: Ninguno.
    Devuelve: Ninguno.
    """
    while True:
        limpiar_pantalla()
        print("╔══════════════════════════════════════════════════════════╗")
        print("║    MÓDULO 3: VECTORES, MATRICES Y ECUACIONES MATRICIALES ║")
        print("╠══════════════════════════════════════════════════════════╣")
        print("║                                                          ║")
        print("║   1. Operaciones con Vectores en Rⁿ                      ║")
        print("║   2. Operaciones Matriciales Básicas                     ║")
        print("║   3. Ecuaciones Matriciales (Ax = b)                     ║")
        print("║   4. Volver al Menú Principal                            ║")
        print("║                                                          ║")
        print("╚══════════════════════════════════════════════════════════╝")

        opc = pedir_entero("Seleccione una opción: ", minimo=1, maximo=4)
        if opc == 4:
            break
        elif opc == 1:
            menu_vectores()
        elif opc == 2:
            menu_matrices()
        elif opc == 3:
            limpiar_pantalla()
            resolver_ecuacion_matricial()
            pausar()