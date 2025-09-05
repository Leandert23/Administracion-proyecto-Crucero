from django.contrib import admin
from django.urls import path
from .views import *



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', panel_inicio, name='panel_inicio'),
    path('prueba/', prueba, name='prueba_de_htmls'),
    path('panel/', panel_servicio_medico, name='panel_personal_medico'),
    path('inventario/', panel_inventario, name='panel_inventario'),
    path('agregar-historial-medico/', agregar_historial, name='agregar_historial'),
    path('historial-medico/', historial_medico, name='historial_medico'),
    path('mantenimiento/', comunicacion_mantenimiento, name='comunicacion_mantenimiento'),
    path('modificar-cuarto/', modificar_cuartos, name='modificar_cuarto'),
    path('historial-medico/editar/<int:paciente_id>/', editar_paciente, name='editar_paciente'),
    path('historial-medico/eliminar/<int:paciente_id>/', eliminar_paciente, name='eliminar_paciente'),
    path('inventario/agregar/', agregar_inventario, name='agregar_inventario'),
    path('inventario/editar/', agregar_inventario, name='editar_inventario'),
]

