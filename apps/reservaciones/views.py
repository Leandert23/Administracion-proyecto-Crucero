from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta, date
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import (
    Entretenimiento,
    Mesa,
    EventoPersonalizado,
    Reserva,
    Restaurante
)
from ..cruceros.models import Crucero, Habitacion, TipoHabitacion, Viaje
from ..entretenimiento.models import Actividad, ActividadRutinaria
from ..cruceros.Services.fecha_general import obtener_fecha_actual
import json

def crucero_se_encuentra_en_planificacion():
    return True  # Aquí después vendrá la lógica real del otro módulo

# PÁGINAS PRINCIPALES

def inicio(request):
    return render(request, "App/inicio")


def reservas(request, crucero=None):
    # Si la URL pasa el nombre del crucero, se usa ese; si no, se intenta por GET o sesión
    crucero_nombre = crucero or request.GET.get("crucero") or request.session.get("crucero_seleccionado")
    crucero_obj = None
    if crucero_nombre:
        crucero_obj = Crucero.objects.filter(nombre=crucero_nombre).first()
        request.session["crucero_seleccionado"] = crucero_nombre
    viaje = Viaje.objects.filter(crucero=crucero_obj, estado="activo").first() if crucero_obj else None

    return render(request, "App/reservas.html", {
        "crucero": crucero_obj,
        "viaje": viaje,
    })

# HABITACIONES

#@login_required
def reservacion_habitaciones(request, crucero):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    viaje = Viaje.objects.filter(crucero=crucero_obj, estado="planificacion").first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero_obj})

    if not crucero_obj.se_encuentra_en_planificacion:
        messages.warning(request, "Ya no puedes reservar habitaciones, el crucero zarpó.")
        return redirect("reservas")

    habitaciones = Habitacion.objects.filter(
        crucero=crucero_obj,
        reservada=False
    ).order_by("tipo_habitacion__precio_base")

    return render(request, "App/reservacion_habitaciones.html", {
        "habitaciones": habitaciones,
        "viaje": viaje,
        "crucero": crucero_obj,
    })


#@login_required
def reservar_habitacion(request, crucero, habitacion_id):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    viaje = Viaje.objects.filter(crucero=crucero_obj, estado="planificacion").first()
    habitacion = get_object_or_404(Habitacion, id=habitacion_id, crucero=crucero_obj)

    if not habitacion.reservada:
        fecha_inicio = viaje.fecha_inicio
        fecha_fin = viaje.fecha_fin

        Reserva.objects.create(
            habitacion=habitacion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado="confirmada",
        )

        habitacion.reservada = True
        habitacion.save()

        return redirect("mis_reservas", crucero=crucero)

    return redirect("reservacion_habitaciones", crucero=crucero)

# ENTRETENIMIENTO

#@login_required
def catalogo_entretenimiento(request, crucero):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    viaje = Viaje.objects.filter(crucero=crucero_obj, estado__in=["activo", "planificacion"]).first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero_obj})

    if crucero_obj.se_encuentra_en_planificacion:
        return render(request, "App/no_viaje.html", {"crucero": crucero_obj})
    else:
        actividades = Entretenimiento.objects.filter(
            crucero=crucero_obj,
            dia=crucero_obj.dia_actual_de_viaje,
            reservada=False
        ).order_by("precio")

    return render(request, "App/catalogo_entretenimiento.html", {
        "actividades": actividades,
        "viaje": viaje,
        "crucero": crucero_obj,
    })


#@login_required
def reservar_entretenimiento(request, crucero, entretenimiento_id):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    actividad = get_object_or_404(Entretenimiento, id=entretenimiento_id, crucero=crucero_obj)

    if not actividad.reservada:
        Reserva.objects.create(
            entretenimientoP=actividad,
            costo=actividad.precio,
            estado="confirmada",
        )
        actividad.reservada = True
        actividad.save()

    return redirect("mis_reservas", crucero=crucero)

# MESAS (Restaurantes)

#@login_required
def reservar_restaurante(request, crucero):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    restaurantes = Restaurante.objects.filter(crucero=crucero_obj)

    viaje = Viaje.objects.filter(crucero=crucero_obj, estado__in=["activo", "planificacion"]).first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero_obj})

    if crucero_obj.se_encuentra_en_planificacion:
        return render(request, "App/no_viaje.html", {"crucero": crucero_obj})
    else:
        return render(request, "App/reservar_restaurante.html", {
        "restaurantes": restaurantes,
        "crucero": crucero_obj,
    })


