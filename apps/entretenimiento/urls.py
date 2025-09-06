from django.urls import path
from . import views

app_name = 'entretenimiento'

urlpatterns = [
    path('<int:crucero_id>/', views.entretenimiento_view, name='entretenimiento'),
    path('registro/', views.registro_view, name='registro'),
]
