"""
Sistema de notificaciones optimizado en tiempo real
"""
from typing import List, Dict
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal

from .config import SystemConfig


class NotificationService:
    """Servicio de notificaciones optimizado"""
    
    @staticmethod
    def get_critical_alerts() -> List[Dict]:
        """Obtiene alertas críticas del sistema"""
        alerts = []
        
        # Cache para evitar consultas repetitivas
        cache_key = 'critical_alerts'
        cached_alerts = cache.get(cache_key)
        
        if cached_alerts:
            return cached_alerts
        
        # Verificar piscinas críticas
        alerts.extend(NotificationService._check_critical_pools())
        
        # Verificar stock crítico
        alerts.extend(NotificationService._check_critical_inventory())
        
        # Verificar tareas vencidas críticas
        alerts.extend(NotificationService._check_critical_tasks())
        
        # Ordenar por prioridad
        alerts.sort(key=lambda x: x['priority'], reverse=True)
        
        # Cache por 30 segundos
        cache.set(cache_key, alerts, 30)
        return alerts
    
    @staticmethod
    def _check_critical_pools() -> List[Dict]:
        """Verifica piscinas con parámetros críticos"""
        from mantenimiento.models import Piscina
        
        alerts = []
        
        for piscina in Piscina.objects.filter(en_servicio=True):
            ultima_medicion = piscina.mediciones.first()
            
            if not ultima_medicion:
                alerts.append({
                    'type': 'critical',
                    'priority': 9,
                    'module': 'piscinas',
                    'title': 'Piscina sin mediciones',
                    'message': f'Piscina {piscina.nombre} no tiene mediciones registradas',
                    'action_url': f'/piscinas/medicion/crear/',
                    'timestamp': timezone.now()
                })
                continue
            
            # Verificar rangos críticos
            ph = ultima_medicion.ph
            cloro = ultima_medicion.cloro_mg_l
            
            if ph and SystemConfig.is_ph_critical(ph):
                alerts.append({
                    'type': 'critical',
                    'priority': 10,
                    'module': 'piscinas',
                    'title': 'pH Crítico',
                    'message': f'Piscina {piscina.nombre}: pH {ph} - ACCIÓN INMEDIATA REQUERIDA',
                    'action_url': f'/piscinas/medicion/crear/',
                    'timestamp': ultima_medicion.fecha_hora
                })
            
            if cloro and SystemConfig.is_cloro_critical(cloro):
                alerts.append({
                    'type': 'critical',
                    'priority': 10,
                    'module': 'piscinas',
                    'title': 'Cloro Crítico',
                    'message': f'Piscina {piscina.nombre}: Cloro {cloro} mg/L - ACCIÓN INMEDIATA REQUERIDA',
                    'action_url': f'/piscinas/medicion/crear/',
                    'timestamp': ultima_medicion.fecha_hora
                })
        
        return alerts
    
    @staticmethod
    def _check_critical_inventory() -> List[Dict]:
        """Verifica inventario crítico"""
        from mantenimiento.models import InventarioProducto
        from django.db.models import F
        
        alerts = []
        
        # Stock crítico (stock actual <= 0 o muy bajo)
        items_criticos = InventarioProducto.objects.filter(
            Q(stock_actual__lte=0) | Q(stock_actual__lte=F('stock_minimo') * Decimal('0.5'))
        )
        
        for item in items_criticos:
            if item.stock_actual <= 0:
                priority = 10
                title = 'Stock Agotado'
                message = f'{item.producto.nombre} - Stock agotado'
            else:
                priority = 8
                title = 'Stock Crítico'
                message = f'{item.producto.nombre} - Stock muy bajo ({item.stock_actual})'
            
            alerts.append({
                'type': 'critical',
                'priority': priority,
                'module': 'inventario',
                'title': title,
                'message': message,
                'action_url': f'/inventario/actualizar/{item.id}/',
                'timestamp': item.fecha_ultima_actualizacion
            })
        
        return alerts
    
    @staticmethod
    def _check_critical_tasks() -> List[Dict]:
        """Verifica tareas críticas vencidas"""
        from mantenimiento.models import TareaMantenimiento
        from datetime import timedelta
        
        alerts = []
        
        # Tareas vencidas con prioridad alta/crítica
        tareas_criticas_vencidas = TareaMantenimiento.objects.filter(
            estado__in=['creada', 'planificada', 'asignada'],
            prioridad__in=['alta', 'critica', 'emergencia'],
            fecha_programada__lt=timezone.now()
        )
        
        for tarea in tareas_criticas_vencidas:
            dias_vencida = (timezone.now().date() - tarea.fecha_programada.date()).days
            
            alerts.append({
                'type': 'critical',
                'priority': 9 if tarea.prioridad == 'emergencia' else 7,
                'module': 'tareas',
                'title': f'Tarea {tarea.prioridad.upper()} vencida',
                'message': f'{tarea.titulo} - Vencida hace {dias_vencida} días',
                'action_url': f'/tareas/{tarea.id}/',
                'timestamp': tarea.fecha_programada
            })
        
        return alerts
    
    @staticmethod
    def clear_cache():
        """Limpia cache de notificaciones"""
        cache.delete('critical_alerts')
        cache.delete('piscinas_alerts_data')
        cache.delete_many([f'dashboard_data_{key}' for key in ['all', '1', '2', '3']])


class AlertManager:
    """Gestor de alertas optimizado"""
    
    @staticmethod
    def get_dashboard_alerts(limit: int = 5) -> List[Dict]:
        """Obtiene alertas para mostrar en dashboard"""
        all_alerts = NotificationService.get_critical_alerts()
        return all_alerts[:limit]
    
    @staticmethod
    def get_alerts_by_module(module: str) -> List[Dict]:
        """Obtiene alertas de un módulo específico"""
        all_alerts = NotificationService.get_critical_alerts()
        return [alert for alert in all_alerts if alert['module'] == module]
    
    @staticmethod
    def get_alert_count() -> int:
        """Cuenta total de alertas críticas"""
        return len(NotificationService.get_critical_alerts())
    
    @staticmethod
    def mark_alert_seen(alert_id: str):
        """Marca una alerta como vista (para futuras implementaciones)"""
        # Implementación futura para tracking de alertas vistas
        pass
