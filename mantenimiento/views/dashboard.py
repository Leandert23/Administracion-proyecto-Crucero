from django.shortcuts import render
from django.db.models import F
from django.utils import timezone
from datetime import timedelta

from mantenimiento.models import (
    Equipo,
    TareaMantenimiento,
    InventarioProducto,
    Piscina,
)


def dashboard(request):
    # Manejar selección de crucero global
    if request.method == 'POST' and request.POST.get('_set_crucero'):
        crucero_id = request.POST.get('crucero_id') or None
        if crucero_id:
            request.session['crucero_id'] = int(crucero_id)
        else:
            request.session.pop('crucero_id', None)
    """Dashboard principal del módulo de mantenimiento"""
    # Filtro por crucero si hay uno seleccionado
    filtros = {}
    if getattr(request, 'session', None) and request.session.get('crucero_id'):
        filtros['ubicacion__crucero_id'] = request.session['crucero_id']

    total_equipos = Equipo.objects.filter(**filtros).count()
    equipos_operativos = Equipo.objects.filter(estado='operativo', **filtros).count()
    equipos_mantenimiento = Equipo.objects.filter(estado='mantenimiento', **filtros).count()
    equipos_averiados = Equipo.objects.filter(estado='averiado', **filtros).count()
    equipos_fuera_servicio = Equipo.objects.filter(estado='fuera_servicio', **filtros).count()

    tareas_qs = TareaMantenimiento.objects.all()
    if request.session.get('crucero_id'):
        tareas_qs = tareas_qs.filter(crucero_id=request.session['crucero_id'])

    tareas_pendientes = tareas_qs.filter(estado__in=['creada', 'planificada', 'asignada']).count()
    tareas_en_progreso = tareas_qs.filter(estado='en_progreso').count()
    tareas_completadas = tareas_qs.filter(estado='completada').count()
    tareas_vencidas = tareas_qs.filter(
        estado__in=['creada', 'planificada', 'asignada'],
        fecha_programada__lt=timezone.now(),
    ).count()

    inv_qs = InventarioProducto.objects.filter(stock_actual__lte=F('stock_minimo'))
    if request.session.get('crucero_id'):
        inv_qs = inv_qs.filter(crucero_id=request.session['crucero_id'])
    productos_stock_bajo = inv_qs.count()

    piscinas_con_alerta = 0
    for piscina in Piscina.objects.all():
        ultima_medicion = piscina.mediciones.first()
        if ultima_medicion and ultima_medicion.necesita_alerta:
            piscinas_con_alerta += 1
        elif not ultima_medicion:
            piscinas_con_alerta += 1

    proximas_vencer = tareas_qs.filter(
        estado__in=['creada', 'planificada', 'asignada'],
        fecha_programada__range=[timezone.now(), timezone.now() + timedelta(days=7)],
    )[:5]

    context = {
        'total_equipos': total_equipos,
        'equipos_operativos': equipos_operativos,
        'equipos_mantenimiento': equipos_mantenimiento,
        'equipos_averiados': equipos_averiados,
        'equipos_fuera_servicio': equipos_fuera_servicio,
        'tareas_pendientes': tareas_pendientes,
        'tareas_en_progreso': tareas_en_progreso,
        'tareas_completadas': tareas_completadas,
        'tareas_vencidas': tareas_vencidas,
        'productos_stock_bajo': productos_stock_bajo,
        'proximas_vencer': proximas_vencer,
        'piscinas_con_alerta': piscinas_con_alerta,
    }

    return render(request, 'mantenimiento/dashboard.html', context)


