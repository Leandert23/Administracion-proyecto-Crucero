from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from mantenimiento.core.services import DashboardService
from mantenimiento.core.notifications import AlertManager


def dashboard(request):
    """Dashboard principal optimizado con alertas"""
    try:
        crucero_id = request.session.get('crucero_id')
        context = DashboardService.get_dashboard_data(crucero_id)
        
        # Agregar alertas críticas
        context['critical_alerts'] = AlertManager.get_dashboard_alerts(limit=5)
        context['total_alerts'] = AlertManager.get_alert_count()
        
        return render(request, 'mantenimiento/dashboard.html', context)
    except Exception as e:
        return render(request, 'mantenimiento/dashboard.html', {'error': str(e)})


@require_GET
def dashboard_update_data(request):
    """Actualización AJAX optimizada del dashboard"""
    try:
        crucero_id = request.session.get('crucero_id')
        data = DashboardService.get_dashboard_data(crucero_id)
        
        # Asegurar que tenemos datos válidos
        tareas_chart_data = data.get('tareas_chart_data', [0, 0, 0, 0])
        if not isinstance(tareas_chart_data, list) or len(tareas_chart_data) != 4:
            tareas_chart_data = [0, 0, 0, 0]
        
        return JsonResponse({
            'success': True,
            'data': {
                'tareas_chart_data': tareas_chart_data,
                'preventivo_counts': data.get('preventivo_counts', []),
                'correctivo_counts': data.get('correctivo_counts', []),
                'stats': {
                    'total_equipos': data.get('total_equipos', 0),
                    'tareas_pendientes': data.get('tareas_pendientes', 0),
                    'productos_stock_bajo': data.get('productos_stock_bajo', 0),
                    'piscinas_con_alerta': 0  # Simplificado por ahora
                },
                'alerts': AlertManager.get_dashboard_alerts(limit=3),
                'total_alerts': AlertManager.get_alert_count()
            },
            'timestamp': data.get('last_updated', timezone.now()).isoformat()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


