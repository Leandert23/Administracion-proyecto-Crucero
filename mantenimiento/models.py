from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import timedelta
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


class Crucero(models.Model):
    """Instancia de crucero operando (soporta múltiples cruceros simultáneos)."""
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.ForeignKey(TipoCrucero, on_delete=models.PROTECT)
    tz_offset_minutos = models.IntegerField(default=-300, help_text="Offset minutos respecto a UTC para 'Hora del Barco'")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipo.get_tipo_display()})"

    class Meta:
        verbose_name = "Crucero"
        verbose_name_plural = "Cruceros"

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
    crucero = models.ForeignKey('Crucero', on_delete=models.CASCADE, null=True, blank=True, help_text="Crucero al que pertenece esta ubicación")
    activa = models.BooleanField(default=True)
    
    @property
    def codigo_ubicacion(self):
        """Genera el código de ubicación en formato XABCD"""
        return f"{self.cubierta}{self.uso}{self.identificador}{self.numero:0>2}"
    
    def clean(self):
        # Validar que el identificador sea una letra
        if not re.match(r'^[A-Z]$', self.identificador.upper()):
            raise ValidationError('El identificador debe ser una letra (A-Z)')
        
        # Validar que el número sea válido y no sea 00
        if not re.match(r'^[0-9]{1,2}$', self.numero):
            raise ValidationError('El número debe ser de 1 o 2 dígitos')
        
        numero_int = int(self.numero)
        if numero_int < 1 or numero_int > 99:
            raise ValidationError('El número debe estar entre 01 y 99')
        
        # Validar cubierta según tipo de crucero
        if self.crucero and self.crucero.tipo:
            max_cubiertas = {
                'pequeño': 12,
                'mediano': 15,
                'grande': 18
            }
            tipo_crucero = self.crucero.tipo.tipo
            if tipo_crucero in max_cubiertas and self.cubierta > max_cubiertas[tipo_crucero]:
                raise ValidationError(
                    f'El crucero {self.crucero.tipo.get_tipo_display()} solo tiene {max_cubiertas[tipo_crucero]} cubiertas. '
                    f'Cubierta {self.cubierta} no es válida.'
                )
    
    def save(self, *args, **kwargs):
        self.identificador = self.identificador.upper()
        self.numero = f"{int(self.numero):02d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.codigo_ubicacion} - {self.descripcion}"
    
    def delete(self, *args, **kwargs):
        # Verificar si hay equipos en esta ubicación
        if self.equipo_set.exists():
            raise ValidationError(f'No se puede eliminar la ubicación {self.codigo_ubicacion} porque tiene equipos asignados.')
        # Verificar si hay tareas asociadas
        if self.tareamantenimiento_set.exists():
            raise ValidationError(f'No se puede eliminar la ubicación {self.codigo_ubicacion} porque tiene tareas asociadas.')
        super().delete(*args, **kwargs)
    
    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
        unique_together = ['cubierta', 'uso', 'identificador', 'numero', 'crucero']


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
    
    def delete(self, *args, **kwargs):
        # Verificar si hay inventario activo
        if self.inventarioproducto_set.filter(stock_actual__gt=0).exists():
            raise ValidationError('No se puede eliminar un producto con inventario activo.')
        # Verificar si está siendo usado en tareas
        if self.productoutilizado_set.exists():
            raise ValidationError('No se puede eliminar un producto que ha sido utilizado en tareas.')
        super().delete(*args, **kwargs)
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"


