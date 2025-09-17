from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST
import json
from django.core.paginator import Paginator
from django.db.models import Sum
from django.db import transaction
from apps.creador_embarcaciones.models import Embarcacion, Locales
from apps.almacen.models import SeccionAlmacen, OrdenCompra
from apps.almacen.models import MensajeParaCompras
from apps.almacen.models import SolicitudSalida
from apps.almacen.Services.products import retirar_producto_fefo, retirar_producto_fifo
from apps.almacen.Services.products import calcular_asignacion_lotes
from apps.cruceros.Services.fecha_general import obtener_fecha_actual
from datetime import timedelta

def mostrar_vista_almacen(request, embarcacion_id):
    embarcacion = get_object_or_404(Embarcacion, pk=embarcacion_id)
    secciones = SeccionAlmacen.objects.filter(local_tipo_almacen__cubierta__embarcacion=embarcacion).select_related('local_tipo_almacen')
    try:
        fecha_actual = obtener_fecha_actual()
    except Exception:
        from datetime import date
        fecha_actual = date.today()
    fecha_min_caducidad = fecha_actual + timedelta(days=1)
    return render(request, "almacen.html", {
        "embarcacion": embarcacion,
        'secciones': secciones,
        'fecha_actual_sistema': fecha_actual,
        'fecha_min_caducidad': fecha_min_caducidad
    })


@require_GET
def obtener_locales_tipo_almacen(request, embarcacion_id):
    """Devuelve JSON con los locales de tipo almacén para la embarcación dada."""
    embarcacion = get_object_or_404(Embarcacion, pk=embarcacion_id)
    locales_almacen = Locales.objects.filter(cubierta__embarcacion=embarcacion, tipo='almacen').values('id', 'nombre')
    return JsonResponse({'success': True, 'locales': list(locales_almacen)})



@require_POST
def crear_seccion(request):
    """Crea una SeccionAlmacen a partir de un POST form-encoded.

    Espera los campos simplificados: local_tipo_almacen_id, nombre, tipo.
    No se solicita capacidad/temperatura/humedad desde el formulario; la vista
    usará valores por defecto (capacidad=1, temperatura/humedad=None).
    Responde JSON: {'success': True, 'id': <pk>} o {'success': False, 'errores': {campo: mensaje}, 'error': 'codigo'}
    """
    try:
        data = request.POST
        local_tipo_almacen_id = data.get('local_tipo_almacen_id')
        nombre = (data.get('nombre') or '').strip()
        tipo = data.get('tipo')
        # Not requesting capacidad/temperatura/humedad from the simplified form
        capacidad = None
        temperatura = None
        humedad = None

        errores = {}

        if not local_tipo_almacen_id:
            errores['local_tipo_almacen'] = 'Local tipo almacén requerido.'
        else:
            try:
                local_tipo_almacen = Locales.objects.get(pk=int(local_tipo_almacen_id), tipo='almacen')
            except Locales.DoesNotExist:
                errores['local_tipo_almacen'] = 'Local tipo almacén no encontrado.'
            except Exception:
                errores['local_tipo_almacen'] = 'Error al obtener local tipo almacén.'

        if not nombre:
            errores['nombre'] = 'Nombre requerido.'

        if not tipo:
            errores['tipo'] = 'Tipo requerido.'

        # Since the simplified form doesn't provide capacidad, temperatura or humedad,
        # use sensible defaults: capacidad=1, temperatura/humedad=None
        capacidad_int = 1
        temp_val = None
        hum_val = None

        if errores:
            return JsonResponse({'success': False, 'errores': errores}, status=400)

        # Crear sección
        seccion = SeccionAlmacen(
            local_tipo_almacen=local_tipo_almacen,
            nombre=nombre,
            tipo=tipo,
            capacidad=capacidad_int,
            temperatura=temp_val,
            humedad=hum_val,
            esta_activa=True
        )

        try:
            seccion.full_clean()
            seccion.save()
        except Exception as ex:
            # Manejar errores de validación o unicidad
            err_resp = {}
            try:
                from django.core.exceptions import ValidationError
                if isinstance(ex, ValidationError):
                    if hasattr(ex, 'message_dict'):
                        for k, v in ex.message_dict.items():
                            err_resp[k] = '; '.join(v)
                    else:
                        err_resp['__all__'] = str(ex)
                else:
                    err_resp['__all__'] = str(ex)
            except Exception:
                err_resp['__all__'] = str(ex)

            return JsonResponse({'success': False, 'errores': err_resp}, status=400)

        # Retornar éxito
        return JsonResponse({'success': True, 'id': seccion.id, 'nombre': seccion.nombre})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)





