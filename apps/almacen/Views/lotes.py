from django.views.decorators.http import require_POST
from django.http import JsonResponse
from datetime import date
from apps.cruceros.Services.fecha_general import obtener_fecha_actual
from apps.almacen.models import Producto, Lote, MovimientoAlmacen, OrdenCompra
from apps.almacen.Services.products import retirar_producto_fefo, retirar_producto_fifo
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction
from apps.almacen.models import SolicitudSalida, ProductoSolicitado

@require_POST
@csrf_exempt
def solicitar_productos(request):
    # Now support batch requests: POST 'productos' = JSON list of {producto: id, cantidad: n}
    descripcion = (request.POST.get('descripcion') or '').strip()
    productos_json = request.POST.get('productos')
    crucero_id = request.POST.get('crucero_id')

    # Build items list: [{producto_id:int, cantidad:int}, ...]
    items = []
    if productos_json:
        try:
            parsed = json.loads(productos_json)
            if isinstance(parsed, list):
                for it in parsed:
                    pid = it.get('producto') or it.get('id')
                    qty = it.get('cantidad') or it.get('cantidad')
                    items.append({'producto': int(pid), 'cantidad': int(qty)})
            else:
                return JsonResponse({'success': False, 'mensaje': 'Formato de productos inválido.'}, status=400)
        except Exception:
            return JsonResponse({'success': False, 'mensaje': 'JSON inválido en productos.'}, status=400)
    else:
        # Fallback single-product payload (compatibilidad): producto & cantidad
        producto_id = request.POST.get('producto')
        cantidad_cruda = request.POST.get('cantidad')
        if not producto_id:
            return JsonResponse({'success': False, 'mensaje': 'Producto requerido.'}, status=400)
        try:
            items.append({'producto': int(producto_id), 'cantidad': int(cantidad_cruda)})
        except Exception:
            return JsonResponse({'success': False, 'mensaje': 'Cantidad inválida.'}, status=400)

    # Validate items and create Solicitud + ProductoSolicitado records
    try:
        # Determine modulo from POST (accept both 'modulo' and legacy 'modulo_entrega')
        # Also accept an optional X-MODULO header. Default to 'ALMACEN'.
        modulo_entrada = (
            (request.POST.get('modulo') or request.POST.get('modulo_entrega'))
            or request.META.get('HTTP_X_MODULO')
            or ''
        ).strip()
        modulo_lookup = {opcion[0].lower(): opcion[0] for opcion in MovimientoAlmacen.TIPO_MODULO}
        modulo = modulo_lookup.get(modulo_entrada.lower(), 'ALMACEN')

        with transaction.atomic():
            solicitud = SolicitudSalida.objects.create(descripcion=descripcion, modulo=modulo)
            created = 0
            for it in items:
                pid = it.get('producto')
                qty = it.get('cantidad')
                if not pid or not isinstance(qty, int) or qty <= 0:
                    transaction.set_rollback(True)
                    return JsonResponse({'success': False, 'mensaje': 'Producto o cantidad inválida.'}, status=400)
                try:
                    producto = Producto.objects.get(pk=pid)
                except Producto.DoesNotExist:
                    transaction.set_rollback(True)
                    return JsonResponse({'success': False, 'mensaje': f'Producto {pid} no encontrado.'}, status=404)

                ProductoSolicitado.objects.create(
                    solicitud=solicitud,
                    producto=producto,
                    cantidad=qty,
                    unidad=producto.medida or 'U'
                )
                created += 1

        return JsonResponse({'success': True, 'solicitud_id': solicitud.id, 'items_creados': created})
    except Exception as e:
        return JsonResponse({'success': False, 'mensaje': 'Error interno al crear la solicitud.'}, status=500)

