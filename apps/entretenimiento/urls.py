from django.urls import path
from . import views

app_name = 'entretenimiento'

urlpatterns = [
    path('', views.entretenimiento_view, name='entretenimiento'),
    path('registro/', views.registro_view, name='registro'),
]
