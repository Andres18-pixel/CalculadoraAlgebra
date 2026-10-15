"""
=============================================================================
PROGRAMA 2: CONVERSIÓN DE BASES NUMÉRICAS
=============================================================================
Este módulo permite realizar conversiones numéricas enteras entre distintas 
bases (Decimal, Binario, Octal y Hexadecimal) usando divisiones y multiplicaciones 
sucesivas, mostrando el desglose algebraico en pantalla.

Procedimiento Algebraico Equivalente:
1. Decimal a Base B (B = 2, 8, 16):
   Se divide sucesivamente N / B. Los residuos forman los dígitos de la base 
   destino en orden inverso (de abajo hacia arriba / del último al primero).
   N_decimal = r_k * B^k + ... + r_1 * B^1 + r_0 * B^0

2. Base B a Decimal (B = 2, 8, 16):
   Se evalúa la combinación lineal de potencias de la base:
   Valor = Σ (dígito_i * B^i) para i desde 0 hasta el número de dígitos - 1.
=============================================================================
"""

from utilidades import limpiar_pantalla, pausar, pedir_entero

MAPPING_HEX = "0123456789ABCDEF"

def decimal_a_base(numero_dec, base):
    """
    Convierte un número entero decimal a una base destino (2, 8 o 16),
    mostrando el algoritmo de divisiones sucesivas.
    
    Parámetros:
      - numero_dec (int): Número decimal a convertir.
      - base (int): Base destino (2, 8 o 16).
      
    Devuelve:
      - str: Representación en la base seleccionada.
    """
    if numero_dec == 0:
        print("\n Procedimiento Algebraico (Divisiones Sucesivas):")
        print("  0 / base = 0 | Residuo = 0")
        return "0"

    print("\n Procedimiento Algebraico (Divisiones Sucesivas):")
    print(f" {'Dividendo':>12} │ {'Divisor':>8} │ {'Cociente':>10} │ {'Residuo':>8} │ {'Simbolo':>8}")
    print(" ─────────────┼──────────┼────────────┼──────────┼─────────")

    residuos = []
    temp = abs(numero_dec)

    while temp > 0:
        cociente = temp // base
        residuo = temp % base
        simbolo = MAPPING_HEX[residuo]
        residuos.append(simbolo)
        print(f" {temp:>12} │ {base:>8} │ {cociente:>10} │ {residuo:>8} │ {simbolo:>8}")
        temp = cociente

    residuos.reverse()
    resultado = "".join(residuos)
    if numero_dec < 0:
        resultado = "-" + resultado

    print(f"\n Se leen los residuos desde el último obtenido hasta el primero:")
    print(f" Resultado en Base {base}: {resultado}")
    return resultado

def base_a_decimal(cadena_num, base):
    """
    Convierte un número en base B (2, 8, 16) a Decimal evaluando su polinomio 
    y combinación lineal de potencias.
    
    Parámetros:
      - cadena_num (str): Cadena de texto que representa el número en base B.
      - base (int): Base origen (2, 8 o 16).
      
    Devuelve:
      - int: Valor decimal resultante.
    """
    cadena_num = cadena_num.strip().upper()
    es_negativo = False
    if cadena_num.startswith("-"):
        es_negativo = True
        cadena_num = cadena_num[1:]

    # Validar caracteres válidos para la base dada
    caracteres_validos = MAPPING_HEX[:base]
    for c in cadena_num:
        if c not in caracteres_validos:
            print(f"\n Error: El símbolo '{c}' no es válido para la base {base}.")
            return None

    n = len(cadena_num)
    print("\n Procedimiento Algebraico (Combinación Lineal de Potencias):")
    
    terminos_str = []
    evaluaciones_str = []
    total_decimal = 0

    for i, c in enumerate(cadena_num):
        exponente = n - 1 - i
        valor_digito = MAPPING_HEX.index(c)
        contribucion = valor_digito * (base ** exponente)
        total_decimal += contribucion
        
        terminos_str.append(f"({c} · {base}^{exponente})")
        evaluaciones_str.append(f"({valor_digito} · {base ** exponente})")

    # Construir ecuación explicativa
    eq1 = " + ".join(terminos_str)
    eq2 = " + ".join(evaluaciones_str)
    
    print(f"  Desarrollo Polinómico : {eq1}")
    print(f"  Sustitución Numérica  : {eq2}")
    print(f"  Suma Evaluada         : {total_decimal}")

    if es_negativo:
        total_decimal = -total_decimal
        print(f"  Aplica Signo Negativo : {total_decimal}")

    return total_decimal

def ejecutar_modulo_bases():
    """
    Submenú principal para la conversión de bases numéricas.
    
    Parámetros: Ninguno.
    Devuelve: Ninguno.
    """
    while True:
        limpiar_pantalla()
        print("╔══════════════════════════════════════════════════════════╗")
        print("║          MÓDULO 2: CONVERTIDOR DE BASES NUMÉRICAS        ║")
        print("╠══════════════════════════════════════════════════════════╣")
        print("║                                                          ║")
        print("║   1. Convertir Decimal a Binario                         ║")
        print("║   2. Convertir Decimal a Octal                           ║")
        print("║   3. Convertir Decimal a Hexadecimal                     ║")
        print("║   4. Convertir Binario a Decimal                         ║")
        print("║   5. Convertir Octal a Decimal                           ║")
        print("║   6. Convertir Hexadecimal a Decimal                     ║")
        print("║   7. Volver al Menú Principal                            ║")
        print("║                                                          ║")
        print("╚══════════════════════════════════════════════════════════╝")

        opc = pedir_entero("Seleccione una opción: ", minimo=1, maximo=7)

        if opc == 7:
            break

        limpiar_pantalla()

        if opc in [1, 2, 3]:
            bases_dest = {1: 2, 2: 8, 3: 16}
            b_dest = bases_dest[opc]
            print(f"─── CONVERSIÓN DECIMAL ───> BASE {b_dest} ───\n")
            num = pedir_entero(" Ingrese un número entero decimal: ")
            decimal_a_base(num, b_dest)

        elif opc in [4, 5, 6]:
            bases_orig = {4: 2, 5: 8, 6: 16}
            b_orig = bases_orig[opc]
            print(f"─── CONVERSIÓN BASE {b_orig} ───> DECIMAL ───\n")
            cad = input(f" Ingrese un número en Base {b_orig}: ")
            res = base_a_decimal(cad, b_orig)
            if res is not None:
                print(f"\n Resultado Decimal: {res}")

        pausar()