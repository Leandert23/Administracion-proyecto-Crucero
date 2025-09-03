from django.contrib import admin
from django.urls import path
from .views import panel_personal_medico , panel_inicio , panel_inventario , agregar_historial , historial_medico , prueba



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', panel_inicio, name='panel_inicio'),
    path('prueba/', prueba, name= 'prueba de htmls'),
    path('personal-medico/', panel_personal_medico, name='panel_personal_medico'),
    path('inventario/', panel_inventario, name='panel_inventario'),
    path('agregar-historial-medico/', agregar_historial, name='agregar_historial'),
    path('historial-medico/', historial_medico, name = 'historial_medico'),


]
    
