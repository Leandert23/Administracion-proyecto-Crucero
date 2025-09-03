from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),                        
    path("reservas/", views.reservas, name="reservas"),             
    path("reservas.html", views.reservas),
    path("viaje/<str:crucero>/", views.estado_viaje, name="estado_viaje"),
    path("reservas/<str:crucero>/habitaciones/", views.reservacion_habitaciones, name="reservacion_habitaciones"),
    path("habitacion/<str:crucero>/<int:habitacion_id>/reservar/", views.reservar_habitacion, name="reservar_habitacion"),
    path("reservas/<str:crucero>/entretenimiento/", views.catalogo_entretenimiento, name="catalogo_entretenimiento"),
    path("mis-reservas/<str:crucero>/", views.mis_reservas, name="mis_reservas"),
    path("entretenimiento/<str:crucero>/<int:entretenimiento_id>/reservar/",
     views.reservar_entretenimiento, name="reservar_entretenimiento"),
    path("mis-reservas/<str:crucero>/<int:reserva_id>/cancelar/", views.cancelar_reserva, name="cancelar_reserva"),
]




