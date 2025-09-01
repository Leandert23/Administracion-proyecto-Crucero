from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from datetime import timedelta

from .models import (
    TipoCrucero, Ubicacion, CategoriaProducto, Producto, InventarioProducto,
    TipoEquipo, Equipo, TareaMantenimiento, ProductoUtilizado, 
    HistorialMantenimiento, ReporteIncidente, Personal, AsignacionPersonal, CambioEstado,
    Piscina, MedicionPiscina
)
from .forms import (
    UbicacionForm, ProductoForm, InventarioProductoForm, EquipoForm,
    TareaMantenimientoForm, ReporteIncidenteForm, AsignacionPersonalForm, ProductoUtilizadoForm,
    PiscinaForm, MedicionPiscinaForm
)



def dashboard(request):
    """Dashboard principal del módulo de mantenimiento"""
    # Estadísticas generales
    total_equipos = Equipo.objects.count()
    equipos_operativos = Equipo.objects.filter(estado='operativo').count()
    equipos_mantenimiento = Equipo.objects.filter(estado='mantenimiento').count()
    equipos_averiados = Equipo.objects.filter(estado='averiado').count()
    equipos_fuera_servicio = Equipo.objects.filter(estado='fuera_servicio').count()
    
    # Tareas por estado actualizado
    tareas_pendientes = TareaMantenimiento.objects.filter(estado__in=['creada', 'planificada', 'asignada']).count()
    tareas_en_progreso = TareaMantenimiento.objects.filter(estado='en_progreso').count()
    tareas_completadas = TareaMantenimiento.objects.filter(estado='completada').count()
    tareas_vencidas = TareaMantenimiento.objects.filter(
        estado__in=['creada', 'planificada', 'asignada'],
        fecha_programada__lt=timezone.now()
    ).count()
    
    # Productos con stock bajo
    productos_stock_bajo = InventarioProducto.objects.filter(
        stock_actual__lte=F('stock_minimo')
    ).count()
    
    # Incidentes sin resolver
    incidentes_pendientes = ReporteIncidente.objects.filter(resuelto=False).count()
    
    # Tareas próximas a vencer (próximos 7 días)
    proximas_vencer = TareaMantenimiento.objects.filter(
        estado__in=['creada', 'planificada', 'asignada'],
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

    # Mantenimientos por tamaño de crucero y tipo (preventivo/correctivo)
    # Construir etiquetas en orden definido por el catálogo del modelo
    label_map = dict(TipoCrucero.TIPOS_CRUCERO)
    tipos_orden = [codigo for codigo, _ in TipoCrucero.TIPOS_CRUCERO]
    crucero_labels = [label_map.get(codigo, codigo) for codigo in tipos_orden]
    # Inicializar conteos en 0
    preventivo_counts = [0, 0, 0]
    correctivo_counts = [0, 0, 0]
    agregados = (
        TareaMantenimiento.objects
        .filter(tipo__in=['preventivo', 'correctivo'], tipo_crucero__tipo__in=tipos_orden)
        .values('tipo_crucero__tipo', 'tipo')
        .annotate(total=Count('id'))
    )
    indice_por_tipo = {codigo: idx for idx, codigo in enumerate(tipos_orden)}
    for fila in agregados:
        idx = indice_por_tipo.get(fila['tipo_crucero__tipo'])
        if idx is None:
            continue
        if fila['tipo'] == 'preventivo':
            preventivo_counts[idx] = fila['total']
        elif fila['tipo'] == 'correctivo':
            correctivo_counts[idx] = fila['total']

    # Datos para charts
    equipos_chart_data = [
        equipos_operativos,
        equipos_mantenimiento,
        equipos_averiados,
        equipos_fuera_servicio,
    ]
    tareas_chart_data = [
        tareas_pendientes,
        tareas_en_progreso,
        tareas_completadas,
        tareas_vencidas,
    ]
    
    # Construir segmentos para enlaces rápidos
    tipos_qs = TipoCrucero.objects.filter(tipo__in=tipos_orden).values('id', 'tipo')
    tipo_to_id = {t['tipo']: t['id'] for t in tipos_qs}
    crucero_segments = []
    for idx, codigo in enumerate(tipos_orden):
        crucero_segments.append({
            'id': tipo_to_id.get(codigo),
            'label': crucero_labels[idx],
            'preventivo': preventivo_counts[idx],
            'correctivo': correctivo_counts[idx],
        })
    
    # Asegurar que los datos sean válidos para Chart.js
    preventivo_counts = [max(0, int(x)) for x in preventivo_counts]
    correctivo_counts = [max(0, int(x)) for x in correctivo_counts]

    # Progreso (barras horizontales) por tipo de crucero
    totals_counts = [p + c for p, c in zip(preventivo_counts, correctivo_counts)]
    max_total = max(totals_counts) if totals_counts else 0
    if max_total == 0:
        crucero_progress = [
            {
                'label': crucero_labels[idx],
                'percent': 0,
                'total': totals_counts[idx] if idx < len(totals_counts) else 0,
                'preventivo': preventivo_counts[idx] if idx < len(preventivo_counts) else 0,
                'correctivo': correctivo_counts[idx] if idx < len(correctivo_counts) else 0,
                'color': color
            }
            for idx, color in enumerate(['bg-success', 'bg-warning', 'bg-info'])
        ]
    else:
        crucero_progress = []
        color_classes = ['bg-success', 'bg-warning', 'bg-info']
        for idx, total in enumerate(totals_counts):
            percent = int(round((total / max_total) * 100))
            crucero_progress.append({
                'label': crucero_labels[idx],
                'percent': percent,
                'total': total,
                'preventivo': preventivo_counts[idx],
                'correctivo': correctivo_counts[idx],
                'color': color_classes[idx % len(color_classes)]
            })

    context = {
        'total_equipos': total_equipos,
        'equipos_operativos': equipos_operativos,
        'equipos_mantenimiento': equipos_mantenimiento,
        'equipos_averiados': equipos_averiados,
        'equipos_fuera_servicio': equipos_fuera_servicio,
        'tareas_pendientes': tareas_pendientes,
        'tareas_en_progreso': tareas_en_progreso,
        'tareas_vencidas': tareas_vencidas,
        'tareas_completadas': tareas_completadas,
        'productos_stock_bajo': productos_stock_bajo,
        'incidentes_pendientes': incidentes_pendientes,
        'proximas_vencer': proximas_vencer,
        'equipos_revision_proxima': equipos_revision_proxima,
        # datos para gráfico por tamaño de crucero
        'crucero_labels': crucero_labels,
        'preventivo_counts': preventivo_counts,
        'correctivo_counts': correctivo_counts,
        # datos para charts de estado
        'equipos_chart_data': equipos_chart_data,
        'tareas_chart_data': tareas_chart_data,
        'crucero_segments': crucero_segments,
        'crucero_progress': crucero_progress,
    }
    
    return render(request, 'mantenimiento/dashboard.html', context)


# Vistas para Ubicaciones

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



def ubicacion_delete(request, pk):
    """Eliminar ubicación"""
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    if request.method == 'POST':
        ubicacion.delete()
        messages.success(request, 'Ubicación eliminada exitosamente.')
        return redirect('mantenimiento:ubicacion_list')
    
    return render(request, 'mantenimiento/ubicacion_confirm_delete.html', {'ubicacion': ubicacion})


# Vistas para Productos

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



def producto_delete(request, pk):
    """Eliminar producto"""
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('mantenimiento:producto_list')
    
    return render(request, 'mantenimiento/producto_confirm_delete.html', {'producto': producto})


# Vistas para Inventario

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
            inventarios = inventarios.filter(stock_actual__lte=F('stock_minimo'))
        elif estado_stock == 'bajo':
            inventarios = inventarios.filter(
                stock_actual__gt=F('stock_minimo'),
                stock_actual__lte=F('stock_minimo') * 1.5
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



def stock_bajo(request):
    """Productos con stock bajo"""
    inventarios = InventarioProducto.objects.filter(
        stock_actual__lte=F('stock_minimo')
    ).select_related('producto', 'tipo_crucero')
    
    context = {
        'inventarios': inventarios,
    }
    return render(request, 'mantenimiento/stock_bajo.html', context)


# Vistas para Equipos

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



def equipo_delete(request, pk):
    """Eliminar equipo"""
    equipo = get_object_or_404(Equipo, pk=pk)
    if request.method == 'POST':
        equipo.delete()
        messages.success(request, 'Equipo eliminado exitosamente.')
        return redirect('mantenimiento:equipo_list')
    
    return render(request, 'mantenimiento/equipo_confirm_delete.html', {'equipo': equipo})


# Vistas para Tareas de Mantenimiento

def tarea_list(request):
    """Lista de tareas de mantenimiento"""
    tareas = TareaMantenimiento.objects.select_related('equipo', 'ubicacion', 'asignado_a').all()
    
    # Filtros
    tipo = request.GET.get('tipo')
    estado = request.GET.get('estado')
    prioridad = request.GET.get('prioridad')
    asignado = request.GET.get('asignado')
    tipo_crucero_id = request.GET.get('tipo_crucero')
    
    if tipo:
        tareas = tareas.filter(tipo=tipo)
    if estado:
        tareas = tareas.filter(estado=estado)
    if prioridad:
        tareas = tareas.filter(prioridad=prioridad)
    if asignado:
        tareas = tareas.filter(asignado_a__id=asignado)
    if tipo_crucero_id:
        tareas = tareas.filter(tipo_crucero__id=tipo_crucero_id)
    
    # Paginación
    paginator = Paginator(tareas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'tipos': TareaMantenimiento.TIPOS_TAREA,
        'estados': TareaMantenimiento.ESTADOS,
        'prioridades': TareaMantenimiento.PRIORIDADES,
        'tipos_crucero': TipoCrucero.objects.all(),
    }
    return render(request, 'mantenimiento/tarea_list.html', context)



def tarea_create(request):
    """Crear nueva tarea"""
    if request.method == 'POST':
        form = TareaMantenimientoForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            if not tarea.tipo_crucero:
                messages.error(request, 'Debe seleccionar el tipo de crucero para la tarea.')
            else:
                tarea.save()
                messages.success(request, 'Tarea creada exitosamente.')
                return redirect('mantenimiento:tarea_list')
    else:
        form = TareaMantenimientoForm()
    
    return render(request, 'mantenimiento/tarea_form.html', {'form': form, 'action': 'Crear'})



def tarea_detail(request, pk):
    """Detalle de tarea con gestión completa de estados"""
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    productos_utilizados = ProductoUtilizado.objects.filter(tarea=tarea)
    personal_asignado = tarea.personal_asignado
    cambios_estado = tarea.cambios_estado.all()[:10]
    
    # Calcular estados posibles
    estados_posibles = []
    for estado_code, estado_nombre in TareaMantenimiento.ESTADOS:
        if tarea.puede_cambiar_estado(estado_code):
            estados_posibles.append((estado_code, estado_nombre))
    
    asignacion_form = AsignacionPersonalForm()
    producto_form = ProductoUtilizadoForm()
    
    # Filtrar personal disponible
    personal_disponible = Personal.objects.filter(activo=True, disponible=True)
    asignacion_form.fields['personal'].queryset = personal_disponible
    
    # Filtrar productos activos
    productos_activos = Producto.objects.filter(activo=True)
    producto_form.fields['producto'].queryset = productos_activos
    
    try:
        historial = HistorialMantenimiento.objects.get(tarea=tarea)
    except HistorialMantenimiento.DoesNotExist:
        historial = None
    
    context = {
        'tarea': tarea,
        'productos_utilizados': productos_utilizados,
        'personal_asignado': personal_asignado,
        'cambios_estado': cambios_estado,
        'estados_posibles': estados_posibles,
        'historial': historial,
        'asignacion_form': asignacion_form,
        'producto_form': producto_form,
        'puede_iniciar': tarea.puede_iniciar,
        'materiales_necesarios': tarea.materiales_necesarios,
    }
    return render(request, 'mantenimiento/tarea_detail.html', context)



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



def tarea_delete(request, pk):
    """Eliminar tarea"""
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    if request.method == 'POST':
        tarea.delete()
        messages.success(request, 'Tarea eliminada exitosamente.')
        return redirect('mantenimiento:tarea_list')
    
    return render(request, 'mantenimiento/tarea_confirm_delete.html', {'tarea': tarea})






# Vistas para Reportes de Incidentes

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



def incidente_create(request):
    """Crear nuevo incidente"""
    if request.method == 'POST':
        form = ReporteIncidenteForm(request.POST)
        if form.is_valid():
            incidente = form.save(commit=False)
            if hasattr(request, 'user') and getattr(request, 'user', None) and getattr(request.user, 'is_authenticated', False):
                incidente.reportado_por = request.user
            incidente.save()
            messages.success(request, 'Incidente reportado exitosamente.')
            return redirect('mantenimiento:incidente_list')
    else:
        form = ReporteIncidenteForm()
    
    return render(request, 'mantenimiento/incidente_form.html', {'form': form, 'action': 'Crear'})



def incidente_detail(request, pk):
    """Detalle de incidente"""
    incidente = get_object_or_404(ReporteIncidente, pk=pk)
    
    context = {
        'incidente': incidente,
    }
    return render(request, 'mantenimiento/incidente_detail.html', context)



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

def reportes(request):
    """Página principal de reportes"""
    return render(request, 'mantenimiento/reportes.html')



def reporte_tareas_pendientes(request):
    """Reporte de tareas pendientes"""
    tareas_pendientes = TareaMantenimiento.objects.filter(
        estado__in=['creada', 'planificada', 'asignada']
    ).order_by('fecha_programada')
    tareas_vencidas = tareas_pendientes.filter(fecha_programada__lt=timezone.now())
    
    context = {
        'tareas_pendientes': tareas_pendientes,
        'tareas_vencidas': tareas_vencidas,
    }
    return render(request, 'mantenimiento/reporte_tareas_pendientes.html', context)



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
        stock_actual__lte=F('stock_minimo')
    ).select_related('producto', 'tipo_crucero')
    
    context = {
        'productos_consumo': productos_consumo,
        'productos_stock_bajo': productos_stock_bajo,
        'fecha_inicio': fecha_inicio,
    }
    return render(request, 'mantenimiento/reporte_consumo_productos.html', context)






@require_POST
def tarea_asignar_personal(request, pk):
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    form = AsignacionPersonalForm(request.POST)
    if form.is_valid():
        asignacion = form.save(commit=False)
        asignacion.tarea = tarea
        asignacion.save()
        messages.success(request, 'Personal asignado a la tarea.')
    else:
        messages.error(request, 'Error al asignar personal.')
    return redirect('mantenimiento:tarea_detail', pk=pk)


@require_POST
def tarea_registrar_producto(request, pk):
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    form = ProductoUtilizadoForm(request.POST)
    if form.is_valid():
        pu = form.save(commit=False)
        pu.tarea = tarea
        try:
            pu.save()
            messages.success(request, 'Producto registrado y stock actualizado.')
        except Exception as e:
            messages.error(request, f'No se pudo registrar el producto: {e}')
    else:
        messages.error(request, 'Datos inválidos del producto.')
    return redirect('mantenimiento:tarea_detail', pk=pk)


@require_POST
def tarea_cambiar_estado(request, pk):
    """Cambiar estado de una tarea"""
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    nuevo_estado = request.POST.get('nuevo_estado')
    observaciones = request.POST.get('observaciones', '')
    
    if not nuevo_estado:
        messages.error(request, 'Debe seleccionar un estado.')
        return redirect('mantenimiento:tarea_detail', pk=pk)
    
    try:
        # Validaciones específicas por estado
        if nuevo_estado == 'en_progreso' and not tarea.personal_asignado.exists():
            messages.error(request, 'No se puede iniciar una tarea sin personal asignado.')
            return redirect('mantenimiento:tarea_detail', pk=pk)
        
        if nuevo_estado == 'completada' and tarea.productos_utilizados.count() == 0:
            messages.warning(request, 'Se completó la tarea sin registrar productos utilizados.')
        
        # Registrar el estado anterior antes del cambio
        estado_anterior = tarea.estado
        
        tarea.cambiar_estado(nuevo_estado, observaciones=observaciones)
        
        # Registrar el cambio en el historial
        CambioEstado.objects.create(
            tarea=tarea,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            observaciones=observaciones,
            usuario=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
        )
        
        messages.success(request, f'Estado cambiado a: {dict(TareaMantenimiento.ESTADOS)[nuevo_estado]}')
        
    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f'Error al cambiar estado: {e}')
    
    return redirect('mantenimiento:tarea_detail', pk=pk)


