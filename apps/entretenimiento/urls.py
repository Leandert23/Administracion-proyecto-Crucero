from django.urls import path
from . import views

app_name = 'entretenimiento'

urlpatterns = [
    path('<int:crucero_id>/', views.entretenimiento_view, name='entretenimiento'),
    path('<int:crucero_id>/cargar-datos-precargados/', views.cargar_datos_precargados, name='cargar_datos_precargados'),
    path('registro/', views.registro_view, name='registro'),
    path('eliminar-actividades-rutinarias/', views.eliminar_actividades_rutinarias, name='eliminar_actividades_rutinarias'),
    path('eliminar-actividades-pago/', views.eliminar_actividades_pago, name='eliminar_actividades_pago'),
]