#[(nombreProducto, cantidad)]
@require_GET
def obtener_ordenes_compra_por_registrar(request):
    ordenes_compra = OrdenCompra.objects.filter(estado="POR_REGISTRAR").select_related('producto__seccion')
    
    
    
    
    
    
    page_number = request.GET.get('page', 1)
    paginator = Paginator(ordenes_compra, 10)
    page_obj = paginator.get_page(page_number)

    tabla_html = render(request, 'partials/tabla_ordenes_compra.html', {
        'ordenes': page_obj.object_list
    }).content.decode('utf-8')
    paginacion_html = render(request, 'partials/botones_paginacion.html', {
        'page_obj': page_obj,
        'page_label': 'órdenes',
        'js_function': 'cargarPaginaOrdenes',
        'summary_id': 'ordenes-summary'
    }).content.decode('utf-8')
    return JsonResponse({'success': True, 'tabla_html': tabla_html, 'paginacion_html': paginacion_html, 'total': ordenes_compra.count()})











@require_GET
def detalle_orden_compra(request, orden_id):
    orden = get_object_or_404(OrdenCompra.objects.select_related('producto__seccion'), pk=orden_id)
    prod = orden.producto
    return JsonResponse({
        'success': True,
        'orden': {
            'id': orden.id,
            'cantidad_productos': orden.cantidad_productos,
            'estado': orden.estado,
        },
        'producto': {
            'id': prod.id,
            'nombre': prod.nombre,
            'tipo': prod.tipo,
            'subtipo': prod.subtipo,
            'medida': prod.get_medida_display(),
            'seccion': prod.seccion.nombre
        }
    })



