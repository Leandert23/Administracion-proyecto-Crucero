


from django.urls import path
from .views import dashboard_view, proveedores_view, eliminar_proveedor, registrar_compra_view, compras_registradas_view, registrar_solicitud_compra_view, lista_solicitudes_view, detalle_solicitud_view, procesar_solicitud_view, historial_compras_view, procesar_materiales_solicitud_view, compras_lote_registradas_view, detalle_compra_lote_view, historial_compras_lote_view

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('proveedores/', proveedores_view, name='proveedores'),
    path('proveedores/eliminar/', eliminar_proveedor, name='eliminar_proveedor'),
    path('compras/registrar/', registrar_compra_view, name='registrar_compra'),
    path('compras/registradas/', compras_registradas_view, name='compras_registradas'),
    path('solicitudes/registrar/', registrar_solicitud_compra_view, name='registrar_solicitud_compra'),
    path('solicitudes/', lista_solicitudes_view, name='lista_solicitudes'),
    path('solicitudes/<int:solicitud_id>/', detalle_solicitud_view, name='detalle_solicitud'),
    path('solicitudes/<int:solicitud_id>/procesar/', procesar_solicitud_view, name='procesar_solicitud'),
    path('compras/historial/', historial_compras_view, name='historial_compras'),
    path('solicitudes/<int:solicitud_id>/procesar-materiales/', procesar_materiales_solicitud_view, name='procesar_materiales_solicitud'),
    path('compras/lotes/', compras_lote_registradas_view, name='compras_lote_registradas'),
    path('compras/lote/<int:compra_id>/', detalle_compra_lote_view, name='detalle_compra_lote'),
    path('compras/lotes/historial/', historial_compras_lote_view, name='historial_compras_lote'),
]
