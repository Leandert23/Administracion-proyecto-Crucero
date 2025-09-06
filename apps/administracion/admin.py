from django.contrib import admin
from .models import Administracion, Alerta, Modulo, Rol, UsuarioRol

@admin.register(Administracion)
class AdministracionAdmin(admin.ModelAdmin):
    list_display = ['crucero', 'costos_totales', 'ganancias_totales', 'presupuesto_estimado']
    list_filter = ['crucero']
    search_fields = ['crucero__nombre']

@admin.register(Alerta)
class AlertaAdmin(admin.ModelAdmin):
    list_display = ['mensaje', 'fecha', 'leida', 'administracion']
    list_filter = ['leida', 'fecha']
    search_fields = ['mensaje']

@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'modulo', 'activo']
    list_filter = ['tipo', 'modulo', 'activo']
    search_fields = ['nombre', 'modulo__nombre']
    list_select_related = ['modulo']

@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'rol', 'fecha_asignacion', 'fecha_expiracion', 'activo', 'asignado_por']
    list_filter = ['activo', 'fecha_asignacion', 'rol__modulo', 'rol__tipo']
    search_fields = ['usuario__username', 'usuario__email', 'rol__nombre']
    list_select_related = ['usuario', 'rol', 'rol__modulo', 'asignado_por']
    readonly_fields = ['fecha_asignacion']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'rol', 'rol__modulo', 'asignado_por')