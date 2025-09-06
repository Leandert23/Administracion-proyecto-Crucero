from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Actividad, ActividadRutinaria, RegistroActividadPago, RegistroActividadRut
from ..cruceros.models import Crucero, Viaje
from ..reservaciones.models import Reserva
from django.db.models import Q
from datetime import timedelta
from apps.cruceros.Services.fecha_general import obtener_fecha_actual
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .utils import cargar_actividades_entretenimiento
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import json
import uuid
import os
from datetime import time
from decimal import Decimal

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


@csrf_exempt
@require_POST
def eliminar_actividades_rutinarias(request):
    """Vista para eliminar todos los registros de actividades rutinarias"""

    try:
        # Verificar que el request sea AJAX
        if not request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Esta vista solo acepta peticiones AJAX.'
            })

        # Contar registros antes de eliminar
        registros_antes = ActividadRutinaria.objects.count()

        # Eliminar todos los registros de actividades rutinarias
        ActividadRutinaria.objects.all().delete()

        # Contar registros después de eliminar
        registros_despues = ActividadRutinaria.objects.count()
        registros_eliminados = registros_antes - registros_despues

        return JsonResponse({
            'success': True,
            'message': f'Se eliminaron {registros_eliminados} actividades rutinarias exitosamente.',
            'registros_eliminados': registros_eliminados
        })

    except Exception as e:
        print(f"Error al eliminar actividades rutinarias: {str(e)}")
        import traceback
        traceback.print_exc()

        return JsonResponse({
            'success': False,
            'message': 'Ocurrió un error al eliminar las actividades rutinarias.'
        })


@csrf_exempt
@require_POST
def eliminar_actividades_pago(request):
    """Vista para eliminar todos los registros de actividades de pago"""

    try:
        # Verificar que el request sea AJAX
        if not request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Esta vista solo acepta peticiones AJAX.'
            })

        # Contar registros antes de eliminar
        registros_antes = Actividad.objects.count()

        # Eliminar todos los registros de actividades de pago
        Actividad.objects.all().delete()

        # Contar registros después de eliminar
        registros_despues = Actividad.objects.count()
        registros_eliminados = registros_antes - registros_despues

        return JsonResponse({
            'success': True,
            'message': f'Se eliminaron {registros_eliminados} actividades de pago exitosamente.',
            'registros_eliminados': registros_eliminados
        })

    except Exception as e:
        print(f"Error al eliminar actividades de pago: {str(e)}")
        import traceback
        traceback.print_exc()

        return JsonResponse({
            'success': False,
            'message': 'Ocurrió un error al eliminar las actividades de pago.'
        })


@csrf_exempt
@require_POST
def cargar_datos_precargados(request, crucero_id):
    """Vista para cargar datos precargados de actividades según el tipo de crucero"""

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

        # Validar que se proporcione el tipo de actividad
        if 'tipo_actividad' not in data:
            return JsonResponse({
                'success': False,
                'message': 'El tipo de actividad es requerido.'
            })

        tipo_actividad = data['tipo_actividad']

        # Validar que el tipo sea válido
        if tipo_actividad not in ['rutinaria', 'pago']:
            return JsonResponse({
                'success': False,
                'message': 'El tipo de actividad debe ser "rutinaria" o "pago".'
            })

        # Obtener el crucero
        try:
            crucero = Crucero.objects.get(pk=crucero_id)
        except Crucero.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'El crucero especificado no existe.'
            })

        # Obtener el viaje activo o en planificación
        viaje = crucero.viajes.filter(estado__in=["planificacion", "activo"]).order_by('fecha_inicio').first()
        if not viaje:
            return JsonResponse({
                'success': False,
                'message': 'No se encontró un viaje activo o en planificación para este crucero.'
            })

        # Llamar a la función para cargar actividades
        try:
            resultado = cargar_actividades_entretenimiento(viaje)

            # Contar actividades creadas según el tipo solicitado
            if tipo_actividad == 'rutinaria':
                actividades_creadas = len(resultado.get('rutinarias', []))
                mensaje = f'Se cargaron {actividades_creadas} actividades rutinarias exitosamente.'
            else:  # tipo_actividad == 'pago'
                actividades_creadas = len(resultado.get('pago', []))
                mensaje = f'Se cargaron {actividades_creadas} actividades de pago exitosamente.'

            return JsonResponse({
                'success': True,
                'message': mensaje,
                'actividades_creadas': actividades_creadas,
                'tipo_crucero': crucero.tipo_crucero,
                'tipo_actividad': tipo_actividad
            })

        except Exception as e:
            print(f"Error al cargar actividades: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': 'Ocurrió un error al cargar las actividades.'
            })

    except Exception as e:
        print(f"Error crítico en cargar_datos_precargados: {str(e)}")
        import traceback
        traceback.print_exc()

        return JsonResponse({
            'success': False,
            'message': 'Ocurrió un error interno del servidor.'
        })


