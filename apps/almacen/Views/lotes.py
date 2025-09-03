from django.views.decorators.http import require_POST
from django.http import JsonResponse
from datetime import date
from apps.almacen.models import Producto, Lote, MovimientoAlmacen
from apps.almacen.Services.products import retirar_producto_fefo, retirar_producto_fifo

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
        
        return JsonResponse({
            'success': True, 
            'lote_id': lote.id, 
            'movimiento_id': movimiento.id
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
    modulo_entrada = (request.POST.get('modulo_entrega') or '').strip()
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
    
    modulo_lookup = {opcion[0].lower(): opcion[0] for opcion in MovimientoAlmacen.TIPO_MODULO}
    modulo = modulo_lookup.get(modulo_entrada.lower(), 'COMPRAS')
    
    stock_actual = producto.cantidad
    if stock_actual < cantidad:
        return JsonResponse({
            'success': False,
            'error': 'stock_insuficiente',
            'mensaje': 'Stock insuficiente para realizar la salida.',
            'detalle': f'Disponible {stock_actual}, solicitado {cantidad}'
        }, status=409)
    
    tiene_lotes_con_fecha = producto.lotes.filter(
        cantidad_productos__gt=0, 
        fecha_caducidad__isnull=False
    ).exists()
    
    metodo = 'FEFO' if tiene_lotes_con_fecha else 'FIFO'
    
    try:
        if metodo == 'FEFO':
            retirar_producto_fefo(producto.pk, cantidad, modulo, descripcion=descripcion)
        else:
            retirar_producto_fifo(producto.pk, cantidad, modulo, descripcion=descripcion)
        
        return JsonResponse({
            'success': True, 
            'producto_id': producto.pk, 
            'retirado': cantidad, 
            'metodo': metodo
        })
        
    except ValueError as error:
        return JsonResponse({
            'success': False,
            'error': 'operacion_invalida',
            'mensaje': str(error)
        }, status=400)
        
    except Exception as error:
        return JsonResponse({
            'success': False,
            'error': 'error_interno',
            'mensaje': 'Error inesperado al registrar la salida.',
            'detalle': str(error)
        }, status=500)