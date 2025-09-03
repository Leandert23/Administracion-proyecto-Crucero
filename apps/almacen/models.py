from django.db import models
from django.db.models import Max, Sum
from django.core.exceptions import ValidationError

from ..cruceros.Services.fecha_general import obtener_fecha_actual
from ..cruceros.models import Instalacion


class SeccionAlmacen(models.Model):
    TIPOS_SECCION = [
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
    tipo = models.CharField(max_length=20, choices=TIPOS_SECCION)
    capacidad = models.PositiveIntegerField()
    temperatura = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humedad = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    esta_activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sección de Almacén"
        verbose_name_plural = "Secciones de Almacén"
        unique_together = ["almacen", "nombre"]

    def __str__(self):
        return f"{self.almacen.nombre} - {self.nombre} ({self.tipo})"


class Producto(models.Model):
    TIPOS_PRODUCTO = [
        ("COMIDA", "Comida"),
        ("BIENES", "Bienes"),
    ]

    SUBTIPOS_PRODUCTO = [
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

    UNIDADES_MEDIDA = [
        ("L", "Litros"),
        ("M", "Metros"),
        ("K", "Kilogramos"),
        ("U", "Unidades"),
    ]

    SUBTIPOS_POR_TIPO = {
        "COMIDA": {"CADUCABLE", "NO_CADUCABLE", "REFRIGERADO", "NO_REFRIGERADO", "BEBIDA", "LICOR"},
        "BIENES": {"REPUESTOS", "LIMPIEZA", "MEDICOS", "ACTIVOS"},
    }

    nombre = models.CharField(max_length=100, db_index=True)
    tipo = models.CharField(max_length=10, choices=TIPOS_PRODUCTO)
    subtipo = models.CharField(max_length=15, choices=SUBTIPOS_PRODUCTO, blank=True, null=True)
    seccion = models.ForeignKey('SeccionAlmacen', on_delete=models.CASCADE, related_name='productos')
    cantidad_ideal = models.PositiveIntegerField()
    medida = models.CharField(max_length=1, choices=UNIDADES_MEDIDA)
    
    @property
    def cantidad(self):
        total = self.lotes.aggregate(total=Sum('cantidad_productos'))['total'] or 0
        return total

    @property
    def estado(self):
        cantidad_actual = self.cantidad
        
        if cantidad_actual <= 0:
            return 'NO HAY STOCK'
        if cantidad_actual <= self.cantidad_ideal * 0.30:
            return 'BAJO'
        if cantidad_actual <= self.cantidad_ideal * 0.60:
            return 'MEDIO'
        return 'ALTO'

    def limpiar(self):
        if self.subtipo:
            subtipo_mayusculas = self.subtipo.upper()
            tipo_mayusculas = self.tipo.upper()
            
            if tipo_mayusculas in self.SUBTIPOS_POR_TIPO:
                if subtipo_mayusculas not in self.SUBTIPOS_POR_TIPO[tipo_mayusculas]:
                    raise ValidationError({
                        "subtipo": f"El subtipo '{self.subtipo}' no es válido para el tipo '{self.tipo}'."
                    })
            else:
                raise ValidationError({"tipo": "Tipo de producto desconocido."})

    def save(self, *args, **kwargs):
        self.limpiar()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        indexes = [
            models.Index(fields=["tipo", "subtipo"], name="indice_producto_tipo_subtipo"),
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
        if not self.numero_lote:
            maximo = Lote.objects.filter(producto=self.producto).aggregate(Max('numero_lote'))
            maximo_actual = maximo.get('numero_lote__max') or 0
            self.numero_lote = maximo_actual + 1

        super().save(*args, **kwargs)


class MovimientoAlmacen(models.Model):
    TIPOS_MOVIMIENTO = [
        ("IN", "Ingreso"),
        ("OUT", "Egreso"),
        ("NEW", "Creado"),
        ("MERMA", "Merma"),
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
        ("ALMACEN", "Almacén"),
        ("SERVICIO_MEDICO", "Servicio Médico"),
        ("ADMINISTRACION", "Administración")
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPOS_MOVIMIENTO)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="movimientos")
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name="lotes", null=True, blank=True)
    cantidad = models.PositiveIntegerField(null=True, blank=True)
    fecha = models.DateField(default=obtener_fecha_actual)
    modulo = models.CharField(max_length=20, choices=TIPO_MODULO)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = "Movimiento de Producto"
        verbose_name_plural = "Movimientos de Producto"