def crear_actividad_rutinaria_view(request, crucero_id):
    """Vista para mostrar el formulario de creación de actividades rutinarias"""

    # Obtener el crucero
    crucero = get_object_or_404(Crucero, pk=crucero_id)

    # Obtener el viaje activo o en planificación
    viaje = crucero.viajes.filter(estado__in=["planificacion", "activo"]).order_by('fecha_inicio').first()

    if request.method == 'POST':
        return crear_actividad_rutinaria_post(request, crucero, viaje)

    context = {
        'crucero': crucero,
        'viaje': viaje,
        'dias_opciones': [(i, f"Día {i}") for i in range(1, 9)],
    }

    return render(request, 'entretenimiento/crear_actividad_rutinaria.html', context)


@csrf_exempt
def crear_actividad_rutinaria_post(request, crucero, viaje):
    """Vista para procesar la creación de actividades rutinarias"""

    try:
        # Validar campos requeridos
        required_fields = ['titulo', 'descripcion', 'dia_crucero', 'hora_inicio', 'hora_fin', 'maximo_actividad', 'ubicacion']
        for field in required_fields:
            if field not in request.POST or not request.POST[field].strip():
                return JsonResponse({
                    'success': False,
                    'message': f'El campo {field.replace("_", " ").title()} es requerido.'
                })

        titulo = request.POST['titulo'].strip()
        descripcion = request.POST['descripcion'].strip()
        dia_crucero = int(request.POST['dia_crucero'])
        hora_inicio_str = request.POST['hora_inicio']
        hora_fin_str = request.POST['hora_fin']
        maximo_actividad = int(request.POST['maximo_actividad'])
        ubicacion = request.POST['ubicacion'].strip()

        # Validar rangos
        if dia_crucero < 1 or dia_crucero > 8:
            return JsonResponse({
                'success': False,
                'message': 'El día del crucero debe estar entre 1 y 8.'
            })

        if maximo_actividad < 0:
            return JsonResponse({
                'success': False,
                'message': 'El máximo de participantes debe ser mayor o igual a 0.'
            })

        # Convertir horas y validar minutos
        try:
            hora_inicio = time.fromisoformat(hora_inicio_str)
            hora_fin = time.fromisoformat(hora_fin_str)

            # Validar que los minutos estén entre 0 y 59
            if hora_inicio.minute < 0 or hora_inicio.minute > 59:
                return JsonResponse({
                    'success': False,
                    'message': 'Los minutos de la hora de inicio deben estar entre 00 y 59.'
                })

            if hora_fin.minute < 0 or hora_fin.minute > 59:
                return JsonResponse({
                    'success': False,
                    'message': 'Los minutos de la hora de fin deben estar entre 00 y 59.'
                })

            # Validar que la hora de fin sea al menos 30 minutos después de la hora de inicio
            minutos_inicio = hora_inicio.hour * 60 + hora_inicio.minute
            minutos_fin = hora_fin.hour * 60 + hora_fin.minute

            if minutos_fin < minutos_inicio + 30:
                return JsonResponse({
                    'success': False,
                    'message': 'La hora de fin debe ser al menos 30 minutos después de la hora de inicio.'
                })

        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de hora inválido. Use HH:MM.'
            })

        # Manejar la imagen si se subió
        img_src = None
        if 'imagen' in request.FILES:
            imagen = request.FILES['imagen']

            # Validar formato JPG
            if not imagen.content_type == 'image/jpeg':
                return JsonResponse({
                    'success': False,
                    'message': 'Solo se permiten imágenes en formato JPG.'
                })

            # Validar tamaño máximo 500KB
            if imagen.size > 500 * 1024:  # 500KB en bytes
                return JsonResponse({
                    'success': False,
                    'message': 'La imagen no puede superar los 500KB.'
                })

            # Generar nombre único para la imagen
            extension = os.path.splitext(imagen.name)[1]
            nombre_unico = f"{uuid.uuid4().hex}{extension}"

            # Guardar la imagen
            file_path = os.path.join('img', nombre_unico)
            file_name = default_storage.save(file_path, ContentFile(imagen.read()))

            # Guardar solo el nombre del archivo en img_src
            img_src = nombre_unico

        # Crear la actividad rutinaria
        actividad = ActividadRutinaria.objects.create(
            viaje=viaje,
            titulo=titulo,
            descripcion=descripcion,
            dia_crucero=dia_crucero,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            maximo_actividad=maximo_actividad,
            ubicacion=ubicacion,
            img_src=img_src
        )

        return JsonResponse({
            'success': True,
            'message': f'Actividad rutinaria "{titulo}" creada exitosamente.',
            'actividad_id': actividad.id_actividad
        })

    except Exception as e:
        print(f"Error al crear actividad rutinaria: {str(e)}")
        import traceback
        traceback.print_exc()

        return JsonResponse({
            'success': False,
            'message': 'Ocurrió un error al crear la actividad rutinaria.'
        })


