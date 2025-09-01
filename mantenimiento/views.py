from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import json

from .models import (
    TipoCrucero, Ubicacion, CategoriaProducto, Producto, InventarioProducto,
    TipoEquipo, Equipo, TareaMantenimiento, ProductoUtilizado, 
    HistorialMantenimiento, ReporteIncidente
)
from .forms import (
    UbicacionForm, ProductoForm, InventarioProductoForm, EquipoForm,
    TareaMantenimientoForm, ReporteIncidenteForm
)


@login_required
def dashboard(request):
    """Dashboard principal del módulo de mantenimiento"""
    # Estadísticas generales
    total_equipos = Equipo.objects.count()
    equipos_operativos = Equipo.objects.filter(estado='operativo').count()
    equipos_mantenimiento = Equipo.objects.filter(estado='mantenimiento').count()
    equipos_averiados = Equipo.objects.filter(estado='averiado').count()
    
    # Tareas pendientes
    tareas_pendientes = TareaMantenimiento.objects.filter(estado='pendiente').count()
    tareas_en_progreso = TareaMantenimiento.objects.filter(estado='en_progreso').count()
    tareas_vencidas = TareaMantenimiento.objects.filter(
        estado='pendiente',
        fecha_programada__lt=timezone.now()
    ).count()
    
    # Productos con stock bajo
    productos_stock_bajo = InventarioProducto.objects.filter(
        stock_actual__lte=models.F('stock_minimo')
    ).count()
    
    # Incidentes sin resolver
    incidentes_pendientes = ReporteIncidente.objects.filter(resuelto=False).count()
    
    # Tareas próximas a vencer (próximos 7 días)
    proximas_vencer = TareaMantenimiento.objects.filter(
        estado='pendiente',
        fecha_programada__range=[
            timezone.now(),
            timezone.now() + timedelta(days=7)
        ]
    )[:5]
    
    # Equipos con revisión próxima
    equipos_revision_proxima = Equipo.objects.filter(
        proxima_revision__range=[
            timezone.now(),
            timezone.now() + timedelta(days=30)
        ]
    )[:5]
    
    context = {
        'total_equipos': total_equipos,
        'equipos_operativos': equipos_operativos,
        'equipos_mantenimiento': equipos_mantenimiento,
        'equipos_averiados': equipos_averiados,
        'tareas_pendientes': tareas_pendientes,
        'tareas_en_progreso': tareas_en_progreso,
        'tareas_vencidas': tareas_vencidas,
        'productos_stock_bajo': productos_stock_bajo,
        'incidentes_pendientes': incidentes_pendientes,
        'proximas_vencer': proximas_vencer,
        'equipos_revision_proxima': equipos_revision_proxima,
    }
    
    return render(request, 'mantenimiento/dashboard.html', context)


# Vistas para Ubicaciones
@login_required
def ubicacion_list(request):
    """Lista de ubicaciones"""
    ubicaciones = Ubicacion.objects.all().order_by('cubierta', 'uso', 'identificador', 'numero')
    
    # Filtros
    cubierta = request.GET.get('cubierta')
    uso = request.GET.get('uso')
    activa = request.GET.get('activa')
    
    if cubierta:
        ubicaciones = ubicaciones.filter(cubierta=cubierta)
    if uso:
        ubicaciones = ubicaciones.filter(uso=uso)
    if activa:
        ubicaciones = ubicaciones.filter(activa=activa == 'true')
    
    # Paginación
    paginator = Paginator(ubicaciones, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'cubiertas': range(1, 19),
        'usos': Ubicacion.USOS_UBICACION,
    }
    return render(request, 'mantenimiento/ubicacion_list.html', context)


@login_required
def ubicacion_create(request):
    """Crear nueva ubicación"""
    if request.method == 'POST':
        form = UbicacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ubicación creada exitosamente.')
            return redirect('mantenimiento:ubicacion_list')
    else:
        form = UbicacionForm()
    
    return render(request, 'mantenimiento/ubicacion_form.html', {'form': form, 'action': 'Crear'})


@login_required
def ubicacion_detail(request, pk):
    """Detalle de ubicación"""
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    equipos = Equipo.objects.filter(ubicacion=ubicacion)
    tareas = TareaMantenimiento.objects.filter(ubicacion=ubicacion)[:10]
    
    context = {
        'ubicacion': ubicacion,
        'equipos': equipos,
        'tareas': tareas,
    }
    return render(request, 'mantenimiento/ubicacion_detail.html', context)


