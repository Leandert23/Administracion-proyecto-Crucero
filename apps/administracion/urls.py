from django.urls import path
from . import views

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard, name='dashboard'),

    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/crucero/<int:crucero_id>/', views.dashboard_crucero, name='dashboard_crucero'),
    path('dashboard/empresa/', views.dashboard_empresa, name='dashboard_empresa'),

    # Gestión de roles
    path('roles/', views.gestion_roles, name='gestion_roles'),

    # Estados
    path('sin-permisos/', views.sin_permisos, name='sin_permisos'),
]
