"""
=============================================================================
MÓDULO DE UTILIDADES Y FUNCIONES AUXILIARES
=============================================================================
Proporciona funciones para la gestión de la pantalla, formateo e impresión 
de matrices y vectores, y la validación de entradas de usuario para evitar 
fallos en la consola.
=============================================================================
"""

import os
import sys

def limpiar_pantalla():
    """
    Limpia la terminal según el sistema operativo detectado.
    
    Parámetros: Ninguno.
    Devuelve: Ninguno.
    """
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def pausar():
    """
    Pausa la ejecución del programa hasta que el usuario presione Enter.
    
    Parámetros: Ninguno.
    Devuelve: Ninguno.
    """
    input("\nPresione [ENTER] para continuar...")

def pedir_entero(mensaje, minimo=None, maximo=None):
    """
    Solicita un número entero al usuario y valida que sea un entero válido y
    opcionalmente que se encuentre dentro de un rango específico.
    
    Parámetros:
      - mensaje (str): Mensaje que se muestra al usuario.
      - minimo (int, opcional): Valor mínimo permitido.
      - maximo (int, opcional): Valor máximo permitido.
      
    Devuelve:
      - int: Número entero ingresado y validado.
    """
    while True:
        try:
            val = int(input(mensaje))
            if minimo is not None and val < minimo:
                print(f" Error: El valor debe ser mayor o igual a {minimo}.")
                continue
            if maximo is not None and val > maximo:
                print(f" Error: El valor debe ser menor o igual a {maximo}.")
                continue
            return val
        except ValueError:
            print(" Error: Por favor, ingrese un número entero válido.")

def pedir_flotante(mensaje):
    """
    Solicita un número real (flotante) al usuario y valida que sea correcto.
    
    Parámetros:
      - mensaje (str): Mensaje mostrado al pedir la entrada.
      
    Devuelve:
      - float: Número real validado.
    """
    while True:
        try:
            val = float(input(mensaje))
            return val
        except ValueError:
            print(" Error: Por favor, ingrese un valor numérico válido.")

def pedir_vector(n, nombre="v"):
    """
    Solicita los componentes de un vector de dimensión n al usuario.
    
    Parámetros:
      - n (int): Dimensión del vector.
      - nombre (str): Etiqueta para identificar el vector en la interfaz.
      
    Devuelve:
      - list: Lista de floats representando el vector de n elementos.
    """
    print(f"\n--- Ingrese las componentes del vector {nombre} ({n} dimensiones) ---")
    vec = []
    for i in range(n):
        val = pedir_flotante(f" Componente [{i + 1}]: ")
        vec.append(val)
    return vec

def pedir_matriz(m, n, nombre="A"):
    """
    Solicita los coeficientes de una matriz m x n fila por fila.
    
    Parámetros:
      - m (int): Número de filas.
      - n (int): Número de columnas.
      - nombre (str): Nombre identifacador de la matriz.
      
    Devuelve:
      - list: Lista anidada de m x n floats.
    """
    print(f"\n--- Ingrese las entradas de la matriz {nombre} ({m}x{n}) ---")
    matriz = []
    for i in range(m):
        fila = []
        print(f" Fila {i + 1}:")
        for j in range(n):
            val = pedir_flotante(f"  Entrada [{i + 1},{j + 1}]: ")
            fila.append(val)
        matriz.append(fila)
    return matriz

def formatear_numero(val, precision=4):
    """
    Formatea un número flotante para evitar ceros negativos (-0.0) y redondea 
    valores cercanos a enteros para mejorar la visualización.
    
    Parámetros:
      - val (float): Número a formatear.
      - precision (int): Cantidad de decimales.
      
    Devuelve:
      - str: Cadena de texto formateada.
    """
    if abs(val) < 1e-9:
        val = 0.0
    if abs(val - round(val)) < 1e-9:
        return f"{int(round(val))}"
    return f"{round(val, precision)}"

def imprimir_matriz(matriz):
    """
    Imprime una matriz dada de forma alineada en filas y columnas.
    
    Parámetros:
      - matriz (list): Lista anidada representando la matriz.
      
    Devuelve: Ninguno.
    """
    if not matriz or not matriz[0]:
        print(" [ Matriz Vacía ]")
        return
    
    for fila in matriz:
        str_fila = [formatear_numero(val) for val in fila]
        anchos = [len(s) for s in str_fila]
        max_ancho = max(anchos) if anchos else 6
        
        linea = "  │ "
        for s in str_fila:
            linea += f"{s:>{max_ancho + 2}} "
        linea += "│"
        print(linea)

def imprimir_matriz_aumentada(A, b):
    """
    Imprime una matriz aumentada [A|b] con separadores verticales legibles.
    
    Parámetros:
      - A (list): Lista anidada m x n (matriz de coeficientes).
      - b (list): Lista de m elementos (vector de términos independientes).
      
    Devuelve: Ninguno.
    """
    m = len(A)
    n = len(A[0]) if m > 0 else 0
    
    # Calcular anchos
    anchos = []
    for j in range(n):
        col_max = 0
        for i in range(m):
            s = formatear_numero(A[i][j])
            if len(s) > col_max:
                col_max = len(s)
        anchos.append(max(col_max, 4))
        
    b_max = 0
    for i in range(m):
        s = formatear_numero(b[i])
        if len(s) > b_max:
            b_max = len(s)
    b_max = max(b_max, 4)

    for i in range(m):
        linea = "  │ "
        for j in range(n):
            s = formatear_numero(A[i][j])
            linea += f"{s:>{anchos[j] + 2}} "
        linea += "│ "
        linea += f"{formatear_numero(b[i]):>{b_max + 2}} │"
        print(linea)