from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    TipoCrucero, Ubicacion, CategoriaProducto, Producto, InventarioProducto,
    TipoEquipo, Equipo, TareaMantenimiento, ProductoUtilizado, 
    HistorialMantenimiento, ReporteIncidente
)


@admin.register(TipoCrucero)
class TipoCruceroAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'capacidad_pasajeros', 'numero_tripulantes', 'numero_cubiertas']
    list_filter = ['tipo']
    search_fields = ['tipo']


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ['codigo_ubicacion', 'cubierta', 'get_uso_display', 'descripcion', 'activa']
    list_filter = ['cubierta', 'uso', 'activa']
    search_fields = ['descripcion', 'identificador', 'numero']
    ordering = ['cubierta', 'uso', 'identificador', 'numero']
    
    def codigo_ubicacion(self, obj):
        return obj.codigo_ubicacion
    codigo_ubicacion.short_description = 'Código Ubicación'


@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ['get_categoria_display', 'descripcion']
    search_fields = ['categoria', 'descripcion']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'unidad', 'activo', 'fecha_creacion']
    list_filter = ['categoria', 'unidad', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    ordering = ['categoria', 'nombre']


class InventarioProductoInline(admin.TabularInline):
    model = InventarioProducto
    extra = 0
    readonly_fields = ['estado_stock']


@admin.register(InventarioProducto)
class InventarioProductoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo_crucero', 'cantidad_requerida', 'stock_actual', 'stock_minimo', 'estado_stock_colored', 'ubicacion']
    list_filter = ['tipo_crucero', 'producto__categoria']
    search_fields = ['producto__nombre']
    readonly_fields = ['estado_stock']
    
    def estado_stock_colored(self, obj):
        estado = obj.estado_stock
        colors = {
            'crítico': 'red',
            'bajo': 'orange', 
            'normal': 'green'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(estado, 'black'),
            estado.upper()
        )
    estado_stock_colored.short_description = 'Estado del Stock'


@admin.register(TipoEquipo)
class TipoEquipoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'requiere_mantenimiento_programado', 'frecuencia_mantenimiento_dias']
    list_filter = ['requiere_mantenimiento_programado']
    search_fields = ['nombre', 'descripcion']


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo_equipo', 'ubicacion', 'estado', 'dias_hasta_revision']
    list_filter = ['tipo_equipo', 'estado', 'ubicacion__cubierta']
    search_fields = ['codigo', 'nombre', 'observaciones']
    date_hierarchy = 'fecha_instalacion'
    
    def dias_hasta_revision(self, obj):
        dias = obj.dias_hasta_revision()
        if dias is not None:
            if dias < 0:
                return format_html('<span style="color: red; font-weight: bold;">Vencido ({} días)</span>', abs(dias))
            elif dias <= 7:
                return format_html('<span style="color: orange; font-weight: bold;">{} días</span>', dias)
            else:
                return f'{dias} días'
        return 'No programada'
    dias_hasta_revision.short_description = 'Días hasta revisión'


class ProductoUtilizadoInline(admin.TabularInline):
    model = ProductoUtilizado
    extra = 0


@admin.register(TareaMantenimiento)
class TareaMantenimientoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'prioridad_colored', 'estado_colored', 'asignado_a', 'fecha_programada', 'dias_vencimiento_colored']
    list_filter = ['tipo', 'prioridad', 'estado', 'fecha_programada', 'asignado_a']
    search_fields = ['titulo', 'descripcion']
    date_hierarchy = 'fecha_programada'
    inlines = [ProductoUtilizadoInline]
    
    fieldsets = (
        ('Información General', {
            'fields': ('titulo', 'descripcion', 'tipo', 'prioridad')
        }),
        ('Ubicación y Equipo', {
            'fields': ('ubicacion', 'equipo')
        }),
        ('Asignación', {
            'fields': ('asignado_a', 'creado_por')
        }),
        ('Fechas y Tiempos', {
            'fields': ('fecha_programada', 'fecha_inicio', 'fecha_completada', 'tiempo_estimado_horas', 'tiempo_real_horas')
        }),
        ('Estado y Observaciones', {
            'fields': ('estado', 'observaciones')
        })
    )
    
    def prioridad_colored(self, obj):
        colors = {
            'baja': 'green',
            'media': 'orange',
            'alta': 'red',
            'critica': 'darkred'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.prioridad, 'black'),
            obj.get_prioridad_display().upper()
        )
    prioridad_colored.short_description = 'Prioridad'
    
    def estado_colored(self, obj):
        colors = {
            'pendiente': 'orange',
            'en_progreso': 'blue',
            'completada': 'green',
            'cancelada': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.estado, 'black'),
            obj.get_estado_display().upper()
        )
    estado_colored.short_description = 'Estado'
    
    def dias_vencimiento_colored(self, obj):
        dias = obj.dias_vencimiento
        if dias < 0:
            return format_html('<span style="color: red; font-weight: bold;">Vencida ({} días)</span>', abs(dias))
        elif dias <= 3:
            return format_html('<span style="color: orange; font-weight: bold;">{} días</span>', dias)
        else:
            return f'{dias} días'
    dias_vencimiento_colored.short_description = 'Días para vencimiento'


@admin.register(ProductoUtilizado)
class ProductoUtilizadoAdmin(admin.ModelAdmin):
    list_display = ['tarea', 'producto', 'cantidad_utilizada', 'fecha_utilizacion']
    list_filter = ['producto__categoria', 'fecha_utilizacion']
    search_fields = ['tarea__titulo', 'producto__nombre']


@admin.register(HistorialMantenimiento)
class HistorialMantenimientoAdmin(admin.ModelAdmin):
    list_display = ['tarea', 'firma_tecnico', 'costo_estimado', 'fecha_registro']
    list_filter = ['fecha_registro', 'firma_tecnico']
    search_fields = ['tarea__titulo', 'resultado', 'problemas_encontrados']
    readonly_fields = ['fecha_registro']


@admin.register(ReporteIncidente)
class ReporteIncidenteAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'severidad_colored', 'ubicacion', 'reportado_por', 'fecha_reporte', 'resuelto']
    list_filter = ['severidad', 'resuelto', 'fecha_reporte']
    search_fields = ['titulo', 'descripcion']
    date_hierarchy = 'fecha_reporte'
    
    def severidad_colored(self, obj):
        colors = {
            'menor': 'green',
            'moderada': 'orange',
            'mayor': 'red',
            'critica': 'darkred'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.severidad, 'black'),
            obj.get_severidad_display().upper()
        )
    severidad_colored.short_description = 'Severidad'


# Personalización del admin site
admin.site.site_header = "Administración del Sistema de Cruceros"
admin.site.site_title = "Crucero Admin"
admin.site.index_title = "Panel de Administración - Módulo de Mantenimiento"
