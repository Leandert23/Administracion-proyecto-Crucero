from django.contrib import admin
from .models import ConfiguracionSistema, LogActividad, BackupSistema, ReporteSistema


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'valor', 'fecha_actualizacion']
    list_filter = ['fecha_creacion', 'fecha_actualizacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(LogActividad)
class LogActividadAdmin(admin.ModelAdmin):
    list_display = ['fecha_hora', 'usuario', 'tipo_actividad', 'modulo', 'descripcion']
    list_filter = ['tipo_actividad', 'modulo', 'fecha_hora', 'crucero']
    search_fields = ['descripcion', 'usuario__username', 'modulo']
    readonly_fields = ['fecha_hora']
    date_hierarchy = 'fecha_hora'


@admin.register(BackupSistema)
class BackupSistemaAdmin(admin.ModelAdmin):
    list_display = ['nombre_archivo', 'estado', 'tamaño_archivo', 'fecha_creacion', 'usuario']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['nombre_archivo', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_completado']


@admin.register(ReporteSistema)
class ReporteSistemaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo_reporte', 'fecha_generacion', 'usuario', 'crucero']
    list_filter = ['tipo_reporte', 'fecha_generacion', 'crucero']
    search_fields = ['nombre', 'usuario__username']
    readonly_fields = ['fecha_generacion']