def crear_actividad_pago_view(request, crucero_id):
    """Vista para mostrar y procesar el formulario de creación de actividades de pago"""
    crucero = get_object_or_404(Crucero, pk=crucero_id)
    viaje = crucero.viajes.filter(estado__in=["planificacion", "activo"]).order_by('fecha_inicio').first()

    if request.method == 'POST':
        return crear_actividad_pago_post(request, crucero_id)

    context = {
        'crucero': crucero,
        'viaje': viaje,
        'tipo_actividad': 'pago'
    }

    return render(request, 'entretenimiento/crear_actividad_pago.html', context)


def crear_actividad_pago_post(request, crucero_id):
    """Vista para procesar la creación de actividades de pago"""

    try:
        # Obtener crucero y viaje
        crucero = get_object_or_404(Crucero, pk=crucero_id)
        viaje = crucero.viajes.filter(estado__in=["planificacion", "activo"]).order_by('fecha_inicio').first()

        if not viaje:
            return JsonResponse({
                'success': False,
                'message': 'No se encontró un viaje activo o en planificación para este crucero.'
            })
        # Validar datos requeridos
        required_fields = ['titulo', 'descripcion', 'dia_crucero', 'coste', 'hora_inicio', 'hora_fin', 'maximoActividad']
        for field in required_fields:
            if field not in request.POST or not request.POST[field].strip():
                return JsonResponse({
                    'success': False,
                    'message': f'El campo {field} es requerido.'
                })

        # Extraer datos del formulario
        titulo = request.POST['titulo'].strip()
        descripcion = request.POST['descripcion'].strip()
        dia_crucero = int(request.POST['dia_crucero'])
        coste_str = request.POST['coste'].strip()
        hora_inicio_str = request.POST['hora_inicio']
        hora_fin_str = request.POST['hora_fin']
        maximoActividad = int(request.POST['maximoActividad'])

        # Validar y convertir coste
        try:
            coste = Decimal(coste_str)
            if coste < 0:
                return JsonResponse({
                    'success': False,
                    'message': 'El coste debe ser mayor o igual a 0.'
                })
        except (ValueError, Decimal.InvalidOperation):
            return JsonResponse({
                'success': False,
                'message': 'El coste debe ser un número válido.'
            })

        # Validar rangos
        if dia_crucero < 1 or dia_crucero > 8:
            return JsonResponse({
                'success': False,
                'message': 'El día del crucero debe estar entre 1 y 8.'
            })

        if maximoActividad < 0:
            return JsonResponse({
                'success': False,
                'message': 'El máximo de participantes debe ser mayor o igual a 0.'
            })

        # Convertir horas y validar minutos
        try:
            hora_inicio = time.fromisoformat(hora_inicio_str)
            hora_fin = time.fromisoformat(hora_fin_str)

            # Validar que los minutos estén entre 0 y 59
            if hora_inicio.minute < 0 or hora_inicio.minute > 59:
                return JsonResponse({
                    'success': False,
                    'message': 'Los minutos de la hora de inicio deben estar entre 00 y 59.'
                })

            if hora_fin.minute < 0 or hora_fin.minute > 59:
                return JsonResponse({
                    'success': False,
                    'message': 'Los minutos de la hora de fin deben estar entre 00 y 59.'
                })

            # Validar que la hora de fin sea al menos 30 minutos después de la hora de inicio
            minutos_inicio = hora_inicio.hour * 60 + hora_inicio.minute
            minutos_fin = hora_fin.hour * 60 + hora_fin.minute

            if minutos_fin < minutos_inicio + 30:
                return JsonResponse({
                    'success': False,
                    'message': 'La hora de fin debe ser al menos 30 minutos después de la hora de inicio.'
                })

        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Formato de hora inválido. Use HH:MM.'
            })

        # Validar imagen si se proporciona
        img_src = None
        if 'imagen' in request.FILES:
            imagen = request.FILES['imagen']

            # Validar tipo de archivo
            if not imagen.content_type in ['image/jpeg', 'image/jpg']:
                return JsonResponse({
                    'success': False,
                    'message': 'Solo se permiten imágenes JPG.'
                })

            # Validar tamaño (500KB máximo)
            if imagen.size > 500 * 1024:
                return JsonResponse({
                    'success': False,
                    'message': 'La imagen debe ser menor a 500KB.'
                })

            # Generar nombre único para la imagen
            extension = os.path.splitext(imagen.name)[1]
            nombre_unico = f"{uuid.uuid4().hex}{extension}"

            # Guardar la imagen
            file_path = os.path.join('img', nombre_unico)
            file_name = default_storage.save(file_path, ContentFile(imagen.read()))

            # Guardar solo el nombre del archivo en img_src
            img_src = nombre_unico

        # Crear la actividad de pago
        actividad = Actividad.objects.create(
            viaje=viaje,
            titulo=titulo,
            descripcion=descripcion,
            dia_crucero=dia_crucero,
            coste=coste,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            maximoActividad=maximoActividad,
            img_src=img_src
        )

        return JsonResponse({
            'success': True,
            'message': f'Actividad de pago "{titulo}" creada exitosamente.',
            'actividad_id': actividad.id_actividad
        })

    except Exception as e:
        print(f"Error al crear actividad de pago: {str(e)}")
        import traceback
        traceback.print_exc()

        return JsonResponse({
            'success': False,
            'message': 'Ocurrió un error al crear la actividad de pago.'
        })


