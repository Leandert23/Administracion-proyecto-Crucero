from django.urls import path
from . import views
from .Views.sales import sell_product_view

app_name = 'ventas'

urlpatterns = [
    # Vista principal con crucero_id 
    path('<int:crucero_id>/', views.dashboard_ventas, name='dashboard'),
    
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
]
