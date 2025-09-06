from django.contrib import admin
from .models import Modulo, Rol, UsuarioRol, SolicitudCompra


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'modulo', 'tipo', 'activo']
    list_filter = ['modulo', 'tipo', 'activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['modulo', 'nombre']


@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'rol', 'esta_activo', 'fecha_asignacion', 'fecha_expiracion']
    list_filter = ['esta_activo', 'rol__modulo', 'fecha_asignacion']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'rol__nombre']
    ordering = ['-fecha_asignacion']
    raw_id_fields = ['usuario', 'asignado_por']


@admin.register(SolicitudCompra)
class SolicitudCompraAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'solicitante', 'modulo', 'estado', 'costo_estimado', 'fecha_solicitud']
    list_filter = ['estado', 'modulo', 'fecha_solicitud']
    search_fields = ['titulo', 'descripcion', 'solicitante__username']
    ordering = ['-fecha_solicitud']
    readonly_fields = ['fecha_solicitud']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('solicitante', 'modulo', 'aprobado_por')
