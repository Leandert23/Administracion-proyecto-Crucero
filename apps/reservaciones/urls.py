from django.urls import path
from . import views

urlpatterns = [
    path("z", views.inicio, name="inicio"),
    path("", views.reservas, name="reservas"),

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
]