@csrf_exempt
def api_get_activities(request, crucero_id):
    """Vista API para obtener todas las actividades de un crucero"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})

    try:
        # Obtener crucero y viaje
        crucero = get_object_or_404(Crucero, pk=crucero_id)
        viaje = crucero.viajes.filter(estado__in=["planificacion", "activo"]).order_by('fecha_inicio').first()

        if not viaje:
            return JsonResponse({
                'success': False,
                'message': 'No se encontró un viaje activo o en planificación para este crucero.'
            })

        activities_data = []

        # Obtener actividades de pago
        actividades_pago = Actividad.objects.filter(viaje=viaje).order_by('dia_crucero', 'hora_inicio')
        for actividad in actividades_pago:
            activities_data.append({
                'id_actividad': actividad.id_actividad,
                'titulo': actividad.titulo,
                'descripcion': actividad.descripcion,
                'dia_crucero': actividad.dia_crucero,
                'hora_inicio': str(actividad.hora_inicio),
                'hora_fin': str(actividad.hora_fin),
                'maximo_participantes': actividad.maximoActividad,
                'coste': str(actividad.coste) if actividad.coste else None,
                'ubicacion': None,
                'img_src': actividad.img_src,
                'type': 'pago'
            })

        # Obtener actividades rutinarias
        actividades_rutinarias = ActividadRutinaria.objects.filter(viaje=viaje).order_by('dia_crucero', 'hora_inicio')
        for actividad in actividades_rutinarias:
            activities_data.append({
                'id_actividad': actividad.id_actividad,
                'titulo': actividad.titulo,
                'descripcion': actividad.descripcion,
                'dia_crucero': actividad.dia_crucero,
                'hora_inicio': str(actividad.hora_inicio),
                'hora_fin': str(actividad.hora_fin),
                'maximo_participantes': actividad.maximo_actividad,
                'coste': None,
                'ubicacion': actividad.ubicacion,
                'img_src': actividad.img_src,
                'type': 'rutinaria'
            })

        return JsonResponse({
            'success': True,
            'activities': activities_data,
            'total': len(activities_data)
        })

    except Exception as e:
        print(f"Error al obtener actividades: {str(e)}")
        import traceback
        traceback.print_exc()

        return JsonResponse({
            'success': False,
            'message': 'Ocurrió un error al obtener las actividades.'
        })


@csrf_exempt
def api_delete_activity(request, crucero_id):
    """Vista API para eliminar una actividad específica"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})

    try:
        import json
        data = json.loads(request.body)
        activity_id = data.get('activity_id')
        activity_type = data.get('activity_type')

        if not activity_id or not activity_type:
            return JsonResponse({
                'success': False,
                'message': 'ID de actividad y tipo son requeridos.'
            })

        # Obtener crucero y viaje
        crucero = get_object_or_404(Crucero, pk=crucero_id)
        viaje = crucero.viajes.filter(estado__in=["planificacion", "activo"]).order_by('fecha_inicio').first()

        if not viaje:
            return JsonResponse({
                'success': False,
                'message': 'No se encontró un viaje activo o en planificación para este crucero.'
            })

        # Eliminar la actividad según su tipo
        if activity_type == 'pago':
            actividad = get_object_or_404(Actividad, id_actividad=activity_id, viaje=viaje)
            actividad.delete()
            message = f'Actividad de pago "{actividad.titulo}" eliminada exitosamente.'

        elif activity_type == 'rutinaria':
            actividad = get_object_or_404(ActividadRutinaria, id_actividad=activity_id, viaje=viaje)
            actividad.delete()
            message = f'Actividad rutinaria "{actividad.titulo}" eliminada exitosamente.'

        else:
            return JsonResponse({
                'success': False,
                'message': 'Tipo de actividad no válido.'
            })

        return JsonResponse({
            'success': True,
            'message': message
        })

    except Actividad.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Actividad de pago no encontrada.'
        })

    except ActividadRutinaria.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Actividad rutinaria no encontrada.'
        })

    except Exception as e:
        print(f"Error al eliminar actividad: {str(e)}")
        import traceback
        traceback.print_exc()

        return JsonResponse({
            'success': False,
            'message': 'Ocurrió un error al eliminar la actividad.'
        })