@require_POST
def registrar_lote(request):
    datos = request.POST
    try:
        producto = Producto.objects.get(pk=datos.get('producto'))
    except Producto.DoesNotExist:
        return JsonResponse({'success': False})
    
    try:
        cantidad = int(datos.get('cantidad_productos') or 0)
    except ValueError:
        cantidad = 0
    
    try:
        precio = int(datos.get('precio_lote') or 0)
    except ValueError:
        precio = 0
    
    fecha_caducidad_valor = datos.get('fecha_caducidad')
    fecha_caducidad = None
    
    if fecha_caducidad_valor:
        try:
            partes = [int(parte) for parte in fecha_caducidad_valor.split('-')]
            fecha_caducidad = date(partes[0], partes[1], partes[2])
        except (ValueError, IndexError):
            fecha_caducidad = None

    # Validación: si se proporciona fecha de caducidad, debe ser estrictamente mayor a la fecha actual del sistema (no hoy ni pasado)
    if fecha_caducidad:
        try:
            fecha_actual_sistema = obtener_fecha_actual()
        except Exception:
            # Fallback silencioso a fecha de servidor si el registro de fecha no existe
            fecha_actual_sistema = date.today()
        if fecha_caducidad <= fecha_actual_sistema:
            return JsonResponse({
                'success': False,
                'error': 'fecha_caducidad_invalida',
                'mensaje': 'La fecha de caducidad debe ser mayor a la fecha actual del sistema.'
            }, status=400)
    
    orden_id = datos.get('orden_compra_id')
    orden = None
    if orden_id:
        try:
            orden = OrdenCompra.objects.get(pk=orden_id, producto=producto)
        except OrdenCompra.DoesNotExist:
            orden = None

    try:
        lote = Lote(
            producto=producto,
            cantidad_productos=cantidad,
            precio_lote=precio,
            fecha_caducidad=fecha_caducidad
        )
        lote.save()
        movimiento = MovimientoAlmacen.objects.create(
            tipo='IN',
            producto=producto,
            lote=lote,
            cantidad=cantidad,
            modulo='ALMACEN'
        )

        comparacion = None
        if orden and orden.estado == 'POR_REGISTRAR':
            # Comparar cantidades
            if cantidad < orden.cantidad_productos:
                print("Se debe devolucion")
                comparacion = 'PARCIAL'
            else:
                comparacion = 'COMPLETA'
            # Actualizar estado a aprobada/registrada (no existe estado final, reutilizamos APROBADA)
            orden.estado = 'APROBADA'
            orden.save(update_fields=['estado'])
            # Enviar señal de decisión de solicitud de almacén
            from apps.almacen.signals import enviar_decision_solicitud_almacen
            enviar_decision_solicitud_almacen(orden)

        return JsonResponse({
            'success': True,
            'lote_id': lote.id,
            'movimiento_id': movimiento.id,
            'orden_id': orden.id if orden else None,
            'comparacion': comparacion
        })

    except Exception as e:
        try:
            lote.delete()
        except Exception:
            pass
        return JsonResponse({'success': False})


@require_POST
def registrar_salida(request):
    producto_id = request.POST.get('producto')
    cantidad_cruda = request.POST.get('cantidad_productos', '')
    modulo_entrada = (request.POST.get('modulo_entrega') or request.POST.get('modulo') or '').strip()
    descripcion = (request.POST.get('descripcion') or '').strip()
    
    if not producto_id:
        return JsonResponse({
            'success': False, 
            'error': 'producto_requerido', 
            'mensaje': 'Debe seleccionar un producto.'
        }, status=400)
    
    try:
        producto = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'producto_no_encontrado', 
            'mensaje': 'El producto no existe.'
        }, status=404)
    
    try:
        cantidad = int(cantidad_cruda)
    except ValueError:
        return JsonResponse({
            'success': False, 
            'error': 'cantidad_invalida', 
            'mensaje': 'La cantidad debe ser un número entero.'
        }, status=400)
    
    if cantidad <= 0:
        return JsonResponse({
            'success': False, 
            'error': 'cantidad_no_valida', 
            'mensaje': 'La cantidad debe ser mayor a 0.'
        }, status=400)
    
    # Mapear modulo a opciones conocidas; por defecto 'ALMACEN'
    modulo_lookup = {opcion[0].lower(): opcion[0] for opcion in MovimientoAlmacen.TIPO_MODULO}
    modulo = modulo_lookup.get(modulo_entrada.lower(), 'ALMACEN')

    # En lugar de retirar stock inmediatamente, creamos una SolicitudSalida
    try:
        with transaction.atomic():
            solicitud = SolicitudSalida.objects.create(descripcion=descripcion, modulo=modulo)
            ProductoSolicitado.objects.create(
                solicitud=solicitud,
                producto=producto,
                cantidad=cantidad,
                unidad=producto.medida or 'U'
            )

        return JsonResponse({'success': True, 'solicitud_id': solicitud.id, 'items_creados': 1})
    except Exception as error:
        return JsonResponse({'success': False, 'error': 'error_interno', 'mensaje': 'Error al crear la solicitud', 'detalle': str(error)}, status=500)