#@login_required
def primer_restaurante(request, crucero):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    mesas = Mesa.objects.filter(crucero=crucero_obj, restaurante__nombre="L'odissea della Toscana", reservada=False)
    viaje = Viaje.objects.filter(crucero=crucero_obj).first()

    return render(request, "App/primer_restaurante.html", {
        "mesas": mesas,
        "crucero": crucero_obj,
        "viaje": viaje,
    })


#@login_required
def segundo_restaurante(request, crucero):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    mesas = Mesa.objects.filter(crucero=crucero_obj, restaurante__nombre="Odessa Al-Bahr", reservada=False)
    viaje = Viaje.objects.filter(crucero=crucero_obj).first()

    return render(request, "App/segundo_restaurante.html", {
        "mesas": mesas,
        "crucero": crucero_obj,
        "viaje": viaje,
    })

#@login_required
def reservar_mesa(request, crucero, mesa_id):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    mesa = get_object_or_404(Mesa, id=mesa_id, crucero=crucero_obj)

    if not mesa.reservada:
        Reserva.objects.create(
            mesa=mesa,
            estado="confirmada",
        )
        mesa.reservada = True
        mesa.save()

    return redirect("mis_reservas", crucero=crucero)

# EVENTOS PERSONALIZADOS

#@login_required
def organizar_evento(request, crucero):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    viaje = Viaje.objects.filter(crucero=crucero_obj).first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero_obj})

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        materiales = request.POST.get("materiales")
        dia = int(request.POST.get("dia"))

        if crucero_obj.se_encuentra_en_viaje:
            if dia < crucero_obj.dia_actual_de_viaje:
                messages.error(
                    request,
                    f"No puedes organizar eventos para días anteriores al día {crucero.dia_actual_de_viaje}."
                )
                return redirect("organizar_evento", crucero=crucero)

        evento = EventoPersonalizado.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            materiales=materiales,
            dia=dia,
            crucero=crucero_obj,
        )

        Reserva.objects.create(
            evento_personalizado=evento,
            estado="pendiente",
        )

        return redirect("mis_reservas", crucero=crucero)

    dias = range(1, 9)
    viaje = Viaje.objects.filter(crucero=crucero_obj, estado__in=["activo", "planificacion"]).first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero_obj})

    return render(request, "App/organizar_evento.html", {
        "crucero": crucero_obj,
        "viaje": viaje,
        "dias": dias
    })

# MIS RESERVAS

#@login_required
def mis_reservas(request, crucero):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    reservas_habitaciones = Reserva.objects.filter(habitacion__isnull=False, habitacion__crucero=crucero_obj
    )
    reservas_entretenimiento = Reserva.objects.filter(
        (Q(entretenimientoP__isnull=False) & Q(entretenimientoP__crucero=crucero_obj)) |
        (Q(entretenimientoR__isnull=False) & Q(entretenimientoR__crucero=crucero_obj))
    )
    reservas_mesas = Reserva.objects.filter(mesa__isnull=False, mesa__crucero=crucero_obj
    )
    reservas_eventos = Reserva.objects.filter(evento_personalizado__isnull=False, evento_personalizado__crucero=crucero_obj
    )

    total = 0

    for r in reservas_habitaciones:
        total += int(r.habitacion.tipo_habitacion.precio_base)

    for r in reservas_entretenimiento:
        total += int(r.costo)

    for r in reservas_mesas:
        total += int(r.mesa.restaurante.precio) if hasattr(r.mesa.restaurante, "precio") else 40

    for r in reservas_eventos:
        total += 700.00

    return render(request, "App/mis_reservas.html", {
        "crucero": crucero_obj,
        "reservas_habitaciones": reservas_habitaciones,
        "reservas_entretenimiento": reservas_entretenimiento,
        "reservas_mesas": reservas_mesas,
        "reservas_eventos": reservas_eventos,
        "total": total,
    })

# CANCELAR RESERVA

