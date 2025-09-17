from django.urls import path
from django.shortcuts import render
from . import views
from .Views.sales import sell_product_view

app_name = 'ventas'

urlpatterns = [
    # Vista principal con crucero_id 
    path('<int:crucero_id>/', views.dashboard_ventas, name='ventas'),
    
    # Ventas con crucero_id
    path('<int:crucero_id>/ventas/', views.lista_ventas, name='lista_ventas'),
    path('<int:crucero_id>/ventas/nueva/', views.nueva_venta, name='nueva_venta'),
    path('<int:crucero_id>/ventas/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
    path('<int:crucero_id>/ventas/<int:venta_id>/editar/', views.editar_venta, name='editar_venta'),
    
    # Gestión de clientes con crucero_id
    path('<int:crucero_id>/clientes/', views.lista_clientes, name='lista_clientes'),
    path('<int:crucero_id>/clientes/nuevo/', views.nuevo_cliente, name='nuevo_cliente'),
    path('<int:crucero_id>/clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    path('<int:crucero_id>/sell/', sell_product_view, name='sell_product'),
    path('<int:crucero_id>/sale_success/', lambda request, crucero_id: render(request, 'ventas/sale_success.html'), name='sale_success'),
    path('<int:crucero_id>/sale_fail/', lambda request, crucero_id: render(request, 'ventas/sale_fail.html'), name='sale_fail'),
    
    # ========== URLs PARA VENTAS DE HABITACIONES ==========
    # Vista principal de ventas de habitaciones por embarcación
    path('habitaciones/<int:embarcacion_id>/', views.ventas_habitaciones_home, name='ventas_habitaciones_home'),
    
    # Venta de habitaciones
    path('habitaciones/<int:embarcacion_id>/vender/<int:habitacion_id>/', views.vender_habitacion, name='vender_habitacion'),
    
    # Listado y detalles de ventas por embarcación
    path('habitaciones/<int:embarcacion_id>/ventas/', views.lista_ventas_habitaciones, name='lista_ventas_habitaciones'),
    path('habitaciones/<int:embarcacion_id>/ventas/<int:venta_id>/', views.detalle_venta_habitacion, name='detalle_venta_habitacion'),
]
