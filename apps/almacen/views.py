from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string

from ..cruceros.models import Crucero, Instalacion
from .models import Producto, SeccionAlmacen

def mostrar_vista_almacen(request, crucero_id):
    crucero = get_object_or_404(Crucero, pk=crucero_id)
    instalaciones = Instalacion.objects.filter(crucero=crucero, tipo='almacen')
    secciones = SeccionAlmacen.objects.filter(almacen__in=instalaciones, esta_activa=True).select_related('almacen')
    return render(request, "almacen.html", {"crucero":crucero, 'secciones': secciones})

def inventario_modal_ajax(request):
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


def crear_producto(request):
    """Crea un producto desde el modal. Devuelve JSON con estado y errores.
    Espera POST con: nombre, tipo, subtipo (opcional), cantidad_ideal, medida, seccion.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('Método no permitido')

    data = request.POST
    nombre = (data.get('nombre') or '').strip()
    tipo = data.get('tipo') or ''
    subtipo = data.get('subtipo') or None
    cantidad_ideal = data.get('cantidad_ideal')
    medida = data.get('medida') or ''
    seccion_id = data.get('seccion')

    errores = {}
    if not nombre:
        errores['nombre'] = 'Nombre requerido'
    if not tipo:
        errores['tipo'] = 'Tipo requerido'
    if cantidad_ideal in (None, ''):
        errores['cantidad_ideal'] = 'Cantidad ideal requerida'
    else:
        try:
            cantidad_ideal = int(cantidad_ideal)
            if cantidad_ideal < 0:
                errores['cantidad_ideal'] = 'Debe ser >= 0'
        except ValueError:
            errores['cantidad_ideal'] = 'Debe ser un número'
    if not medida:
        errores['medida'] = 'Unidad requerida'
    if not seccion_id:
        errores['seccion'] = 'Sección requerida'

    seccion = None
    if seccion_id:
        try:
            seccion = SeccionAlmacen.objects.get(pk=seccion_id)
        except SeccionAlmacen.DoesNotExist:
            errores['seccion'] = 'Sección inválida'

    if errores:
        return JsonResponse({'success': False, 'errors': errores}, status=400)

    producto = Producto(
        nombre=nombre,
        tipo=tipo,
        subtipo=subtipo or None,
        cantidad_ideal=cantidad_ideal,
        medida=medida,
        seccion=seccion
    )
    try:
        producto.save()
    except Exception as e:
        # Extrae mensajes de ValidationError si aplica
        errores['__all__'] = str(e)
        return JsonResponse({'success': False, 'errors': errores}, status=400)

    return JsonResponse({'success': True, 'producto': {
        'id': producto.id,
        'nombre': producto.nombre,
        'tipo': producto.tipo,
        'subtipo': producto.subtipo,
        'cantidad_ideal': producto.cantidad_ideal,
        'medida': producto.medida,
        'seccion': producto.seccion_id,
    }})