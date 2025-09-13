from django.shortcuts import render
from django.utils import timezone
from django.db.models import F, Sum
from datetime import timedelta

from ..models import (
    TareaMantenimiento,
    Equipo,
    ProductoUtilizado,
    InventarioProducto,
)


def reportes(request):
    return render(request, 'mantenimiento/reportes.html')


def reporte_tareas_pendientes(request):
    tareas_pendientes = TareaMantenimiento.objects.filter(
        estado__in=['creada', 'planificada', 'asignada']
    ).order_by('fecha_programada')
    tareas_vencidas = tareas_pendientes.filter(fecha_programada__lt=timezone.now())
    return render(request, 'mantenimiento/reporte_tareas_pendientes.html', {
        'tareas_pendientes': tareas_pendientes,
        'tareas_vencidas': tareas_vencidas,
    })


def reporte_equipos_vencidos(request):
    equipos_vencidos = Equipo.objects.filter(
        proxima_revision__lt=timezone.now()
    ).order_by('proxima_revision')
    equipos_proximos = Equipo.objects.filter(
        proxima_revision__range=[timezone.now(), timezone.now() + timedelta(days=30)]
    ).order_by('proxima_revision')
    return render(request, 'mantenimiento/reporte_equipos_vencidos.html', {
        'equipos_vencidos': equipos_vencidos,
        'equipos_proximos': equipos_proximos,
    })


def reporte_consumo_productos(request):
    fecha_inicio = timezone.now() - timedelta(days=30)
    productos_consumo = ProductoUtilizado.objects.filter(
        fecha_utilizacion__gte=fecha_inicio
    ).values('producto__nombre').annotate(
        total_consumido=Sum('cantidad_utilizada')
    ).order_by('-total_consumido')[:10]

    try:
        productos_stock_bajo = InventarioProducto.objects.filter(
            stock_actual__lte=F('stock_minimo')
        ).select_related('producto', 'tipo_crucero')
    except Exception:
        # Fallback si hay problemas con la comparación F
        productos_stock_bajo = []
        try:
            all_items = InventarioProducto.objects.select_related('producto', 'tipo_crucero').all()
            productos_stock_bajo = [item for item in all_items if item.stock_actual <= item.stock_minimo]
        except:
            productos_stock_bajo = []

    return render(request, 'mantenimiento/reporte_consumo_productos.html', {
        'productos_consumo': productos_consumo,
        'productos_stock_bajo': productos_stock_bajo,
        'fecha_inicio': fecha_inicio,
    })


