from django.urls import path
from . import views

urlpatterns = [
    path("<int:crucero_id>", views.mostrar_vista_almacen, name="vista_almacen"),
    path("buscar/", views.buscar_producto, name="buscar_producto"),
    path("inventario/modal-ajax/", views.inventario_modal_ajax, name="inventario_modal_ajax"),
]