def api_get_reservas(request, crucero_id):
    """Vista API para obtener todas las reservas relacionadas con actividades de entretenimiento"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})

    try:
        # Obtener crucero y viaje
        crucero = get_object_or_404(Crucero, pk=crucero_id)
        viaje = crucero.viajes.filter(estado__in=["planificacion", "activo"]).order_by('fecha_inicio').first()

        if not viaje:
            return JsonResponse({
                'success': False,
                'message': 'No se encontró un viaje activo o en planificación para este crucero.'
            })

        reservas_data = []

        # Obtener reservas de actividades de pago
        reservas_pago = Reserva.objects.filter(
            actividad_pago__viaje=viaje,
            actividad_pago__isnull=False
        ).select_related('actividad_pago').order_by('-fecha_creacion')

        for reserva in reservas_pago:
            reservas_data.append({
                'id': reserva.id,
                'nombre': reserva.nombre_cliente or '',
                'apellido': reserva.apellido_cliente or '',
                'n_habitacion': reserva.codigo_ubicacion_habitacion or '',
                'n_personas': reserva.numero_personas,
                'fecha_reserva': reserva.fecha_creacion.strftime('%Y-%m-%d'),
                'hora_reserva': reserva.fecha_creacion.strftime('%H:%M'),
                'dia_actividad': reserva.actividad_pago.dia_crucero,
                'nombre_actividad': reserva.actividad_pago.titulo,
                'tipo_actividad': 'pago',
                'coste': str(reserva.actividad_pago.coste) if reserva.actividad_pago.coste else None,
                'ubicacion': None,
                'descripcion_actividad': reserva.actividad_pago.descripcion
            })

        # Obtener reservas de actividades rutinarias
        reservas_rutinarias = Reserva.objects.filter(
            actividad_rutinaria__viaje=viaje,
            actividad_rutinaria__isnull=False
        ).select_related('actividad_rutinaria').order_by('-fecha_creacion')

        for reserva in reservas_rutinarias:
            reservas_data.append({
                'id': reserva.id,
                'nombre': reserva.nombre_cliente or '',
                'apellido': reserva.apellido_cliente or '',
                'n_habitacion': reserva.codigo_ubicacion_habitacion or '',
                'n_personas': reserva.numero_personas,
                'fecha_reserva': reserva.fecha_creacion.strftime('%Y-%m-%d'),
                'hora_reserva': reserva.fecha_creacion.strftime('%H:%M'),
                'dia_actividad': reserva.actividad_rutinaria.dia_crucero,
                'nombre_actividad': reserva.actividad_rutinaria.titulo,
                'tipo_actividad': 'rutinaria',
                'coste': None,
                'ubicacion': reserva.actividad_rutinaria.ubicacion,
                'descripcion_actividad': reserva.actividad_rutinaria.descripcion
            })

        # Ordenar por fecha de creación (más recientes primero)
        reservas_data.sort(key=lambda x: x['fecha_reserva'] + ' ' + x['hora_reserva'], reverse=True)

        return JsonResponse({
            'success': True,
            'reservas': reservas_data,
            'total': len(reservas_data)
        })

    except Exception as e:
        print(f"Error al obtener reservas: {str(e)}")
        import traceback
        traceback.print_exc()

        return JsonResponse({
            'success': False,
            'message': 'Ocurrió un error al obtener las reservas.'
        })