from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import re


class TipoCrucero(models.Model):
    """Modelo para los diferentes tipos de crucero"""
    TIPOS_CRUCERO = [
        ('pequeño', 'Crucero Pequeño (2000 pasajeros)'),
        ('mediano', 'Crucero Mediano (4000 pasajeros)'), 
        ('grande', 'Crucero Grande (6000 pasajeros)'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPOS_CRUCERO, unique=True)
    capacidad_pasajeros = models.IntegerField()
    numero_tripulantes = models.IntegerField()
    numero_cubiertas = models.IntegerField()
    
    def __str__(self):
        return f"{self.get_tipo_display()}"
    
    class Meta:
        verbose_name = "Tipo de Crucero"
        verbose_name_plural = "Tipos de Crucero"


class Ubicacion(models.Model):
    """Modelo para las ubicaciones siguiendo el formato XABCD"""
    USOS_UBICACION = [
        (0, 'Habitaciones - Babor'),
        (1, 'Habitaciones - Estribor'),
        (2, 'Restaurantes'),
        (3, 'Bares/Cafés'),
        (4, 'Almacenes'),
        (5, 'Sitios de entretenimiento'),
        (6, 'Libre para especificar'),
        (7, 'Libre para especificar'),
        (8, 'Libre para especificar'),
        (9, 'Libre para especificar'),
    ]
    
    cubierta = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(18)],
        help_text="Número de cubierta (1-18)"
    )
    uso = models.IntegerField(
        choices=USOS_UBICACION,
        help_text="Tipo de uso de la ubicación"
    )
    identificador = models.CharField(
        max_length=1,
        help_text="Identificador único (A-Z)"
    )
    numero = models.CharField(
        max_length=2,
        help_text="Número de ubicación (01-99)"
    )
    
    descripcion = models.CharField(max_length=200, blank=True)
    activa = models.BooleanField(default=True)
    
    @property
    def codigo_ubicacion(self):
        """Genera el código de ubicación en formato XABCD"""
        return f"{self.cubierta}{self.uso}{self.identificador}{self.numero:0>2}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Validar que el identificador sea una letra
        if not re.match(r'^[A-Z]$', self.identificador.upper()):
            raise ValidationError('El identificador debe ser una letra (A-Z)')
        
        # Validar que el número sea válido
        if not re.match(r'^\d{1,2}$', self.numero):
            raise ValidationError('El número debe ser de 1 o 2 dígitos')
    
    def save(self, *args, **kwargs):
        self.identificador = self.identificador.upper()
        self.numero = f"{int(self.numero):02d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.codigo_ubicacion} - {self.descripcion}"
    
    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
        unique_together = ['cubierta', 'uso', 'identificador', 'numero']


class CategoriaProducto(models.Model):
    """Categorías de productos de mantenimiento"""
    CATEGORIAS = [
        ('quimicos_limpieza', 'Productos Químicos de Limpieza e Higiene'),
        ('consumibles_higiene', 'Consumibles de Higiene (Descartables)'),
        ('repuestos_criticos', 'Repuestos Críticos y Filtros'),
        ('fluidos_lubricantes', 'Fluidos y Lubricantes'),
        ('herramientas_seguridad', 'Herramientas y Equipos de Seguridad'),
    ]
    
    categoria = models.CharField(max_length=30, choices=CATEGORIAS, unique=True)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.get_categoria_display()
    
    class Meta:
        verbose_name = "Categoría de Producto"
        verbose_name_plural = "Categorías de Productos"


class Producto(models.Model):
    """Productos de mantenimiento basados en el Excel"""
    UNIDADES = [
        ('litro', 'Litro'),
        ('kg', 'Kilogramo'),
        ('rollo', 'Rollo'),
        ('paquete', 'Paquete'),
        ('unidad', 'Unidad'),
        ('set', 'Set'),
        ('par', 'Par'),
    ]
    
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    unidad = models.CharField(max_length=20, choices=UNIDADES)
    descripcion = models.TextField(blank=True)
    notas = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.get_unidad_display()})"
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"


