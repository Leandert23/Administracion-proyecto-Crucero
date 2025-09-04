from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class Barco(models.Model):
    """Modelo para almacenar información de los barcos"""
    nombre = models.CharField(max_length=100, unique=True)
    capacidad = models.PositiveIntegerField(help_text="Capacidad total de pasajeros")
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Barco"
        verbose_name_plural = "Barcos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Ruta(models.Model):
    """Modelo para almacenar las rutas de crucero"""
    nombre = models.CharField(max_length=200)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    duracion_dias = models.PositiveIntegerField()
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Ruta"
        verbose_name_plural = "Rutas"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.origen} - {self.destino})"


class Viaje(models.Model):
    """Modelo para almacenar los viajes específicos"""
    ESTADO_CHOICES = [
        ('programado', 'Programado'),
        ('en_curso', 'En Curso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    barco = models.ForeignKey(Barco, on_delete=models.CASCADE, related_name='viajes')
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='viajes')
    fecha_salida = models.DateTimeField()
    fecha_llegada = models.DateTimeField()
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='programado')
    capacidad_disponible = models.PositiveIntegerField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Viaje"
        verbose_name_plural = "Viajes"
        ordering = ['-fecha_salida']

    def __str__(self):
        return f"{self.barco} - {self.ruta} ({self.fecha_salida.strftime('%d/%m/%Y')})"

    def save(self, *args, **kwargs):
        # Calcular capacidad disponible si es un nuevo viaje
        if not self.pk:
            self.capacidad_disponible = self.barco.capacidad
        super().save(*args, **kwargs)


class TipoCabina(models.Model):
    """Modelo para los tipos de cabina disponibles"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    capacidad_personas = models.PositiveIntegerField()
    precio_por_noche = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Cabina"
        verbose_name_plural = "Tipos de Cabina"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.capacidad_personas} personas)"


class Cabina(models.Model):
    """Modelo para las cabinas específicas de cada barco"""
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('reservada', 'Reservada'),
        ('ocupada', 'Ocupada'),
        ('mantenimiento', 'En Mantenimiento'),
    ]

    barco = models.ForeignKey(Barco, on_delete=models.CASCADE, related_name='cabinas')
    tipo_cabina = models.ForeignKey(TipoCabina, on_delete=models.CASCADE, related_name='cabinas')
    numero = models.CharField(max_length=20)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cabina"
        verbose_name_plural = "Cabinas"
        unique_together = ['barco', 'numero']
        ordering = ['barco', 'numero']

    def __str__(self):
        return f"{self.barco} - Cabina {self.numero} ({self.tipo_cabina.nombre})"


class Reserva(models.Model):
    """Modelo principal para las reservas de cabina"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
               ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]

    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, related_name='reservas')
    cabina = models.ForeignKey(Cabina, on_delete=models.CASCADE, related_name='reservas')
    cliente = models.ForeignKey('ventas.Cliente', on_delete=models.CASCADE, related_name='reservas')
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    notas = models.TextField(blank=True)
    agente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reservas_creadas')

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha_reserva']

    def __str__(self):
        return f"Reserva {self.id} - {self.cliente} - {self.viaje}"

    def save(self, *args, **kwargs):
        # Calcular precio total basado en la duración del viaje y tipo de cabina
        if not self.pk:  # Solo para nuevas reservas
            duracion_noches = (self.viaje.fecha_llegada - self.viaje.fecha_salida).days
            self.precio_total = self.cabina.tipo_cabina.precio_por_noche * duracion_noches
        
        # Actualizar estado de la cabina
        if self.estado == 'confirmada':
            self.cabina.estado = 'reservada'
            self.cabina.save()
        elif self.estado == 'cancelada' and self.cabina.estado == 'reservada':
            self.cabina.estado = 'disponible'
            self.cabina.save()
        
        super().save(*args, **kwargs)


class Pasajero(models.Model):
    """Modelo para almacenar información de los pasajeros de cada reserva"""
    TIPO_DOCUMENTO_CHOICES = [
        ('dni', 'DNI'),
        ('pasaporte', 'Pasaporte'),
        ('cedula', 'Cédula'),
        ('otro', 'Otro'),
    ]

    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='pasajeros')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES)
    numero_documento = models.CharField(max_length=50)
    nacionalidad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    es_titular = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Pasajero"
        verbose_name_plural = "Pasajeros"
        ordering = ['-es_titular', 'apellido', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.reserva}"


class ServicioAdicional(models.Model):
    """Modelo para servicios adicionales que se pueden contratar"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Servicio Adicional"
        verbose_name_plural = "Servicios Adicionales"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


class ServicioReserva(models.Model):
    """Modelo para relacionar servicios adicionales con reservas"""
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='servicios')
    servicio = models.ForeignKey(ServicioAdicional, on_delete=models.CASCADE, related_name='reservas')
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_contratacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Servicio de Reserva"
        verbose_name_plural = "Servicios de Reserva"
        unique_together = ['reserva', 'servicio']

    def __str__(self):
        return f"{self.servicio} - {self.reserva}"

    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
