from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.creador_embarcaciones.models import Habitaciones, Embarcacion

class Cliente(models.Model):
    """Modelo para almacenar información de los clientes"""
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Venta(models.Model):
    """Modelo principal para registrar todas las ventas del sistema"""
    TIPO_VENTA_CHOICES = [
        ('reserva', 'Reserva de Cabina'),
        ('restaurante', 'Restaurante'),
        ('bar_snack', 'Bar/Snack'),
        ('entretenimiento', 'Entretenimiento'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]
    
    crucero = models.ForeignKey('cruceros.Crucero', on_delete=models.CASCADE, related_name='ventas')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='ventas')
    tipo_venta = models.CharField(max_length=20, choices=TIPO_VENTA_CHOICES)
    descripcion = models.TextField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_venta']
    
    def __str__(self):
        return f"Venta {self.id} - {self.cliente} - {self.get_tipo_venta_display()}"

class DetalleVenta(models.Model):
    """Modelo para almacenar los detalles de cada venta"""
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    concepto = models.CharField(max_length=200)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"
    
    def __str__(self):
        return f"{self.concepto} - {self.venta}"
    
    def save(self, *args, **kwargs):
        # Calcular automáticamente el subtotal
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

class MetodoPago(models.Model):
    """Modelo para los métodos de pago disponibles"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
    
    def __str__(self):
        return self.nombre

class Pago(models.Model):
    """Modelo para registrar los pagos de las ventas"""
    ESTADO_PAGO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado'),
    ]
    
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='pagos')
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='pendiente')
    referencia = models.CharField(max_length=100, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-fecha_pago']
    
    def __str__(self):
        return f"Pago {self.id} - {self.venta} - {self.monto}"


class VentaHabitacion(models.Model):
    """Modelo específico para ventas de habitaciones"""
    ESTADO_CHOICES = [
        ('reservada', 'Reservada'),
        ('ocupada', 'Ocupada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    # Información de la habitación
    habitacion = models.ForeignKey(
        Habitaciones, 
        on_delete=models.CASCADE, 
        related_name='ventas_habitacion'
    )
    embarcacion = models.ForeignKey(
        Embarcacion,
        on_delete=models.CASCADE,
        related_name='ventas_habitaciones'
    )
    
    # Información del cliente
    nombre_cliente = models.CharField(max_length=100, verbose_name="Nombre")
    apellido_cliente = models.CharField(max_length=100, verbose_name="Apellido")
    numero_pasaporte = models.CharField(max_length=50, verbose_name="Número de Pasaporte")
    
    # Información de la venta
    precio_venta = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Precio de Venta"
    )
    fecha_venta = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Venta")
    fecha_checkin = models.DateField(verbose_name="Fecha de Check-in", null=True, blank=True)
    fecha_checkout = models.DateField(verbose_name="Fecha de Check-out", null=True, blank=True)
    
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='reservada',
        verbose_name="Estado"
    )
    
    # Información adicional
    notas = models.TextField(blank=True, verbose_name="Notas adicionales")
    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Vendedor"
    )
    
    class Meta:
        verbose_name = "Venta de Habitación"
        verbose_name_plural = "Ventas de Habitaciones"
        ordering = ['-fecha_venta']
        unique_together = ['habitacion', 'fecha_checkin']  # Una habitación no puede venderse dos veces para la misma fecha
    
    def __str__(self):
        return f"Habitación {self.habitacion.numero} - {self.nombre_cliente} {self.apellido_cliente}"
    
    @property
    def nombre_completo_cliente(self):
        return f"{self.nombre_cliente} {self.apellido_cliente}"
    
    @property
    def duracion_estadia(self):
        if self.fecha_checkin and self.fecha_checkout:
            return (self.fecha_checkout - self.fecha_checkin).days
        return 0
    
    def save(self, *args, **kwargs):
        # Asignar automáticamente la embarcación basada en la habitación
        if self.habitacion and not self.embarcacion:
            self.embarcacion = self.habitacion.cubierta.embarcacion
        super().save(*args, **kwargs)
