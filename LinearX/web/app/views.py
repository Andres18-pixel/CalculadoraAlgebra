import json
import sys
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from core.motor import MotorAlgebra


def index(request):
    return render(request, 'index.html')


@csrf_exempt
def calcular_api(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Metodo no permitido'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        modulo = data.get('modulo')

        if modulo == 'vectores':
            op = data.get('op')
            if op in ['suma', 'resta']:
                u = [float(x) for x in data.get('u', [])]
                v = [float(x) for x in data.get('v', [])]
                out = MotorAlgebra.sumar_vectores(u, v) if op == 'suma' else MotorAlgebra.restar_vectores(u, v)
                return JsonResponse({'status': 'ok', 'resultado': out['resultado'], 'log': out['log']})
            elif op == 'escalar':
                k = float(data.get('k', 1))
                v = [float(x) for x in data.get('v', [])]
                out = MotorAlgebra.escalar_vector(k, v)
                return JsonResponse({'status': 'ok', 'resultado': out['resultado'], 'log': out['log']})
            elif op == 'punto':
                u = [float(x) for x in data.get('u', [])]
                v = [float(x) for x in data.get('v', [])]
                out = MotorAlgebra.producto_punto(u, v)
                return JsonResponse({'status': 'ok', 'resultado': out['resultado'], 'log': out['log']})
            elif op == 'combinacion':
                vecs = [[float(x) for x in sub] for sub in data.get('vecs', [])]
                b = [float(x) for x in data.get('b', [])]
                out = MotorAlgebra.combinacion_lineal(vecs, b)
                return JsonResponse({'status': 'ok', 'log': out['log'], 'sol': out.get('sol')})

        elif modulo == 'matrices':
            op = data.get('op')
            A = [[float(x) for x in fila] for fila in data.get('A', [])]
            if op == 'escalar':
                k = float(data.get('k', 1))
                out = MotorAlgebra.escalar_matriz(k, A)
            else:
                B = [[float(x) for x in fila] for fila in data.get('B', [])]
                if op == 'suma':
                    out = MotorAlgebra.sumar_matrices(A, B)
                elif op == 'resta':
                    out = MotorAlgebra.restar_matrices(A, B)
                elif op == 'multiplicacion':
                    out = MotorAlgebra.multiplicar_matrices(A, B)
            return JsonResponse({'status': 'ok', 'resultado': out['resultado'], 'log': out['log']})

        elif modulo == 'inversa':
            A = [[float(x) for x in fila] for fila in data.get('A', [])]
            pasos = data.get('pasos', True)
            out = MotorAlgebra.inversa_gauss_jordan(A, mostrar_pasos=pasos)
            return JsonResponse({
                'status': 'ok',
                'existe': out['existe'],
                'determinante': out.get('determinante'),
                'inversa': out['inversa'],
                'comprobacion': out['comprobacion'],
                'log': out['log']
            })

        elif modulo == 'determinantes':
            A = [[float(x) for x in fila] for fila in data.get('A', [])]
            metodo = data.get('metodo', 'lu')
            pasos = data.get('pasos', True)

            if metodo == 'lu':
                out = MotorAlgebra.determinante_lu(A, mostrar_pasos=pasos)
            elif metodo == 'cofactores':
                out = MotorAlgebra.determinante_cofactores(A, mostrar_pasos=pasos)
            elif metodo == 'sarrus':
                out = MotorAlgebra.determinante_sarrus(A, mostrar_pasos=pasos)

            return JsonResponse({'status': 'ok', 'determinante': out['determinante'], 'log': out['log']})

        elif modulo == 'ecuaciones':
            A = [[float(x) for x in fila] for fila in data.get('A', [])]
            b = [float(x) for x in data.get('b', [])]
            metodo = data.get('metodo', 'gauss')

            if metodo == 'gauss':
                out = MotorAlgebra.gauss_jordan(A, b)
            else:
                out = MotorAlgebra.cramer(A, b)

            return JsonResponse({'status': 'ok', 'estado': out['estado'], 'sol': out.get('sol'), 'log': out['log']})

        elif modulo == 'recomendar_metodo':
            expr = data.get('expr', '')
            raw_a = data.get('a')
            raw_b = data.get('b')
            a = float(raw_a) if raw_a not in [None, ''] else None
            b = float(raw_b) if raw_b not in [None, ''] else None
            out = MotorAlgebra.recomendar_metodo(expr, a, b)
            return JsonResponse({
                'status': 'ok',
                'log': out['log'],
                'recomendacion': out['recomendacion'],
                'intervalos': out.get('intervalos', [])
            })

        elif modulo == 'biseccion':
            expr = data.get('expr', '')
            submetodo = data.get('submetodo', 'biseccion')
            solo_grafica = data.get('solo_grafica', False)
            raw_tol = data.get('tol', 1e-6)
            tol = float(raw_tol) if raw_tol not in [None, ''] else 1e-6
            raw_max_iter = data.get('max_iter', 100)
            max_iter = int(raw_max_iter) if raw_max_iter not in [None, ''] else 100

            raw_xmin = data.get('x_min')
            raw_xmax = data.get('x_max')
            x_min_c = float(raw_xmin) if raw_xmin not in [None, ''] else None
            x_max_c = float(raw_xmax) if raw_xmax not in [None, ''] else None

            raw_a = data.get('a')
            raw_b = data.get('b')
            a_val = float(raw_a) if raw_a not in [None, ''] else None
            b_val = float(raw_b) if raw_b not in [None, ''] else None

            if solo_grafica:
                grafica_data = MotorAlgebra.generar_grafica_biseccion(expr, a_val, b_val, None, x_min_c, x_max_c)
                return JsonResponse({'status': 'ok', 'exito': True, 'grafica': grafica_data})

            if submetodo == 'newton':
                raw_x0 = data.get('x0')
                if raw_x0 in [None, '']:
                    grafica_data = MotorAlgebra.generar_grafica_biseccion(expr, None, None, None, x_min_c, x_max_c)
                    return JsonResponse({'status': 'ok', 'exito': False, 'filas': [], 'log': "Ingrese el punto inicial x0.", 'grafica': grafica_data})
                x0 = float(raw_x0)
                out = MotorAlgebra.metodo_newton_raphson(expr, x0, tol, max_iter)
                grafica_data = MotorAlgebra.generar_grafica_biseccion(expr, x0, None, out['raiz'], x_min_c, x_max_c)

            elif submetodo == 'secante':
                raw_x0 = data.get('x0')
                raw_x1 = data.get('x1')
                if raw_x0 in [None, ''] or raw_x1 in [None, '']:
                    grafica_data = MotorAlgebra.generar_grafica_biseccion(expr, None, None, None, x_min_c, x_max_c)
                    return JsonResponse({'status': 'ok', 'exito': False, 'filas': [], 'log': "Ingrese x0 y x1 iniciales.", 'grafica': grafica_data})
                x0 = float(raw_x0)
                x1 = float(raw_x1)
                out = MotorAlgebra.metodo_secante(expr, x0, x1, tol, max_iter)
                grafica_data = MotorAlgebra.generar_grafica_biseccion(expr, x0, x1, out['raiz'], x_min_c, x_max_c)

            else:
                if a_val is None or b_val is None:
                    grafica_data = MotorAlgebra.generar_grafica_biseccion(expr, None, None, None, x_min_c, x_max_c)
                    return JsonResponse({'status': 'ok', 'exito': False, 'filas': [], 'log': "Ingrese 'a' y 'b'.", 'grafica': grafica_data})

                if submetodo == 'regla_falsa':
                    out = MotorAlgebra.metodo_regla_falsa(expr, a_val, b_val, tol, max_iter)
                else:
                    out = MotorAlgebra.metodo_biseccion(expr, a_val, b_val, tol, max_iter)

                grafica_data = MotorAlgebra.generar_grafica_biseccion(expr, a_val, b_val, out['raiz'], x_min_c, x_max_c)

            return JsonResponse({
                'status': 'ok',
                'exito': out['exito'],
                'filas': out['filas'],
                'log': out['log'],
                'grafica': grafica_data
            })

        elif modulo == 'romanos':
            modo = data.get('modo', 'r2a')
            val = data.get('val', '').strip()
            if modo == 'r2a':
                res = MotorAlgebra.romano_a_arabico(val)
            else:
                res = MotorAlgebra.arabico_a_romano(int(val))
            return JsonResponse({'status': 'ok', 'resultado': res})

        return JsonResponse({'status': 'error', 'message': 'Modulo no valido'}, status=400)

    except Exception as err:
        return JsonResponse({'status': 'error', 'message': str(err)}, status=400)