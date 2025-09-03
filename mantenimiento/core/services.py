"""
Servicios optimizados del sistema con cache
"""
from typing import Dict, List, Optional
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import F, Q, Count
from django.db import models
from django.core.cache import cache
from django.conf import settings

from .config import SystemConfig


class DashboardService:
    """Servicio optimizado para el dashboard"""
    
    @staticmethod
    def get_dashboard_data(crucero_id: Optional[int] = None):
        """Obtiene todos los datos del dashboard de forma optimizada con cache"""
        
        # Clave de cache única por crucero
        cache_key = f'dashboard_data_v2_{crucero_id or "all"}'
        cached_data = cache.get(cache_key)
        from mantenimiento.models import (
            Equipo, TareaMantenimiento, InventarioProducto, 
            Piscina, TipoCrucero
        )
        
        # Filtros base (sin limitar por crucero para reflejar todo el sistema)
        equipment_filters = {}
        task_filters = {}
        inventory_filters = {}
        
        # Si hay cache, mezclar con datos dinámicos (incidentes) para no mostrar vacío
        if cached_data:
            dynamic_incidents = DashboardService._get_incidents_data(crucero_id)
            merged = {**cached_data, **dynamic_incidents, 'last_updated': timezone.now()}
            return merged

        # Una sola consulta por modelo para eficiencia
        equipos_data = Equipo.objects.filter(**equipment_filters).values('estado').distinct()
        tareas_data = TareaMantenimiento.objects.filter(**task_filters).values('estado', 'tipo').distinct()
        inventario_data = InventarioProducto.objects.filter(**inventory_filters).annotate(
            es_stock_bajo=F('stock_actual') <= F('stock_minimo')
        )
        
        # Procesar datos
        equipment_summary = DashboardService._process_equipment_data(equipos_data)
        task_summary = DashboardService._process_task_data(tareas_data)
        inventory_summary = DashboardService._process_inventory_data(inventario_data)
        chart_data = DashboardService._get_chart_data()
        
        # Obtener datos adicionales para el dashboard
        additional_data = DashboardService._get_additional_data()
        # Datos dinámicos (no cacheables): incidentes
        dynamic_incidents = DashboardService._get_incidents_data(crucero_id)
        
        result = {
            **equipment_summary,
            **task_summary,
            **inventory_summary,
            **chart_data,
            **additional_data,
            **dynamic_incidents,
            'last_updated': timezone.now()
        }
        
        # Guardar en cache por 10s para frescura
        cache.set(cache_key, result, 10)
        return result
    
    @staticmethod
    def _process_equipment_data(equipos_data):
        """Procesa datos de equipos de forma optimizada"""
        from mantenimiento.models import Equipo
        
        # Contar por estado usando agregación
        counts = Equipo.objects.values('estado').annotate(count=models.Count('id'))
        estado_counts = {item['estado']: item['count'] for item in counts}
        
        return {
            'total_equipos': sum(estado_counts.values()),
            'equipos_operativos': estado_counts.get('operativo', 0),
            'equipos_mantenimiento': estado_counts.get('mantenimiento', 0),
            'equipos_averiados': estado_counts.get('averiado', 0),
            'equipos_fuera_servicio': estado_counts.get('fuera_servicio', 0)
        }
    
    @staticmethod
    def _process_task_data(tareas_data):
        """Procesa datos de tareas de forma optimizada"""
        from mantenimiento.models import TareaMantenimiento, ReporteIncidente
        
        try:
            # Contar estados de tareas de forma simple
            pendientes = TareaMantenimiento.objects.filter(estado__in=['creada', 'planificada', 'asignada']).count()
            en_progreso = TareaMantenimiento.objects.filter(estado='en_progreso').count()
            completadas = TareaMantenimiento.objects.filter(estado='completada').count()
            
            # Contar vencidas sin usar comparaciones complejas
            try:
                vencidas = TareaMantenimiento.objects.filter(
                    estado__in=['creada', 'planificada', 'asignada'],
                    fecha_programada__lt=timezone.now()
                ).count()
            except:
                vencidas = 0
            
            # Contar incidentes pendientes (no resueltos)
            try:
                incidentes_pendientes = ReporteIncidente.objects.filter(resuelto=False).count()
            except:
                incidentes_pendientes = 0
            
            return {
                'tareas_pendientes': pendientes,
                'tareas_en_progreso': en_progreso,
                'tareas_completadas': completadas,
                'tareas_vencidas': vencidas,
                'incidentes_pendientes': incidentes_pendientes
            }
        except Exception:
            # Fallback con datos por defecto
            return {
                'tareas_pendientes': 0,
                'tareas_en_progreso': 0,
                'tareas_completadas': 0,
                'tareas_vencidas': 0,
                'incidentes_pendientes': 0
            }
    
    @staticmethod
    def _process_inventory_data(inventario_data):
        """Procesa datos de inventario de forma optimizada"""
        from mantenimiento.models import InventarioProducto
        from django.db.models import Count
        
        # Contar productos con stock bajo de forma más eficiente
        try:
            stock_bajo_count = InventarioProducto.objects.filter(
                stock_actual__lte=F('stock_minimo')
            ).count()
        except Exception:
            # Fallback si hay problemas con la comparación F
            stock_bajo_count = 0
            try:
                for item in InventarioProducto.objects.all():
                    if item.stock_actual <= item.stock_minimo:
                        stock_bajo_count += 1
            except:
                pass
        
        return {'productos_stock_bajo': stock_bajo_count}
    
    @staticmethod
    def _get_chart_data():
        """Obtiene datos para gráficas de forma optimizada"""
        from mantenimiento.models import TareaMantenimiento
        from django.db.models import Count
        
        try:
            # Obtener datos de tareas para el gráfico principal
            task_counts = TareaMantenimiento.objects.aggregate(
                pendientes=Count('id', filter=Q(estado__in=['creada', 'planificada', 'asignada'])),
                en_progreso=Count('id', filter=Q(estado='en_progreso')),
                completadas=Count('id', filter=Q(estado='completada')),
                vencidas=Count('id', filter=Q(
                    estado__in=['creada', 'planificada', 'asignada'],
                    fecha_programada__lt=timezone.now()
                ))
            )
            
            # Datos para gráfico de tareas
            tareas_chart_data = [
                task_counts['pendientes'] or 0,
                task_counts['en_progreso'] or 0, 
                task_counts['completadas'] or 0,
                task_counts['vencidas'] or 0
            ]
        except Exception:
            # Fallback para datos de tareas
            tareas_chart_data = [0, 0, 0, 0]
        
        # Datos por tipo de crucero simplificados
        try:
            from mantenimiento.models import TipoCrucero
            
            preventivo_counts = []
            correctivo_counts = []
            crucero_labels = []
            
            # Obtener datos manualmente para evitar problemas de agregación compleja
            for tipo_key, tipo_display in SystemConfig.TIPOS_CRUCERO:
                try:
                    preventivo_count = TareaMantenimiento.objects.filter(
                        tipo_crucero__tipo=tipo_key, 
                        tipo='preventivo'
                    ).count()
                    correctivo_count = TareaMantenimiento.objects.filter(
                        tipo_crucero__tipo=tipo_key, 
                        tipo='correctivo'
                    ).count()
                except:
                    preventivo_count = 0
                    correctivo_count = 0
                
                crucero_labels.append(tipo_display)
                preventivo_counts.append(preventivo_count)
                correctivo_counts.append(correctivo_count)
                
        except Exception:
            # Fallback con datos por defecto
            crucero_labels = ['Crucero Pequeño', 'Crucero Mediano', 'Crucero Grande']
            preventivo_counts = [0, 0, 0]
            correctivo_counts = [0, 0, 0]
        
        return {
            'tareas_chart_data': tareas_chart_data,
            'crucero_labels': crucero_labels,
            'preventivo_counts': preventivo_counts,
            'correctivo_counts': correctivo_counts
        }
    
    @staticmethod
    def _get_additional_data():
        """Obtiene datos adicionales reales para el dashboard (sin limitar por crucero)."""
        from datetime import timedelta
        try:
            from mantenimiento.models import TareaMantenimiento, Equipo, Piscina
            # Tareas próximas a vencer (7 días)
            fecha_limite = timezone.now() + timedelta(days=7)
            proximas_vencer = list(
                TareaMantenimiento.objects.filter(
                    estado__in=['creada', 'planificada', 'asignada'],
                    fecha_programada__gt=timezone.now(),
                    fecha_programada__lte=fecha_limite
                ).select_related('ubicacion').order_by('fecha_programada')[:5]
            )
            for tarea in proximas_vencer:
                try:
                    tarea.dias_vencimiento = (tarea.fecha_programada.date() - timezone.now().date()).days
                except Exception:
                    tarea.dias_vencimiento = ''

            # Equipos con revisión próxima (30 días)
            fecha_limite_equipos = timezone.now() + timedelta(days=30)
            equipos_revision_proxima = list(
                Equipo.objects.filter(
                    estado='operativo',
                    proxima_revision__gt=timezone.now(),
                    proxima_revision__lte=fecha_limite_equipos
                ).select_related('ubicacion').order_by('proxima_revision')[:5]
            )
            for eq in equipos_revision_proxima:
                try:
                    eq.dias_hasta_revision = (eq.proxima_revision.date() - timezone.now().date()).days
                except Exception:
                    eq.dias_hasta_revision = ''

            # Piscinas con alerta (sin medición en 2 días o última fuera de rango)
            piscinas_con_alerta = 0
            try:
                from mantenimiento.models import MedicionPiscina
                limite = timezone.now() - timedelta(days=2)
                for p in Piscina.objects.all():
                    m = p.mediciones.first()
                    if not m or m.fecha_hora < limite or m.necesita_alerta:
                        piscinas_con_alerta += 1
            except Exception:
                piscinas_con_alerta = 0

            return {
                'proximas_vencer': proximas_vencer,
                'equipos_revision_proxima': equipos_revision_proxima,
                'piscinas_con_alerta': piscinas_con_alerta,
                'crucero_progress': [
                    {'label': 'Crucero Pequeño', 'total': 0, 'preventivo': 0, 'correctivo': 0, 'percent': 0, 'color': 'bg-info'},
                    {'label': 'Crucero Mediano', 'total': 0, 'preventivo': 0, 'correctivo': 0, 'percent': 0, 'color': 'bg-primary'},
                    {'label': 'Crucero Grande', 'total': 0, 'preventivo': 0, 'correctivo': 0, 'percent': 0, 'color': 'bg-success'}
                ],
                'crucero_segments': [
                    {'id': 'pequeño', 'label': 'Crucero Pequeño', 'preventivo': 0, 'correctivo': 0},
                    {'id': 'mediano', 'label': 'Crucero Mediano', 'preventivo': 0, 'correctivo': 0},
                    {'id': 'grande', 'label': 'Crucero Grande', 'preventivo': 0, 'correctivo': 0}
                ],
                'now': timezone.now()
            }
        except Exception:
            return {
                'proximas_vencer': [],
                'equipos_revision_proxima': [],
                'piscinas_con_alerta': 0,
                'crucero_progress': [],
                'crucero_segments': [],
                'now': timezone.now()
            }

    @staticmethod
    def _get_incidents_data(crucero_id: Optional[int] = None):
        """Datos dinámicos de incidentes (no cacheables)."""
        from mantenimiento.models import ReporteIncidente
        filters = {}
        if crucero_id:
            # Filtrar por crucero en la ubicación
            filters['ubicacion__crucero_id'] = crucero_id
        incidentes_recientes = list(
            ReporteIncidente.objects.select_related('ubicacion', 'equipo')
            .filter(**filters)
            .order_by('-fecha_reporte')[:5]
        )
        # Si no hay resultados y había filtro por crucero, caer a global
        if not incidentes_recientes and filters:
            incidentes_recientes = list(
                ReporteIncidente.objects.select_related('ubicacion', 'equipo')
                .order_by('-fecha_reporte')[:5]
            )

        incidentes_pendientes_list = list(
            ReporteIncidente.objects.select_related('ubicacion', 'equipo')
            .filter(resuelto=False, **filters)
            .order_by('-fecha_reporte')[:5]
        )
        if not incidentes_pendientes_list and filters:
            incidentes_pendientes_list = list(
                ReporteIncidente.objects.select_related('ubicacion', 'equipo')
                .filter(resuelto=False)
                .order_by('-fecha_reporte')[:5]
            )
        return {
            'incidentes_recientes': incidentes_recientes,
            'incidentes_pendientes_list': incidentes_pendientes_list,
        }
    