#@login_required
def cancelar_reserva(request, crucero, reserva_id):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if reserva.habitacion:
        reserva.habitacion.reservada = False
        reserva.habitacion.save()

    if reserva.entretenimientoP:
        reserva.entretenimientoP.reservada = False
        reserva.entretenimientoP.save()

    if reserva.entretenimientoR:
        reserva.entretenimientoR.reservada = False
        reserva.entretenimientoR.save()

    if reserva.mesa:
        reserva.mesa.reservada = False
        reserva.mesa.save()

    if reserva.evento_personalizado:
        reserva.evento_personalizado.delete()

    reserva.delete()
    return redirect("mis_reservas", crucero=crucero)

# API ENDPOINTS PARA NUEVA RESERVA

@require_http_methods(["GET"])
def api_tipos_habitacion(request, crucero):
    """API para obtener tipos de habitación disponibles"""
    try:
        crucero_obj = get_object_or_404(Crucero, nombre=crucero)
        tipos = TipoHabitacion.objects.all().values(
            'id', 'nombre', 'capacidad', 'precio_base', 'descripcion'
        )

        return JsonResponse({
            'success': True,
            'tipos': list(tipos)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener tipos de habitación: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def api_habitacion_disponible(request, crucero):
    """API para buscar habitación disponible de un tipo específico"""
    try:
        data = json.loads(request.body)
        tipo_habitacion_id = data.get('tipo_habitacion_id')

        if not tipo_habitacion_id:
            return JsonResponse({
                'success': False,
                'message': 'ID de tipo de habitación requerido'
            })

        crucero_obj = get_object_or_404(Crucero, nombre=crucero)

        # Buscar la primera habitación disponible (reservada=False) del tipo especificado
        habitacion = Habitacion.objects.filter(
            crucero=crucero_obj,
            tipo_habitacion_id=tipo_habitacion_id,
            reservada=False
        ).first()

        if habitacion:
            return JsonResponse({
                'success': True,
                'habitacion': {
                    'id': habitacion.id,
                    'numero': habitacion.numero,
                    'cubierta': habitacion.cubierta,
                    'lado': habitacion.get_lado_display(),
                    'tipo_habitacion': habitacion.tipo_habitacion.nombre,
                    'vista_mar': habitacion.vista_mar
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No hay habitaciones disponibles de este tipo'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al buscar habitación: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def api_crear_reserva(request, crucero):
    """API para crear una nueva reserva"""
    try:
        print(f"DEBUG: Iniciando api_crear_reserva para crucero: {crucero}")
        data = json.loads(request.body)
        print(f"DEBUG: Datos recibidos: {data}")
        crucero_obj = get_object_or_404(Crucero, nombre=crucero)
        print(f"DEBUG: Crucero encontrado: {crucero_obj.nombre}")

        # Validar datos requeridos
        required_fields = ['nombre', 'apellido', 'fecha_nacimiento', 'numero_personas', 'tipo_habitacion_id']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'message': f'Campo requerido faltante: {field}'
                })

        tipo_habitacion_id = data['tipo_habitacion_id']
        numero_personas = data['numero_personas']

        # Verificar que el número de personas no exceda la capacidad del tipo de habitación
        tipo_habitacion = get_object_or_404(TipoHabitacion, id=tipo_habitacion_id)
        if numero_personas > tipo_habitacion.capacidad:
            return JsonResponse({
                'success': False,
                'message': f'El número de personas ({numero_personas}) excede la capacidad del tipo de habitación ({tipo_habitacion.capacidad})'
            })

        # Buscar habitación disponible del tipo especificado
        habitacion = Habitacion.objects.filter(
            crucero=crucero_obj,
            tipo_habitacion_id=tipo_habitacion_id,
            reservada=False
        ).first()

        if not habitacion:
            return JsonResponse({
                'success': False,
                'message': 'No hay habitaciones disponibles de este tipo'
            })

        # Obtener el viaje activo o en planificación
        viaje = Viaje.objects.filter(
            crucero=crucero_obj,
            estado__in=['activo', 'planificacion']
        ).first()

        if not viaje:
            return JsonResponse({
                'success': False,
                'message': 'No hay viaje activo o en planificación para este crucero'
            })

        # Calcular el costo total basado en el precio del tipo de habitación
        costo_total = float(tipo_habitacion.precio_base)
        print(f"DEBUG: Calculando costo total: ${costo_total} (precio base del tipo de habitación)")
        
        # Crear la reserva con el código de ubicación
        print(f"DEBUG: Creando reserva con habitación: {habitacion.numero}, código: {habitacion.codigo_ubicacion}")
        reserva = Reserva.objects.create(
            nombre_cliente=data['nombre'],
            apellido_cliente=data['apellido'],
            fecha_nacimiento_cliente=data['fecha_nacimiento'],
            numero_personas=numero_personas,
            codigo_ubicacion_habitacion=habitacion.codigo_ubicacion,  # Guardar el código de ubicación
            fecha_inicio=viaje.fecha_inicio,
            fecha_fin=viaje.fecha_fin,
            estado="confirmada",
            costo_total=costo_total  # Agregar el costo total calculado
        )
        print(f"DEBUG: Reserva creada con ID: {reserva.id}")

        # Marcar la habitación como reservada
        habitacion.reservada = True
        habitacion.save()
        print(f"DEBUG: Habitación {habitacion.numero} marcada como reservada")

        print(f"DEBUG: Devolviendo respuesta exitosa")
        return JsonResponse({
            'success': True,
            'message': f'Reserva creada exitosamente. Habitación asignada: {habitacion.codigo_ubicacion}',
            'reserva_id': reserva.id,
            'habitacion': {
                'codigo_ubicacion': habitacion.codigo_ubicacion,
                'numero': habitacion.numero,
                'tipo': tipo_habitacion.nombre
            }
        })

    except json.JSONDecodeError as e:
        print(f"DEBUG: JSONDecodeError: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error en el formato de los datos enviados'
        })
    except Exception as e:
        print(f"DEBUG: Exception en api_crear_reserva: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'message': 'Ocurrió un error interno al procesar la reserva. Por favor, inténtelo nuevamente.'
        })

# API ENDPOINTS PARA RESERVA DE ENTRETENIMIENTO

@csrf_exempt
@require_http_methods(["POST"])
def api_buscar_cliente_por_habitacion(request, crucero):
    """API para buscar cliente por número de habitación"""
    try:
        data = json.loads(request.body)
        numero_habitacion = data.get('numero_habitacion')

        if not numero_habitacion:
            return JsonResponse({
                'success': False,
                'message': 'Número de habitación requerido'
            })

        crucero_obj = get_object_or_404(Crucero, nombre=crucero)

        # Buscar reserva por número de habitación (usando codigo_ubicacion_habitacion)
        reserva = Reserva.objects.filter(
            codigo_ubicacion_habitacion=numero_habitacion,
            # Solo reservas activas/confirmadas
        ).first()

        if reserva:
            return JsonResponse({
                'success': True,
                'cliente': {
                    'id': reserva.id,
                    'nombre': reserva.nombre_cliente,
                    'apellido': reserva.apellido_cliente,
                    'fecha_nacimiento': reserva.fecha_nacimiento_cliente.strftime('%Y-%m-%d') if reserva.fecha_nacimiento_cliente else None,
                    'numero_habitacion': reserva.codigo_ubicacion_habitacion
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No se encontró una reserva para este número de habitación'
            })

    except Exception as e:
        print(f"DEBUG: Error en api_buscar_cliente_por_habitacion: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error al buscar cliente'
        })

@require_http_methods(["GET"])
def api_actividades_gratuitas_disponibles(request, crucero):
    """API para obtener actividades gratuitas disponibles"""
    try:
        crucero_obj = get_object_or_404(Crucero, nombre=crucero)

        # Obtener viaje activo del crucero
        viaje = Viaje.objects.filter(
            crucero=crucero_obj,
            estado__in=['activo', 'planificacion']
        ).first()

        if not viaje:
            return JsonResponse({
                'success': False,
                'message': 'No hay viaje activo para este crucero'
            })

        # Obtener actividades gratuitas disponibles para este viaje
        actividades = ActividadRutinaria.objects.filter(viaje=viaje).values(
            'id_actividad', 'titulo', 'descripcion', 'dia_crucero',
            'hora_inicio', 'hora_fin', 'maximo_actividad', 'ubicacion'
        )

        return JsonResponse({
            'success': True,
            'actividades': list(actividades)
        })

    except Exception as e:
        print(f"DEBUG: Error en api_actividades_gratuitas_disponibles: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error al obtener actividades gratuitas'
        })

