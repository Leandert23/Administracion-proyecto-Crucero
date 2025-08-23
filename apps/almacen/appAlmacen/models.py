from django.db import models
from django.db.models import QuerySet

class Almacen(models.Model):
    nombre = models.CharField(max_length=5, unique=True)
    capacidad_total = models.IntegerField(help_text="Capacidad total en m²")
    secciones: QuerySet["SeccionAlmacen"]

    def __str__(self):
        return str(self.nombre)
   
    def capacidad_utilizada(self):
        return sum(seccion.capacidad for seccion in self.secciones.all())
    
    def capacidad_disponible(self):
        return self.capacidad_total.value_from_object(self) - self.capacidad_utilizada()

class SeccionAlmacen(models.Model):
    # Tipos de secciones
    TIPO_SECCION = [
        ('REFRIGERACION', 'Cámara de Refrigeración'),
        ('CONGELACION', 'Cámara de Congelación'),
        ('SECO', 'Almacén Seco'),
        ('ESTANTERIAS', 'Estanterías'),
        ('CUARTO_FRIO', 'Cuarto Frío'),
        ('SILOS', 'Silos'),
        ('TANQUES', 'Tanques'),
    ]
    
    almacen_fk = models.ForeignKey(
        Almacen, 
        on_delete=models.CASCADE,
        related_name="secciones"
    )
    almacen: Almacen
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_SECCION)
    capacidad = models.IntegerField(help_text="Capacidad en m²")
    temperatura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,help_text="Temperatura en °C (si aplica)")
    humedad = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Humedad relativa % (si aplica)"
    )
    esta_activa = models.BooleanField()

    class Meta:
        verbose_name = "Sección de Almacén"
        verbose_name_plural = "Secciones de Almacén"
        unique_together = ['almacen', 'nombre']

    def __str__(self):
        return f"{self.almacen.nombre} - {self.nombre} ({self.tipo})"


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=5, decimal_places=2)
    tipo = models.CharField(max_length=20) # TODO: Necesitamos tener un tipo de producto, CUANDO LOS OTROS MODULOS SE ORGANICEN
    cantidad = models.IntegerField()

    seccion_almacen = models.ForeignKey(
        SeccionAlmacen,
        on_delete=models.CASCADE,
        related_name="productos"
    )

    def save(self, *args, **kwargs):
        if self.cantidad < 0:
            return # TODO: Implementar excepciones personalizadas
        super().save(*args, **kwargs)