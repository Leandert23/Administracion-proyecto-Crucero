from django.db import models
from django.db.models import QuerySet
from datetime import datetime


class Almacen(models.Model):
    nombre = models.CharField(max_length=5, unique=True)
    capacidad_total = models.IntegerField(help_text="Capacidad total en m²")
    secciones: QuerySet["SeccionAlmacen"]

    def __str__(self):
        return str(self.nombre)

    def capacidad_utilizada(self):
        return sum(seccion.capacidad for seccion in self.secciones.all())

    def capacidad_disponible(self):
        return self.capacidad_total - self.capacidad_utilizada()

    class Meta:
        verbose_name = "Almacén"
        verbose_name_plural = "Almacenes"


class SeccionAlmacen(models.Model):
    # Tipos de secciones
    TIPO_SECCION = [
        ("REFRIGERACION", "Cámara de Refrigeración"),
        ("CONGELACION", "Cámara de Congelación"),
        ("SECO", "Almacén Seco"),
        ("ESTANTERIAS", "Estanterías"),
        ("CUARTO_FRIO", "Cuarto Frío"),
        ("SILOS", "Silos"),
        ("TANQUES", "Tanques"),
    ]

    almacen_fk = models.ForeignKey(
        Almacen, on_delete=models.CASCADE, related_name="secciones"
    )
    almacen: Almacen
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_SECCION)
    capacidad = models.IntegerField(help_text="Capacidad en m²")
    temperatura = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Temperatura en °C (si aplica)",
    )
    humedad = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Humedad relativa % (si aplica)",
    )
    esta_activa = models.BooleanField()

    class Meta:
        verbose_name = "Sección de Almacén"
        verbose_name_plural = "Secciones de Almacén"
        unique_together = ["almacen_fk", "nombre"]

    def __str__(self):
        return f"{self.almacen.nombre} - {self.nombre} ({self.tipo})"


class Producto(models.Model):
    TIPO_MEDIDA = [
        ("L", "Litros"),
        ("M", "Metros"),
        ("G", "Gramos"),
        ("U", "Unidades"),
    ]
    TIPO_PRODUCTO = ["Comida", "Bienes"]
    SUBTIPO_PRODUCTO = [
        "Caducable",
        "No caducable" "Refrigerado",
        "No refrigerado",
        "Bebida",
        "Licor",
        "Repuestos",
        "Materiales de limpieza",
        "Materiales medicos",
        "Bienes activos",
    ]
    nombre = models.CharField(max_length=100, unique=True)
    precio = models.DecimalField(max_digits=5, decimal_places=2)
    tipo = models.CharField(
        max_length=20
    )  # TODO: Necesitamos tener un tipo de producto, CUANDO LOS OTROS MODULOS SE ORGANICEN
    cantidad = models.IntegerField()
    medida = models.CharField(choices=TIPO_MEDIDA)

    seccion_almacen = models.ForeignKey(
        SeccionAlmacen, on_delete=models.CASCADE, related_name="productos"
    )

    def save(self, *args, **kwargs):
        if self.cantidad < 0:
            return  # TODO: Implementar excepciones personalizadas
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"


class MovimientoAlmacen(models.Model):
    TIPO_MOVIMIENTO = [
        ("IN", "Ingreso"),
        ("OUT", "Egreso"),
        ("NEW", "Creado"),
    ]
    TIPO_MODULO = [
        ("RESTAURANTE", "Restaurante"),
        ("VENTAS", "Ventas"),
        ("COMPRAS", "Compras"),
        ("BARES_SNACKS", "Bares Snacks"),
        ("MANTENIMIENTO", "Mantenimiento"),
        ("ENTRETENIMIENTO", "Entretenimiento"),
        ("RECURSOS_HUMANOS", "Recursos Humanos"),
        ("RESERVACIONES", "Reservaciones"),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="movimientos"
    )
    cantidad = models.IntegerField()
    fecha = models.DateField(default=datetime.today())
    modulo = models.CharField(max_length=20, choices=TIPO_MODULO)

    class Meta:
        verbose_name = "Movimiento de Producto"
        verbose_name_plural = "Movimientos de Producto"
