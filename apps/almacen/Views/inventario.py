from django.views.decorators.http import require_GET
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.db.models import Q
from datetime import date
from apps.almacen.models import Producto, MovimientoAlmacen, SeccionAlmacen
from apps.cruceros.models import Instalacion
from ...cruceros.Services.fecha_general import obtener_fecha_actual

@require_GET
def obtener_pagina_inventario_productos(request):
    crucero_id = request.GET.get('crucero_id')
    productos = Producto.objects.all()
    
    if crucero_id:
        instalaciones = Instalacion.objects.filter(crucero_id=crucero_id, tipo='almacen')
        secciones = SeccionAlmacen.objects.filter(almacen__in=instalaciones)
        productos = productos.filter(seccion__in=secciones)
    
    productos = productos.order_by('nombre')
    
    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro:
        productos = productos.filter(tipo=tipo_filtro)
    
    subtipo_filtro = request.GET.get('subtipo')
    if subtipo_filtro:
        productos = productos.filter(subtipo=subtipo_filtro)
    
    busqueda = request.GET.get('busqueda')
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)
    
    paginador = Paginator(productos, 20)
    numero_pagina = request.GET.get('page', 1)
    
    try:
        pagina_objeto = paginador.page(numero_pagina)
    except (PageNotAnInteger, EmptyPage):
        pagina_objeto = paginador.page(1)
    
    html_tabla = render_to_string('Partials/tabla_de_productos.html', {
        'page_obj': pagina_objeto
    })
    
    html_paginacion = render_to_string('Partials/botones_paginacion.html', {
        'page_obj': pagina_objeto
    })
    
    return JsonResponse({
        'success': True,
        'tabla_html': html_tabla,
        'paginacion_html': html_paginacion,
        'info_paginacion': {
            'pagina_actual': pagina_objeto.number,
            'total_paginas': paginador.num_pages,
            'total_productos': paginador.count,
            'inicio': pagina_objeto.start_index(),
            'fin': pagina_objeto.end_index()
        }
    })


@require_GET
def buscar_productos(request):
    if request.method != "GET":
        return HttpResponseBadRequest('Método no permitido')
    
    crucero_id = request.GET.get('crucero_id')
    productos = Producto.objects.all()
    
    if crucero_id:
        instalaciones = Instalacion.objects.filter(crucero_id=crucero_id, tipo='almacen')
        secciones = SeccionAlmacen.objects.filter(almacen__in=instalaciones)
        productos = productos.filter(seccion__in=secciones)
    
    productos = productos.order_by('nombre')
    
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)
    
    html_lista = render_to_string('Partials/lista_resultados_productos.html', {
        'productos': productos
    })
    
    return JsonResponse({
        "success": True,
        "lista_html": html_lista,
        "total": productos.count()
    })


@require_GET
def obtener_movimientos_inventario(request):
    crucero_id = request.GET.get('crucero_id')
    movimientos = MovimientoAlmacen.objects.select_related('producto', 'producto__seccion', 'lote')
    
    if crucero_id:
        instalaciones = Instalacion.objects.filter(crucero_id=crucero_id, tipo='almacen')
        secciones = SeccionAlmacen.objects.filter(almacen__in=instalaciones)
        movimientos = movimientos.filter(producto__seccion__in=secciones)
    
    tipo_movimiento = request.GET.get('tipo')
    if tipo_movimiento in {'IN', 'OUT', 'NEW'}:
        movimientos = movimientos.filter(tipo=tipo_movimiento)
    
    rango_tiempo = request.GET.get('rango')
    if rango_tiempo in {'today', 'week'}:
        hoy = obtener_fecha_actual()
        if rango_tiempo == 'today':
            movimientos = movimientos.filter(fecha=hoy)
        elif rango_tiempo == 'week':
            desde = hoy - date.resolution * 6
            movimientos = movimientos.filter(fecha__gte=desde, fecha__lte=hoy)
    
    texto_busqueda = (request.GET.get('busqueda') or '').strip()
    if texto_busqueda:
        movimientos = movimientos.filter(
            Q(producto__nombre__icontains=texto_busqueda) |
            Q(descripcion__icontains=texto_busqueda) |
            Q(modulo__icontains=texto_busqueda)
        )
    
    movimientos = movimientos.order_by('-fecha', '-id')
    
    paginador = Paginator(movimientos, 15)
    numero_pagina = request.GET.get('page', 1)
    
    try:
        pagina_objeto = paginador.page(numero_pagina)
    except (PageNotAnInteger, EmptyPage):
        pagina_objeto = paginador.page(1)
    
    tabla_html = render_to_string('Partials/tabla_movimientos.html', {
        'page': pagina_objeto
    })
    
    pie_pagina_html = render_to_string('Partials/botones_paginacion.html', {
        'page_obj': pagina_objeto
    })
    
    return JsonResponse({
        'success': True,
        'tabla_html': tabla_html,
        'footer_html': pie_pagina_html,
        'info_paginacion': {
            'pagina_actual': pagina_objeto.number,
            'total_paginas': paginador.num_pages,
            'total_movimientos': paginador.count,
            'inicio': pagina_objeto.start_index(),
            'fin': pagina_objeto.end_index()
        }
    })


@require_GET
def obtener_detalle_producto(request):
    producto_id = request.GET.get('id')
    
    if not producto_id:
        return JsonResponse({'success': False, 'error': 'id_requerido'})
    
    try:
        producto = Producto.objects.select_related('seccion').get(pk=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'no_encontrado'})
    
    return JsonResponse({
        'success': True,
        'producto': {
            'id': producto.id,
            'nombre': producto.nombre,
            'tipo': producto.tipo,
            'subtipo': producto.subtipo,
            'cantidad_ideal': producto.cantidad_ideal,
            'medida': producto.medida,
            'seccion': producto.seccion_id
        }
    })


@require_GET
def obtener_lotes_producto(request):
    producto_id = request.GET.get('producto')
    
    if not producto_id:
        return JsonResponse({'success': False, 'error': 'producto_requerido'})
    
    try:
        producto = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'producto_no_encontrado'})
    
    # Solo lotes con stock disponible (>0)
    lotes = producto.lotes.filter(cantidad_productos__gt=0).order_by('-fecha_ingreso', '-id')
    
    html = render_to_string('Partials/tabla_lotes_producto.html', {
        'producto': producto,
        'lotes': lotes
    })
    
    return JsonResponse({
        'success': True, 
        'html': html, 
        'total_lotes': lotes.count()
    })


@require_GET
def obtener_lotes_producto_json(request):
    producto_id = request.GET.get('producto')
    
    if not producto_id:
        return JsonResponse({'success': False, 'error': 'producto_requerido'}, status=400)
    
    try:
        producto = Producto.objects.get(pk=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'producto_no_encontrado'}, status=404)
    
    # Solo incluir lotes con cantidad disponible (>0)
    lotes = producto.lotes.filter(cantidad_productos__gt=0).order_by('-fecha_ingreso', '-id')
    datos_lotes = []
    
    for lote in lotes:
        datos_lotes.append({
            'id': lote.id,
            'disponible': lote.cantidad_productos,
            'fecha_caducidad': lote.fecha_caducidad.isoformat() if lote.fecha_caducidad else None
        })
        
    return JsonResponse({'success': True, 'lotes': datos_lotes})