@require_http_methods(["GET"])
def api_actividades_pago_disponibles(request, crucero):
    """API para obtener actividades de pago disponibles"""
    try:
        crucero_obj = get_object_or_404(Crucero, nombre=crucero)

        # Obtener viaje activo del crucero
        viaje = Viaje.objects.filter(
            crucero=crucero_obj,
            estado__in=['activo', 'planificacion']
        ).first()

        if not viaje:
            return JsonResponse({
                'success': False,
                'message': 'No hay viaje activo para este crucero'
            })

        # Obtener actividades de pago disponibles para este viaje
        actividades = Actividad.objects.filter(viaje=viaje).values(
            'id_actividad', 'titulo', 'descripcion', 'coste',
            'dia_crucero', 'hora_inicio', 'hora_fin', 'maximoActividad'
        )

        return JsonResponse({
            'success': True,
            'actividades': list(actividades)
        })

    except Exception as e:
        print(f"DEBUG: Error en api_actividades_pago_disponibles: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error al obtener actividades de pago'
        })

@csrf_exempt
@require_http_methods(["POST"])
def api_crear_reserva_entretenimiento(request, crucero):
    """API para crear reserva de entretenimiento"""
    try:
        data = json.loads(request.body)
        crucero_obj = get_object_or_404(Crucero, nombre=crucero)

        # Validar datos requeridos
        required_fields = ['cliente_id', 'tipo_actividad', 'numero_participantes']
        if data['tipo_actividad'] in ['pago', 'gratuito']:
            required_fields.append('actividad_id')

        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'message': f'Campo requerido faltante: {field}'
                })

        # Obtener la reserva del cliente
        reserva_cliente = get_object_or_404(Reserva, id=data['cliente_id'])

        # Obtener viaje activo
        viaje = Viaje.objects.filter(
            crucero=crucero_obj,
            estado__in=['activo', 'planificacion']
        ).first()

        if not viaje:
            return JsonResponse({
                'success': False,
                'message': 'No hay viaje activo para este crucero'
            })

        numero_participantes = int(data['numero_participantes'])

        if data['tipo_actividad'] == 'pago':
            # Crear reserva de actividad de pago
            actividad = get_object_or_404(Actividad, id_actividad=data['actividad_id'])

            # Calcular costo total
            costo_total = actividad.coste * numero_participantes

            # Crear nueva reserva para la actividad
            reserva_actividad = Reserva.objects.create(
                nombre_cliente=reserva_cliente.nombre_cliente,
                apellido_cliente=reserva_cliente.apellido_cliente,
                fecha_nacimiento_cliente=reserva_cliente.fecha_nacimiento_cliente,
                numero_personas=numero_participantes,
                codigo_ubicacion_habitacion=reserva_cliente.codigo_ubicacion_habitacion,
                actividad_pago=actividad,
                costo_total=costo_total,
                fecha_inicio=viaje.fecha_inicio,
                fecha_fin=viaje.fecha_fin,
                estado="confirmada"
            )

            return JsonResponse({
                'success': True,
                'message': f'Reserva de actividad de pago creada exitosamente. Costo total: ${costo_total}',
                'reserva_id': reserva_actividad.id,
                'actividad': {
                    'titulo': actividad.titulo,
                    'costo_unitario': float(actividad.coste),
                    'costo_total': float(costo_total)
                }
            })

        elif data['tipo_actividad'] == 'gratuito':
            # Crear reserva de actividad gratuita
            actividad_gratuita = get_object_or_404(ActividadRutinaria, id_actividad=data['actividad_id'])

            # Crear nueva reserva para la actividad gratuita
            reserva_actividad = Reserva.objects.create(
                nombre_cliente=reserva_cliente.nombre_cliente,
                apellido_cliente=reserva_cliente.apellido_cliente,
                fecha_nacimiento_cliente=reserva_cliente.fecha_nacimiento_cliente,
                numero_personas=numero_participantes,
                codigo_ubicacion_habitacion=reserva_cliente.codigo_ubicacion_habitacion,
                actividad_rutinaria=actividad_gratuita,
                costo_total=0.00,  # Actividades gratuitas no tienen costo
                fecha_inicio=viaje.fecha_inicio,
                fecha_fin=viaje.fecha_fin,
                estado="confirmada"
            )

            return JsonResponse({
                'success': True,
                'message': 'Reserva de actividad gratuita creada exitosamente.',
                'reserva_id': reserva_actividad.id,
                'actividad': {
                    'titulo': actividad_gratuita.titulo,
                    'ubicacion': actividad_gratuita.ubicacion,
                    'dia_crucero': actividad_gratuita.dia_crucero
                }
            })

        else:
            return JsonResponse({
                'success': False,
                'message': 'Tipo de actividad no válido'
            })

    except Exception as e:
        print(f"DEBUG: Error en api_crear_reserva_entretenimiento: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'message': 'Error al crear reserva de entretenimiento'
        })

