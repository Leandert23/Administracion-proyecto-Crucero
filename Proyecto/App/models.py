from django.db import models
from django.conf import settings



# TIPOS DE HABITACIONES

class TipoHabitacion(models.Model):
    CATEGORIAS = [
        ("basico", "Camarote Básico"),
        ("premium", "Camarote Premium"),
    ]
    SUBTIPOS = [
        ("sencillo", "Sencillo (2 personas)"),
        ("doble", "Doble (4 personas)"),
    ]

    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default="basico")
    subtipo = models.CharField(max_length=20, choices=SUBTIPOS, default="sencillo")
    capacidad = models.IntegerField(default=2)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)

    def __str__(self):
        return f"{self.get_categoria_display()} - {self.get_subtipo_display()}"



# HABITACIONES

class Habitacion(models.Model):
    LADOS = [
        ("babor", "Babor"),
        ("estribor", "Estribor"),
    ]

    crucero = models.CharField(max_length=20)  # vision, voyager, oasis
    numero = models.CharField(max_length=10)
    piso = models.IntegerField(default=1)
    lado = models.CharField(max_length=10, choices=LADOS)
    vista_mar = models.BooleanField(default=False)
    reservada = models.BooleanField(default=False)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    tipo_habitacion = models.ForeignKey(TipoHabitacion, on_delete=models.CASCADE)

    def _str_(self):
        return f"{self.crucero} - Hab {self.numero} ({self.tipo_habitacion})"



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

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservas")
    habitacion = models.ForeignKey(Habitacion, null=True, blank=True, on_delete=models.CASCADE)
    entretenimiento = models.ForeignKey(Entretenimiento, null=True, blank=True, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, null=True, blank=True, on_delete=models.CASCADE)
    evento_personalizado = models.ForeignKey(EventoPersonalizado, null=True, blank=True, on_delete=models.CASCADE)

    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        if self.habitacion:
            return f"Reserva Habitación {self.habitacion.numero} ({self.usuario})"
        if self.entretenimiento:
            return f"Reserva Entretenimiento {self.entretenimiento.nombre} ({self.usuario})"
        if self.mesa:
            return f"Reserva Mesa {self.mesa.numero} ({self.usuario})"
        if self.evento_personalizado:
            return f"Reserva Evento {self.evento_personalizado.nombre} ({self.usuario})"
        return f"Reserva #{self.id} ({self.usuario})"
