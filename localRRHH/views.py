from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Personal
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Sum, Count
from datetime import datetime, time
import random


def index(request):
    error_message = ''
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre', '').strip()
            apellido = request.POST.get('apellido', '').strip()
            salario = request.POST.get('salario')
            edad = request.POST.get('edad')
            anios_experiencia = request.POST.get('anios_experiencia')
            categoria = request.POST.get('categoria')
            puesto = request.POST.get('puesto')
            horario_entrada = request.POST.get('horario_entrada')
            horario_salida = request.POST.get('horario_salida')
            dia_inicio = request.POST.get('dia_inicio')
            dia_fin = request.POST.get('dia_fin')
            pStatus = request.POST.get('pStatus')
            

            personal = Personal(
                nombre=nombre,
                apellido=apellido,
                salario=int(salario) if salario else 0,
                edad=int(edad) if edad else 0,
                anios_experiencia=int(anios_experiencia) if anios_experiencia else 0,
                categoria=categoria,
                puesto=puesto,
                horario_entrada=horario_entrada,
                horario_salida=horario_salida,
                dia_inicio=dia_inicio,
                dia_fin=dia_fin,
                pStatus=int(pStatus) if pStatus else 1,
                
            )

            personal.full_clean()  # Invoca validaciones
            personal.save()
            return redirect('index')

        except (ValidationError, ValueError, IntegrityError) as e:
            error_message = str(e)

    personal_list = Personal.objects.all()

    # Calcular estadísticas
    total_salarios = Personal.objects.aggregate(total=Sum('salario'))['total'] or 0
    personal_activo = Personal.objects.filter(pStatus=1).count()
    personal_inactivo = Personal.objects.filter(pStatus=2).count()
    personal_de_baja = Personal.objects.filter(pStatus=3).count()
    personal_amonestado = Personal.objects.filter(amon_estado=True).count()

    return render(request, 'rrhh.html', {
        'personal_list': personal_list,
        'error_message': error_message,
        'total_salarios': total_salarios,
        'personal_activo': personal_activo,
        'personal_inactivo': personal_inactivo,
        'personal_de_baja': personal_de_baja,
        'personal_amonestado': personal_amonestado,
    })




