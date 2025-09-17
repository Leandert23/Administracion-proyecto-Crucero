from django.contrib import admin
from .models import Embarcacion, Ruta, Dia, TipoEmbarcacion, Cubierta, Locales, Habitaciones, TipoHabitacion, TipoLocal


@admin.register(Embarcacion)
class EmbarcacionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Embarcacion
    """
    # Campos que se mostrarán en la lista
    list_display = [
        'identificador', 'nombre', 'tipo', 'puerto_base',
        'estado_operativo', 'capacidad_pasajeros', 'fecha_creacion'
    ]

    # Campos por los que se puede filtrar
    list_filter = [
        'estado_operativo', 'tipo', 'bandera', 'puerto_base',
        'tipo_combustible', 'fecha_creacion'
    ]

    # Campos por los que se puede buscar
    search_fields = [
        'identificador', 'nombre', 'tipo', 'puerto_base', 'bandera'
    ]

    # Campos de solo lectura
    readonly_fields = ['area_utilizable', 'fecha_creacion', 'fecha_actualizacion']

    # Organización de los campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'tipo', 'identificador', 'estado_operativo', 'descripcion')
        }),
        ('Fechas Importantes', {
            'fields': ('fecha_botadura', 'fecha_adquisicion')
        }),
        ('Capacidades', {
            'fields': ('capacidad_pasajeros', 'capacidad_tripulacion')
        }),
        ('Dimensiones Físicas', {
            'fields': ('tonelaje', 'eslora', 'manga', 'altura', 'numero_cubiertas', 'area_utilizable')
        }),
        ('Alojamiento', {
            'fields': ('maximo_habitacion_pasajeros', 'maximo_habitacion_tripulantes')
        }),
        ('Información de Registro', {
            'fields': ('bandera', 'puerto_base')
        }),
        ('Información Técnica del Motor', {
            'fields': ('modelo_motor', 'velocidad_maxima')
        }),
        ('Mantenimiento', {
            'fields': ('ultimo_mantenimiento', 'proximo_mantenimiento')
        }),
        ('Información de Combustible', {
            'fields': ('tipo_combustible', 'consumo_combustible', 'capacidad_combustible')
        }),
        ('Relaciones', {
            'fields': ('ruta',)
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    # Configuración de paginación
    list_per_page = 25

    # Ordenamiento por defecto
    ordering = ['-fecha_creacion']


@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Ruta
    """
    # Campos que se mostrarán en la lista
    list_display = [
        'titulo', 'numero_dias', 'fecha_creacion'
    ]

    # Campos por los que se puede filtrar
    list_filter = [
        'numero_dias', 'fecha_creacion'
    ]

    # Campos por los que se puede buscar
    search_fields = [
        'titulo', 'descripcion'
    ]

    # Campos de solo lectura
    readonly_fields = ['fecha_creacion']

    # Organización de los campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion')
        }),
        ('Duración', {
            'fields': ('numero_dias',)
        }),
        ('Metadata', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )

    # Configuración de paginación
    list_per_page = 25

    # Ordenamiento por defecto
    ordering = ['titulo']


