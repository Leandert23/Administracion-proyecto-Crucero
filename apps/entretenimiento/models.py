from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from ..cruceros.models import Crucero, Viaje

class Actividad(models.Model):
    # ID único de la actividad (se crea automáticamente)
    id_actividad = models.AutoField(primary_key=True)
    # Relación con Viaje (actividad ligada a un viaje específico)
    viaje = models.ForeignKey(
        Viaje,
        on_delete=models.CASCADE,
        related_name='actividades',
        null=True,
        blank=True,
        help_text="Viaje al que pertenece esta actividad"
    )
    
    # Título de la actividad
    titulo = models.CharField(
        max_length=200,
        help_text="Título de la actividad"
    )
    
    # Descripción detallada
    descripcion = models.TextField(
        help_text="Descripción completa de la actividad"
    )
    
    # Día del crucero
    dia_crucero = models.IntegerField(
    help_text="Día del crucero (1-8)",
    choices=[(i, f"Día {i}") for i in range(1, 9)],  # Opciones del 1 al 8
    validators=[MinValueValidator(1), MaxValueValidator(8)]  # Validación
)
    
    # Coste de la actividad
    coste = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Coste de la actividad en euros"
    )
    
    # Hora de inicio
    hora_inicio = models.TimeField(
        help_text="Hora de inicio de la actividad"
    )
    
    # Hora de fin
    hora_fin = models.TimeField(
        help_text="Hora de finalización de la actividad"
    )
    
    # Máximo de participantes
    maximoActividad = models.IntegerField(
        help_text="Número máximo de participantes"
    )

    # URL de la imagen de la actividad
    img_src = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL o ruta de la imagen de la actividad"
    )

    class Meta:
        db_table = 'actividades_pago'  # ← Nombre de tabla personalizado
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ['dia_crucero', 'hora_inicio']
    
    def __str__(self):
        return f"{self.titulo} - {self.dia_crucero}"


class ActividadRutinaria(models.Model):
    # ID único de la actividad rutinaria (se crea automáticamente)
    id_actividad = models.AutoField(primary_key=True)
    viaje = models.ForeignKey(
        Viaje,
        on_delete=models.CASCADE,
        related_name='actividades_rutinarias',
        null=True,
        blank=True,
        help_text="Viaje al que pertenece esta actividad rutinaria"
    )

    # Título de la actividad
    titulo = models.CharField(
        max_length=200,
        help_text="Título de la actividad rutinaria"
    )

    # Descripción detallada
    descripcion = models.TextField(
        help_text="Descripción completa de la actividad rutinaria"
    )

    # Día del crucero
    dia_crucero = models.IntegerField(
        help_text="Día del crucero (1-8)",
        choices=[(i, f"Día {i}") for i in range(1, 9)],  # Opciones del 1 al 8
        validators=[MinValueValidator(1), MaxValueValidator(8)]  # Validación
    )

    # Hora de inicio
    hora_inicio = models.TimeField(
        help_text="Hora de inicio de la actividad"
    )

    # Hora de fin
    hora_fin = models.TimeField(
        help_text="Hora de finalización de la actividad"
    )

    # Máximo de participantes
    maximo_actividad = models.IntegerField(
        help_text="Número máximo de participantes"
    )

    # Ubicación de la actividad
    ubicacion = models.CharField(
        max_length=200,
        help_text="Ubicación donde se realiza la actividad"
    )

    # URL de la imagen de la actividad
    img_src = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL o ruta de la imagen de la actividad"
    )

    class Meta:
        db_table = 'actividad_rutinaria'  # ← Nombre de tabla personalizado
        verbose_name = "Actividad Rutinaria"
        verbose_name_plural = "Actividades Rutinarias"
        ordering = ['dia_crucero', 'hora_inicio']

    def __str__(self):
        return f"{self.titulo} - Día {self.dia_crucero} ({self.ubicacion})"


class RegistroActividadPago(models.Model):
    # ID único del registro (se crea automáticamente)
    id = models.AutoField(primary_key=True)
    viaje = models.ForeignKey(
        Viaje,
        on_delete=models.CASCADE,
        related_name='registros_pago_actividades',
        null=True,
        blank=True,
        help_text="Viaje asociado al registro de actividad de pago"
    )

    # Nombre del cliente
    nombre = models.CharField(
        max_length=100,
        help_text="Nombre del cliente"
    )

    # Apellido del cliente
    apellido = models.CharField(
        max_length=100,
        help_text="Apellido del cliente"
    )

    # Número de habitación
    n_habitacion = models.CharField(
        max_length=20,
        help_text="Número de habitación del cliente"
    )

    # Número de personas
    n_personas = models.IntegerField(
        help_text="Número de personas incluidas en el registro"
    )

    # Monto total
    monto_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Monto total del pago"
    )

    # Estado del registro
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
    ]
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        help_text="Estado actual del registro"
    )

    # ID de factura
    id_factura = models.CharField(
        max_length=50,
        unique=True,
        help_text="Identificador único de la factura"
    )

    # Fecha de creación automática
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de creación del registro"
    )

    class Meta:
        db_table = 'registro_actividad_pago'  # ← Nombre de tabla personalizado
        verbose_name = "Registro de Actividad de Pago"
        verbose_name_plural = "Registros de Actividades de Pago"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} {self.apellido} - Habitación {self.n_habitacion} - {self.monto_total}€"


class RegistroActividadRut(models.Model):
    # ID único del registro (se crea automáticamente)
    id = models.AutoField(primary_key=True)
    viaje = models.ForeignKey(
        Viaje,
        on_delete=models.CASCADE,
        related_name='registros_rutinarios',
        null=True,
        blank=True,
        help_text="Viaje asociado al registro de actividad rutinaria"
    )

    # Nombre del cliente
    nombre = models.CharField(
        max_length=100,
        help_text="Nombre del cliente"
    )

    # Apellido del cliente
    apellido = models.CharField(
        max_length=100,
        help_text="Apellido del cliente"
    )

    # Número de habitación
    n_habitacion = models.CharField(
        max_length=20,
        help_text="Número de habitación del cliente"
    )

    # Número de personas
    n_personas = models.IntegerField(
        help_text="Número de personas incluidas en el registro"
    )

    # Fecha de creación automática
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de creación del registro"
    )

    class Meta:
        db_table = 'registro_actividad_rut'  # ← Nombre de tabla personalizado
        verbose_name = "Registro de Actividad Rutinaria"
        verbose_name_plural = "Registros de Actividades Rutinarias"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} {self.apellido} - Habitación {self.n_habitacion} ({self.n_personas} personas)"