@csrf_exempt
@require_POST
def personal_delete(request, pk):
    try:
        personal = Personal.objects.filter(id=pk).first()
        if not personal:
            return JsonResponse({'error': 'Personal no encontrado'}, status=404)
        # Los datos de amonestación están incorporados en la fila Personal
        personal.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def personal_update(request, pk):
    try:
        try:
            data = json.loads(request.body)
        except Exception:
            data = request.POST.dict()

        personal = Personal.objects.filter(id=pk).first()
        if not personal:
            return JsonResponse({'error': 'Personal no encontrado'}, status=404)

        # Campos editables
        salario = int(data.get('salario', personal.salario))
        categoria = data.get('categoria', personal.categoria)
        puesto = data.get('puesto', personal.puesto)
        pStatus = int(data.get('pStatus', personal.pStatus))

        # Nuevos campos de horario y días, usar valor actual si no vienen
        horario_entrada = data.get('horario_entrada', None)
        horario_salida = data.get('horario_salida', None)
        dia_inicio = data.get('dia_inicio', None)
        dia_fin = data.get('dia_fin', None)

        personal.salario = salario
        personal.categoria = categoria
        personal.puesto = puesto
        personal.pStatus = pStatus
        # Asignar horarios - convertir string HH:MM a time si es necesario
        if horario_entrada is not None:
            from datetime import datetime
            personal.horario_entrada = datetime.strptime(horario_entrada, '%H:%M').time()
        if horario_salida is not None:
            from datetime import datetime
            personal.horario_salida = datetime.strptime(horario_salida, '%H:%M').time()

        # Asignar días si vienen
        if dia_inicio is not None:
            personal.dia_inicio = dia_inicio
        if dia_fin is not None:
            personal.dia_fin = dia_fin

        personal.full_clean()
        personal.save()

        # Amonestación
        amon = data.get('amonestacion') or {}
        estado_raw = amon.get('estado') if isinstance(amon, dict) else data.get('amonestacion_estado')
        detalle = amon.get('detalle') if isinstance(amon, dict) else data.get('amonestacion_detalle')

        estado_bool = False
        if isinstance(estado_raw, bool):
            estado_bool = estado_raw
        elif estado_raw is not None:
            try:
                estado_str = str(estado_raw).strip().lower()
                if estado_str in ['true', '1', 'yes', 'y']:
                    estado_bool = True
                else:
                    estado_bool = False
            except Exception:
                estado_bool = False

        personal.amon_estado = estado_bool
        personal.amon_detalle = detalle or '' if estado_bool else ''

        personal.full_clean()
        personal.save()

        response = {
            'id': personal.id,
            'salario': personal.salario,
            'edad': personal.edad,
            'anios_experiencia': personal.anios_experiencia,
            'categoria': personal.categoria,
            'puesto': personal.puesto,
            'pStatus': personal.pStatus,
            'amonestacion': {
                'estado': personal.amon_estado,
                'detalle': personal.amon_detalle or ''
            },
            'horario_entrada': personal.horario_entrada.strftime('%H:%M') if personal.horario_entrada else '',
            'horario_salida': personal.horario_salida.strftime('%H:%M') if personal.horario_salida else '',
            'dia_inicio': personal.dia_inicio or '',
            'dia_fin': personal.dia_fin or '',
        }

        return JsonResponse(response)

    except ValidationError as e:
        return JsonResponse({'error': e.message_dict if hasattr(e, 'message_dict') else str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




@csrf_exempt
@require_POST
def generar_plantel(request):
    try:
        print(f"DEBUG - Función generar_plantel llamada")
        data = json.loads(request.body) if request.body else {}
        cantidad = int(data.get('cantidad', 0))
        print(f"DEBUG - Cantidad recibida: {cantidad}")

        if cantidad <= 0:
            print(f"DEBUG - Cantidad inválida: {cantidad}")
            return JsonResponse({'error': 'Cantidad inválida. Debe ser un número entero mayor que cero.'}, status=400)

        # Prioridades: Mantenimiento, Culinario, Entretenimiento, Medico, Administrativo
        prioridades = [
            ('Mantenimiento', 30),
            ('Culinario', 25),
            ('Entretenimiento', 20),
            ('Medico', 15),
            ('Administrativo', 10),
        ]

        puestos_por_categoria = {
            'Mantenimiento': ['Plomero', 'Ingeniero', 'Conserje', 'Tecnico'],
            'Culinario': ['Cocinero', 'Mesero', 'Chef', 'Barista', 'Repostero', 'Bartender', 'Sous chef', 'Sommelier', 'Jefe de Alimentos'],
            'Entretenimiento': ['Animadores', "DJ's", 'Musicos', 'Bailarines', 'Guias Turisticos'],
            'Medico': ['Enfermero', 'Medico General', 'Medico en Jefe', 'Paramedico'],
            'Administrativo': ['Gerente', 'Cajero']
        }

        exclusiones = {}

        # Listas de nombres y apellidos para generar personal
        nombres = ['Ana', 'Luis', 'Jose', 'Maria', 'Pablo', 'Carmen', 'Juan', 'Marta', 'Diego', 'Laura', 'Raul', 'Nora', 'Elena', 'Carlos', 'Sofia', 
                   'Pedro', 'Lucia', 'Andres', 'Rosa', 'Victor', 'Fernando', 'Gloria', 'Sebastian', 'Isabel', 'Miguel', 'Patricia', 'Jorge', 'Paula', 'Alberto', 'Clara']
        apellidos = ['Garcia', 'Martinez', 'Lopez', 'Hernandez', 'Gonzalez', 'Perez', 'Sanchez', 'Ramirez', 'Torres', 'Flores', 'Diaz', 'Vargas', 'Rojas', 'Castro', 'Ortega',
                     'Molina', 'Silva', 'Cruz', 'Herrera', 'Mendez', 'Vega', 'Soto', 'Castillo', 'Navarro', 'Delgado', 'Ramos', 'Mora', 'Guerrero', 'Pineda', 'Campos']
        salarios_permitidos = [s for s in range(800, 3001, 250)]
        
        # Horarios y días de trabajo
        horarios_entrada = ['06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00']
        horarios_salida = ['14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00']
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

        # Calcular distribución basada en porcentajes
        distribucion = {}
        total_asignado = 0
        for categoria, porcentaje in prioridades:
            asignados = int(cantidad * porcentaje / 100)
            distribucion[categoria] = asignados
            total_asignado += asignados
        
        # Ajustar para que la suma sea exactamente la cantidad solicitada
        diferencia = cantidad - total_asignado
        if diferencia != 0:
            distribucion['Mantenimiento'] = distribucion.get('Mantenimiento', 0) + diferencia
        
        print(f"DEBUG - Cantidad solicitada: {cantidad}")
        print(f"DEBUG - Total asignado antes del ajuste: {total_asignado}")
        print(f"DEBUG - Diferencia: {diferencia}")

        creados = 0
        errores = []
        print(f"DEBUG - Distribución calculada: {distribucion}")

        for categoria, num in distribucion.items():
            print(f"DEBUG - Procesando categoría: {categoria}, cantidad: {num}")
            puestos = puestos_por_categoria.get(categoria, [])
            for i in range(num):
                try:
                    print(f"DEBUG - Creando empleado {i+1} de {num} para {categoria}")
                    nombre = random.choice(nombres)[:10].capitalize()
                    apellido = random.choice(apellidos)[:10].capitalize()
                    puesto = random.choice(puestos) if puestos else 'No Ocupado'
                    if puesto in exclusiones:
                        puestos_alt = [p for p in puestos if p not in exclusiones]
                        puesto = random.choice(puestos_alt) if puestos_alt else 'No Ocupado'

                    salario = random.choice(salarios_permitidos)
                    edad = random.randint(21, 65)
                    max_exp = max(0, edad // 2)
                    anios_experiencia = random.randint(0, min(max_exp, 40))
                    
                    # Generar horarios y días aleatorios que cumplan las validaciones
                    horario_entrada = random.choice(horarios_entrada)
                    # Asegurar que la salida sea después de la entrada
                    horarios_salida_validos = [h for h in horarios_salida if h > horario_entrada]
                    if not horarios_salida_validos:
                        horarios_salida_validos = ['18:00', '19:00', '20:00']  # Horarios por defecto
                    horario_salida = random.choice(horarios_salida_validos)
                    
                    # Asegurar que el día fin sea igual o posterior al día inicio
                    dia_inicio = random.choice(dias_semana)
                    indice_inicio = dias_semana.index(dia_inicio)
                    dias_fin_validos = dias_semana[indice_inicio:]  # Desde el día inicio hasta el final
                    dia_fin = random.choice(dias_fin_validos)

                    personal = Personal(
                        nombre=nombre,
                        apellido=apellido,
                        salario=salario,
                        edad=edad,
                        anios_experiencia=anios_experiencia,
                        categoria=categoria,
                        puesto=puesto,
                        horario_entrada=horario_entrada,
                        horario_salida=horario_salida,
                        dia_inicio=dia_inicio,
                        dia_fin=dia_fin,
                        pStatus=1,
                    )
                    personal.full_clean()
                    personal.save()
                    creados += 1
                    print(f"DEBUG - Empleado creado exitosamente: {nombre} {apellido}")
                except Exception as e:
                    print(f"DEBUG - Error creando empleado {i+1} para {categoria}: {str(e)}")
                    print(f"DEBUG - Datos del empleado: nombre={nombre}, apellido={apellido}, puesto={puesto}, edad={edad}")
                    errores.append(f"{categoria}-{i+1}: {str(e)}")
                    continue

        print(f"DEBUG - Total creados: {creados}, Errores: {len(errores)}")
        if errores:
            print(f"DEBUG - Lista de errores: {errores[:5]}")  # Mostrar solo los primeros 5 errores
        return JsonResponse({'success': True, 'creados': creados, 'created_count': creados, 'distribucion': distribucion, 'errores': errores})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
@require_POST
def vaciar_plantel(request):
    try:
        personal_count = Personal.objects.count()
        # ahora las amonestaciones están dentro de Personal
        amon_count = Personal.objects.filter(amon_estado=True).count()
        Personal.objects.all().delete()
        return JsonResponse({'success': True, 'eliminados': personal_count, 'personal_eliminado': personal_count, 'amonestaciones_eliminadas': amon_count})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
