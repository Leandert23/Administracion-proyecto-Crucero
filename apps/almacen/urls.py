from django.urls import path
from . import views

urlpatterns = [
    path("<int:crucero_id>", views.mostrar_vista_almacen, name="vista_almacen"),
    path("inventario/paginas-producto/", views.inventario_paginas_producto, name="inventario_modal_ajax"),
    path("inventario/seleccion-producto/", views.buscar_productos, name="inventario_buscar_procutos"),
    path("crear-producto/", views.crear_producto, name="crear_producto"),
    path("registrar-lote/", views.registrar_lote, name="registrar_lote"),
    path("registrar-salida/", views.registrar_salida, name="registrar_salida"),
]
