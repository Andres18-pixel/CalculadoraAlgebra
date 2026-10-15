"""
=============================================================================
                          UNIVERSIDAD AMERICANA (UAM)
                   FACULTAD DE INGENIERÍA Y ARQUITECTURA (FIA)
                          ASIGNATURA: ÁLGEBRA LINEAL
=============================================================================
 PROYECTO: Calculadora de Álgebra Lineal en Consola - "LINEARX"
 DOCENTE: Ing. Nombre del Profesor
 INTEGRANTES:
   - Nombre Completo Integrante 1
   - Nombre Completo Integrante 2
 CARRERA: Ingeniería en Sistemas de Información / Computación
 GRUPO: 1er Año
 FECHA: 2026
=============================================================================
 ARCHIVO MAIN.PY: Punto de entrada principal y navegador del sistema.
=============================================================================
"""

import sys
from utilidades import limpiar_pantalla, pedir_entero
from programa1_sistemas import ejecutar_modulo_sistemas
from programa2_bases import ejecutar_modulo_bases
from programa3_vectores import ejecutar_modulo_vectores

def mostrar_menu_principal():
    """
    Muestra la interfaz principal del programa LINEARX.
    
    Parámetros: Ninguno.
    Devuelve: Ninguno.
    """
    limpiar_pantalla()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                     L I N E A R X                        ║")
    print("║          Calculadora de Álgebra Lineal - UAM             ║")
    print("╠══════════════════════════════════════════════════════════╣")
    print("║                                                          ║")
    print("║   1. Análisis de Sistemas (Gauss-Jordan)                 ║")
    print("║   2. Convertidor de Bases Numéricas                      ║")
    print("║   3. Operaciones con Vectores y Matrices                 ║")
    print("║   4. Salir del Programa                                  ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")

def main():
    """
    Bucle de control principal para la navegación de la aplicación.
    
    Parámetros: Ninguno.
    Devuelve: Ninguno.
    """
    while True:
        mostrar_menu_principal()
        opcion = pedir_entero("Seleccione una opción: ", minimo=1, maximo=4)

        if opcion == 1:
            ejecutar_modulo_sistemas()
        elif opcion == 2:
            ejecutar_modulo_bases()
        elif opcion == 3:
            ejecutar_modulo_vectores()
        elif opcion == 4:
            limpiar_pantalla()
            print("\n" + "="*55)
            print(" Gracias por utilizar LINEARX. ¡Hasta pronto!")
            print(" Universidad Americana (UAM) - 2026")
            print("="*55 + "\n")
            sys.exit(0)

if __name__ == "__main__":
    main()