class PiscinaService:
    """Servicio optimizado para piscinas"""
    
    @staticmethod
    def get_piscinas_with_alerts():
        """Obtiene piscinas con alertas de forma optimizada con cache"""
        
        cache_key = 'piscinas_alerts_data'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        from mantenimiento.models import Piscina
        
        # Una sola consulta con prefetch para optimizar
        piscinas = Piscina.objects.select_related('ubicacion', 'tipo_crucero').prefetch_related('mediciones')
        
        result = []
        for piscina in piscinas:
            # Usar first() que está optimizado
            ultima_medicion = piscina.mediciones.first()
            
            alert_info = {
                'piscina': piscina,
                'ultima_medicion': ultima_medicion,
                'tiene_alerta': False,
                'tipo_alerta': ''
            }
            
            if ultima_medicion:
                if ultima_medicion.necesita_alerta:
                    alert_info['tiene_alerta'] = True
                    alert_info['tipo_alerta'] = ultima_medicion.tipo_alerta
                
                # Verificar días sin medición
                dias_sin_medicion = (timezone.now().date() - ultima_medicion.fecha_hora.date()).days
                if dias_sin_medicion > 1:
                    alert_info['tiene_alerta'] = True
                    if alert_info['tipo_alerta']:
                        alert_info['tipo_alerta'] += ' / '
                    alert_info['tipo_alerta'] += f'SIN MEDICIÓN ({dias_sin_medicion} días)'
            else:
                alert_info['tiene_alerta'] = True
                alert_info['tipo_alerta'] = 'SIN MEDICIONES'
            
            result.append(alert_info)
        
        # Guardar en cache por 1 minuto
        cache.set(cache_key, result, 60)
        return result
    
    @staticmethod
    def get_trends_data(piscina_id: int, days: int = 14):
        """Obtiene datos de tendencias optimizado"""
        from mantenimiento.models import Piscina
        from datetime import timedelta
        
        try:
            piscina = Piscina.objects.select_related('ubicacion').get(pk=piscina_id)
        except Piscina.DoesNotExist:
            return None
        
        fecha_limite = timezone.now() - timedelta(days=days)
        mediciones = piscina.mediciones.filter(
            fecha_hora__gte=fecha_limite
        ).order_by('fecha_hora').values('fecha_hora', 'ph', 'cloro_mg_l', 'temperatura_c')
        
        # Procesar datos para gráficas
        fechas = []
        ph_values = []
        cloro_values = []
        temperatura_values = []
        
        for m in mediciones:
            fechas.append(m['fecha_hora'].strftime('%Y-%m-%d %H:%M'))
            ph_values.append(float(m['ph']) if m['ph'] else None)
            cloro_values.append(float(m['cloro_mg_l']) if m['cloro_mg_l'] else None)
            temperatura_values.append(float(m['temperatura_c']) if m['temperatura_c'] else None)
        
        return {
            'piscina': piscina,
            'fechas': fechas,
            'ph_values': ph_values,
            'cloro_values': cloro_values,
            'temperatura_values': temperatura_values
        }


