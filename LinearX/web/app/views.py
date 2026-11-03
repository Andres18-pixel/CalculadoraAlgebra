import json
import sys
import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Añadimos la carpeta raíz del proyecto para importar el motor matemático (core/motor.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from core.motor import MotorAlgebra


def index(request):
    """Renderiza la interfaz principal del Dashboard Web."""
    return render(request, 'index.html')


@csrf_exempt
def calcular_api(request):
    """Endpoint único que procesa todas las operaciones matemáticas recibidas desde la web."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        modulo = data.get('modulo')

        # --- VECTORES ---
        if modulo == 'vectores':
            op = data.get('op')
            if op in ['suma', 'resta']:
                u = [float(x) for x in data.get('u', [])]
                v = [float(x) for x in data.get('v', [])]
                res = MotorAlgebra.sumar_vectores(u, v) if op == 'suma' else MotorAlgebra.restar_vectores(u, v)
                return JsonResponse({'status': 'ok', 'resultado': res})
            elif op == 'escalar':
                k = float(data.get('k', 1))
                v = [float(x) for x in data.get('v', [])]
                res = MotorAlgebra.escalar_vector(k, v)
                return JsonResponse({'status': 'ok', 'resultado': res})
            elif op == 'combinacion':
                vecs = [[float(x) for x in sub] for sub in data.get('vecs', [])]
                b = [float(x) for x in data.get('b', [])]
                out = MotorAlgebra.combinacion_lineal(vecs, b)
                return JsonResponse({'status': 'ok', 'log': out['log'], 'sol': out.get('sol')})

        # --- MATRICES ---
        elif modulo == 'matrices':
            op = data.get('op')
            A = [[float(x) for x in fila] for fila in data.get('A', [])]
            if op == 'escalar':
                k = float(data.get('k', 1))
                res = MotorAlgebra.escalar_matriz(k, A)
            else:
                B = [[float(x) for x in fila] for fila in data.get('B', [])]
                if op == 'suma':
                    res = MotorAlgebra.sumar_matrices(A, B)
                elif op == 'resta':
                    res = MotorAlgebra.restar_matrices(A, B)
                elif op == 'multiplicacion':
                    res = MotorAlgebra.multiplicar_matrices(A, B)
            return JsonResponse({'status': 'ok', 'resultado': res})

        # --- INVERSA ---
        elif modulo == 'inversa':
            A = [[float(x) for x in fila] for fila in data.get('A', [])]
            pasos = data.get('pasos', True)
            out = MotorAlgebra.inversa_gauss_jordan(A, mostrar_pasos=pasos)
            return JsonResponse({
                'status': 'ok',
                'existe': out['existe'],
                'inversa': out['inversa'],
                'comprobacion': out['comprobacion'],
                'log': out['log']
            })

        # --- DETERMINANTES ---
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

        # --- ECUACIONES ---
        elif modulo == 'ecuaciones':
            A = [[float(x) for x in fila] for fila in data.get('A', [])]
            b = [float(x) for x in data.get('b', [])]
            metodo = data.get('metodo', 'gauss')
            
            if metodo == 'gauss':
                out = MotorAlgebra.gauss_jordan(A, b)
            else:
                out = MotorAlgebra.cramer(A, b)
            
            return JsonResponse({'status': 'ok', 'estado': out['estado'], 'sol': out.get('sol'), 'log': out['log']})

        # --- BISECCIÓN ---
        elif modulo == 'biseccion':
            expr = data.get('expr', '')
            a = float(data.get('a', 0))
            b = float(data.get('b', 0))
            tol = float(data.get('tol', 0.0001))
            out = MotorAlgebra.metodo_biseccion(expr, a, b, tol)
            
            # Generar datos para la gráfica si el método converge con éxito
            grafica_data = None
            if out['exito']:
                grafica_data = MotorAlgebra.generar_grafica_biseccion(expr, a, b, out['raiz'])

            return JsonResponse({
                'status': 'ok', 
                'exito': out['exito'], 
                'filas': out['filas'], 
                'log': out['log'],
                'grafica': grafica_data
            })

        # --- ROMANOS ---
        elif modulo == 'romanos':
            modo = data.get('modo', 'r2a')
            val = data.get('val', '').strip()
            if modo == 'r2a':
                res = MotorAlgebra.romano_a_arabico(val)
            else:
                res = MotorAlgebra.arabico_a_romano(int(val))
            return JsonResponse({'status': 'ok', 'resultado': res})

        return JsonResponse({'status': 'error', 'message': 'Módulo no válido'}, status=400)

    except Exception as err:
        return JsonResponse({'status': 'error', 'message': str(err)}, status=400)