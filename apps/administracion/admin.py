from django.contrib import admin
from .models import Dashboard, Alerta, Habitaciones

admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['crucero', 'precio_combustible', 'costos_totales', 'ganancias_totales', 'presupuesto_estimado']
    list_filter = ['crucero']
    search_fields = ['crucero__nombre']
    fields = ['crucero', 'precio_combustible', 'costos_totales', 'ganancias_totales', 'presupuesto_estimado', 'num_pasajeros_actual', 'num_empleados_actual']
    
    def get_readonly_fields(self, request, obj=None):
        # Hacer que solo el precio_combustible sea editable por el administrador
        if obj:  # Si es una edición
            return ['crucero', 'costos_totales', 'ganancias_totales', 'presupuesto_estimado', 'num_pasajeros_actual', 'num_empleados_actual']
        return ['costos_totales', 'ganancias_totales', 'presupuesto_estimado', 'num_pasajeros_actual', 'num_empleados_actual']
    
    def get_fieldsets(self, request, obj=None):
        """Organizar los campos en secciones para mejor usabilidad"""
        return [
            ('Configuración del Crucero', {
                'fields': ['crucero', 'precio_combustible'],
                'description': 'Configure el precio del combustible para este crucero específico. Este valor se utiliza para calcular el presupuesto estimado.'
            }),
            ('Métricas Calculadas (Solo Lectura)', {
                'fields': ['costos_totales', 'ganancias_totales', 'presupuesto_estimado', 'num_pasajeros_actual', 'num_empleados_actual'],
                'description': 'Estos valores se calculan automáticamente basándose en las operaciones del crucero.'
            }),
        ]
    
admin.register(Habitaciones)
class HabitacionesAdmin(admin.ModelAdmin):
    list_display = ['nombre_usuario', 'tipo', 'cubierta', 'precio_base', 'costo_final', 'estado']
    list_filter = ['tipo', 'estado', 'cubierta__crucero']
    search_fields = ['nombre_usuario', 'ubicacion']

admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ['crucero', 'mensaje', 'fecha', 'leida']
    list_filter = ['leida', 'fecha', 'crucero__crucero']
    search_fields = ['mensaje', 'crucero__crucero__nombre']