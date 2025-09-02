from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string

from datetime import date

from ..cruceros.models import Crucero, Instalacion
from ..cruceros.Services.fecha_general import obtener_fecha_actual
from .models import Producto, SeccionAlmacen, Lote, MovimientoAlmacen
from .Services.products import retirar_producto_fifo, retirar_producto_fefo  # (podrían dejarse de usar si lógica local)
from django.views.decorators.http import require_POST
from django.db import transaction


def mostrar_vista_almacen(request, crucero_id):
    crucero = get_object_or_404(Crucero, pk=crucero_id)
    instalaciones = Instalacion.objects.filter(crucero=crucero, tipo='almacen')
    secciones = SeccionAlmacen.objects.filter(almacen__in=instalaciones, esta_activa=True).select_related('almacen')
    return render(request, "almacen.html", {"crucero":crucero, 'secciones': secciones})

def inventario_paginas_producto(request):
    crucero_id = request.GET.get('crucero_id')
    if crucero_id:
        instalaciones = Instalacion.objects.filter(crucero_id=crucero_id, tipo='almacen')
        secciones = SeccionAlmacen.objects.filter(almacen__in=instalaciones)
        productos = Producto.objects.filter(seccion__in=secciones).order_by('nombre')

    tipo_filtro = request.GET.get('tipo', '')
    if tipo_filtro:
        productos = productos.filter(tipo=tipo_filtro)

    subtipo_filtro = request.GET.get('subtipo', '')
    if subtipo_filtro:
        productos = productos.filter(subtipo=subtipo_filtro)

    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)

    paginator = Paginator(productos, 20)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    # Pasa el page_obj por una plantilla y devuelve el html
    html_tabla = render_to_string('partials/tabla_de_productos.html', {
        'page_obj': page_obj
    })

    html_paginacion = render_to_string('partials/botones_paginacion.html', {
        'page_obj': page_obj
    })

    return JsonResponse({
        'success': True,
        'tabla_html': html_tabla,
        'paginacion_html': html_paginacion,
        'info_paginacion': {
            'pagina_actual': page_obj.number,
            'total_paginas': paginator.num_pages,
            'total_productos': paginator.count,
            'inicio': page_obj.start_index(),
            'fin': page_obj.end_index()
        }
    })


@require_POST
def crear_producto(request):
    data = request.POST
    nombre = (data.get('nombre') or '').strip()
    tipo = data.get('tipo') or ''
    subtipo = data.get('subtipo') or None
    try:
        cantidad_ideal = int(data.get('cantidad_ideal') or 0)
    except Exception:
        cantidad_ideal = 0
    medida = data.get('medida') or ''
    seccion = None
    seccion_id = data.get('seccion')
    if seccion_id:
        try:
            seccion = SeccionAlmacen.objects.get(pk=seccion_id)
        except Exception:
            seccion = None
    try:
        producto = Producto(
            nombre=nombre,
            tipo=tipo,
            subtipo=subtipo or None,
            cantidad_ideal=cantidad_ideal,
            medida=medida,
            seccion=seccion
        )
        producto.save()
        return JsonResponse({'success': True, 'producto': {'id': producto.id, 'nombre': producto.nombre}})
    except Exception:
        return JsonResponse({'success': False})