class InventarioProducto(models.Model):
    """Stock de productos por tipo de crucero"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo_crucero = models.ForeignKey(TipoCrucero, on_delete=models.CASCADE)
    crucero = models.ForeignKey('Crucero', on_delete=models.CASCADE, null=True, blank=True)
    cantidad_requerida = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    stock_minimo = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    stock_actual = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    def clean(self):
        # Validar que stock_minimo no sea mayor que cantidad_requerida
        if self.stock_minimo > self.cantidad_requerida:
            raise ValidationError('El stock mínimo no puede ser mayor que la cantidad requerida.')
        
        # Validar que el stock actual no sea negativo (doble verificación)
        if self.stock_actual < 0:
            raise ValidationError('El stock actual no puede ser negativo.')
    
    @property
    def estado_stock(self):
        if self.stock_actual <= self.stock_minimo:
            return 'crítico'
        elif self.stock_actual <= self.stock_minimo * Decimal('1.5'):
            return 'bajo'
        else:
            return 'normal'
    
    def __str__(self):
        crucero_etq = f" - {self.crucero.nombre}" if self.crucero else ""
        return f"{self.producto.nombre} - {self.tipo_crucero.tipo}{crucero_etq} - Stock: {self.stock_actual}"
    
    class Meta:
        verbose_name = "Inventario de Producto"
        verbose_name_plural = "Inventario de Productos"
        unique_together = ['producto', 'tipo_crucero', 'crucero']


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
    
    def clean(self):
        # Validar formato del código (ejemplo: EQ-TIPO-0001)
        if self.codigo and not re.match(r'^[A-Z]{2,3}-[A-Z]{2,4}-\d{4}$', self.codigo.upper()):
            raise ValidationError(
                'El código del equipo debe seguir el formato: XX-XXXX-0000 '
                '(ej: EQ-PUMP-0001, AC-HVAC-0023)'
            )
        
        # Validar que fecha_instalacion sea futura (planificada)
        if self.fecha_instalacion and self.fecha_instalacion <= timezone.now().date():
            raise ValidationError('La fecha de instalación debe ser futura.')
        
        # Validar que proxima_revision > ultima_revision
        if self.ultima_revision and self.proxima_revision:
            if self.proxima_revision <= self.ultima_revision:
                raise ValidationError('La próxima revisión debe ser posterior a la última revisión.')
        
        # Validar que próxima revisión sea futura
        if self.proxima_revision and self.proxima_revision < timezone.now():
            raise ValidationError('La próxima revisión debe ser una fecha futura.')
    
    def save(self, *args, **kwargs):
        # Normalizar código a mayúsculas
        if self.codigo:
            self.codigo = self.codigo.upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def dias_hasta_revision(self):
        if self.proxima_revision:
            return (self.proxima_revision.date() - timezone.now().date()).days
        return None
    
    def delete(self, *args, **kwargs):
        # No permitir eliminar equipos con tareas en progreso
        tareas_activas = self.tareamantenimiento_set.filter(
            estado__in=['en_progreso', 'asignada', 'planificada']
        )
        if tareas_activas.exists():
            raise ValidationError(
                f'No se puede eliminar el equipo {self.codigo} porque tiene {tareas_activas.count()} tareas activas.'
            )
        super().delete(*args, **kwargs)
    
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
    horas_turno = models.DecimalField(
        max_digits=4, decimal_places=1, default=Decimal('8.0'),
        validators=[MinValueValidator(Decimal('0.5')), MaxValueValidator(Decimal('12'))]
    )
    
    def clean(self):
        # Validar que las horas de turno sean razonables
        if self.horas_turno > Decimal('12'):
            raise ValidationError('Las horas de turno no pueden exceder 12 horas por seguridad laboral.')
        if self.horas_turno < Decimal('0.5'):
            raise ValidationError('Las horas de turno deben ser al menos 0.5 horas.')
    
    def __str__(self):
        return f"{self.nombre} ({self.get_rol_display()})"
    
    def delete(self, *args, **kwargs):
        # Verificar si tiene tareas asignadas activas
        tareas_activas = self.asignacionpersonal_set.filter(
            tarea__estado__in=['asignada', 'en_progreso']
        )
        if tareas_activas.exists():
            raise ValidationError(
                f'No se puede eliminar a {self.nombre} porque tiene {tareas_activas.count()} tareas activas asignadas.'
            )
        super().delete(*args, **kwargs)


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
    crucero = models.ForeignKey('Crucero', on_delete=models.CASCADE, null=True, blank=True)
    
    asignado_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_creadas')
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_programada = models.DateTimeField()
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    
    tiempo_estimado_horas = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('1.0'),
        validators=[MinValueValidator(Decimal('0.5')), MaxValueValidator(Decimal('24'))]
    )
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
        
        # Validar tiempo estimado
        if self.tiempo_estimado_horas > Decimal('24'):
            raise ValidationError('El tiempo estimado no puede exceder 24 horas. Para tareas más largas, divida en subtareas.')
        
        # Validar coherencia entre prioridad y tipo
        if self.tipo == 'emergencia' and self.prioridad not in ['alta', 'critica', 'emergencia']:
            raise ValidationError('Las tareas de emergencia deben tener prioridad alta, crítica o emergencia.')
        
        # Validar que no haya duplicados activos para el mismo equipo
        if self.equipo and self.pk is None:  # Solo en creación
            tareas_activas = TareaMantenimiento.objects.filter(
                equipo=self.equipo,
                estado__in=['creada', 'planificada', 'asignada', 'en_progreso']
            )
            if tareas_activas.exists():
                raise ValidationError(
                    f'Ya existe una tarea activa para el equipo {self.equipo.codigo}. '
                    'Complete o cancele la tarea existente antes de crear una nueva.'
                )
    
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
    
    class Meta:
        unique_together = ['tarea', 'personal']


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
            filtros = {'producto': self.producto, 'tipo_crucero': self.tarea.tipo_crucero}
            if getattr(self.tarea, 'crucero_id', None):
                filtros['crucero'] = self.tarea.crucero
            inv = InventarioProducto.objects.get(**filtros)
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
    tipo_crucero = models.ForeignKey(TipoCrucero, on_delete=models.CASCADE, null=True, blank=True, help_text="Tipo de crucero donde ocurrió el incidente")
    severidad = models.CharField(max_length=20, choices=SEVERIDADES)
    
    reportado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    
    tarea_generada = models.ForeignKey(TareaMantenimiento, on_delete=models.SET_NULL, null=True, blank=True)
    resuelto = models.BooleanField(default=False)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    
    def generar_tarea_correctiva(self, usuario=None):
        """Genera automáticamente una tarea correctiva basada en el incidente"""
        if self.tarea_generada:
            return self.tarea_generada
        
        # Determinar prioridad basada en severidad
        prioridad_map = {
            'menor': 'baja',
            'moderada': 'media',
            'mayor': 'alta',
            'critica': 'critica',
        }
        
        tarea = TareaMantenimiento.objects.create(
            titulo=f"Correctivo: {self.titulo}",
            descripcion=f"Tarea generada automáticamente por incidente:\n\n{self.descripcion}",
            tipo='correctivo',
            prioridad=prioridad_map.get(self.severidad, 'media'),
            ubicacion=self.ubicacion,
            equipo=self.equipo,
            tipo_crucero=self.tipo_crucero,
            fecha_programada=timezone.now() + timedelta(hours=2),  # 2 horas para resolver
            creado_por=usuario,
        )
        
        self.tarea_generada = tarea
        self.save(update_fields=['tarea_generada'])
        
        return tarea
    
    def __str__(self):
        return f"Incidente: {self.titulo} - {self.get_severidad_display()}"
    
    class Meta:
        verbose_name = "Reporte de Incidente"
        verbose_name_plural = "Reportes de Incidentes"
        ordering = ['-fecha_reporte']


# ------------------------
# Módulo de Piscinas
# ------------------------

class Piscina(models.Model):
    """Piscinas del crucero"""
    nombre = models.CharField(max_length=100)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE)
    tipo_crucero = models.ForeignKey(TipoCrucero, on_delete=models.SET_NULL, null=True, blank=True)
    volumen_m3 = models.DecimalField(max_digits=7, decimal_places=2, validators=[MinValueValidator(Decimal('0.1'))])
    en_servicio = models.BooleanField(default=True)
    fecha_ultima_limpieza = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"Piscina {self.nombre} ({self.ubicacion.codigo_ubicacion})"
    
    class Meta:
        verbose_name = "Piscina"
        verbose_name_plural = "Piscinas"


class MedicionPiscina(models.Model):
    """Mediciones de parámetros de piscinas"""
    ESTADO_FILTRO = [
        ('ok', 'OK'),
        ('retrolavado', 'Requiere Retrolavado'),
        ('mantenimiento', 'Mantenimiento Requerido'),
    ]
    piscina = models.ForeignKey(Piscina, on_delete=models.CASCADE, related_name='mediciones')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ph = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(Decimal('0.0')), MaxValueValidator(Decimal('14.0'))])
    cloro_mg_l = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.0')), MaxValueValidator(Decimal('10.0'))])
    temperatura_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    turbidez_ntu = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    presion_filtro_bar = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    estado_filtro = models.CharField(max_length=20, choices=ESTADO_FILTRO, default='ok')
    retrolavado_realizado = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)
    
    def clean(self):
        # Validaciones básicas de rango
        if self.ph is not None and (self.ph < Decimal('0') or self.ph > Decimal('14')):
            raise ValidationError('El pH debe estar entre 0 y 14.')
        if self.cloro_mg_l is not None and (self.cloro_mg_l < Decimal('0') or self.cloro_mg_l > Decimal('10')):
            raise ValidationError('El cloro debe estar entre 0 y 10 mg/L.')
        
        # Validaciones de rangos críticos que requieren acción inmediata
        if self.ph is not None:
            if self.ph < Decimal('6.8'):
                raise ValidationError('⚠️ pH CRÍTICO BAJO (< 6.8): Riesgo de corrosión y molestias. Aplicar elevador de pH INMEDIATAMENTE.')
            elif self.ph > Decimal('8.2'):
                raise ValidationError('⚠️ pH CRÍTICO ALTO (> 8.2): Riesgo de incrustaciones y reducción de eficacia del cloro. Aplicar reductor de pH INMEDIATAMENTE.')
        
        if self.cloro_mg_l is not None:
            if self.cloro_mg_l < Decimal('0.5'):
                raise ValidationError('⚠️ CLORO CRÍTICO BAJO (< 0.5 mg/L): Riesgo sanitario alto. Aplicar hipoclorito de sodio INMEDIATAMENTE.')
            elif self.cloro_mg_l > Decimal('5'):
                raise ValidationError('⚠️ CLORO CRÍTICO ALTO (> 5 mg/L): Riesgo de irritación severa. Suspender dosificación y ventilar área INMEDIATAMENTE.')
        
        # Validar temperatura realista
        if self.temperatura_c is not None:
            if self.temperatura_c < Decimal('10') or self.temperatura_c > Decimal('40'):
                raise ValidationError('La temperatura debe estar entre 10°C y 40°C.')
        
        # No permitir mediciones futuras
        if hasattr(self, 'fecha_hora') and self.fecha_hora and self.fecha_hora > timezone.now():
            raise ValidationError('No se pueden registrar mediciones futuras.')
    
    @property
    def en_rango(self):
        """Rangos típicos: pH 7.2-7.8, Cloro 1-3 mg/L"""
        ok_ph = self.ph is not None and Decimal('7.2') <= self.ph <= Decimal('7.8')
        ok_cl = self.cloro_mg_l is not None and Decimal('1') <= self.cloro_mg_l <= Decimal('3')
        return ok_ph and ok_cl
    
    @property
    def necesita_alerta(self):
        """Determina si la medición necesita alerta"""
        return not self.en_rango
    
    @property
    def tipo_alerta(self):
        """Tipo de alerta según el parámetro fuera de rango"""
        alertas = []
        if self.ph is not None and not (Decimal('7.2') <= self.ph <= Decimal('7.8')):
            if self.ph < Decimal('7.2'):
                alertas.append('pH BAJO')
            else:
                alertas.append('pH ALTO')
        
        if self.cloro_mg_l is not None and not (Decimal('1') <= self.cloro_mg_l <= Decimal('3')):
            if self.cloro_mg_l < Decimal('1'):
                alertas.append('CLORO BAJO')
            else:
                alertas.append('CLORO ALTO')
        
        return ' / '.join(alertas) if alertas else ''
    
    @property
    def recomendacion(self):
        """Recomendación de acción basada en mediciones"""
        recomendaciones = []
        
        if self.ph is not None:
            if self.ph < Decimal('7.2'):
                recomendaciones.append('Agregar elevador de pH')
            elif self.ph > Decimal('7.8'):
                recomendaciones.append('Agregar reductor de pH')
        
        if self.cloro_mg_l is not None:
            if self.cloro_mg_l < Decimal('1'):
                recomendaciones.append('Agregar hipoclorito de sodio')
            elif self.cloro_mg_l > Decimal('3'):
                recomendaciones.append('Suspender dosificación de cloro temporalmente')
        
        if self.presion_filtro_bar is not None and self.presion_filtro_bar > Decimal('2.0'):
            recomendaciones.append('Realizar retrolavado del filtro')
        
        return ' • '.join(recomendaciones) if recomendaciones else 'Parámetros normales'
    
    def __str__(self):
        return f"Medición {self.piscina.nombre} - {self.fecha_hora:%Y-%m-%d %H:%M}"
    
    class Meta:
        verbose_name = "Medición de Piscina"
        verbose_name_plural = "Mediciones de Piscina"
        ordering = ['-fecha_hora']


# Nuevos modelos para funcionalidades avanzadas

class PlantillaTarea(models.Model):
    """Plantillas de tareas estándar (SOP)"""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo_equipo = models.ForeignKey(TipoEquipo, on_delete=models.CASCADE, null=True, blank=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.CASCADE, null=True, blank=True)
    tipo_tarea = models.CharField(max_length=20, choices=TareaMantenimiento.TIPOS_TAREA)
    tiempo_estimado_horas = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.0'))
    prioridad_default = models.CharField(max_length=20, choices=TareaMantenimiento.PRIORIDADES, default='media')
    instrucciones = models.TextField(help_text="Instrucciones paso a paso")
    productos_necesarios = models.ManyToManyField(Producto, through='ProductoPlantilla', blank=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Plantilla: {self.nombre}"
    
    class Meta:
        verbose_name = "Plantilla de Tarea"
        verbose_name_plural = "Plantillas de Tareas"


class ProductoPlantilla(models.Model):
    """Productos necesarios para una plantilla de tarea"""
    plantilla = models.ForeignKey(PlantillaTarea, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_estimada = models.DecimalField(max_digits=10, decimal_places=2)
    obligatorio = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.plantilla.nombre} - {self.producto.nombre}"


class ChecklistItem(models.Model):
    """Items de checklist para tareas"""
    tarea = models.ForeignKey(TareaMantenimiento, on_delete=models.CASCADE, related_name='checklist_items')
    descripcion = models.CharField(max_length=300)
    completado = models.BooleanField(default=False)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    usuario_completado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    orden = models.IntegerField(default=1)
    obligatorio = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if self.completado and not self.fecha_completado:
            self.fecha_completado = timezone.now()
        elif not self.completado:
            self.fecha_completado = None
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.tarea.titulo} - {self.descripcion}"
    
    class Meta:
        ordering = ['orden', 'id']


class AdjuntoTarea(models.Model):
    """Adjuntos (imágenes, PDFs) para tareas"""
    TIPOS_ARCHIVO = [
        ('imagen', 'Imagen'),
        ('pdf', 'PDF'),
        ('documento', 'Documento'),
        ('otro', 'Otro'),
    ]
    
    tarea = models.ForeignKey(TareaMantenimiento, on_delete=models.CASCADE, related_name='adjuntos')
    archivo = models.FileField(upload_to='adjuntos_tareas/%Y/%m/')
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPOS_ARCHIVO)
    descripcion = models.TextField(blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.tarea.titulo} - {self.nombre}"
    
    class Meta:
        ordering = ['-fecha_subida']


class MantenimientoRecurrente(models.Model):
    """Configuración de mantenimientos recurrentes"""
    FRECUENCIAS = [
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
        ('bimestral', 'Bimestral'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo_equipo = models.ForeignKey(TipoEquipo, on_delete=models.CASCADE)
    tipo_crucero = models.ForeignKey(TipoCrucero, on_delete=models.CASCADE)
    plantilla_tarea = models.ForeignKey(PlantillaTarea, on_delete=models.CASCADE, null=True, blank=True)
    frecuencia = models.CharField(max_length=20, choices=FRECUENCIAS)
    dias_adelanto = models.IntegerField(default=0, help_text="Días de anticipación para crear la tarea")
    activo = models.BooleanField(default=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    ultima_generacion = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.get_frecuencia_display()}"
    
    class Meta:
        verbose_name = "Mantenimiento Recurrente"
        verbose_name_plural = "Mantenimientos Recurrentes"


class FiltroGuardado(models.Model):
    """Filtros guardados para listas de tareas"""
    nombre = models.CharField(max_length=100)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    filtros = models.JSONField(default=dict)  # Almacena los parámetros del filtro
    publico = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} {'(Público)' if self.publico else '(Privado)'}"
    
    class Meta:
        verbose_name = "Filtro Guardado"
        verbose_name_plural = "Filtros Guardados"