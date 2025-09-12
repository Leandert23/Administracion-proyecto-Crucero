from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Personal, Amonestacion
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Sum, Count
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
            pStatus = request.POST.get('pStatus')

            personal = Personal(
                nombre=nombre,
                apellido=apellido,
                salario=int(salario) if salario else 0,
                edad=int(edad) if edad else 0,
                anios_experiencia=int(anios_experiencia) if anios_experiencia else 0,
                categoria=categoria,
                puesto=puesto,
                pStatus=int(pStatus) if pStatus else 1,
            )

            personal.full_clean()  # Invoca validaciones
            personal.save()
            return redirect('index')

        except (ValidationError, ValueError, IntegrityError) as e:
            error_message = str(e)

    # Obtener todos los objetos Personal para mostrar
    personal_list = Personal.objects.select_related('amonestacion').all()

    # Calcular estadísticas
    total_salarios = Personal.objects.aggregate(total=Sum('salario'))['total'] or 0
    personal_activo = Personal.objects.filter(pStatus=1).count()
    personal_inactivo = Personal.objects.filter(pStatus=2).count()
    personal_de_baja = Personal.objects.filter(pStatus=3).count()
    personal_amonestado = Amonestacion.objects.filter(estado=True).count()

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

        # Eliminar amonestación relacionada si existe
        Amonestacion.objects.filter(personal=personal).delete()
        personal.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def personal_update(request, pk):
    try:
        # Aceptamos JSON o form-data
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

        personal.salario = salario
        personal.categoria = categoria
        personal.puesto = puesto
        personal.pStatus = pStatus
        personal.full_clean()
        personal.save()

        # Amonestacion: interpretar correctamente booleanos y strings que representen true/false
        amon = data.get('amonestacion') or {}
        estado_raw = amon.get('estado') if isinstance(amon, dict) else data.get('amonestacion_estado')
        detalle = amon.get('detalle') if isinstance(amon, dict) else data.get('amonestacion_detalle')

        # Normalizar a booleano
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

        if estado_bool:
            # Guardar o actualizar amonestación respetando el estado (True)
            Amonestacion.objects.update_or_create(personal=personal, defaults={'estado': True, 'detalle': detalle or ''})
        else:
            # Eliminar amonestación si existe o mantenerla inactiva
            Amonestacion.objects.filter(personal=personal).delete()

        # Preparar respuesta con datos actualizados
        amon_obj = Amonestacion.objects.filter(personal=personal).first()
        response = {
            'id': personal.id,
            'salario': personal.salario,
            'edad': personal.edad,
            'anios_experiencia': personal.anios_experiencia,
            'categoria': personal.categoria,
            'puesto': personal.puesto,
            'pStatus': personal.pStatus,
            'amonestacion': {
                'estado': amon_obj.estado if amon_obj else False,
                'detalle': amon_obj.detalle if amon_obj else ''
            }
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
        data = json.loads(request.body) if request.body else {}
        cantidad = int(data.get('cantidad', 0))

        if cantidad not in [630, 1300, 1950]:
            return JsonResponse({'error': 'Cantidad inválida. Debe ser 630, 1300 o 1950.'}, status=400)

        # Prioridades: Mantenimiento, Culinario, Entretenimiento, Medico, Administrativo
        prioridades = [
            ('Mantenimiento', 30),
            ('Culinario', 25),
            ('Entretenimiento', 20),
            ('Medico', 15),
            ('Administrativo', 10),
        ]

        # Puestos por categoria (lista simplificada)
        puestos_por_categoria = {
            'Mantenimiento': ['Plomero', 'Ingeniero', 'Conserje', 'Tecnico'],
            'Culinario': ['Cocinero', 'Mesero', 'Chef', 'Barista', 'Repostero', 'Bartender'],
            'Entretenimiento': ['Animadores', "DJ's", 'Musicos', 'Bailarines', 'Guias Turisticos'],
            'Medico': ['Enfermero', 'Medico General', 'Medico en Jefe', 'Paramedico'],
            'Administrativo': ['Gerente', 'Cajero']
        }

        # Excluir ciertos puestos de generación genérica
        exclusiones = {'Chef', 'Medico en Jefe', 'Doctor Especialista', 'Guias Turisticos', 'Ingeniero', 'Gerente', 'Plomero', 'Musicos'}

        # Intentar obtener listas desde tablas opcionales (si el proyecto las contiene), sino usar fallback en memoria
        try:
            # Modelos opcionales que podrían existir: NombrePool, ApellidoPool, SalarioOption
            from .models import NombrePool, ApellidoPool, SalarioOption
            nombres = list(NombrePool.objects.values_list('nombre', flat=True)) or []
            apellidos = list(ApellidoPool.objects.values_list('apellido', flat=True)) or []
            salarios_permitidos = list(SalarioOption.objects.values_list('salario', flat=True)) or [s for s in range(800, 3001, 250)]
        except Exception:
            nombres = ['Ana','Luis','Jose','Maria','Pablo','Carmen','Juan','Marta','Diego','Laura','Raul','Nora','Elena','Carlos','Sofia','Pedro','Lucia','Andres','Rosa','Victor']
            apellidos = ['Garcia','Martinez','Lopez','Hernandez','Gonzalez','Perez','Sanchez','Ramirez','Torres','Flores','Diaz','Vargas','Rojas','Castro','Ortega','Molina','Silva','Cruz','Herrera','Mendez']
            salarios_permitidos = [s for s in range(800, 3001, 250)]

        # Calcular distribución
        distribucion = {}
        restantes = cantidad
        for categoria, porcentaje in prioridades:
            asignados = int(cantidad * porcentaje / 100)
            distribucion[categoria] = asignados
            restantes -= asignados
        if restantes > 0:
            distribucion['Mantenimiento'] = distribucion.get('Mantenimiento', 0) + restantes

        creados = 0
        errores = []

        for categoria, num in distribucion.items():
            puestos = puestos_por_categoria.get(categoria, [])
            for i in range(num):
                try:
                    nombre = random.choice(nombres)[:10].capitalize()
                    apellido = random.choice(apellidos)[:10].capitalize()
                    puesto = random.choice(puestos) if puestos else 'No Ocupado'
                    # Si el puesto está en exclusiones, saltarlo y elegir otro puesto común
                    if puesto in exclusiones:
                        # elegir un puesto alternativo no excluido dentro de la categoria
                        puestos_alt = [p for p in puestos if p not in exclusiones]
                        puesto = random.choice(puestos_alt) if puestos_alt else 'No Ocupado'

                    salario = random.choice(salarios_permitidos)
                    # Edad apropiada para un trabajador de crucero
                    edad = random.randint(21, 65)
                    # Años de experiencia deben ser coherentes: no más de la mitad de la edad y limitar razonablemente (p.ej. 40)
                    max_exp = max(0, edad // 2)
                    anios_experiencia = random.randint(0, min(max_exp, 40))

                    personal = Personal(
                        nombre=nombre,
                        apellido=apellido,
                        salario=salario,
                        edad=edad,
                        anios_experiencia=anios_experiencia,
                        categoria=categoria,
                        puesto=puesto,
                        pStatus=1,
                    )
                    personal.full_clean()
                    personal.save()
                    creados += 1
                except Exception as e:
                    errores.append(str(e))
                    continue

        return JsonResponse({'success': True, 'creados': creados, 'created_count': creados, 'distribucion': distribucion, 'errores': errores})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def vaciar_plantel(request):
    try:
        personal_count = Personal.objects.count()
        amon_count = Amonestacion.objects.count()
        Amonestacion.objects.all().delete()
        Personal.objects.all().delete()
        return JsonResponse({'success': True, 'eliminados': personal_count + amon_count, 'personal_eliminado': personal_count, 'amonestaciones_eliminadas': amon_count})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