@require_POST
def registrar_lote(request):
    data = request.POST
    producto = None
    try:
        producto = Producto.objects.get(pk=data.get('producto'))
    except Exception:
        return JsonResponse({'success': False})
    try:
        cantidad = int(data.get('cantidad_productos') or 0)
    except Exception:
        cantidad = 0
    try:
        precio = int(data.get('precio_lote') or 0)
    except Exception:
        precio = 0
    fecha_caducidad_val = data.get('fecha_caducidad') or None
    fecha_caducidad_date = None
    if fecha_caducidad_val:
        try:
            partes = [int(p) for p in fecha_caducidad_val.split('-')]
            fecha_caducidad_date = date(partes[0], partes[1], partes[2])
        except Exception:
            fecha_caducidad_date = None
    try:
        lote = Lote(
            producto=producto,
            cantidad_productos=cantidad,
            precio_lote=precio,
            fecha_caducidad=fecha_caducidad_date
        )
        lote.save()
        modulo_valor = data.get('modulo') or 'COMPRAS'  # Compras envia por defecto
        try:
            movimiento = MovimientoAlmacen.objects.create(
                tipo='IN',
                producto=producto,
                lote=lote,
                cantidad=cantidad,
                modulo=modulo_valor
            )
            return JsonResponse({'success': True, 'lote_id': lote.id, 'movimiento_id': movimiento.id})
        except Exception:
            try:
                lote.delete()
            except Exception:
                pass
            return JsonResponse({'success': False})
    except Exception:
        return JsonResponse({'success': False})

def buscar_productos(request):
    if (request.method != "GET"):
        return HttpResponseBadRequest('Método no permitido')
    
    crucero_id = request.GET.get('crucero_id')
    if crucero_id:
        instalaciones = Instalacion.objects.filter(crucero_id=crucero_id, tipo='almacen')
        secciones = SeccionAlmacen.objects.filter(almacen__in=instalaciones)
        productos = Producto.objects.filter(seccion__in=secciones).order_by('nombre')
    
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)
        
    html_lista = render_to_string('partials/lista_resultados_productos.html', { 'productos': productos })

    return JsonResponse({
        "success": True,
        "lista_html": html_lista,
        "total": productos.count()
    })


@require_POST
def registrar_salida(request):
    producto_id = request.POST.get('producto') or ''
    cantidad_raw = request.POST.get('cantidad_productos', '')
    modulo_input = (request.POST.get('modulo_entrega') or '').strip()
    descripcion = (request.POST.get('descripcion') or '').strip()

    if not producto_id:
        return JsonResponse({'success': False, 'error': 'producto_requerido', 'mensaje': 'Debe seleccionar un producto.'}, status=400)
    try:
        producto = Producto.objects.get(pk=producto_id)
    except Exception:
        return JsonResponse({'success': False, 'error': 'producto_no_encontrado', 'mensaje': 'El producto no existe.'}, status=404)
    try:
        cantidad = int(cantidad_raw)
    except Exception:
        return JsonResponse({'success': False, 'error': 'cantidad_invalida', 'mensaje': 'La cantidad debe ser un número entero.'}, status=400)
    if cantidad <= 0:
        return JsonResponse({'success': False, 'error': 'cantidad_no_valida', 'mensaje': 'La cantidad debe ser mayor a 0.'}, status=400)

    modulo_lookup = {c[0].lower(): c[0] for c in MovimientoAlmacen.TIPO_MODULO}
    modulo = modulo_lookup.get(modulo_input.lower(), 'COMPRAS')

    stock_actual = producto.cantidad
    if stock_actual < cantidad:
        return JsonResponse({
            'success': False,
            'error': 'stock_insuficiente',
            'mensaje': 'Stock insuficiente para realizar la salida.',
            'detalle': f'Disponible {stock_actual}, solicitado {cantidad}'
        }, status=409)

    metodo = 'FEFO' if producto.lotes.filter(cantidad_productos__gt=0, fecha_caducidad__isnull=False).exists() else 'FIFO'

    try:
        if metodo == 'FEFO':
            retirar_producto_fefo(producto.pk, cantidad, modulo, descripcion=descripcion)
        else:
            retirar_producto_fifo(producto.pk, cantidad, modulo, descripcion=descripcion)
        return JsonResponse({'success': True, 'producto_id': producto.pk, 'retirado': cantidad, 'metodo': metodo})
    except ValueError as ve:
        return JsonResponse({
            'success': False,
            'error': 'operacion_invalida',
            'mensaje': str(ve)
        }, status=400)
    except Exception as ex:
        return JsonResponse({
            'success': False,
            'error': 'error_interno',
            'mensaje': 'Error inesperado al registrar la salida.',
            'detalle': str(ex)
        }, status=500)
