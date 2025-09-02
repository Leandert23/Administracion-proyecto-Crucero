from django.db import models
from django.db.models import Max, Sum
from django.core.exceptions import ValidationError

from ..cruceros.Services.fecha_general import obtener_fecha_actual
from ..cruceros.models import Instalacion

class SeccionAlmacen(models.Model):
    TIPO_SECCION = [
        ("REFRIGERACION", "Cámara de Refrigeración"),
        ("CONGELACION", "Cámara de Congelación"),
        ("SECO", "Almacén Seco"),
        ("ESTANTERIAS", "Estanterías"),
        ("CUARTO_FRIO", "Cuarto Frío"),
        ("SILOS", "Silos"),
        ("TANQUES", "Tanques"),
    ]

    almacen = models.ForeignKey(
        Instalacion,
        on_delete=models.CASCADE,
        related_name="secciones",
        limit_choices_to={"tipo": "almacen"}
    )
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_SECCION)
    capacidad = models.PositiveIntegerField(help_text="Capacidad en m²")
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
    esta_activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sección de Almacén"
        verbose_name_plural = "Secciones de Almacén"
        unique_together = ["almacen", "nombre"]

    def __str__(self):
        return f"{self.almacen.nombre} - {self.nombre} ({self.tipo})"


class Producto(models.Model):
    TIPO_PRODUCTO_CHOICES = [
        ("COMIDA", "Comida"),
        ("BIENES", "Bienes"),
    ]

    SUBTIPO_PRODUCTO_CHOICES = [
        ("CADUCABLE", "Caducable"),
        ("NO_CADUCABLE", "No caducable"),
        ("REFRIGERADO", "Refrigerado"),
        ("NO_REFRIGERADO", "No refrigerado"),
        ("BEBIDA", "Bebida"),
        ("LICOR", "Licor"),
        ("REPUESTOS", "Repuestos"),
        ("LIMPIEZA", "Materiales de limpieza"),
        ("MEDICOS", "Materiales médicos"),
        ("ACTIVOS", "Bienes activos"),
    ]

    MEDIDA_CHOICES = [
        ("L", "Litros"),
        ("M", "Metros"),
        ("K", "Kilogramos"),
        ("U", "Unidades"),
    ]

    SUBTIPOS_VALIDOS_POR_TIPO = {
        "COMIDA": {"CADUCABLE", "NO_CADUCABLE", "REFRIGERADO", "NO_REFRIGERADO", "BEBIDA", "LICOR"},
        "BIENES": {"REPUESTOS", "LIMPIEZA", "MEDICOS", "ACTIVOS"},
    }

    nombre = models.CharField(max_length=100, db_index=True)
    tipo = models.CharField(max_length=10, choices=TIPO_PRODUCTO_CHOICES)
    subtipo = models.CharField(
        max_length=15,
        choices=SUBTIPO_PRODUCTO_CHOICES,
        blank=True,
        null=True,
        help_text="Subclasificación (opcional)"
    )
    seccion = models.ForeignKey('SeccionAlmacen', on_delete=models.CASCADE, related_name='productos')
    cantidad_ideal = models.PositiveIntegerField(null=False)
    medida = models.CharField(max_length=1, choices=MEDIDA_CHOICES)
    
    @property
    def cantidad(self):
        # aggregate hace una sola operación de suma en el lado de la base de datos,
        # de esa manera evitamos sumar con bucles de python (más lento)
        total = self.lotes.aggregate(total=Sum('cantidad_productos'))['total'] or 0
        return total

    @property
    def estado(self):
        cantidad = self.cantidad
        if cantidad is None:
            raise Exception(f"Error: La cantidad del producto {self.nombre} es inválida")
        if cantidad <= 0:
            return 'NO HAY STOCK'
        if cantidad <= self.cantidad_ideal * 0.30:
            return 'BAJO'
        if cantidad <= self.cantidad_ideal * 0.60:
            return 'MEDIO'
        else: 
            return 'ALTO'

    
    def clean(self):
        if self.subtipo:
            subtipo_up = self.subtipo.upper()
            tipo_up = (self.tipo or "").upper()
            if tipo_up in self.SUBTIPOS_VALIDOS_POR_TIPO:
                if subtipo_up not in self.SUBTIPOS_VALIDOS_POR_TIPO[tipo_up]:
                    raise ValidationError({
                        "subtipo": f"El subtipo '{self.subtipo}' no es válido para el tipo '{self.tipo}'."
                    })
            else:
                raise ValidationError({"tipo": "Tipo de producto desconocido."})

    def save(self, *args, **kwargs):
        self.full_clean(exclude=None)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        indexes = [
            models.Index(fields=["tipo", "subtipo"], name="idx_producto_tipo_subtipo"),
        ]

class Lote(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="lotes")
    numero_lote = models.IntegerField()
    cantidad_productos = models.PositiveIntegerField()
    precio_lote = models.PositiveIntegerField()
    fecha_ingreso = models.DateField(default=obtener_fecha_actual)
    fecha_caducidad = models.DateField(null=True)
    
    class Meta:
        verbose_name = "Lote de Producto"
        verbose_name_plural = "Lotes de Producto"
        unique_together = [["producto", "numero_lote"]] 

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad_productos}"

    def save(self, *args, **kwargs):
        """Asignar automáticamente numero_lote incremental por producto si no se provee."""
        if not getattr(self, 'numero_lote', None):
            max_val = Lote.objects.filter(producto=self.producto).aggregate(Max('numero_lote'))
            current_max = max_val.get('numero_lote__max') or 0
            self.numero_lote = current_max + 1

        super().save(*args, **kwargs)

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
        Producto,
        on_delete=models.CASCADE,
        related_name="movimientos"
    )
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name="lotes")
    cantidad = models.PositiveIntegerField()
    fecha = models.DateField(default=obtener_fecha_actual)
    modulo = models.CharField(max_length=20, choices=TIPO_MODULO)
    descripcion = models.CharField(max_length=255, blank=True, null=True, help_text="Descripción o nota del movimiento")
    
    class Meta:
        verbose_name = "Movimiento de Producto"
        verbose_name_plural = "Movimientos de Producto"