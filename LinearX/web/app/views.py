import sys
from pathlib import Path
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

RUTA_LINEARX = Path(__file__).resolve().parents[2]
if str(RUTA_LINEARX) not in sys.path:
    sys.path.insert(0, str(RUTA_LINEARX))

from core.motor import MotorAlgebra


def index(request):
    return render(request, 'index.html')


def _parse_float_opt(val):
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    return float(s)


@csrf_exempt
def calcular_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Metodo HTTP no permitido. Use POST.'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        modulo = data.get('modulo')

        # ==================== MODULO 01: VECTORES ====================
        if modulo == 'vectores':
            op = data.get('op')
            if op == 'suma':
                res = MotorAlgebra.sumar_vectores(data.get('u', []), data.get('v', []))
            elif op == 'resta':
                res = MotorAlgebra.restar_vectores(data.get('u', []), data.get('v', []))
            elif op == 'escalar':
                res = MotorAlgebra.escalar_vector(float(data.get('k', 1)), data.get('v', []))
            elif op == 'punto':
                res = MotorAlgebra.producto_punto(data.get('u', []), data.get('v', []))
            elif op == 'combinacion':
                res = MotorAlgebra.combinacion_lineal(data.get('vecs', []), data.get('b', []))
            else:
                raise ValueError(f"Operacion de vectores no reconocida: {op}")
            return JsonResponse({'status': 'ok', **res})

        # ==================== MODULO 02: ALGEBRA DE MATRICES ====================
        elif modulo == 'matrices':
            op = data.get('op')
            if op == 'combinacion_lineal':
                res = MotorAlgebra.combinacion_matrices(
                    data.get('A'),
                    data.get('B'),
                    data.get('C'),
                    data.get('alpha', 1),
                    data.get('beta', 1),
                    data.get('gamma', 0)
                )
            elif op == 'suma':
                res = MotorAlgebra.sumar_matrices(data.get('A'), data.get('B'))
            elif op == 'resta':
                res = MotorAlgebra.restar_matrices(data.get('A'), data.get('B'))
            elif op == 'multiplicacion':
                res = MotorAlgebra.multiplicar_matrices(data.get('A'), data.get('B'))
            elif op == 'escalar':
                res = MotorAlgebra.escalar_matriz(data.get('k', 1), data.get('A'))
            else:
                raise ValueError(f"Operacion de matrices no reconocida: {op}")
            return JsonResponse({'status': 'ok', **res})

        # ==================== MODULO 03: INVERSA Y DETERMINANTE ====================
        elif modulo == 'inversa':
            A = data.get('A')
            pasos = bool(data.get('pasos', True))
            res = MotorAlgebra.inversa_gauss_jordan(A, mostrar_pasos=pasos)
            return JsonResponse({'status': 'ok', **res})

        # ==================== MODULO 04: DETERMINANTES ====================
        elif modulo == 'determinantes':
            metodo = data.get('metodo', 'lu')
            A = data.get('A')
            if metodo == 'lu':
                res = MotorAlgebra.determinante_lu(A)
            elif metodo == 'cofactores':
                res = MotorAlgebra.determinante_cofactores(A)
            elif metodo == 'sarrus':
                res = MotorAlgebra.determinante_sarrus(A)
            else:
                raise ValueError(f"Metodo de determinante no reconocido: {metodo}")
            return JsonResponse({'status': 'ok', **res})

        # ==================== MODULO 05: SISTEMAS CUADRADOS ====================
        elif modulo == 'ecuaciones':
            metodo = data.get('metodo', 'gauss')
            A = data.get('A')
            b = data.get('b')
            if metodo == 'gauss':
                res = MotorAlgebra.gauss_jordan(A, b)
            elif metodo == 'cramer':
                res = MotorAlgebra.cramer(A, b)
            else:
                raise ValueError(f"Metodo de sistema lineal no reconocido: {metodo}")
            return JsonResponse({'status': 'ok', **res})

        # ==================== MODULO 06: RAICES Y ASESOR ====================
        elif modulo == 'recomendar_metodo':
            expr = data.get('expr', '')
            if not expr.strip():
                raise ValueError("Ingrese una funcion f(x) antes de consultar al asesor.")
            a = _parse_float_opt(data.get('a'))
            b = _parse_float_opt(data.get('b'))
            res = MotorAlgebra.recomendar_metodo(expr, a=a, b=b)
            return JsonResponse({'status': 'ok', **res})

        elif modulo == 'biseccion':
            expr = data.get('expr', '')
            if not expr.strip():
                raise ValueError("La expresion f(x) no puede estar vacia.")

            if data.get('solo_grafica'):
                a = _parse_float_opt(data.get('a'))
                b = _parse_float_opt(data.get('b'))
                grafica = MotorAlgebra.generar_grafica_biseccion(expr, a_orig=a, b_orig=b, raiz=None)
                return JsonResponse({'status': 'ok', 'grafica': grafica})

            submetodo = data.get('submetodo', 'biseccion')
            tol = float(data.get('tol', 1e-6))
            max_iter = int(data.get('max_iter', 100))

            if submetodo == 'biseccion':
                a = float(data.get('a'))
                b = float(data.get('b'))
                res = MotorAlgebra.metodo_biseccion(expr, a, b, tol=tol, max_iter=max_iter)
                grafica = MotorAlgebra.generar_grafica_biseccion(expr, a_orig=a, b_orig=b, raiz=res.get('raiz'))
            elif submetodo == 'regla_falsa':
                a = float(data.get('a'))
                b = float(data.get('b'))
                res = MotorAlgebra.metodo_regla_falsa(expr, a, b, tol=tol, max_iter=max_iter)
                grafica = MotorAlgebra.generar_grafica_biseccion(expr, a_orig=a, b_orig=b, raiz=res.get('raiz'))
            elif submetodo == 'newton':
                x0 = float(data.get('x0'))
                res = MotorAlgebra.metodo_newton_raphson(expr, x0, tol=tol, max_iter=max_iter)
                raiz = res.get('raiz')
                grafica = MotorAlgebra.generar_grafica_biseccion(expr, a_orig=x0, b_orig=raiz, raiz=raiz)
            elif submetodo == 'secante':
                x0 = float(data.get('x0'))
                x1 = float(data.get('x1'))
                res = MotorAlgebra.metodo_secante(expr, x0, x1, tol=tol, max_iter=max_iter)
                grafica = MotorAlgebra.generar_grafica_biseccion(expr, a_orig=x0, b_orig=x1, raiz=res.get('raiz'))
            else:
                raise ValueError(f"Metodo numerico no reconocido: {submetodo}")

            return JsonResponse({'status': 'ok', **res, 'grafica': grafica})

        # ==================== MODULO 07: SISTEMAS RECTANGULARES ====================
        elif modulo == 'sistemas_rectangulares':
            res = MotorAlgebra.sistema_rectangular(data.get('A'), data.get('b'))
            return JsonResponse({'status': 'ok', **res})

        # ==================== MODULO 08: INDEPENDENCIA LINEAL ====================
        elif modulo == 'independencia_lineal':
            res = MotorAlgebra.independencia_lineal(data.get('vecs'))
            return JsonResponse({'status': 'ok', **res})

        # ==================== MODULO 09: ROMANOS ====================
        elif modulo == 'romanos':
            modo = data.get('modo')
            val = str(data.get('val', '')).strip()
            if modo == 'r2a':
                num = MotorAlgebra.romano_a_arabico(val)
                log = f"CONVERSION ROMANO -> ARABIGO\n• Romano : {val.upper()}\n• Arabigo: {num}"
                return JsonResponse({'status': 'ok', 'resultado': num, 'log': log})
            elif modo == 'a2r':
                rom = MotorAlgebra.arabico_a_romano(int(val))
                log = f"CONVERSION ARABIGO -> ROMANO\n• Arabigo: {val}\n• Romano : {rom}"
                return JsonResponse({'status': 'ok', 'resultado': rom, 'log': log})
            else:
                raise ValueError(f"Modo romano no reconocido: {modo}")

        else:
            return JsonResponse({'status': 'error', 'message': f"Modulo desconocido: {modulo}"}, status=400)

    except Exception as exc:
        return JsonResponse({'status': 'error', 'message': str(exc)})