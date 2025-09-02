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
        cache_key = f'dashboard_data_{crucero_id or "all"}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        from mantenimiento.models import (
            Equipo, TareaMantenimiento, InventarioProducto, 
            Piscina, TipoCrucero
        )
        
        # Filtros base
        equipment_filters = {}
        task_filters = {}
        inventory_filters = {}
        
        if crucero_id:
            equipment_filters['ubicacion__crucero_id'] = crucero_id
            task_filters['crucero_id'] = crucero_id
            inventory_filters['crucero_id'] = crucero_id
        
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
        
        result = {
            **equipment_summary,
            **task_summary,
            **inventory_summary,
            **chart_data,
            'last_updated': timezone.now()
        }
        
        # Guardar en cache por 2 minutos
        cache.set(cache_key, result, 120)
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
        from mantenimiento.models import TareaMantenimiento
        from django.db.models import Count, Q
        
        # Usar agregación para contar estados
        task_counts = TareaMantenimiento.objects.aggregate(
            pendientes=Count('id', filter=Q(estado__in=['creada', 'planificada', 'asignada'])),
            en_progreso=Count('id', filter=Q(estado='en_progreso')),
            completadas=Count('id', filter=Q(estado='completada')),
            vencidas=Count('id', filter=Q(
                estado__in=['creada', 'planificada', 'asignada'],
                fecha_programada__lt=timezone.now()
            ))
        )
        
        return {
            'tareas_pendientes': task_counts['pendientes'],
            'tareas_en_progreso': task_counts['en_progreso'],
            'tareas_completadas': task_counts['completadas'],
            'tareas_vencidas': task_counts['vencidas']
        }
    
    @staticmethod
    def _process_inventory_data(inventario_data):
        """Procesa datos de inventario de forma optimizada"""
        from mantenimiento.models import InventarioProducto
        from django.db.models import Count
        
        # Contar productos con stock bajo de forma más eficiente
        stock_bajo_count = InventarioProducto.objects.filter(
            stock_actual__lte=F('stock_minimo')
        ).count()
        
        return {'productos_stock_bajo': stock_bajo_count}
    
    @staticmethod
    def _get_chart_data():
        """Obtiene datos para gráficas de forma optimizada"""
        from mantenimiento.models import TipoCrucero, TareaMantenimiento
        from django.db.models import Count
        
        # Datos por tipo de crucero usando agregación
        chart_data = TipoCrucero.objects.annotate(
            preventivo_count=Count('tareamantenimiento', filter=Q(tareamantenimiento__tipo='preventivo')),
            correctivo_count=Count('tareamantenimiento', filter=Q(tareamantenimiento__tipo='correctivo'))
        ).values('tipo', 'preventivo_count', 'correctivo_count')
        
        crucero_labels = []
        preventivo_counts = []
        correctivo_counts = []
        
        for item in chart_data:
            crucero_labels.append(dict(SystemConfig.TIPOS_CRUCERO)[item['tipo']])
            preventivo_counts.append(item['preventivo_count'])
            correctivo_counts.append(item['correctivo_count'])
        
        return {
            'crucero_labels': crucero_labels,
            'preventivo_counts': preventivo_counts,
            'correctivo_counts': correctivo_counts
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
