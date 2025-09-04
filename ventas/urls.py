from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    # Dashboard y vistas principales
    path('', views.dashboard_ventas, name='dashboard'),
    path('ventas/', views.lista_ventas, name='lista_ventas'),
    path('ventas/nueva/', views.nueva_venta, name='nueva_venta'),
    path('ventas/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
    path('ventas/<int:venta_id>/editar/', views.editar_venta, name='editar_venta'),
    
    # Gestión de clientes
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/nuevo/', views.nuevo_cliente, name='nuevo_cliente'),
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
]
