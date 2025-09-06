from django.contrib import admin
from django.urls import path
from .views import *



urlpatterns = [
    path('zzz', panel_inicio, name='panel_inicio_servicio_medico'),
    path('prueba/', prueba, name='prueba_de_htmls'),
    path('', panel_servicio_medico, name='panel_personal_medico'),
    path('inventario/', panel_inventario, name='panel_inventario'),
    path('agregar-historial-medico/', agregar_historial, name='agregar_historial'),
    path('historial-medico/', historial_medico, name='historial_medico'),
    path('mantenimiento/', comunicacion_mantenimiento, name='comunicacion_mantenimiento'),
    path('modificar-cuarto/', modificar_cuartos, name='modificar_cuarto'),
    path('historial-medico/editar/<int:paciente_id>/', editar_paciente, name='editar_paciente'),
    path('historial-medico/eliminar/<int:paciente_id>/', eliminar_paciente, name='eliminar_paciente'),
    path('inventario/agregar/', agregar_inventario, name='agregar_inventario'),
    path('inventario/editar/', agregar_inventario, name='editar_inventario'),
    
    
    # URLs para sistema de urgencias
    path('urgencias/', panel_urgencias, name='panel_urgencias'),
    path('api/urgencias/enviar/', api_enviar_urgencia, name='api_enviar_urgencia'),
    path('api/urgencias/atendida/<int:notificacion_id>/', api_marcar_atendida, name='api_marcar_atendida'),
    path('api/test/', api_test_urgencia, name='api_test_urgencia'),
    
    # URLs para gestión de historiales médicos
    path('api/historiales/generar-aleatorios/', api_generar_historiales_aleatorios, name='api_generar_historiales_aleatorios'),
    path('api/historiales/borrar-todos/', api_borrar_todos_historiales, name='api_borrar_todos_historiales'),
]

