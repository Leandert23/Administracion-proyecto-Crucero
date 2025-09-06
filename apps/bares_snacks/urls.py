from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('<int:crucero_id>/', views.bares_view, name='bares'),
    path('habitaciones/', views.habitaciones_list_api, name='habitaciones-list-api'),
    path('ingredientes-almacen/', views.ingredientes_almacen_api, name='ingredientes-almacen-api'),
    path('categorias-almacen/', views.categorias_almacen_api, name='categorias-almacen-api'),
    path('crear-producto-bar/', views.crear_producto_bar_api, name='crear-producto-bar-api'),
    path('productos-almacen-filtrados/', views.productos_almacen_filtrados_api, name='productos-almacen-filtrados-api'),
    path('productos-bar/', views.productos_bar_api, name='productos-bar-api'),
    path('disponibilidad-productos/', views.disponibilidad_productos_api, name='disponibilidad-productos-api'),
    path('eliminar-producto-bar/', views.eliminar_producto_bar_api, name='eliminar-producto-bar-api'),
    path('actualizar-producto-bar/', views.actualizar_producto_bar_api, name='actualizar-producto-bar-api'),
    path('producto-bar/<int:producto_id>/receta/', views.receta_producto_bar_api, name='receta-producto-bar-api'),
    path('producto-bar/<int:producto_id>/receta/guardar/', views.guardar_receta_producto_bar_api, name='guardar-receta-producto-bar-api'),
    path('crear-pedido/', views.crear_pedido_api, name='crear-pedido-api'),
    path('pedido/<int:pedido_id>/eliminar/', views.eliminar_pedido_api, name='eliminar-pedido-api'),
    path('bares/', views.bares_list_api, name='bares-list-api'),
    path('puntos-venta/', views.puntos_venta_bares_api, name='puntos-venta-bares-api'),
    path('pedidos/', views.pedidos_list_api, name='pedidos-list-api'),
    path('pedido/<int:pedido_id>/estado/', views.actualizar_estado_pedido_api, name='actualizar-estado-pedido-api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)