def tarea_workflow(request, pk):
    """Vista del flujo de trabajo de una tarea"""
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    cambios = tarea.cambios_estado.all()
    
    # Crear timeline del workflow
    timeline = []
    for cambio in cambios:
        timeline.append({
            'fecha': cambio.fecha_cambio,
            'estado': dict(TareaMantenimiento.ESTADOS)[cambio.estado_nuevo],
            'observaciones': cambio.observaciones,
            'usuario': cambio.usuario.username if cambio.usuario else 'Sistema',
        })
    
    context = {
        'tarea': tarea,
        'timeline': timeline,
    }
    return render(request, 'mantenimiento/tarea_workflow.html', context)


# ------------------------
# Piscinas
# ------------------------

def piscina_list(request):
    piscinas = ( 
        Piscina.objects.select_related('ubicacion', 'tipo_crucero')
    )
    return render(request, 'mantenimiento/piscina_list.html', {'piscinas': piscinas})


def piscina_create(request):
    if request.method == 'POST':
        form = PiscinaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Piscina creada exitosamente.')
            return redirect('mantenimiento:piscina_list')
    else:
        form = PiscinaForm()
    return render(request, 'mantenimiento/piscina_form.html', {'form': form, 'action': 'Crear'})


def piscina_update(request, pk):
    piscina = get_object_or_404(Piscina, pk=pk)
    if request.method == 'POST':
        form = PiscinaForm(request.POST, instance=piscina)
        if form.is_valid():
            form.save()
            messages.success(request, 'Piscina actualizada exitosamente.')
            return redirect('mantenimiento:piscina_list')
    else:
        form = PiscinaForm(instance=piscina)
    return render(request, 'mantenimiento/piscina_form.html', {'form': form, 'action': 'Editar', 'piscina': piscina})


def piscina_detail(request, pk):
    piscina = get_object_or_404(Piscina, pk=pk)
    mediciones = piscina.mediciones.all()[:20]
    return render(request, 'mantenimiento/piscina_detail.html', {'piscina': piscina, 'mediciones': mediciones})


def medicion_piscina_create(request):
    if request.method == 'POST':
        form = MedicionPiscinaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medición registrada exitosamente.')
            return redirect('mantenimiento:piscina_list')
    else:
        form = MedicionPiscinaForm()
    return render(request, 'mantenimiento/medicion_piscina_form.html', {'form': form})


