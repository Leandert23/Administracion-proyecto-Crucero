from django.urls import path
from . import views

app_name = 'entretenimiento'

urlpatterns = [
    path('', views.entretenimiento_main_view, name='entretenimiento_main'),
    path('<int:crucero_id>/', views.entretenimiento_view, name='entretenimiento'),
    path('<int:crucero_id>/crear-actividad-pago/', views.crear_actividad_pago_view, name='crear_actividad_pago'),
    path('<int:crucero_id>/crear-actividad-rutinaria/', views.crear_actividad_rutinaria_view, name='crear_actividad_rutinaria'),
    path('<int:crucero_id>/api/actividades/', views.api_get_activities, name='api_actividades'),
    path('<int:crucero_id>/api/eliminar-actividad/', views.eliminar_actividad, name='eliminar_actividad'),
    path('eliminar-actividades-rutinarias/', views.eliminar_actividades_rutinarias, name='eliminar_actividades_rutinarias'),
    path('eliminar-actividades-pago/', views.eliminar_actividades_pago, name='eliminar_actividades_pago'),
    path('registro/', views.registro_view, name='registro'),
    path('<int:crucero_id>/cargar-datos-precargados/', views.cargar_datos_precargados, name='cargar_datos_precargados'),
]
