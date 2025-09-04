from django.contrib import admin
from .models import (
    Barco, Ruta, Viaje, TipoCabina, Cabina, 
    Reserva, Pasajero, ServicioAdicional, ServicioReserva
)


@admin.register(Barco)
class BarcoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'capacidad', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'origen', 'destino', 'duracion_dias', 'activa']
    list_filter = ['activa', 'duracion_dias', 'fecha_creacion']
    search_fields = ['nombre', 'origen', 'destino']
    ordering = ['nombre']


@admin.register(Viaje)
class ViajeAdmin(admin.ModelAdmin):
    list_display = ['barco', 'ruta', 'fecha_salida', 'fecha_llegada', 'precio_base', 'estado', 'capacidad_disponible']
    list_filter = ['estado', 'barco', 'ruta', 'fecha_salida']
    search_fields = ['barco__nombre', 'ruta__nombre']
    date_hierarchy = 'fecha_salida'
    ordering = ['-fecha_salida']


@admin.register(TipoCabina)
class TipoCabinaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'capacidad_personas', 'precio_por_noche', 'activo']
    list_filter = ['activo', 'capacidad_personas']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


@admin.register(Cabina)
class CabinaAdmin(admin.ModelAdmin):
    list_display = ['barco', 'numero', 'tipo_cabina', 'estado', 'activa']
    list_filter = ['estado', 'activa', 'barco', 'tipo_cabina']
    search_fields = ['numero', 'barco__nombre']
    ordering = ['barco', 'numero']


class PasajeroInline(admin.TabularInline):
    model = Pasajero
    extra = 1
    fields = ['nombre', 'apellido', 'fecha_nacimiento', 'tipo_documento', 'numero_documento', 'es_titular']


class ServicioReservaInline(admin.TabularInline):
    model = ServicioReserva
    extra = 1
    fields = ['servicio', 'cantidad', 'precio_unitario', 'subtotal']
    readonly_fields = ['subtotal']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'viaje', 'cabina', 'estado', 'precio_total', 'fecha_reserva', 'agente']
    list_filter = ['estado', 'fecha_reserva', 'viaje__barco', 'agente']
    search_fields = ['cliente__nombre', 'cliente__apellido', 'viaje__barco__nombre']
    readonly_fields = ['fecha_reserva', 'fecha_modificacion', 'precio_total']
    date_hierarchy = 'fecha_reserva'
    inlines = [PasajeroInline, ServicioReservaInline]
    fieldsets = (
        ('Información de la Reserva', {
            'fields': ('viaje', 'cabina', 'cliente', 'estado', 'agente')
        }),
        ('Información Financiera', {
            'fields': ('precio_total', 'notas')
        }),
        ('Fechas', {
            'fields': ('fecha_reserva', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Pasajero)
class PasajeroAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'reserva', 'fecha_nacimiento', 'tipo_documento', 'es_titular']
    list_filter = ['tipo_documento', 'nacionalidad', 'es_titular']
    search_fields = ['nombre', 'apellido', 'numero_documento']
    ordering = ['-es_titular', 'apellido', 'nombre']


@admin.register(ServicioAdicional)
class ServicioAdicionalAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


@admin.register(ServicioReserva)
class ServicioReservaAdmin(admin.ModelAdmin):
    list_display = ['reserva', 'servicio', 'cantidad', 'precio_unitario', 'subtotal', 'fecha_contratacion']
    list_filter = ['servicio', 'fecha_contratacion']
    search_fields = ['reserva__cliente__nombre', 'servicio__nombre']
    readonly_fields = ['subtotal', 'fecha_contratacion']
    ordering = ['-fecha_contratacion']