@require_POST
def reportar_defecto_orden(request):
    """Marca una orden de compra como DENEGADA y adjunta/crea un MensajeParaCompras

    Espera JSON o form-encoded con: orden_id, producto (opcional), cantidad_llegada, descripcion
    Responde JSON {'success': True}
    """
    try:
        # parse body
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body.decode('utf-8') or '{}')
        else:
            data = request.POST

        orden_id = data.get('orden_id') or data.get('orden') or data.get('orden_compra_id')
        cantidad = data.get('cantidad_llegada') or data.get('cantidad')
        descripcion = (data.get('descripcion') or data.get('notas') or data.get('notas_defecto') or '').strip()

        if not orden_id:
            return JsonResponse({'success': False, 'error': 'orden_id_requerido'}, status=400)

        orden = get_object_or_404(OrdenCompra.objects.select_related('compra_lote'), pk=int(orden_id))

        # marcar orden como DENEGADA
        orden.estado = 'DENEGADA'
        orden.save()

        # obtener compra_lote asociado y el mensaje vinculado
        compra_lote = getattr(orden, 'compra_lote', None)
        if compra_lote:
            # preparar texto con la cantidad llegada
            try:
                cantidad_int = int(cantidad) if cantidad is not None and str(cantidad).strip() != '' else None
            except Exception:
                cantidad_int = None

            llegada_line = ''
            if cantidad_int is not None:
                llegada_line = f"llegó {cantidad_int}\n"
            elif cantidad is not None and str(cantidad).strip() != '':
                # si no se pudo parsear a int, usar el valor tal cual
                llegada_line = f"llegó {cantidad}\n"

            # construir la descripcion final que guardaremos
            descripcion_final = descripcion or ''
            if llegada_line:
                if descripcion_final:
                    descripcion_final = f"{llegada_line}\n\n{descripcion_final}"
                else:
                    descripcion_final = llegada_line

            # buscar un mensaje existente
            mensaje = compra_lote.mensajes_para_almacen.first()
            if not mensaje:
                # crear uno nuevo con la descripción recibida
                MensajeParaCompras.objects.create(compra_lote=compra_lote, descripcion=descripcion_final)
            else:
                # anexar la nueva descripción al mensaje existente
                actual = (mensaje.descripcion or '').strip()
                if actual:
                    nuevo = actual + '\n\n' + descripcion_final if descripcion_final else actual
                else:
                    nuevo = descripcion_final
                mensaje.descripcion = nuevo
                mensaje.save()

        # Emitir la señal de decisión para que los receivers procesen la compra_lote
        try:
            # Import local para evitar problemas de importación circular
            from apps.almacen.signals import enviar_decision_solicitud_almacen
            if getattr(orden, 'compra_lote', None):
                # No pasamos mensaje explícito: la función leerá el MensajeParaCompras asociado y lo usará
                enviar_decision_solicitud_almacen(orden)
        except Exception:
            # No bloquear la vista por fallos en handlers de señal; opcional: loggear
            pass

        return JsonResponse({'success': True, 'orden_id': orden.id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def obtener_listado_solicitudes(request):
    """Devuelve HTML parcial con la tabla de solicitudes (paginado).

    Nota: únicamente devuelve solicitudes con estado 'PENDIENTE' para que el modal
    muestre solo las solicitudes por procesar.
    """
    # Anotar con la suma de cantidades solicitadas para mostrar unidades totales
    qs = SolicitudSalida.objects.filter(estado='PENDIENTE').annotate(total_unidades=Sum('productos_solicitados__cantidad')).order_by('-fecha_creacion')
    page_number = int(request.GET.get('page', 1))
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(page_number)

    tabla_html = render(request, 'partials/tabla_solicitudes.html', {
        'solicitudes': page_obj.object_list
    }).content.decode('utf-8')

    paginacion_html = render(request, 'partials/botones_paginacion.html', {
        'page_obj': page_obj,
        'page_label': 'solicitudes',
        'js_function': 'cargarPaginaSolicitudes',
        'summary_id': 'solicitudes-summary'
    }).content.decode('utf-8')

    return JsonResponse({
        'success': True,
        'tabla_html': tabla_html,
        'paginacion_html': paginacion_html,
        'total': qs.count()
    })


@require_GET
def detalle_solicitud(request, solicitud_id):
    """Devuelve HTML parcial con los productos y cantidades de una solicitud."""
    solicitud = get_object_or_404(SolicitudSalida.objects.prefetch_related('productos_solicitados__producto'), pk=solicitud_id)
    html = render(request, 'partials/detalle_solicitud.html', {'solicitud': solicitud}).content.decode('utf-8')
    return JsonResponse({'success': True, 'html': html})


@require_GET
def obtener_solicitudes_aprobadas(request):
    """Devuelve HTML parcial con la tabla de solicitudes aprobadas asociadas a la embarcación actual.

    Parámetros (GET): page (opcional), embarcacion_id (opcional - si no se recibe se listan todas)
    """
    embarcacion_id = request.GET.get('embarcacion_id')
    qs = SolicitudSalida.objects.filter(estado='APROBADA')
    # Si se proporciona embarcacion_id intentamos filtrar por relación a través de productos->seccion->local_tipo_almacen->cubierta->embarcacion
    if embarcacion_id:
        qs = qs.filter(productos_solicitados__producto__seccion__local_tipo_almacen__cubierta__embarcacion_id=embarcacion_id).distinct()
    qs = qs.annotate(total_unidades=Sum('productos_solicitados__cantidad')).order_by('-fecha_creacion')

    page_number = int(request.GET.get('page', 1))
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(page_number)

    tabla_html = render(request, 'partials/tabla_solicitudes_aprobadas.html', {
        'solicitudes': page_obj.object_list
    }).content.decode('utf-8')

    paginacion_html = render(request, 'partials/botones_paginacion.html', {
        'page_obj': page_obj,
        'page_label': 'solicitudes aprobadas',
        'js_function': 'cargarPaginaSolicitudesAprobadas',
        'summary_id': 'solicitudes-aprobadas-summary'
    }).content.decode('utf-8')

    return JsonResponse({'success': True, 'tabla_html': tabla_html, 'paginacion_html': paginacion_html, 'total': qs.count()})





@require_POST
def aceptar_solicitud(request):
    """Marca una SolicitudSalida como Aprobada. Acepta JSON o form-encoded body con 'id' o 'solicitud_id'."""
    try:
        sid = None
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body.decode('utf-8') or '{}')
            sid = data.get('id') or data.get('solicitud_id')
        else:
            sid = request.POST.get('id') or request.POST.get('solicitud_id')

        if not sid:
            return JsonResponse({'success': False, 'error': 'id_requerido'}, status=400)

        solicitud = get_object_or_404(SolicitudSalida, pk=int(sid))
        # Sólo aceptar si está pendiente
        if solicitud.estado != 'PENDIENTE':
            return JsonResponse({'success': False, 'error': 'estado_no_permitido', 'estado_actual': solicitud.estado}, status=400)

        solicitud.estado = 'APROBADA'
        solicitud.save()
        return JsonResponse({'success': True, 'id': solicitud.id, 'estado': solicitud.estado})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
def rechazar_solicitud(request):
    """Marca una SolicitudSalida como Rechazada. Acepta JSON o form-encoded body con 'id' o 'solicitud_id'."""
    try:
        sid = None
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body.decode('utf-8') or '{}')
            sid = data.get('id') or data.get('solicitud_id')
        else:
            sid = request.POST.get('id') or request.POST.get('solicitud_id')

        if not sid:
            return JsonResponse({'success': False, 'error': 'id_requerido'}, status=400)

        solicitud = get_object_or_404(SolicitudSalida, pk=int(sid))
        # Sólo rechazar si está pendiente
        if solicitud.estado != 'PENDIENTE':
            return JsonResponse({'success': False, 'error': 'estado_no_permitido', 'estado_actual': solicitud.estado}, status=400)

        solicitud.estado = 'RECHAZADA'
        solicitud.save()
        return JsonResponse({'success': True, 'id': solicitud.id, 'estado': solicitud.estado})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)@require_POST

