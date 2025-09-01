from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
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
        elif self.stock_actual <= self.stock_minimo * Decimal('1.5'):
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


class Personal(models.Model):
    """Personal del crucero para tareas de mantenimiento"""
    ROLES = [
        ('tecnico', 'Técnico'),
        ('supervisor', 'Supervisor'),
        ('operador', 'Operador'),
        ('limpieza', 'Limpieza'),
    ]
    NIVELES = [
        ('junior', 'Junior'),
        ('medio', 'Medio'),
        ('senior', 'Senior'),
    ]
    nombre = models.CharField(max_length=100)
    rol = models.CharField(max_length=20, choices=ROLES)
    nivel = models.CharField(max_length=20, choices=NIVELES, default='medio')
    activo = models.BooleanField(default=True)
    disponible = models.BooleanField(default=True)
    horas_turno = models.DecimalField(max_digits=4, decimal_places=1, default=Decimal('8.0'))
    
    def __str__(self):
        return f"{self.nombre} ({self.get_rol_display()})"


class TareaMantenimiento(models.Model):
    """Tareas de mantenimiento"""
    TIPOS_TAREA = [
        ('preventivo', 'Mantenimiento Preventivo'),
        ('correctivo', 'Mantenimiento Correctivo'),
        ('emergencia', 'Emergencia'),
        ('inspeccion', 'Inspección'),
        ('limpieza', 'Limpieza'),
        ('reparacion', 'Reparación'),
    ]
    
    PRIORIDADES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
        ('emergencia', 'Emergencia Crítica'),
    ]
    
    ESTADOS = [
        ('creada', 'Creada'),
        ('planificada', 'Planificada'),
        ('asignada', 'Asignada'),
        ('en_progreso', 'En Progreso'),
        ('esperando_materiales', 'Esperando Materiales'),
        ('esperando_personal', 'Esperando Personal'),
        ('pausada', 'Pausada'),
        ('revision', 'En Revisión'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('rechazada', 'Rechazada'),
    ]
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS_TAREA)
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='media')
    estado = models.CharField(max_length=25, choices=ESTADOS, default='creada')
    
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, null=True, blank=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    tipo_crucero = models.ForeignKey(TipoCrucero, on_delete=models.CASCADE, null=True, blank=True)
    
    asignado_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_creadas')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_programada = models.DateTimeField()
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    
    tiempo_estimado_horas = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.0'))
    tiempo_real_horas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    observaciones = models.TextField(blank=True)
    
    def clean(self):
        # Ubicación coherente con equipo si se indica
        if self.equipo and self.ubicacion_id and self.equipo.ubicacion_id != self.ubicacion_id:
            raise ValidationError('La ubicación de la tarea debe coincidir con la del equipo seleccionado.')
        # Fechas coherentes
        if self.fecha_programada and self.fecha_programada < timezone.now() and self.estado in ['creada', 'planificada']:
            raise ValidationError('La fecha programada no puede estar en el pasado para tareas nuevas.')
        if self.estado == 'completada' and not self.fecha_completada:
            raise ValidationError('Debe registrar fecha de completado para una tarea completada.')
    
    def puede_cambiar_estado(self, nuevo_estado):
        """Define las transiciones válidas de estado"""
        transiciones = {
            'creada': ['planificada', 'cancelada'],
            'planificada': ['asignada', 'cancelada'],
            'asignada': ['en_progreso', 'esperando_materiales', 'esperando_personal', 'cancelada'],
            'en_progreso': ['pausada', 'esperando_materiales', 'revision', 'completada'],
            'esperando_materiales': ['en_progreso', 'cancelada'],
            'esperando_personal': ['asignada', 'cancelada'],
            'pausada': ['en_progreso', 'cancelada'],
            'revision': ['completada', 'en_progreso', 'rechazada'],
            'completada': [],
            'cancelada': [],
            'rechazada': ['planificada'],
        }
        return nuevo_estado in transiciones.get(self.estado, [])
    
    def cambiar_estado(self, nuevo_estado, usuario=None, observaciones=''):
        """Cambia el estado de la tarea con validaciones"""
        if not self.puede_cambiar_estado(nuevo_estado):
            raise ValidationError(f'No se puede cambiar de {self.get_estado_display()} a {dict(self.ESTADOS)[nuevo_estado]}')
        
        estado_anterior = self.estado
        self.estado = nuevo_estado
        
        # Actualizar fechas según el estado
        if nuevo_estado == 'en_progreso' and not self.fecha_inicio:
            self.fecha_inicio = timezone.now()
        elif nuevo_estado == 'completada':
            self.fecha_completada = timezone.now()
            if self.equipo:
                self.equipo.ultima_revision = timezone.now()
                self.equipo.save()
        
        self.save()
        
        # Registrar el cambio en el historial - se hace desde la vista
    
    @property
    def personal_asignado(self):
        """Obtiene el personal asignado a esta tarea"""
        return self.asignaciones.filter(estado__in=['asignado', 'en_progreso'])
    
    @property
    def materiales_necesarios(self):
        """Verifica si tiene todos los materiales necesarios"""
        for producto in self.productos_utilizados.all():
            try:
                inv = InventarioProducto.objects.get(
                    producto=producto.producto, 
                    tipo_crucero=self.tipo_crucero
                )
                if inv.stock_actual < producto.cantidad_utilizada:
                    return False
            except InventarioProducto.DoesNotExist:
                return False
        return True
    
    @property
    def puede_iniciar(self):
        """Determina si la tarea puede iniciarse"""
        return (self.estado in ['asignada', 'planificada'] and 
                self.personal_asignado.exists() and 
                self.materiales_necesarios)
    
    def __str__(self):
        return f"{self.titulo} - {self.get_estado_display()}"
    
    @property
    def dias_vencimiento(self):
        return (self.fecha_programada.date() - timezone.now().date()).days
    
    class Meta:
        verbose_name = "Tarea de Mantenimiento"
        verbose_name_plural = "Tareas de Mantenimiento"
        ordering = ['fecha_programada', 'prioridad']


