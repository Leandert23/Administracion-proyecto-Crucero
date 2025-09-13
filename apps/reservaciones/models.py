from django.db import models
from django.conf import settings
from ..cruceros.models import Habitacion
from ..entretenimiento.models import Actividad, ActividadRutinaria





# RESTAURANTE Y MESAS

class Restaurante(models.Model):
    crucero = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} ({self.crucero})"


class Mesa(models.Model):
    crucero = models.CharField(max_length=20)
    numero = models.CharField(max_length=10)
    capacidad = models.IntegerField(default=4)
    reservada = models.BooleanField(default=False)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name="mesas")

    def __str__(self):
        return f"Mesa {self.numero} - {self.restaurante.nombre}"



# ENTRETENIMIENTO

class Entretenimiento(models.Model):
    crucero = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    dia = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reservada = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} (Día {self.dia}) - {self.crucero}"



# EVENTOS PERSONALIZADOS

class EventoPersonalizado(models.Model):
    crucero = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    materiales = models.TextField(blank=True, null=True)
    dia = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=700.00)  # Precio fijo

    def save(self, *args, **kwargs):
        if self.materiales:
            lista_materiales = [m.strip() for m in self.materiales.split(",") if m.strip()]
            if len(lista_materiales) > 10:
                raise ValueError("No se permiten más de 10 materiales en un evento personalizado.")
        super().save(*args, **kwargs)

    def _str_(self):
        return f"Evento: {self.nombre} (Día {self.dia}) - {self.crucero}"


# VIAJE

class Viaje(models.Model):
    crucero = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    dia_actual = models.PositiveIntegerField(default=0)  # Día 0 = planificación
    total_dias = models.PositiveIntegerField(default=8)  # Viaje siempre de 8 días

    def __str__(self):
        return f"Viaje {self.nombre} ({self.crucero}) - Día {self.dia_actual}/{self.total_dias}"



# RESERVAS

class Reserva(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
    ]

    # Datos del cliente
    nombre_cliente = models.CharField(max_length=100, blank=True, null=True)
    apellido_cliente = models.CharField(max_length=100, blank=True, null=True)
    fecha_nacimiento_cliente = models.DateField(blank=True, null=True)
    numero_personas = models.PositiveIntegerField(default=1)

    # Código de ubicación de la habitación (en lugar de FK)
    codigo_ubicacion_habitacion = models.CharField(max_length=6, blank=True, null=True, help_text="Código UUAIII de la habitación reservada")

    # Relaciones con actividades de entretenimiento
    actividad_pago = models.ForeignKey(Actividad, null=True, blank=True, on_delete=models.CASCADE, related_name='reservas_pago')
    actividad_rutinaria = models.ForeignKey(ActividadRutinaria, null=True, blank=True, on_delete=models.CASCADE, related_name='reservas_rutinarias')

    # Costo total calculado
    costo_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    mesa = models.ForeignKey(Mesa, null=True, blank=True, on_delete=models.CASCADE)
    evento_personalizado = models.ForeignKey(EventoPersonalizado, null=True, blank=True, on_delete=models.CASCADE)

    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        cliente_info = f"{self.nombre_cliente} {self.apellido_cliente}" if self.nombre_cliente else f"Cliente #{self.id}"
        if self.codigo_ubicacion_habitacion:
            return f"Reserva Habitación {self.codigo_ubicacion_habitacion} ({cliente_info})"
        if self.actividad_pago:
            return f"Reserva Actividad Pago {self.actividad_pago.titulo} ({cliente_info})"
        if self.actividad_rutinaria:
            return f"Reserva Actividad Rutinaria {self.actividad_rutinaria.titulo} ({cliente_info})"
        if self.mesa:
            return f"Reserva Mesa {self.mesa.numero} ({cliente_info})"
        if self.evento_personalizado:
            return f"Reserva Evento {self.evento_personalizado.nombre} ({cliente_info})"
        return f"Reserva #{self.id} ({cliente_info})"