def entregar_solicitud(request):
    """Marca una SolicitudSalida como COMPLETADA y puede realizar otras acciones de entrega."""
    try:
        sid = None
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body.decode('utf-8') or '{}')
            sid = data.get('id') or data.get('solicitud_id')
        else:
            sid = request.POST.get('id') or request.POST.get('solicitud_id')

        if not sid:
            return JsonResponse({'success': False, 'error': 'id_requerido'}, status=400)

        solicitud = get_object_or_404(SolicitudSalida.objects.prefetch_related('productos_solicitados__producto'), pk=int(sid))
        if solicitud.estado != 'APROBADA':
            return JsonResponse({'success': False, 'error': 'estado_no_permitido', 'estado_actual': solicitud.estado}, status=400)

        # Procesar cada producto solicitado: retirar stock siguiendo FIFO/FEFO según lotes
        try:
            with transaction.atomic():
                productos_solicitados = solicitud.productos_solicitados.select_related('producto').all()
                # Usar el modulo de la solicitud para los movimientos (fallback a 'ALMACEN')
                modulo_mov = (getattr(solicitud, 'modulo', None) or 'ALMACEN')
                for ps in productos_solicitados:
                    producto = ps.producto
                    cantidad = int(ps.cantidad or 0)
                    # Determinar método: FEFO si existen lotes con fecha de caducidad
                    tiene_lotes_con_fecha = producto.lotes.filter(cantidad_productos__gt=0, fecha_caducidad__isnull=False).exists()
                    if tiene_lotes_con_fecha:
                        retirar_producto_fefo(producto.pk, cantidad, modulo_mov, descripcion=f'Entrega solicitud #{solicitud.id}')
                    else:
                        retirar_producto_fifo(producto.pk, cantidad, modulo_mov, descripcion=f'Entrega solicitud #{solicitud.id}')

                # Si todo fue bien, marcar solicitud como completada
                solicitud.estado = 'COMPLETADA'
                solicitud.save()

        except ValueError as ve:
            # error lanzado por la lógica de retiro (por ejemplo stock insuficiente)
            return JsonResponse({'success': False, 'error': 'stock_insuficiente', 'detalle': str(ve)}, status=409)
        except Exception as ex:
            return JsonResponse({'success': False, 'error': 'error_interno', 'detalle': str(ex)}, status=500)

        return JsonResponse({'success': True, 'id': solicitud.id, 'estado': solicitud.estado})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_GET
def entrega_preview(request, solicitud_id):
    """Devuelve una previsualización de los lotes que se utilizarían para cumplir una solicitud.

    Responde JSON con lista por producto y asignaciones por lote.
    """
    try:
        solicitud = get_object_or_404(SolicitudSalida.objects.prefetch_related('productos_solicitados__producto'), pk=int(solicitud_id))
        productos = []
        for ps in solicitud.productos_solicitados.select_related('producto').all():
            producto = ps.producto
            cantidad = int(ps.cantidad or 0)
            asignaciones, disponible_total = calcular_asignacion_lotes(producto.pk, cantidad)
            productos.append({
                'producto_id': producto.pk,
                'nombre': producto.nombre,
                'unidad': getattr(producto, 'get_medida_display', lambda: '')(),
                'total_solicitado': cantidad,
                'asignaciones': asignaciones,
                'disponible_total': disponible_total,
                'insuficiente': disponible_total < cantidad
            })

        return JsonResponse({'success': True, 'preview': productos})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)