class CambioEstado(models.Model):
    """Historial de cambios de estado de tareas"""
    tarea = models.ForeignKey('TareaMantenimiento', on_delete=models.CASCADE, related_name='cambios_estado')
    estado_anterior = models.CharField(max_length=25)
    estado_nuevo = models.CharField(max_length=25)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.tarea.titulo}: {self.estado_anterior} → {self.estado_nuevo}"
    
    class Meta:
        ordering = ['-fecha_cambio']


class AsignacionPersonal(models.Model):
    """Asignación de personal a tareas"""
    ESTADOS = [
        ('asignado', 'Asignado'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    tarea = models.ForeignKey(TareaMantenimiento, on_delete=models.CASCADE, related_name='asignaciones')
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE)
    horas_asignadas = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.5'))])
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='asignado')
    
    def __str__(self):
        return f"{self.personal} -> {self.tarea} ({self.estado})"


class ProductoUtilizado(models.Model):
    """Productos utilizados en una tarea de mantenimiento"""
    tarea = models.ForeignKey(TareaMantenimiento, on_delete=models.CASCADE, related_name='productos_utilizados')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_utilizada = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_utilizacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad_utilizada} {self.producto.get_unidad_display()}"
    
    def _ajustar_stock(self, diferencia: Decimal):
        # Ajustar stock del inventario del tipo de crucero asociado a la tarea
        try:
            inv = InventarioProducto.objects.get(producto=self.producto, tipo_crucero=self.tarea.tipo_crucero)
        except InventarioProducto.DoesNotExist:
            raise ValidationError('No existe inventario para este producto y tipo de crucero.')
        nuevo = inv.stock_actual - diferencia
        if nuevo < 0:
            raise ValidationError('Stock insuficiente para registrar el consumo de producto.')
        inv.stock_actual = nuevo
        inv.save(update_fields=['stock_actual', 'fecha_ultima_actualizacion'])
    
    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None
        diferencia = self.cantidad_utilizada
        if not es_nuevo:
            anterior = ProductoUtilizado.objects.get(pk=self.pk)
            diferencia = self.cantidad_utilizada - anterior.cantidad_utilizada
        if diferencia != 0:
            self._ajustar_stock(diferencia)
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Reponer el stock al eliminar el registro de uso
        self._ajustar_stock(Decimal('-1') * self.cantidad_utilizada)  # sumar de vuelta
        super().delete(*args, **kwargs)
    
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
    
    reportado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
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
