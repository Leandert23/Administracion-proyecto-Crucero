from django.contrib import admin
from .models import Restaurante, Mesa, Entretenimiento, EventoPersonalizado, Reserva
from . import utils

@admin.action(description="Rellenar habitaciones para el crucero seleccionado")
def accion_rellenar_habitaciones(modeladmin, request, queryset):
    for viaje in queryset:
        utils.rellenar_habitaciones(viaje.crucero)

@admin.action(description="Borrar habitaciones del crucero seleccionado")
def accion_borrar_habitaciones(modeladmin, request, queryset):
    for viaje in queryset:
        utils.borrar_habitaciones(viaje.crucero)


@admin.action(description="Rellenar restaurantes y mesas para el crucero seleccionado")
def accion_rellenar_restaurantes(modeladmin, request, queryset):
    for viaje in queryset:
        utils.rellenar_restaurantes(viaje.crucero)

@admin.action(description="Borrar restaurantes y mesas del crucero seleccionado")
def accion_borrar_restaurantes(modeladmin, request, queryset):
    for viaje in queryset:
        utils.borrar_restaurantes(viaje.crucero)


@admin.action(description="Rellenar entretenimiento para el crucero seleccionado")
def accion_rellenar_entretenimiento(modeladmin, request, queryset):
    for viaje in queryset:
        utils.rellenar_entretenimiento(viaje.crucero)

@admin.action(description="Borrar entretenimiento del crucero seleccionado")
def accion_borrar_entretenimiento(modeladmin, request, queryset):
    for viaje in queryset:
        utils.borrar_entretenimiento(viaje.crucero)

@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "crucero")
    list_filter = ("crucero",)


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ("numero", "crucero", "capacidad", "reservada", "restaurante")
    list_filter = ("crucero", "reservada")


@admin.register(Entretenimiento)
class EntretenimientoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "crucero", "dia", "precio", "reservada")
    list_filter = ("crucero", "dia", "reservada")


@admin.register(EventoPersonalizado)
class EventoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "crucero", "dia")
    list_filter = ("crucero", "dia")


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("estado", "fecha_creacion")
    list_filter = ("estado", "fecha_creacion")


