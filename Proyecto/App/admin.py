from django.contrib import admin
from .models import TipoHabitacion, Habitacion, Reserva, Entretenimiento
from .models import Viaje, Itinerario

@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ("nombre", "dia_actual", "total_dias")
    list_filter = ("total_dias",)
    search_fields = ("nombre",)

@admin.register(Itinerario)
class ItinerarioAdmin(admin.ModelAdmin):
    list_display = ("viaje", "dia", "destino")
    list_filter = ("viaje", "dia")
    search_fields = ("destino",)

@admin.register(TipoHabitacion)
class TipoHabitacionAdmin(admin.ModelAdmin):
    list_display = ("categoria", "subtipo", "capacidad", "precio_base")

@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ("numero", "piso", "lado", "vista_mar", "tipo_habitacion", "reservada")
    list_filter = ("piso", "lado", "vista_mar", "reservada")
    search_fields = ("numero",)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "habitacion", "fecha_inicio", "fecha_fin", "estado")
    list_filter = ("estado", "fecha_inicio", "fecha_fin")
    search_fields = ("usuario__username", "habitacion__numero")

@admin.register(Entretenimiento)
class EntretenimientoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "crucero", "precio", "reservada")
    list_filter = ("crucero", "reservada")
    search_fields = ("nombre",)
