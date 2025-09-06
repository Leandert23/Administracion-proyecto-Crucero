from django.urls import path
from . import views

urlpatterns = [
    path("z", views.inicio, name="inicio"),
    path("<str:crucero>/", views.reservas, name="reservas"),

    # Catálogos
    path("<str:crucero>/habitaciones/", views.reservacion_habitaciones, name="reservacion_habitaciones"),
    path("<str:crucero>/entretenimiento/", views.catalogo_entretenimiento, name="catalogo_entretenimiento"),
    path("<str:crucero>/restaurantes/", views.reservar_restaurante, name="reservar_restaurante"),

    # Reservas
    path("<str:crucero>/habitaciones/<int:habitacion_id>/reservar/", views.reservar_habitacion, name="reservar_habitacion"),
    path("<str:crucero>/entretenimiento/<int:entretenimiento_id>/reservar/", views.reservar_entretenimiento, name="reservar_entretenimiento"),
    path("<str:crucero>/restaurantes/italiano/", views.primer_restaurante, name="primer_restaurante"),
    path("<str:crucero>/restaurantes/árabe/", views.segundo_restaurante, name="segundo_restaurante"),
    path("<str:crucero>/restaurantes/mesa/<int:mesa_id>/", views.reservar_mesa, name="reservar_mesa"),
    path("<str:crucero>/evento/", views.organizar_evento, name="organizar_evento"),

    # Mis reservas y cancelar
    path("<str:crucero>/mis/", views.mis_reservas, name="mis_reservas"),
    path("<str:crucero>/cancelar/<int:reserva_id>/", views.cancelar_reserva, name="cancelar_reserva"),

    # API para nueva reserva
    path("<str:crucero>/api/tipos-habitacion/", views.api_tipos_habitacion, name="api_tipos_habitacion"),
    path("<str:crucero>/api/habitacion-disponible/", views.api_habitacion_disponible, name="api_habitacion_disponible"),
    path("<str:crucero>/api/crear-reserva/", views.api_crear_reserva, name="api_crear_reserva"),

    # API para reserva de entretenimiento
    path("<str:crucero>/api/buscar-cliente/", views.api_buscar_cliente_por_habitacion, name="api_buscar_cliente"),
    path("<str:crucero>/api/actividades-pago/", views.api_actividades_pago_disponibles, name="api_actividades_pago"),
    path("<str:crucero>/api/actividades-gratuitas/", views.api_actividades_gratuitas_disponibles, name="api_actividades_gratuitas"),
    path("<str:crucero>/api/crear-reserva-entretenimiento/", views.api_crear_reserva_entretenimiento, name="api_crear_reserva_entretenimiento"),

    # API para ver reservas
    path("<str:crucero>/api/ver-reservas/", views.api_ver_reservas, name="api_ver_reservas"),
]




