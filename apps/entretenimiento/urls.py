from django.urls import path
from . import views

app_name = 'entretenimiento'

urlpatterns = [
    path('<int:crucero_id>/', views.entretenimiento_view, name='entretenimiento'),
    path('<int:crucero_id>/cargar-datos-precargados/', views.cargar_datos_precargados, name='cargar_datos_precargados'),
    path('<int:crucero_id>/crear-actividad-rutinaria/', views.crear_actividad_rutinaria_view, name='crear_actividad_rutinaria'),
    path('<int:crucero_id>/crear-actividad-pago/', views.crear_actividad_pago_view, name='crear_actividad_pago'),
    path('registro/', views.registro_view, name='registro'),
    path('eliminar-actividades-rutinarias/', views.eliminar_actividades_rutinarias, name='eliminar_actividades_rutinarias'),
    path('eliminar-actividades-pago/', views.eliminar_actividades_pago, name='eliminar_actividades_pago'),
    path('<int:crucero_id>/api/actividades/', views.api_get_activities, name='api_get_activities'),
    path('<int:crucero_id>/api/eliminar-actividad/', views.api_delete_activity, name='api_delete_activity'),
]
