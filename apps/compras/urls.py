from django.urls import path

from .views import dashboard_view, proveedores_view, eliminar_proveedor, registrar_solicitud_compra_view, lista_solicitudes_view, detalle_solicitud_view, procesar_solicitud_view, historial_compras_view, procesar_materiales_solicitud_view, compras_lote_registradas_view, detalle_compra_lote_view, revision_problemas_view

urlpatterns = [
    path('<int:embarcacion_id>/', dashboard_view, name='compras'),
    path('<int:embarcacion_id>/proveedores/', proveedores_view, name='proveedores'),
    path('<int:embarcacion_id>/proveedores/eliminar/', eliminar_proveedor, name='eliminar_proveedor'),
    path('<int:embarcacion_id>/solicitudes/registrar/', registrar_solicitud_compra_view, name='registrar_solicitud_compra'),
    path('<int:embarcacion_id>/solicitudes/', lista_solicitudes_view, name='lista_solicitudes'),
    path('<int:embarcacion_id>/solicitudes/<int:solicitud_id>/', detalle_solicitud_view, name='detalle_solicitud'),
    path('<int:embarcacion_id>/solicitudes/<int:solicitud_id>/procesar/', procesar_solicitud_view, name='procesar_solicitud'),
    path('<int:embarcacion_id>/compras/historial/', historial_compras_view, name='historial_compras'),
    path('<int:embarcacion_id>/compras/revision/', revision_problemas_view, name='revision_problemas'),
    path('<int:embarcacion_id>/solicitudes/<int:solicitud_id>/procesar-materiales/', procesar_materiales_solicitud_view, name='procesar_materiales_solicitud'),
    path('<int:embarcacion_id>/compras/lotes/', compras_lote_registradas_view, name='compras_lote_registradas'),
    path('<int:embarcacion_id>/compras/lote/<int:compra_id>/', detalle_compra_lote_view, name='detalle_compra_lote'),
]
