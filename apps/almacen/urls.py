from django.urls import path
from .Views import general, inventario, lotes, mermas, productos

urlpatterns = [
    path("<int:crucero_id>", general.mostrar_vista_almacen, name="vista_almacen"),
    
    path("crear-producto/", productos.crear_producto, name="crear_producto"),
    path("delete-producto/", productos.eliminar_producto, name="eliminar_producto"),
    path("update-producto/", productos.actualizar_producto, name="actualizar_producto"),
    
    path("registrar-lote/", lotes.registrar_lote, name="registrar_lote"),
    path("registrar-salida/", lotes.registrar_salida, name="registrar_salida"),
    
    path("inventario/paginas-producto/", inventario.obtener_pagina_inventario_productos, name="inventario_pagina_inventario_productos"),
    path("inventario/seleccion-producto/", inventario.buscar_productos, name="inventario_buscar_procutos"),    
    path("inventario/movimientos/", inventario.obtener_movimientos_inventario, name="inventario_tabla_movimientos"),
    path("inventario/producto/", inventario.obtener_detalle_producto, name="inventario_detalle_producto"),
    path("inventario/lotes/", inventario.obtener_lotes_producto, name="inventario_lotes_producto"),
    path("inventario/lotes-json/", inventario.obtener_lotes_producto_json, name="inventario_lotes_producto_json"),
    
    path("registrar-merma/", mermas.registrar_merma, name="registrar_merma"),
    path("ordenes-compra/por-registrar/", general.obtener_ordenes_compra_por_registrar, name="ordenes_compra_por_registrar"),
    path("ordenes-compra/detalle/<int:orden_id>/", general.detalle_orden_compra, name="orden_compra_detalle"),
]