@login_required
def ubicacion_update(request, pk):
    """Editar ubicación"""
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    if request.method == 'POST':
        form = UbicacionForm(request.POST, instance=ubicacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ubicación actualizada exitosamente.')
            return redirect('mantenimiento:ubicacion_detail', pk=pk)
    else:
        form = UbicacionForm(instance=ubicacion)
    
    return render(request, 'mantenimiento/ubicacion_form.html', {
        'form': form, 
        'action': 'Editar',
        'ubicacion': ubicacion
    })


@login_required
def ubicacion_delete(request, pk):
    """Eliminar ubicación"""
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    if request.method == 'POST':
        ubicacion.delete()
        messages.success(request, 'Ubicación eliminada exitosamente.')
        return redirect('mantenimiento:ubicacion_list')
    
    return render(request, 'mantenimiento/ubicacion_confirm_delete.html', {'ubicacion': ubicacion})


# Vistas para Productos
@login_required
def producto_list(request):
    """Lista de productos"""
    productos = Producto.objects.all().order_by('categoria', 'nombre')
    
    # Filtros
    categoria = request.GET.get('categoria')
    activo = request.GET.get('activo')
    
    if categoria:
        productos = productos.filter(categoria__categoria=categoria)
    if activo:
        productos = productos.filter(activo=activo == 'true')
    
    # Paginación
    paginator = Paginator(productos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categorias': CategoriaProducto.objects.all(),
    }
    return render(request, 'mantenimiento/producto_list.html', context)


@login_required
def producto_create(request):
    """Crear nuevo producto"""
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('mantenimiento:producto_list')
    else:
        form = ProductoForm()
    
    return render(request, 'mantenimiento/producto_form.html', {'form': form, 'action': 'Crear'})


@login_required
def producto_detail(request, pk):
    """Detalle de producto"""
    producto = get_object_or_404(Producto, pk=pk)
    inventarios = InventarioProducto.objects.filter(producto=producto)
    productos_utilizados = ProductoUtilizado.objects.filter(producto=producto)[:10]
    
    context = {
        'producto': producto,
        'inventarios': inventarios,
        'productos_utilizados': productos_utilizados,
    }
    return render(request, 'mantenimiento/producto_detail.html', context)


@login_required
def producto_update(request, pk):
    """Editar producto"""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('mantenimiento:producto_detail', pk=pk)
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'mantenimiento/producto_form.html', {
        'form': form, 
        'action': 'Editar',
        'producto': producto
    })


@login_required
def producto_delete(request, pk):
    """Eliminar producto"""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('mantenimiento:producto_list')
    
    return render(request, 'mantenimiento/producto_confirm_delete.html', {'producto': producto})


# Vistas para Inventario
@login_required
def inventario_list(request):
    """Lista de inventario"""
    inventarios = InventarioProducto.objects.select_related('producto', 'tipo_crucero').all()
    
    # Filtros
    tipo_crucero = request.GET.get('tipo_crucero')
    categoria = request.GET.get('categoria')
    estado_stock = request.GET.get('estado_stock')
    
    if tipo_crucero:
        inventarios = inventarios.filter(tipo_crucero__tipo=tipo_crucero)
    if categoria:
        inventarios = inventarios.filter(producto__categoria__categoria=categoria)
    if estado_stock:
        if estado_stock == 'critico':
            inventarios = inventarios.filter(stock_actual__lte=models.F('stock_minimo'))
        elif estado_stock == 'bajo':
            inventarios = inventarios.filter(
                stock_actual__gt=models.F('stock_minimo'),
                stock_actual__lte=models.F('stock_minimo') * 1.5
            )
    
    # Paginación
    paginator = Paginator(inventarios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tipos_crucero': TipoCrucero.objects.all(),
        'categorias': CategoriaProducto.objects.all(),
    }
    return render(request, 'mantenimiento/inventario_list.html', context)


