from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q

from ..cruceros.models import Crucero, Instalacion
from .models import Producto, SeccionAlmacen

def mostrar_vista_almacen(request, crucero_id):
    crucero = get_object_or_404(Crucero, pk=crucero_id)
    return render(request, "almacen.html", {"crucero":crucero})

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