from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from apps.almacen.models import Producto, MovimientoAlmacen, SeccionAlmacen

@require_POST
def crear_producto(request):
    datos = request.POST
    
    nombre = (datos.get('nombre') or '').strip()
    tipo = datos.get('tipo') or ''
    subtipo = datos.get('subtipo')
    medida = datos.get('medida') or ''
    
    try:
        cantidad_ideal = int(datos.get('cantidad_ideal') or 0)
    except ValueError:
        cantidad_ideal = 0
    
    seccion_id = datos.get('seccion')
    seccion = None
    
    if seccion_id:
        try:
            seccion = SeccionAlmacen.objects.get(pk=seccion_id)
        except SeccionAlmacen.DoesNotExist:
            pass
    
    try:
        if not nombre:
            return JsonResponse({'success': False, 'error': 'nombre_requerido', 'mensaje': 'El nombre es obligatorio.'}, status=400)
        if not seccion:
            return JsonResponse({'success': False, 'error': 'seccion_invalida', 'mensaje': 'Sección no encontrada.'}, status=400)
        producto = Producto(
            nombre=nombre,
            tipo=tipo,
            subtipo=subtipo or None,
            cantidad_ideal=cantidad_ideal,
            medida=medida,
            seccion=seccion
        )
        producto.save()

        movimiento = MovimientoAlmacen.objects.create(
            tipo='NEW',
            producto=producto,
            lote=None,
            cantidad=None,
            modulo='ALMACEN',
            descripcion='Creación de producto'
        )

        return JsonResponse({
            'success': True,
            'producto': {'id': producto.id, 'nombre': producto.nombre},
            'movimiento_new_id': movimiento.id
        })
    except ValidationError as ve:
        # Estructura de errores de Django: {campo: [mensajes]}
        detalles = {campo: errs for campo, errs in ve.message_dict.items()}
        # Flatten para compatibilidad con manejador existente (toma un solo string por campo)
        errores_flat = {campo: ' '.join(errs) for campo, errs in detalles.items()}
        return JsonResponse({'success': False, 'error': 'validacion', 'detalles': detalles, 'errores': errores_flat}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'error_interno', 'mensaje': 'No se pudo crear el producto.'}, status=500)


@require_POST
def eliminar_producto(request):
    producto_id = request.POST.get('producto_id') or request.POST.get('id')
    
    if not producto_id:
        return JsonResponse({
            'success': False, 
            'error': 'id_requerido', 
            'mensaje': 'ID de producto requerido.'
        }, status=400)
    
    try:
        producto = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'no_encontrado', 
            'mensaje': 'Producto no encontrado.'
        }, status=404)
    
    if producto.lotes.exists():
        return JsonResponse({
            'success': False,
            'error': 'tiene_lotes',
            'mensaje': 'No se puede eliminar: el producto tiene lotes registrados.'
        }, status=409)
    
    if producto.cantidad and producto.cantidad > 0:
        return JsonResponse({
            'success': False,
            'error': 'stock_positivo',
            'mensaje': f'No se puede eliminar: stock actual {producto.cantidad} > 0.'
        }, status=409)
    
    try:
        id_producto = producto.id
        producto.delete()
        
        return JsonResponse({'success': True, 'producto_id': id_producto})
        
    except Exception as error:
        return JsonResponse({
            'success': False,
            'error': 'error_eliminando',
            'mensaje': 'Error inesperado eliminando el producto.',
            'detalle': str(error)
        }, status=500)


@require_POST
def actualizar_producto(request):
    datos = request.POST
    producto_id = datos.get('producto_id') or datos.get('id')
    
    if not producto_id:
        return JsonResponse({'success': False, 'error': 'id_requerido'}, status=400)
    
    try:
        producto = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'no_encontrado'}, status=404)
    
    nombre = (datos.get('nombre') or '').strip()
    tipo = datos.get('tipo') or ''
    subtipo = datos.get('subtipo')
    medida = datos.get('medida') or ''
    
    try:
        cantidad_ideal = int(datos.get('cantidad_ideal') or 0)
    except ValueError:
        cantidad_ideal = 0
    
    seccion_id = datos.get('seccion')
    seccion = None
    
    if seccion_id:
        try:
            seccion = SeccionAlmacen.objects.get(pk=seccion_id)
        except SeccionAlmacen.DoesNotExist:
            pass
    
    try:
        if not nombre:
            return JsonResponse({'success': False, 'error': 'nombre_requerido', 'mensaje': 'El nombre es obligatorio.'}, status=400)
        if seccion:
            producto.seccion = seccion
        producto.nombre = nombre
        producto.tipo = tipo
        producto.subtipo = subtipo or None
        producto.cantidad_ideal = cantidad_ideal
        producto.medida = medida
        producto.save()
        return JsonResponse({'success': True, 'producto': {'id': producto.id, 'nombre': producto.nombre}})
    except ValidationError as ve:
        detalles = {campo: errs for campo, errs in ve.message_dict.items()}
        errores_flat = {campo: ' '.join(errs) for campo, errs in detalles.items()}
        return JsonResponse({'success': False, 'error': 'validacion', 'detalles': detalles, 'errores': errores_flat}, status=400)
    except Exception as error:
        return JsonResponse({'success': False, 'error': 'error_actualizando', 'detalle': str(error)}, status=400)
