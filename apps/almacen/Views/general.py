from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator
from apps.cruceros.models import Crucero, Instalacion
from apps.almacen.models import SeccionAlmacen, OrdenCompra
from apps.cruceros.Services.fecha_general import obtener_fecha_actual
from datetime import timedelta

def mostrar_vista_almacen(request, crucero_id):
    crucero = get_object_or_404(Crucero, pk=crucero_id)
    instalaciones = Instalacion.objects.filter(crucero=crucero, tipo='almacen')
    secciones = SeccionAlmacen.objects.filter(almacen__in=instalaciones, esta_activa=True).select_related('almacen')
    try:
        fecha_actual = obtener_fecha_actual()
    except Exception:
        from datetime import date
        fecha_actual = date.today()
    fecha_min_caducidad = fecha_actual + timedelta(days=1)
    return render(request, "almacen.html", {
        "crucero": crucero,
        'secciones': secciones,
        'fecha_actual_sistema': fecha_actual,
        'fecha_min_caducidad': fecha_min_caducidad
    })





#[(nombreProducto, cantidad)]
@require_GET
def obtener_ordenes_compra_por_registrar(request):
    
    ()
    ordenes_compra = OrdenCompra.objects.filter(estado="POR_REGISTRAR").select_related('producto__seccion')
    
    
    
    
    
    
    page_number = request.GET.get('page', 1)
    paginator = Paginator(ordenes_compra, 10)
    page_obj = paginator.get_page(page_number)

    tabla_html = render(request, 'Partials/tabla_ordenes_compra.html', {
        'ordenes': page_obj.object_list
    }).content.decode('utf-8')
    paginacion_html = render(request, 'Partials/botones_paginacion.html', {
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
            'precio_lote': orden.precio_lote,
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