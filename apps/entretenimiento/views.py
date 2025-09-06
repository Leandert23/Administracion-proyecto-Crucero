from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Actividad, ActividadRutinaria, RegistroActividadPago, RegistroActividadRut
from ..cruceros.models import Crucero, Viaje
from django.db.models import Q
from datetime import timedelta
from apps.cruceros.Services.fecha_general import obtener_fecha_actual
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
import os

# Create your views here.

def entretenimiento_view(request, crucero_id):
    """Vista para mostrar la página de entretenimiento de un crucero específico.
    Filtra actividades por el viaje activo o en planificación del crucero.
    """
    
    # Esto se agregó para solo mostrar las actividades de un crucero específico, así se diferencia entre pequeño, mediano, grande
    crucero = get_object_or_404(Crucero, pk=crucero_id)
    viaje = crucero.viajes.filter(estado__in=["planificacion", "activo"]).order_by('fecha_inicio').first()
    # Obtener fecha del sistema (creando registro si no existe)
    fecha_actual_sistema = obtener_fecha_actual()
    if not fecha_actual_sistema:
        try:
            fecha_actual_sistema = obtener_fecha_actual().fecha_actual
        except Exception:
            fecha_actual_sistema = None

    # Obtener el día seleccionado desde los parámetros GET
    dia_seleccionado = request.GET.get('dia')

    # Base queryset filtrada por viaje si existe
    actividades_base = Actividad.objects.filter(viaje=viaje) if viaje else Actividad.objects.none()
    rutinarias_base = ActividadRutinaria.objects.filter(viaje=viaje) if viaje else ActividadRutinaria.objects.none()

    dias_pago = actividades_base.values_list('dia_crucero', flat=True).distinct()
    dias_rutinarias = rutinarias_base.values_list('dia_crucero', flat=True).distinct()
    dias_disponibles = sorted(set(list(dias_pago) + list(dias_rutinarias)))

    fecha_dia_seleccionado = None
    if dia_seleccionado and dia_seleccionado.isdigit():
        dia_seleccionado = int(dia_seleccionado)
        actividades_pago = actividades_base.filter(dia_crucero=dia_seleccionado).order_by('id_actividad')
        actividades_rutinarias = rutinarias_base.filter(dia_crucero=dia_seleccionado).order_by('id_actividad')
        if viaje and viaje.fecha_inicio:
            try:
                fecha_dia_seleccionado = viaje.fecha_inicio + timedelta(days=dia_seleccionado - 1)
            except Exception:
                fecha_dia_seleccionado = None
    else:
        actividades_pago = actividades_base.order_by('id_actividad')
        actividades_rutinarias = rutinarias_base.order_by('id_actividad')
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
        'dia_seleccionado': dia_seleccionado,
        'fecha_actual_sistema': fecha_actual_sistema,
        'fecha_dia_seleccionado': fecha_dia_seleccionado,
        'crucero': crucero,
        'viaje': viaje,
    }

    return render(request, 'entretenimiento/entretenimiento.html', context)


@csrf_exempt
@require_POST
def registro_view(request):
    """Vista para procesar el registro de actividades"""

    # Asegurar que siempre devolvamos JSON
    try:
        # Verificar que el request sea AJAX
        if not request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Esta vista solo acepta peticiones AJAX.'
            })

        # Parsear los datos JSON del request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Los datos enviados no son un JSON válido.'
            })

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

        # Validar que nombre y apellido no estén vacíos después de strip
        if not nombre:
            return JsonResponse({
                'success': False,
                'message': 'El nombre no puede estar vacío.'
            })

        if not apellido:
            return JsonResponse({
                'success': False,
                'message': 'El apellido no puede estar vacío.'
            })

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

                # Obtener viaje desde la actividad
                viaje = actividad.viaje
                if not viaje:
                    return JsonResponse({
                        'success': False,
                        'message': 'La actividad no está asociada a un viaje válido.'
                    })

                # Calcular monto total basado en el costo de la actividad
                monto_total = float(actividad.coste) * n_personas

                # Generar ID de factura único
                id_factura = f"INV-{uuid.uuid4().hex[:8].upper()}"

                # Crear registro de actividad de pago enlazado al viaje
                registro = RegistroActividadPago.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    n_habitacion=n_habitacion,
                    n_personas=n_personas,
                    monto_total=monto_total,
                    estado='pendiente',
                    id_factura=id_factura,
                    viaje=viaje
                )

                mensaje = f"Registro creado exitosamente. Su ID de factura es: {id_factura}"

            except Actividad.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'La actividad seleccionada no existe.'
                })
            except Exception as e:
                print(f"Error al crear registro de pago: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': 'Error al procesar el registro de pago.'
                })

        elif actividad_tipo == 'rutinaria':
            try:
                actividad = ActividadRutinaria.objects.get(id_actividad=actividad_id)

                viaje = actividad.viaje
                if not viaje:
                    return JsonResponse({
                        'success': False,
                        'message': 'La actividad no está asociada a un viaje válido.'
                    })

                # Crear registro de actividad rutinaria enlazado al viaje
                registro = RegistroActividadRut.objects.create(
                    nombre=nombre,
                    apellido=apellido,
                    n_habitacion=n_habitacion,
                    n_personas=n_personas,
                    viaje=viaje
                )

                mensaje = "Registro de actividad rutinaria creado exitosamente."

            except ActividadRutinaria.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'La actividad seleccionada no existe.'
                })
            except Exception as e:
                print(f"Error al crear registro rutinario: {str(e)}")
                return JsonResponse({
                    'success': False,
                    'message': 'Error al procesar el registro de actividad rutinaria.'
                })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Tipo de actividad no válido. Debe ser "pago" o "rutinaria".'
            })

        return JsonResponse({
            'success': True,
            'message': mensaje,
            'registro_id': registro.id if 'registro' in locals() else None,
            'viaje_id': registro.viaje.id if hasattr(registro, 'viaje') and registro.viaje else None
        })

    except Exception as e:
        # Capturar cualquier error inesperado
        print(f"Error crítico en registro_view: {str(e)}")
        import traceback
        traceback.print_exc()

        return JsonResponse({
            'success': False,
            'message': 'Ocurrió un error interno del servidor. Por favor, contacte al administrador.'
        })
