from django.contrib import admin
from .models import Cliente, Venta, DetalleVenta, MetodoPago, Pago

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'email', 'telefono', 'fecha_registro']
    list_filter = ['fecha_registro']
    search_fields = ['nombre', 'apellido', 'email']
    ordering = ['nombre', 'apellido']

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ['concepto', 'cantidad', 'precio_unitario', 'subtotal']
    readonly_fields = ['subtotal']

class PagoInline(admin.TabularInline):
    model = Pago
    extra = 1
    fields = ['metodo_pago', 'monto', 'estado', 'referencia']

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'tipo_venta', 'monto_total', 'estado', 'fecha_venta', 'vendedor']
    list_filter = ['tipo_venta', 'estado', 'fecha_venta', 'vendedor']
    search_fields = ['cliente__nombre', 'cliente__apellido', 'descripcion']
    readonly_fields = ['fecha_venta', 'fecha_modificacion']
    inlines = [DetalleVentaInline, PagoInline]
    fieldsets = (
        ('Información General', {
            'fields': ('cliente', 'tipo_venta', 'descripcion', 'estado', 'vendedor')
        }),
        ('Información Financiera', {
            'fields': ('monto_total', 'notas')
        }),
        ('Fechas', {
            'fields': ('fecha_venta', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre']

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['id', 'venta', 'metodo_pago', 'monto', 'estado', 'fecha_pago']
    list_filter = ['estado', 'metodo_pago', 'fecha_pago']
    search_fields = ['venta__cliente__nombre', 'venta__cliente__apellido', 'referencia']
    readonly_fields = ['fecha_pago']
