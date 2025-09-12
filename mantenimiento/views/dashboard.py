from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ValidationError

from mantenimiento.core.services import DashboardService
from mantenimiento.core.notifications import AlertManager
from mantenimiento.models import TareaMantenimiento, TipoCrucero
from mantenimiento.forms import TareaMantenimientoForm


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
    """Actualización AJAX simplificada del dashboard"""
    try:
        from django.db.models import F
        from mantenimiento.models import (
            TareaMantenimiento,
            Equipo,
            InventarioProducto,
            ReporteIncidente,
        )
        from mantenimiento.core.config import SystemConfig

        # Obtener datos básicos de forma simple
        try:
            total_equipos = Equipo.objects.count()
        except:
            total_equipos = 0

        try:
            tareas_pendientes = TareaMantenimiento.objects.filter(estado__in=['creada', 'planificada', 'asignada']).count()
            tareas_en_progreso = TareaMantenimiento.objects.filter(estado='en_progreso').count()
            tareas_completadas = TareaMantenimiento.objects.filter(estado='completada').count()
            tareas_vencidas = 0  # Simplificado por ahora
        except:
            tareas_pendientes = tareas_en_progreso = tareas_completadas = tareas_vencidas = 0

        try:
            productos_stock_bajo = InventarioProducto.objects.filter(
                stock_actual__lte=F('stock_minimo')
            ).count()
        except:
            productos_stock_bajo = 0

        try:
            incidentes_pendientes = ReporteIncidente.objects.filter(resuelto=False).count()
        except:
            incidentes_pendientes = 0

        # Datos para gráficas
        tareas_chart_data = [tareas_pendientes, tareas_en_progreso, tareas_completadas, tareas_vencidas]

        # Datos por tipo de crucero (reales)
        crucero_labels = []
        preventivo_counts = []
        correctivo_counts = []
        try:
            for tipo_key, tipo_display in SystemConfig.TIPOS_CRUCERO:
                crucero_labels.append(tipo_display)
                preventivo_counts.append(
                    TareaMantenimiento.objects.filter(
                        tipo_crucero__tipo=tipo_key, tipo='preventivo'
                    ).count()
                )
                correctivo_counts.append(
                    TareaMantenimiento.objects.filter(
                        tipo_crucero__tipo=tipo_key, tipo='correctivo'
                    ).count()
                )
        except Exception:
            # Fallback en caso de problema
            crucero_labels = ['Crucero Pequeño', 'Crucero Mediano', 'Crucero Grande']
            preventivo_counts = [0, 0, 0]
            correctivo_counts = [0, 0, 0]

        return JsonResponse({
            'success': True,
            'data': {
                'tareas_chart_data': tareas_chart_data,
                'preventivo_counts': preventivo_counts,
                'correctivo_counts': correctivo_counts,
                'stats': {
                    'total_equipos': total_equipos,
                    'tareas_pendientes': tareas_pendientes,
                    'tareas_en_progreso': tareas_en_progreso,
                    'tareas_completadas': tareas_completadas,
                    'tareas_vencidas': tareas_vencidas,
                    'productos_stock_bajo': productos_stock_bajo,
                    'incidentes_pendientes': incidentes_pendientes,
                    'piscinas_con_alerta': 0
                }
            },
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error en dashboard: {str(e)}',
            'data': {
                'tareas_chart_data': [0, 0, 0, 0],
                'preventivo_counts': [0, 0, 0],
                'correctivo_counts': [0, 0, 0],
                'stats': {
                    'total_equipos': 0,
                    'tareas_pendientes': 0,
                    'tareas_en_progreso': 0,
                    'tareas_completadas': 0,
                    'tareas_vencidas': 0,
                    'productos_stock_bajo': 0,
                    'incidentes_pendientes': 0,
                    'piscinas_con_alerta': 0
                }
            }
        })


# ===== API PARA SISTEMA UNIVERSAL DE TAREAS =====

@csrf_exempt
@require_POST
def create_task_api(request):
    """API para crear tareas desde cualquier módulo"""
    try:
        import json
        data = json.loads(request.body)

        # Validar datos requeridos
        titulo = data.get('titulo', '').strip()
        descripcion = data.get('descripcion', '').strip()

        if not titulo or not descripcion:
            return JsonResponse({
                'success': False,
                'error': 'Título y descripción son requeridos'
            }, status=400)

        # Crear tarea con valores por defecto
        tarea = TareaMantenimiento.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            tipo=data.get('tipo', 'correctivo'),
            prioridad=data.get('prioridad', 'media'),
            estado='creada',
            ubicacion_solicitud=data.get('ubicacion_solicitud', ''),
            equipo_afectado=data.get('equipo_afectado', ''),
            tiempo_estimado_horas=float(data.get('tiempo_estimado', 1.0)),
            fecha_programada=timezone.now() + timezone.timedelta(hours=2),  # 2 horas por defecto
            modulo_origen=data.get('modulo_origen', 'desconocido'),
            origen_url=data.get('origen_url', ''),
        )

        # Asignar tipo de crucero por defecto si existe
        try:
            tipo_crucero_default = TipoCrucero.objects.filter(tipo='mediano').first()
            if tipo_crucero_default:
                tarea.tipo_crucero = tipo_crucero_default
                tarea.save()
        except Exception:
            pass  # Si no hay tipos de crucero, continuar

        return JsonResponse({
            'success': True,
            'task_id': tarea.id,
            'message': 'Tarea creada exitosamente',
            'task_url': f'/tareas/{tarea.id}/'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos JSON inválidos'
        }, status=400)
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)


@require_GET
def task_count_api(request):
    """API para obtener el conteo de tareas pendientes"""
    try:
        # Contar tareas pendientes de todos los módulos
        count = TareaMantenimiento.objects.filter(
            estado__in=['creada', 'planificada', 'asignada']
        ).count()

        return JsonResponse({
            'success': True,
            'count': count
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener conteo: {str(e)}',
            'count': 0
        }, status=500)


