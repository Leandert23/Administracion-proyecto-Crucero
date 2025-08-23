from django.db import models

class Almacen(models.Model):
    nombre = models.CharField(max_length=6, unique=True)
    capacidad_total = models.IntegerField(help_text="Capacidad total en m²")

    def __str__(self):
        return self.nombre
    
    def capacidad_utilizada(self):
        return sum(seccion.capacidad for seccion in self.secciones.all())
    
    def capacidad_disponible(self):
        return self.capacidad_total - self.capacidad_utilizada()

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
        ('SEGURIDAD', 'Área de Seguridad'),
        ('OFICINA', 'Oficina Administrativa'),
        ('RECEPCION', 'Área de Recepción'),
        ('DESPACHO', 'Área de Despacho'),
    ]
    
    almacen = models.ForeignKey(
        Almacen, 
        on_delete=models.CASCADE,
    )
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
    esta_activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sección de Almacén"
        verbose_name_plural = "Secciones de Almacén"
        unique_together = ['almacen', 'nombre']

    def __str__(self):
        return f"{self.almacen.nombre} - {self.nombre} ({self.get_tipo_display()})"