# API ENDPOINT PARA VER RESERVAS

@require_http_methods(["GET"])
def api_ver_reservas(request, crucero):
    """API para obtener todas las reservas con información completa"""
    try:
        crucero_obj = get_object_or_404(Crucero, nombre=crucero)

        # Obtener todas las reservas del crucero
        reservas = Reserva.objects.all().select_related(
            'actividad_pago',
            'actividad_rutinaria',
            'evento_personalizado'
        )

        reservas_data = []

        for reserva in reservas:
            reserva_info = {
                'id': reserva.id,
                'nombre': reserva.nombre_cliente or 'No disponible',
                'apellido': reserva.apellido_cliente or 'No disponible',
                'numero_habitacion': reserva.codigo_ubicacion_habitacion,
                'costo_total': float(reserva.costo_total),
                'numero_personas': reserva.numero_personas,
                'estado': reserva.estado,
                'fecha_creacion': reserva.fecha_creacion.strftime('%Y-%m-%d %H:%M'),
            }

            # Verificar si hay actividad de pago
            if reserva.actividad_pago:
                reserva_info['tipo_reserva'] = 'actividad_pago'
                reserva_info['actividad'] = {
                    'titulo': reserva.actividad_pago.titulo,
                    'descripcion': reserva.actividad_pago.descripcion,
                    'dia_crucero': reserva.actividad_pago.dia_crucero,
                    'hora_inicio': str(reserva.actividad_pago.hora_inicio),
                    'hora_fin': str(reserva.actividad_pago.hora_fin),
                    'costo_unitario': float(reserva.actividad_pago.coste)
                }
            # Verificar si hay actividad rutinaria
            elif reserva.actividad_rutinaria:
                reserva_info['tipo_reserva'] = 'actividad_rutinaria'
                reserva_info['actividad'] = {
                    'titulo': reserva.actividad_rutinaria.titulo,
                    'descripcion': reserva.actividad_rutinaria.descripcion,
                    'dia_crucero': reserva.actividad_rutinaria.dia_crucero,
                    'hora_inicio': str(reserva.actividad_rutinaria.hora_inicio),
                    'hora_fin': str(reserva.actividad_rutinaria.hora_fin),
                    'ubicacion': reserva.actividad_rutinaria.ubicacion
                }
            # Verificar si hay evento personalizado
            elif reserva.evento_personalizado:
                reserva_info['tipo_reserva'] = 'evento_personalizado'
                reserva_info['evento'] = {
                    'titulo': reserva.evento_personalizado.nombre,
                    'descripcion': reserva.evento_personalizado.descripcion,
                    'dia': reserva.evento_personalizado.dia,
                    'ubicacion': reserva.evento_personalizado.ubicacion,
                    'crucero': reserva.evento_personalizado.crucero
                }
            # Si no hay actividades ni eventos, mostrar información de la habitación
            elif reserva.codigo_ubicacion_habitacion:
                reserva_info['tipo_reserva'] = 'habitacion'

                # Buscar información de la habitación usando el código de ubicación
                try:
                    habitacion = Habitacion.objects.select_related('tipo_habitacion').get(
                        codigo_ubicacion=reserva.codigo_ubicacion_habitacion
                    )
                    reserva_info['habitacion'] = {
                        'numero': habitacion.numero,
                        'cubierta': habitacion.cubierta,
                        'lado': habitacion.get_lado_display(),
                        'tipo_habitacion': habitacion.tipo_habitacion.nombre,
                        'capacidad': habitacion.tipo_habitacion.capacidad,
                        'descripcion': habitacion.tipo_habitacion.descripcion or 'Sin descripción',
                        'vista_mar': habitacion.vista_mar,
                        'precio_base': float(habitacion.tipo_habitacion.precio_base)
                    }
                except Habitacion.DoesNotExist:
                    reserva_info['habitacion'] = {
                        'numero': 'No disponible',
                        'cubierta': 'No disponible',
                        'lado': 'No disponible',
                        'tipo_habitacion': 'No disponible',
                        'capacidad': 0,
                        'descripcion': 'Información no disponible',
                        'vista_mar': False,
                        'precio_base': 0
                    }
            else:
                # Reserva sin tipo válido - saltar
                continue

            reservas_data.append(reserva_info)

        return JsonResponse({
            'success': True,
            'reservas': reservas_data,
            'total_reservas': len(reservas_data)
        })

    except Exception as e:
        print(f"DEBUG: Error en api_ver_reservas: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'message': 'Error al obtener las reservas'
        })

