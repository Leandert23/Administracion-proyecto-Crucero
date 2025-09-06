from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Actividad, ActividadRutinaria, RegistroActividadPago, RegistroActividadRut
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import uuid
import os

# Create your views here.

def entretenimiento_view(request):
    """Vista para mostrar la página de entretenimiento"""

    # Obtener el día seleccionado desde los parámetros GET
    dia_seleccionado = request.GET.get('dia')

    # Obtener todos los días disponibles
    dias_pago = Actividad.objects.values_list('dia_crucero', flat=True).distinct()
    dias_rutinarias = ActividadRutinaria.objects.values_list('dia_crucero', flat=True).distinct()
    dias_disponibles = sorted(set(list(dias_pago) + list(dias_rutinarias)))

    # Filtrar actividades según el día seleccionado y ordenar por ID
    if dia_seleccionado and dia_seleccionado.isdigit():
        dia_seleccionado = int(dia_seleccionado)
        actividades_pago = Actividad.objects.filter(dia_crucero=dia_seleccionado).order_by('id_actividad')
        actividades_rutinarias = ActividadRutinaria.objects.filter(dia_crucero=dia_seleccionado).order_by('id_actividad')
    else:
        # Si no hay día seleccionado, mostrar todas las actividades
        actividades_pago = Actividad.objects.all().order_by('id_actividad')
        actividades_rutinarias = ActividadRutinaria.objects.all().order_by('id_actividad')
        dia_seleccionado = None

    # Combinar ambas listas para mostrar las actividades
    todas_actividades = []

    # Agregar actividades de pago
    for actividad in actividades_pago:
        todas_actividades.append({
            'id': actividad.id_actividad,
            'titulo': actividad.titulo,
            'descripcion': actividad.descripcion,
            'tipo': 'pago',
            'dia_crucero': actividad.dia_crucero,
            'hora_inicio': actividad.hora_inicio,
            'hora_fin': actividad.hora_fin,
            'coste': actividad.coste if hasattr(actividad, 'coste') else None,
            'ubicacion': None,
            'img_src': actividad.img_src if actividad.img_src else None
        })

    # Agregar actividades rutinarias
    for actividad in actividades_rutinarias:
        todas_actividades.append({
            'id': actividad.id_actividad,
            'titulo': actividad.titulo,
            'descripcion': actividad.descripcion,
            'tipo': 'rutinaria',
            'dia_crucero': actividad.dia_crucero,
            'hora_inicio': actividad.hora_inicio,
            'hora_fin': actividad.hora_fin,
            'coste': None,
            'ubicacion': actividad.ubicacion if hasattr(actividad, 'ubicacion') else None,
            'img_src': actividad.img_src if actividad.img_src else None
        })

    # Ordenar actividades por ID
    todas_actividades.sort(key=lambda x: x['id'])

    context = {
        'actividades': todas_actividades,
        'dias_disponibles': dias_disponibles,
        'dia_seleccionado': dia_seleccionado
    }

    return render(request, 'entretenimiento/entretenimiento.html', context)


@csrf_exempt
@require_POST
def registro_view(request):
    """Vista para procesar el registro de actividades"""

    try:
        # Parsear los datos JSON del request
        data = json.loads(request.body)

        # Validar datos requeridos
        required_fields = ['nombre', 'apellido', 'n_habitacion', 'n_personas', 'actividad_id', 'actividad_tipo']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({
                    'success': False,
                    'message': f'El campo {field} es requerido.'
                })

        nombre = data['nombre'].strip()
        apellido = data['apellido'].strip()
        n_habitacion = data['n_habitacion'].strip()
        n_personas = data['n_personas']
        actividad_id = data['actividad_id']
        actividad_tipo = data['actividad_tipo']

        # Convertir n_personas a entero si viene como string
        if isinstance(n_personas, str):
            try:
                n_personas = int(n_personas)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'El número de personas debe ser un número válido.'
                })
        elif not isinstance(n_personas, int):
            return JsonResponse({
                'success': False,
                'message': 'El número de personas debe ser un número entero.'
            })

        # Validar que el número de habitación no esté vacío
        if not n_habitacion:
            return JsonResponse({
                'success': False,
                'message': 'El número de habitación no puede estar vacío.'
            })

        # Validar que el número de personas sea válido
        if n_personas < 1 or n_personas > 6:
            return JsonResponse({
                'success': False,
                'message': 'El número de personas debe estar entre 1 y 6.'
            })

        # Convertir actividad_id a entero si viene como string
        if isinstance(actividad_id, str):
            try:
                actividad_id = int(actividad_id)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'El ID de actividad debe ser un número válido.'
                })

        # Obtener la actividad según el tipo
        if actividad_tipo == 'pago':
            try:
                actividad = Actividad.objects.get(id_actividad=actividad_id)

                # Verificar que la actividad tenga un costo válido
                if actividad.coste is None or actividad.coste <= 0:
                    return JsonResponse({
                        'success': False,
                        'message': 'La actividad seleccionada no tiene un precio válido.'
                    })

                # Calcular monto total basado en el costo de la actividad
                monto_total = float(actividad.coste) * n_personas

                # Generar ID de factura único
                id_factura = f"INV-{uuid.uuid4().hex[:8].upper()}"

                # Crear registro de actividad de pago
                registro = RegistroActividadPago.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    n_habitacion=n_habitacion,
                    n_personas=n_personas,
                    monto_total=monto_total,
                    estado='pendiente',
                    id_factura=id_factura
                )

                mensaje = f"Registro creado exitosamente. Su ID de factura es: {id_factura}"

            except Actividad.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'La actividad seleccionada no existe.'
                })
            except Exception as e:
                print(f"Error al crear registro de pago: {e}")
                return JsonResponse({
                    'success': False,
                    'message': 'Error al procesar el registro de pago.'
                })

        elif actividad_tipo == 'rutinaria':
            try:
                actividad = ActividadRutinaria.objects.get(id_actividad=actividad_id)

                # Crear registro de actividad rutinaria
                registro = RegistroActividadRut.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    n_habitacion=n_habitacion,
                    n_personas=n_personas
                )

                mensaje = "Registro de actividad rutinaria creado exitosamente."

            except ActividadRutinaria.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'La actividad seleccionada no existe.'
                })
            except Exception as e:
                print(f"Error al crear registro rutinario: {e}")
                return JsonResponse({
                    'success': False,
                    'message': 'Error al procesar el registro de actividad rutinaria.'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Tipo de actividad no válido.'
            })

        return JsonResponse({
            'success': True,
            'message': mensaje,
            'registro_id': registro.id
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Datos JSON inválidos.'
        })

    except Exception as e:
        print(f"Error en registro_view: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Ocurrió un error interno. Por favor, intente nuevamente.'
        })
