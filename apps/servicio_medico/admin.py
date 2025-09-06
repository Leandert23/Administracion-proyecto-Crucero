from django.contrib import admin
from .models import Medico, Paciente, Inventario, Solicitudmedicamento , Instrumentaria , Insumo, NotificacionUrgencia

# Register your models here.
admin.site.register(Medico)
admin.site.register(Insumo)
admin.site.register(Paciente)
admin.site.register(Inventario)
admin.site.register(Solicitudmedicamento)
admin.site.register(Instrumentaria)

@admin.register(NotificacionUrgencia)
class NotificacionUrgenciaAdmin(admin.ModelAdmin):
    list_display = ['fecha_creacion', 'modulo_origen', 'solicitante', 'ubicacion', 'tipo_urgencia', 'estado']
    list_filter = ['estado', 'modulo_origen', 'fecha_creacion']
    search_fields = ['solicitante', 'ubicacion', 'tipo_urgencia', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_atendida']
    ordering = ['-fecha_creacion']

