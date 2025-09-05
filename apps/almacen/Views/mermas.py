from django.views.decorators.http import require_POST
from django.http import JsonResponse
from apps.almacen.models import Producto, Lote, MovimientoAlmacen

@require_POST
def registrar_merma(request):
    producto_id = request.POST.get('producto')
    lote_id = request.POST.get('lote')
    cantidad_cruda = request.POST.get('cantidad_mermada') or request.POST.get('cantidad') or ''
    descripcion = (request.POST.get('descripcion') or '').strip()
    print("ho")
    if not producto_id:
        return JsonResponse({
            'success': False, 
            'error': 'producto_requerido', 
            'mensaje': 'Debe seleccionar un producto.'
        }, status=400)
    
    if not lote_id:
        return JsonResponse({
            'success': False, 
            'error': 'lote_requerido', 
            'mensaje': 'Debe seleccionar un lote.'
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
        lote = Lote.objects.get(pk=lote_id, producto=producto)
    except Lote.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'lote_no_encontrado', 
            'mensaje': 'El lote no existe para este producto.'
        }, status=404)
    
    try:
        cantidad = int(cantidad_cruda)
    except ValueError:
        return JsonResponse({
            'success': False, 
            'error': 'cantidad_invalida', 
            'mensaje': 'Cantidad inválida.'
        }, status=400)
    
    if cantidad <= 0:
        return JsonResponse({
            'success': False, 
            'error': 'cantidad_no_valida', 
            'mensaje': 'La cantidad debe ser mayor a 0.'
        }, status=400)
    
    if cantidad > lote.cantidad_productos:
        return JsonResponse({
            'success': False, 
            'error': 'cantidad_excede', 
            'mensaje': f'La cantidad excede el stock del lote ({lote.cantidad_productos}).'
        }, status=409)
    
    try:
        lote.cantidad_productos -= cantidad
        lote.save()
        
        movimiento = MovimientoAlmacen.objects.create(
            tipo='MERMA',
            producto=producto,
            lote=lote,
            cantidad=cantidad,
            modulo='ALMACEN',
            descripcion=descripcion or 'Registro de merma'
        )
        
        return JsonResponse({
            'success': True, 
            'movimiento_id': movimiento.id, 
            'producto_id': producto.id, 
            'lote_id': lote.id, 
            'merma': cantidad
        })
        
    except Exception as error:
        return JsonResponse({
            'success': False, 
            'error': 'error_interno', 
            'mensaje': 'No se pudo registrar la merma.', 
            'detalle': str(error)
        }, status=500)