class InventarioProducto(models.Model):
    """Stock de productos por tipo de crucero"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo_crucero = models.ForeignKey(TipoCrucero, on_delete=models.CASCADE)
    cantidad_requerida = models.DecimalField(max_digits=10, decimal_places=2)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    @property
    def estado_stock(self):
        if self.stock_actual <= self.stock_minimo:
            return 'crítico'
        elif self.stock_actual <= self.stock_minimo * 1.5:
            return 'bajo'
        else:
            return 'normal'
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.tipo_crucero.tipo} - Stock: {self.stock_actual}"
    
    class Meta:
        verbose_name = "Inventario de Producto"
        verbose_name_plural = "Inventario de Productos"
        unique_together = ['producto', 'tipo_crucero']


class TipoEquipo(models.Model):
    """Tipos de equipos del crucero"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    requiere_mantenimiento_programado = models.BooleanField(default=True)
    frecuencia_mantenimiento_dias = models.IntegerField(default=30)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Tipo de Equipo"
        verbose_name_plural = "Tipos de Equipos"


class Equipo(models.Model):
    """Equipos específicos del crucero"""
    ESTADOS = [
        ('operativo', 'Operativo'),
        ('mantenimiento', 'En Mantenimiento'),
        ('averiado', 'Averiado'),
        ('fuera_servicio', 'Fuera de Servicio'),
    ]
    
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    tipo_equipo = models.ForeignKey(TipoEquipo, on_delete=models.CASCADE)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='operativo')
    fecha_instalacion = models.DateField()
    ultima_revision = models.DateTimeField(null=True, blank=True)
    proxima_revision = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def dias_hasta_revision(self):
        if self.proxima_revision:
            return (self.proxima_revision.date() - timezone.now().date()).days
        return None
    
    class Meta:
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"


class TareaMantenimiento(models.Model):
    """Tareas de mantenimiento"""
    TIPOS_TAREA = [
        ('preventivo', 'Mantenimiento Preventivo'),
        ('correctivo', 'Mantenimiento Correctivo'),
        ('emergencia', 'Emergencia'),
        ('inspeccion', 'Inspección'),
    ]
    
    PRIORIDADES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS_TAREA)
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='media')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, null=True, blank=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    
    asignado_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tareas_creadas')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_programada = models.DateTimeField()
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    
    tiempo_estimado_horas = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    tiempo_real_horas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.titulo} - {self.get_estado_display()}"
    
    @property
    def dias_vencimiento(self):
        return (self.fecha_programada.date() - timezone.now().date()).days
    
    class Meta:
        verbose_name = "Tarea de Mantenimiento"
        verbose_name_plural = "Tareas de Mantenimiento"
        ordering = ['fecha_programada', 'prioridad']


class ProductoUtilizado(models.Model):
    """Productos utilizados en una tarea de mantenimiento"""
    tarea = models.ForeignKey(TareaMantenimiento, on_delete=models.CASCADE, related_name='productos_utilizados')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_utilizada = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_utilizacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad_utilizada} {self.producto.get_unidad_display()}"
    
    class Meta:
        verbose_name = "Producto Utilizado"
        verbose_name_plural = "Productos Utilizados"


class HistorialMantenimiento(models.Model):
    """Historial de mantenimientos realizados"""
    tarea = models.OneToOneField(TareaMantenimiento, on_delete=models.CASCADE)
    resultado = models.TextField()
    problemas_encontrados = models.TextField(blank=True)
    recomendaciones = models.TextField(blank=True)
    costo_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    firma_tecnico = models.CharField(max_length=100)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Historial - {self.tarea.titulo}"
    
    class Meta:
        verbose_name = "Historial de Mantenimiento"
        verbose_name_plural = "Historial de Mantenimientos"


class ReporteIncidente(models.Model):
    """Reportes de incidentes que requieren mantenimiento"""
    SEVERIDADES = [
        ('menor', 'Menor'),
        ('moderada', 'Moderada'),
        ('mayor', 'Mayor'),
        ('critica', 'Crítica'),
    ]
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    equipo = models.ForeignKey(Equipo, on_delete=models.SET_NULL, null=True, blank=True)
    severidad = models.CharField(max_length=20, choices=SEVERIDADES)
    
    reportado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    
    tarea_generada = models.ForeignKey(TareaMantenimiento, on_delete=models.SET_NULL, null=True, blank=True)
    resuelto = models.BooleanField(default=False)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Incidente: {self.titulo} - {self.get_severidad_display()}"
    
    class Meta:
        verbose_name = "Reporte de Incidente"
        verbose_name_plural = "Reportes de Incidentes"
        ordering = ['-fecha_reporte']
