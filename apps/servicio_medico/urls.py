from django.contrib import admin
from django.urls import path
from .views import *



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', panel_inicio, name='panel_inicio'),
    path('prueba/', prueba, name= 'prueba de htmls'),
    path('servicio-medico/', panel_servicio_medico, name='panel_personal_medico'),
    path('servicio-medico/inventario/', panel_inventario, name='panel_inventario'),
    path('servicio-medico/agregar-historial-medico/', agregar_historial, name='agregar_historial'),
    path('servicio-medico/historial-medico/', historial_medico, name = 'historial_medico'),
    path('servicio-medico/mantenimiento/', comunicacion_mantenmiento, name='comunicacion_mantenimiento'),
    path('servicio-medico/modificar-cuarto/', modificar_cuartos, name='modificar_cuarto'),
    path('servicio-medico/historial-medico/editar/<int:paciente_id>/', editar_paciente, name='editar_paciente'),
    path('servicio-medico/historial-medico/eliminar/<int:paciente_id>/', eliminar_paciente, name='eliminar_paciente'),
    path('servicio-medico/inventario/agregar/', agregar_inventario, name='agregar_inventario'),






]
    