# API ENDPOINT PARA CANCELAR RESERVA

@csrf_exempt
@require_http_methods(["POST"])
def api_cancelar_reserva(request, crucero):
    """API para cancelar una reserva específica"""
    try:
        print(f"DEBUG: Iniciando api_cancelar_reserva para crucero: {crucero}")
        data = json.loads(request.body)
        print(f"DEBUG: Datos recibidos: {data}")
        
        crucero_obj = get_object_or_404(Crucero, nombre=crucero)
        reserva_id = data.get('reserva_id')
        
        if not reserva_id:
            return JsonResponse({
                'success': False,
                'message': 'ID de reserva requerido'
            })
        
        # Buscar la reserva
        reserva = get_object_or_404(Reserva, id=reserva_id)
        print(f"DEBUG: Reserva encontrada - ID: {reserva.id}, Código habitación: {reserva.codigo_ubicacion_habitacion}")
        
        # Verificar que la reserva pertenece al crucero correcto
        if reserva.codigo_ubicacion_habitacion:
            # Para reservas de habitación, verificar que la habitación pertenece al crucero
            print(f"DEBUG: Buscando habitación con código: {reserva.codigo_ubicacion_habitacion} en crucero: {crucero_obj.nombre}")
            habitacion = Habitacion.objects.filter(
                codigo_ubicacion=reserva.codigo_ubicacion_habitacion,
                crucero=crucero_obj
            ).first()
            
            if not habitacion:
                # Debug adicional: buscar todas las habitaciones con ese código
                habitaciones_con_codigo = Habitacion.objects.filter(
                    codigo_ubicacion=reserva.codigo_ubicacion_habitacion
                )
                print(f"DEBUG: Habitaciones encontradas con código {reserva.codigo_ubicacion_habitacion}: {[h.crucero.nombre for h in habitaciones_con_codigo]}")
                
                return JsonResponse({
                    'success': False,
                    'message': f'La reserva no pertenece a este crucero. Código: {reserva.codigo_ubicacion_habitacion}, Crucero solicitado: {crucero_obj.nombre}'
                })
            else:
                print(f"DEBUG: Habitación encontrada - Número: {habitacion.numero}, Crucero: {habitacion.crucero.nombre}")
        elif reserva.evento_personalizado:
            # Para eventos personalizados, verificar que el evento pertenece al crucero
            if reserva.evento_personalizado.crucero != crucero_obj.nombre:
                return JsonResponse({
                    'success': False,
                    'message': f'El evento personalizado no pertenece a este crucero. Crucero del evento: {reserva.evento_personalizado.crucero}, Crucero solicitado: {crucero_obj.nombre}'
                })
            print(f"DEBUG: Evento personalizado encontrado - Título: {reserva.evento_personalizado.nombre}, Crucero: {reserva.evento_personalizado.crucero}")
        
        # Liberar la habitación si es una reserva de habitación
        if reserva.codigo_ubicacion_habitacion:
            habitacion = Habitacion.objects.filter(
                codigo_ubicacion=reserva.codigo_ubicacion_habitacion,
                crucero=crucero_obj
            ).first()
            
            if habitacion:
                habitacion.reservada = False
                habitacion.save()
                print(f"DEBUG: Habitación {habitacion.numero} (código: {habitacion.codigo_ubicacion}) liberada")
        
        # Eliminar la reserva
        reserva.delete()
        print(f"DEBUG: Reserva {reserva_id} eliminada exitosamente")
        
        return JsonResponse({
            'success': True,
            'message': 'Reserva cancelada exitosamente'
        })
        
    except Exception as e:
        print(f"DEBUG: Error en api_cancelar_reserva: {str(e)}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'message': f'Error al cancelar la reserva: {str(e)}'
        })