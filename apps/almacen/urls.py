from django.urls import path
from . import views

urlpatterns = [
    path("<int:crucero_id>", views.mostrar_vista_almacen, name="vista_almacen"),
    path("inventario/modal-ajax/", views.inventario_modal_ajax, name="inventario_modal_ajax"),
    path("crear-producto/", views.crear_producto, name="crear_producto"),
]
