from django.db import models
from django.contrib.auth.models import User

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

class Habitacion(models.Model):
    crucero = models.CharField(max_length=20, choices=[
        ("vision", "Vision of the Seas (Pequeño)"),
        ("voyager", "Voyager of the Seas (Mediano)"),
        ("oasis", "Oasis of the Seas (Grande)"),
    ])
    numero = models.CharField(max_length=10, unique=True)  # código XABCD
    piso = models.IntegerField(default=1)
    lado = models.CharField(max_length=10, choices=[("babor", "Babor"), ("estribor", "Estribor")])
    vista_mar = models.BooleanField(default=False)
    tipo_habitacion = models.ForeignKey(TipoHabitacion, on_delete=models.CASCADE)
    reservada = models.BooleanField(default=False)

    def __str__(self):
        return f"Habitación {self.numero} ({self.tipo_habitacion})"
    
class Entretenimiento(models.Model):
    CRUCEROS = [
        ("vision", "Vision of the Seas"),
        ("voyager", "Voyager of the Seas"),
        ("oasis", "Oasis of the Seas"),
    ]

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    crucero = models.CharField(max_length=20, choices=CRUCEROS)
    dia = models.IntegerField() 
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    reservada = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} (Día {self.dia}) - {self.get_crucero_display()}"
    
class Viaje(models.Model):
    nombre = models.CharField(max_length=100) 
    dia_actual = models.PositiveIntegerField(default=1)
    total_dias = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.nombre} (Día {self.dia_actual}/{self.total_dias})"
    
class Itinerario(models.Model):
    viaje = models.ForeignKey(Viaje, on_delete=models.CASCADE, related_name="itinerario")
    dia = models.PositiveIntegerField()
    destino = models.CharField(max_length=100)
    descripcion = models.TextField()

    class Meta:
        unique_together = ("viaje", "dia")
        ordering = ["dia"]

    def __str__(self):
        return f"Día {self.dia}: {self.destino}"

class Reserva(models.Model):
    ESTADOS = [
        ("pendiente", "Pendiente"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservas")
    habitacion = models.ForeignKey(
        Habitacion, on_delete=models.CASCADE, related_name="reservas", null=True, blank=True
    )
    entretenimiento = models.ForeignKey(
        Entretenimiento, on_delete=models.CASCADE, related_name="reservas", null=True, blank=True
    )
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="pendiente")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserva {self.id} - {self.usuario.username} ({self.estado})"

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ["-fecha_creacion"]