@login_required
def inventario_update(request, pk):
    """Actualizar inventario"""
    inventario = get_object_or_404(InventarioProducto, pk=pk)
    if request.method == 'POST':
        form = InventarioProductoForm(request.POST, instance=inventario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventario actualizado exitosamente.')
            return redirect('mantenimiento:inventario_list')
    else:
        form = InventarioProductoForm(instance=inventario)
    
    return render(request, 'mantenimiento/inventario_form.html', {
        'form': form,
        'inventario': inventario
    })


@login_required
def stock_bajo(request):
    """Productos con stock bajo"""
    inventarios = InventarioProducto.objects.filter(
        stock_actual__lte=models.F('stock_minimo')
    ).select_related('producto', 'tipo_crucero')
    
    context = {
        'inventarios': inventarios,
    }
    return render(request, 'mantenimiento/stock_bajo.html', context)


# Vistas para Equipos
@login_required
def equipo_list(request):
    """Lista de equipos"""
    equipos = Equipo.objects.select_related('tipo_equipo', 'ubicacion').all()
    
    # Filtros
    tipo_equipo = request.GET.get('tipo_equipo')
    estado = request.GET.get('estado')
    cubierta = request.GET.get('cubierta')
    
    if tipo_equipo:
        equipos = equipos.filter(tipo_equipo__id=tipo_equipo)
    if estado:
        equipos = equipos.filter(estado=estado)
    if cubierta:
        equipos = equipos.filter(ubicacion__cubierta=cubierta)
    
    # Paginación
    paginator = Paginator(equipos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tipos_equipo': TipoEquipo.objects.all(),
        'estados': Equipo.ESTADOS,
        'cubiertas': range(1, 19),
    }
    return render(request, 'mantenimiento/equipo_list.html', context)


@login_required
def equipo_create(request):
    """Crear nuevo equipo"""
    if request.method == 'POST':
        form = EquipoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo creado exitosamente.')
            return redirect('mantenimiento:equipo_list')
    else:
        form = EquipoForm()
    
    return render(request, 'mantenimiento/equipo_form.html', {'form': form, 'action': 'Crear'})


@login_required
def equipo_detail(request, pk):
    """Detalle de equipo"""
    equipo = get_object_or_404(Equipo, pk=pk)
    tareas = TareaMantenimiento.objects.filter(equipo=equipo).order_by('-fecha_creacion')[:10]
    historial = HistorialMantenimiento.objects.filter(tarea__equipo=equipo).order_by('-fecha_registro')[:5]
    
    context = {
        'equipo': equipo,
        'tareas': tareas,
        'historial': historial,
    }
    return render(request, 'mantenimiento/equipo_detail.html', context)


@login_required
def equipo_update(request, pk):
    """Editar equipo"""
    equipo = get_object_or_404(Equipo, pk=pk)
    if request.method == 'POST':
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo actualizado exitosamente.')
            return redirect('mantenimiento:equipo_detail', pk=pk)
    else:
        form = EquipoForm(instance=equipo)
    
    return render(request, 'mantenimiento/equipo_form.html', {
        'form': form, 
        'action': 'Editar',
        'equipo': equipo
    })


@login_required
def equipo_delete(request, pk):
    """Eliminar equipo"""
    equipo = get_object_or_404(Equipo, pk=pk)
    if request.method == 'POST':
        equipo.delete()
        messages.success(request, 'Equipo eliminado exitosamente.')
        return redirect('mantenimiento:equipo_list')
    
    return render(request, 'mantenimiento/equipo_confirm_delete.html', {'equipo': equipo})


# Vistas para Tareas de Mantenimiento
@login_required
def tarea_list(request):
    """Lista de tareas de mantenimiento"""
    tareas = TareaMantenimiento.objects.select_related('equipo', 'ubicacion', 'asignado_a').all()
    
    # Filtros
    tipo = request.GET.get('tipo')
    estado = request.GET.get('estado')
    prioridad = request.GET.get('prioridad')
    asignado = request.GET.get('asignado')
    
    if tipo:
        tareas = tareas.filter(tipo=tipo)
    if estado:
        tareas = tareas.filter(estado=estado)
    if prioridad:
        tareas = tareas.filter(prioridad=prioridad)
    if asignado:
        tareas = tareas.filter(asignado_a__id=asignado)
    
    # Paginación
    paginator = Paginator(tareas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tipos': TareaMantenimiento.TIPOS_TAREA,
        'estados': TareaMantenimiento.ESTADOS,
        'prioridades': TareaMantenimiento.PRIORIDADES,
    }
    return render(request, 'mantenimiento/tarea_list.html', context)


@login_required
def tarea_create(request):
    """Crear nueva tarea"""
    if request.method == 'POST':
        form = TareaMantenimientoForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.creado_por = request.user
            tarea.save()
            messages.success(request, 'Tarea creada exitosamente.')
            return redirect('mantenimiento:tarea_list')
    else:
        form = TareaMantenimientoForm()
    
    return render(request, 'mantenimiento/tarea_form.html', {'form': form, 'action': 'Crear'})


@login_required
def tarea_detail(request, pk):
    """Detalle de tarea"""
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    productos_utilizados = ProductoUtilizado.objects.filter(tarea=tarea)
    
    try:
        historial = HistorialMantenimiento.objects.get(tarea=tarea)
    except HistorialMantenimiento.DoesNotExist:
        historial = None
    
    context = {
        'tarea': tarea,
        'productos_utilizados': productos_utilizados,
        'historial': historial,
    }
    return render(request, 'mantenimiento/tarea_detail.html', context)


@login_required
def tarea_update(request, pk):
    """Editar tarea"""
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    if request.method == 'POST':
        form = TareaMantenimientoForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarea actualizada exitosamente.')
            return redirect('mantenimiento:tarea_detail', pk=pk)
    else:
        form = TareaMantenimientoForm(instance=tarea)
    
    return render(request, 'mantenimiento/tarea_form.html', {
        'form': form, 
        'action': 'Editar',
        'tarea': tarea
    })


@login_required
def tarea_delete(request, pk):
    """Eliminar tarea"""
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    if request.method == 'POST':
        tarea.delete()
        messages.success(request, 'Tarea eliminada exitosamente.')
        return redirect('mantenimiento:tarea_list')
    
    return render(request, 'mantenimiento/tarea_confirm_delete.html', {'tarea': tarea})


@login_required
@require_POST
def tarea_iniciar(request, pk):
    """Iniciar tarea"""
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    if tarea.estado == 'pendiente':
        tarea.estado = 'en_progreso'
        tarea.fecha_inicio = timezone.now()
        tarea.save()
        messages.success(request, 'Tarea iniciada exitosamente.')
    else:
        messages.error(request, 'Solo se pueden iniciar tareas pendientes.')
    
    return redirect('mantenimiento:tarea_detail', pk=pk)


@login_required
@require_POST
def tarea_completar(request, pk):
    """Completar tarea"""
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    if tarea.estado == 'en_progreso':
        tarea.estado = 'completada'
        tarea.fecha_completada = timezone.now()
        tarea.save()
        messages.success(request, 'Tarea completada exitosamente.')
    else:
        messages.error(request, 'Solo se pueden completar tareas en progreso.')
    
    return redirect('mantenimiento:tarea_detail', pk=pk)


# Vistas para Reportes de Incidentes
@login_required
def incidente_list(request):
    """Lista de incidentes"""
    incidentes = ReporteIncidente.objects.select_related('ubicacion', 'equipo', 'reportado_por').all()
    
    # Filtros
    severidad = request.GET.get('severidad')
    resuelto = request.GET.get('resuelto')
    
    if severidad:
        incidentes = incidentes.filter(severidad=severidad)
    if resuelto:
        incidentes = incidentes.filter(resuelto=resuelto == 'true')
    
    # Paginación
    paginator = Paginator(incidentes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'severidades': ReporteIncidente.SEVERIDADES,
    }
    return render(request, 'mantenimiento/incidente_list.html', context)


@login_required
def incidente_create(request):
    """Crear nuevo incidente"""
    if request.method == 'POST':
        form = ReporteIncidenteForm(request.POST)
        if form.is_valid():
            incidente = form.save(commit=False)
            incidente.reportado_por = request.user
            incidente.save()
            messages.success(request, 'Incidente reportado exitosamente.')
            return redirect('mantenimiento:incidente_list')
    else:
        form = ReporteIncidenteForm()
    
    return render(request, 'mantenimiento/incidente_form.html', {'form': form, 'action': 'Crear'})


@login_required
def incidente_detail(request, pk):
    """Detalle de incidente"""
    incidente = get_object_or_404(ReporteIncidente, pk=pk)
    
    context = {
        'incidente': incidente,
    }
    return render(request, 'mantenimiento/incidente_detail.html', context)


@login_required
def incidente_update(request, pk):
    """Editar incidente"""
    incidente = get_object_or_404(ReporteIncidente, pk=pk)
    if request.method == 'POST':
        form = ReporteIncidenteForm(request.POST, instance=incidente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Incidente actualizado exitosamente.')
            return redirect('mantenimiento:incidente_detail', pk=pk)
    else:
        form = ReporteIncidenteForm(instance=incidente)
    
    return render(request, 'mantenimiento/incidente_form.html', {
        'form': form, 
        'action': 'Editar',
        'incidente': incidente
    })


@login_required
@require_POST
def incidente_resolver(request, pk):
    """Resolver incidente"""
    incidente = get_object_or_404(ReporteIncidente, pk=pk)
    if not incidente.resuelto:
        incidente.resuelto = True
        incidente.fecha_resolucion = timezone.now()
        incidente.save()
        messages.success(request, 'Incidente resuelto exitosamente.')
    else:
        messages.error(request, 'El incidente ya está resuelto.')
    
    return redirect('mantenimiento:incidente_detail', pk=pk)


# Vistas para Reportes
@login_required
def reportes(request):
    """Página principal de reportes"""
    return render(request, 'mantenimiento/reportes.html')


@login_required
def reporte_tareas_pendientes(request):
    """Reporte de tareas pendientes"""
    tareas_pendientes = TareaMantenimiento.objects.filter(estado='pendiente').order_by('fecha_programada')
    tareas_vencidas = tareas_pendientes.filter(fecha_programada__lt=timezone.now())
    
    context = {
        'tareas_pendientes': tareas_pendientes,
        'tareas_vencidas': tareas_vencidas,
    }
    return render(request, 'mantenimiento/reporte_tareas_pendientes.html', context)


@login_required
def reporte_equipos_vencidos(request):
    """Reporte de equipos con revisión vencida"""
    equipos_vencidos = Equipo.objects.filter(
        proxima_revision__lt=timezone.now()
    ).order_by('proxima_revision')
    
    equipos_proximos = Equipo.objects.filter(
        proxima_revision__range=[
            timezone.now(),
            timezone.now() + timedelta(days=30)
        ]
    ).order_by('proxima_revision')
    
    context = {
        'equipos_vencidos': equipos_vencidos,
        'equipos_proximos': equipos_proximos,
    }
    return render(request, 'mantenimiento/reporte_equipos_vencidos.html', context)


@login_required
def reporte_consumo_productos(request):
    """Reporte de consumo de productos"""
    # Productos más utilizados en el último mes
    fecha_inicio = timezone.now() - timedelta(days=30)
    productos_consumo = ProductoUtilizado.objects.filter(
        fecha_utilizacion__gte=fecha_inicio
    ).values('producto__nombre').annotate(
        total_consumido=Sum('cantidad_utilizada')
    ).order_by('-total_consumido')[:10]
    
    # Productos con stock bajo
    productos_stock_bajo = InventarioProducto.objects.filter(
        stock_actual__lte=models.F('stock_minimo')
    ).select_related('producto', 'tipo_crucero')
    
    context = {
        'productos_consumo': productos_consumo,
        'productos_stock_bajo': productos_stock_bajo,
        'fecha_inicio': fecha_inicio,
    }
    return render(request, 'mantenimiento/reporte_consumo_productos.html', context)


# API endpoints para AJAX
@login_required
def api_ubicaciones(request):
    """API para obtener ubicaciones"""
    ubicaciones = Ubicacion.objects.filter(activa=True)
    data = [{'id': u.id, 'codigo': u.codigo_ubicacion, 'descripcion': u.descripcion} for u in ubicaciones]
    return JsonResponse({'ubicaciones': data})


@login_required
def api_productos(request):
    """API para obtener productos"""
    productos = Producto.objects.filter(activo=True)
    data = [{'id': p.id, 'nombre': p.nombre, 'unidad': p.get_unidad_display()} for p in productos]
    return JsonResponse({'productos': data})


@login_required
def api_equipos(request):
    """API para obtener equipos"""
    equipos = Equipo.objects.all()
    data = [{'id': e.id, 'codigo': e.codigo, 'nombre': e.nombre} for e in equipos]
    return JsonResponse({'equipos': data})


@login_required
def api_tareas(request):
    """API para obtener tareas"""
    tareas = TareaMantenimiento.objects.filter(estado='pendiente')
    data = [{'id': t.id, 'titulo': t.titulo, 'fecha_programada': t.fecha_programada.strftime('%Y-%m-%d')} for t in tareas]
    return JsonResponse({'tareas': data})