class ValidationService:
    """Servicio de validaciones optimizado"""
    
    @staticmethod
    def validate_task_creation(task_data: Dict) -> bool:
        """Valida creación de tarea de forma optimizada"""
        # Validaciones críticas en una sola función
        if task_data.get('tiempo_estimado_horas', 0) > SystemConfig.MAX_HORAS_TAREA:
            raise ValidationError(f'El tiempo estimado no puede exceder {SystemConfig.MAX_HORAS_TAREA} horas')
        
        if task_data.get('tipo') == 'emergencia' and task_data.get('prioridad') not in ['alta', 'critica', 'emergencia']:
            raise ValidationError('Las tareas de emergencia deben tener prioridad alta, crítica o emergencia')
        
        return True
    
    @staticmethod
    def validate_medicion_piscina(ph: Decimal, cloro: Decimal) -> Optional[str]:
        """Valida medición de piscina y retorna alerta si es necesaria"""
        alertas = []
        
        if SystemConfig.is_ph_critical(ph):
            if ph < SystemConfig.PH_RANGO_CRITICO[0]:
                alertas.append('pH CRÍTICO BAJO')
            else:
                alertas.append('pH CRÍTICO ALTO')
        
        if SystemConfig.is_cloro_critical(cloro):
            if cloro < SystemConfig.CLORO_RANGO_CRITICO[0]:
                alertas.append('CLORO CRÍTICO BAJO')
            else:
                alertas.append('CLORO CRÍTICO ALTO')
        
        return ' / '.join(alertas) if alertas else None
    
    @staticmethod
    def validate_stock_operation(stock_actual: Decimal, cantidad_operacion: Decimal) -> bool:
        """Valida operación de stock"""
        if stock_actual - cantidad_operacion < 0:
            raise ValidationError('Stock insuficiente para la operación')
        return True