@admin.register(Dia)
class DiaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Dia
    """
    # Campos que se mostrarán en la lista
    list_display = [
        'numero_dia', 'ruta', 'titulo_dia', 'ubicacion', 'progreso_configuracion'
    ]

    # Campos por los que se puede filtrar
    list_filter = [
        'ruta', 'numero_dia', 'fecha_creacion'
    ]

    # Campos por los que se puede buscar
    search_fields = [
        'titulo_dia', 'ubicacion', 'descripcion', 'ruta__titulo'
    ]

    # Campos de solo lectura
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

    # Organización de los campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('ruta', 'numero_dia', 'titulo_dia', 'ubicacion')
        }),
        ('Detalles del Día', {
            'fields': ('descripcion',),
            'classes': ('collapse',)
        }),
        ('Horarios', {
            'fields': ('hora_llegada', 'hora_salida'),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': ('notas_especiales',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    # Configuración de paginación
    list_per_page = 25

    # Ordenamiento por defecto
    ordering = ['ruta', 'numero_dia']

    def get_queryset(self, request):
        """
        Optimizar las consultas incluyendo la ruta relacionada
        """
        return super().get_queryset(request).select_related('ruta')


@admin.register(Cubierta)
class CubiertaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Cubierta
    """
    # Campos que se mostrarán en la lista
    list_display = ['numero', 'nombre', 'embarcacion', 'area_disponible', 'fecha_creacion']

    # Campos por los que se puede filtrar
    list_filter = ['embarcacion', 'numero', 'fecha_creacion']

    # Campos por los que se puede buscar
    search_fields = ['nombre', 'embarcacion__nombre', 'embarcacion__identificador']

    # Campos de solo lectura
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

    # Organización de los campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('embarcacion', 'numero', 'nombre')
        }),
        ('Especificaciones', {
            'fields': ('area_disponible',)
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    # Configuración de paginación
    list_per_page = 25

    # Ordenamiento por defecto
    ordering = ['embarcacion', 'numero']

    def get_queryset(self, request):
        """
        Optimizar las consultas incluyendo la embarcación relacionada
        """
        return super().get_queryset(request).select_related('embarcacion')


@admin.register(Locales)
class LocalesAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Locales
    """
    # Campos que se mostrarán en la lista
    list_display = ['nombre', 'tipo', 'ID_local', 'estado', 'cubierta', 'ubicacion', 'fecha_creacion']

    # Campos por los que se puede filtrar
    list_filter = ['tipo', 'estado', 'cubierta__embarcacion', 'fecha_creacion']

    # Campos por los que se puede buscar
    search_fields = ['nombre', 'ID_local', 'ubicacion', 'cubierta__embarcacion__nombre']

    # Campos de solo lectura
    readonly_fields = ['ubicacion', 'fecha_creacion', 'fecha_actualizacion']

    # Organización de los campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('tipo', 'nombre', 'ID_local', 'estado')
        }),
        ('Ubicación', {
            'fields': ('cubierta', 'n_cubierta')
        }),
        ('Especificaciones', {
            'fields': ('area_metros_cuadrados',)
        }),
        ('Mantenimiento', {
            'fields': ('ultimo_mantenimiento', 'proximo_mantenimiento')
        }),
        ('Ubicación Generada', {
            'fields': ('ubicacion',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    # Configuración de paginación
    list_per_page = 25

    # Ordenamiento por defecto
    ordering = ['cubierta', 'tipo', 'nombre']

    def get_queryset(self, request):
        """
        Optimizar las consultas incluyendo las relaciones relacionadas
        """
        return super().get_queryset(request).select_related('cubierta__embarcacion')


@admin.register(TipoEmbarcacion)
class TipoEmbarcacionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo TipoEmbarcacion
    """
    # Campos que se mostrarán en la lista
    list_display = ['nombre', 'descripcion', 'fecha_creacion']

    # Campos por los que se puede buscar
    search_fields = ['nombre', 'descripcion']

    # Campos de solo lectura
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

    # Organización de los campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion')
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    # Configuración de paginación
    list_per_page = 25

    # Ordenamiento por defecto
    ordering = ['nombre']


@admin.register(TipoHabitacion)
class TipoHabitacionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo TipoHabitacion
    """
    # Campos que se mostrarán en la lista
    list_display = [
        'nombre', 'tipo', 'area_metros_cuadrados', 'precio_base',
        'estado_default', 'fecha_creacion'
    ]

    # Campos por los que se puede filtrar
    list_filter = [
        'tipo', 'estado_default', 'fecha_creacion'
    ]

    # Campos por los que se puede buscar
    search_fields = ['nombre', 'descripcion']

    # Campos de solo lectura
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

    # Organización de los campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'tipo')
        }),
        ('Especificaciones', {
            'fields': ('area_metros_cuadrados', 'precio_base', 'estado_default')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    # Configuración de paginación
    list_per_page = 25

    # Ordenamiento por defecto
    ordering = ['nombre']


@admin.register(TipoLocal)
class TipoLocalAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo TipoLocal
    """
    # Campos que se mostrarán en la lista
    list_display = [
        'nombre', 'tipo', 'area_metros_cuadrados',
        'estado_default', 'fecha_creacion'
    ]

    # Campos por los que se puede filtrar
    list_filter = [
        'tipo', 'estado_default', 'fecha_creacion'
    ]

    # Campos por los que se puede buscar
    search_fields = ['nombre', 'descripcion']

    # Campos de solo lectura
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']

    # Organización de los campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'tipo')
        }),
        ('Especificaciones', {
            'fields': ('area_metros_cuadrados', 'estado_default')
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    # Configuración de paginación
    list_per_page = 25

    # Ordenamiento por defecto
    ordering = ['nombre']


@admin.register(Habitaciones)
class HabitacionesAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Habitaciones
    """
    # Campos que se mostrarán en la lista
    list_display = ['numero', 'ID_local', 'posicion', 'estado', 'cubierta', 'precio', 'ubicacion', 'fecha_creacion']

    # Campos por los que se puede filtrar
    list_filter = ['posicion', 'estado', 'cubierta__embarcacion', 'tipo_habitacion_estandar', 'fecha_creacion']

    # Campos por los que se puede buscar
    search_fields = ['numero', 'ID_local', 'ubicacion', 'cubierta__embarcacion__nombre']

    # Campos de solo lectura
    readonly_fields = ['ubicacion', 'ID_local', 'fecha_creacion', 'fecha_actualizacion']

    # Organización de los campos en el formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('numero', 'posicion', 'tipo_habitacion_estandar')
        }),
        ('Ubicación', {
            'fields': ('cubierta', 'n_cubierta')
        }),
        ('Especificaciones', {
            'fields': ('area_metros_cuadrados', 'precio')
        }),
        ('Estado', {
            'fields': ('estado', 'id_persona')
        }),
        ('Mantenimiento', {
            'fields': ('ultimo_mantenimiento', 'proximo_mantenimiento')
        }),
        ('IDs Generados', {
            'fields': ('ID_local', 'ubicacion'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

    # Configuración de paginación
    list_per_page = 25

    # Ordenamiento por defecto
    ordering = ['cubierta', 'numero']

    def get_queryset(self, request):
        """
        Optimizar las consultas incluyendo las relaciones relacionadas
        """
        return super().get_queryset(request).select_related('cubierta__embarcacion', 'tipo_habitacion_estandar')
