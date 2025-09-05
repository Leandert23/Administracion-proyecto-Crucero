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
        ("ALIMENTOS_FRESCOS", "Alimentos Frescos"),
        ("ALIMENTOS_SECOS", "Alimentos Secos"),
        ("BEBIDAS", "Bebidas"),
        ("INSUMOS_COCINA", "Insumos de Cocina"),
        ("LIMPIEZA", "Limpieza"),
        ("SUMINISTROS_MEDICOS", "Suministros Médicos"),
        ("MANTENIMIENTO", "Materiales de Mantenimiento"),
        ("REPUESTOS_TECNICOS", "Repuestos Técnicos"),
        ("EQUIPOS", "Equipos"),
        ("TEXTILES", "Textiles"),
        ("OFICINA", "Oficina"),
        ("ENTRETENIMIENTO", "Entretenimiento"),
        ("SPA_GYM", "SPA / GYM"),
        ("SEGURIDAD", "Seguridad"),
        ("MERCHANDISING", "Merchandising"),
        ("TECNOLOGIA", "Tecnología"),
    ]

    # Subtipos globales (pueden reutilizarse entre tipos; se validan según SUBTIPOS_POR_TIPO)
    SUBTIPOS_PRODUCTO = [
        # Alimentos frescos
        ("FRUTA", "Fruta"), ("VERDURA", "Verdura"), ("CARNE", "Carne"), ("PESCADO", "Pescado"), ("MARISCO", "Marisco"),
        ("LACTEOS", "Lácteos"), ("PANIFICADOS", "Panificados"), ("CHARCUTERIA", "Charcutería"),
        # Alimentos secos
        ("CEREAL", "Cereal"), ("PASTA", "Pasta"), ("LEGUMINOSAS", "Leguminosas"), ("ENLATADOS", "Enlatados"),
        ("SNACKS", "Snacks"), ("CONDIMENTOS", "Condimentos"), ("AZUCAR_SAL", "Azúcar / Sal"),
        # Bebidas
        ("AGUA", "Agua"), ("REFRESCO", "Refresco"), ("JUGO", "Jugo"), ("ENERGETICA", "Energética"),
        ("CAFE_TEA", "Café / Té"), ("CERVEZA", "Cerveza"), ("VINO", "Vino"), ("DESTILADO", "Destilado"), ("COCTEL_PREMEZCLA", "Cóctel Premezclado"),
        # Insumos cocina
        ("DESCARTABLES", "Descartables"), ("ENVASES", "Envases"), ("UTENSILIOS", "Utensilios"), ("GAS_COCINA", "Gas Cocina"), ("HIELO", "Hielo"),
        # Limpieza
        ("DETERGENTES", "Detergentes"), ("DESINFECTANTES", "Desinfectantes"), ("UTENSILIOS_LIMPIEZA", "Utensilios Limpieza"), ("PAPEL_SANITARIO", "Papel Sanitario"), ("AMBIENTADORES", "Ambientadores"),
        # Médicos
        ("MEDICAMENTO", "Medicamento"), ("CURACION", "Curación"), ("EQUIPO_DIAGNOSTICO", "Equipo Diagnóstico"), ("EPP", "Equipo Protección Personal"), ("INSTRUMENTAL", "Instrumental"), ("SOLUCION_IV", "Solución IV"),
        # Mantenimiento
        ("PINTURA", "Pintura"), ("LUBRICANTE", "Lubricante"), ("SELLADOR", "Sellador"), ("ADHESIVO", "Adhesivo"), ("ABRASIVO", "Abrasivo"), ("FILTRO", "Filtro"), ("ACEITE", "Aceite"),
        # Repuestos técnicos
        ("MOTOR", "Motor"), ("ELECTRICO", "Eléctrico"), ("HVAC", "HVAC"), ("NAVEGACION", "Navegación"), ("ILUMINACION", "Iluminación"), ("BOMBAS", "Bombas"), ("VALVULAS", "Válvulas"),
        # Equipos
        ("ELECTRODOMESTICO", "Electrodoméstico"), ("AUDIO_VIDEO", "Audio / Video"), ("INFORMATICO", "Informático"), ("GIMNASIO", "Gimnasio"), ("COCINA_INDUSTRIAL", "Cocina Industrial"),
        # Textiles
        ("ROPA_CAMA", "Ropa de Cama"), ("TOALLA", "Toalla"), ("UNIFORME", "Uniforme"), ("CORTINA", "Cortina"), ("TAPICERIA", "Tapicería"),
        # Oficina
        ("PAPELERIA", "Papelería"), ("IMPRESION", "Impresión"), ("ESCRITORIO", "Escritorio"), ("CONSUMIBLE_IT", "Consumible IT"),
        # Entretenimiento
        ("JUEGO_MESA", "Juego de Mesa"), ("JUEGO_VIDEO", "Videojuego"), ("LIBRO_REVISTA", "Libro / Revista"), ("EVENTO", "Evento"), ("SONIDO_LUZ", "Sonido / Luz"),
        # SPA / GYM
        ("COSMETICO", "Cosmético"), ("ACEITE_MASAJE", "Aceite de Masaje"), ("SUPLEMENTO", "Suplemento"), ("ACC_FITNESS", "Accesorio Fitness"),
        # Seguridad
        ("CHALECO_SALVAVIDAS", "Chaleco Salvavidas"), ("EXTINTOR", "Extintor"), ("SENALIZACION", "Señalización"), ("ARNES", "Arnés"), ("BOTIQUIN", "Botiquín"), ("DETECTOR", "Detector"),
        # Merchandising
        ("RECUERDO", "Recuerdo"), ("PRENDA_LOGO", "Prenda con Logo"), ("ACCESORIO_LOGO", "Accesorio con Logo"), ("BEBIDA_PREMIUM", "Bebida Premium"), ("DULCE_GOURMET", "Dulce Gourmet"),
        # Tecnología
        ("ROUTER", "Router"), ("SWITCH", "Switch"), ("CABLEADO", "Cableado"), ("CAMARA_SEGURIDAD", "Cámara de Seguridad"), ("SENSOR", "Sensor"), ("DISPOSITIVO_PORTATIL", "Dispositivo Portátil"),
    ]

    UNIDADES_MEDIDA = [
        ("L", "Litros"),
        ("M", "Metros"),
        ("K", "Kilogramos"),
        ("U", "Unidades"),
    ]

    # Mapeo de subtipos válidos por tipo (sets para validación rápida)
    SUBTIPOS_POR_TIPO = {
        "ALIMENTOS_FRESCOS": {"FRUTA","VERDURA","CARNE","PESCADO","MARISCO","LACTEOS","PANIFICADOS","CHARCUTERIA"},
        "ALIMENTOS_SECOS": {"CEREAL","PASTA","LEGUMINOSAS","ENLATADOS","SNACKS","CONDIMENTOS","AZUCAR_SAL"},
        "BEBIDAS": {"AGUA","REFRESCO","JUGO","ENERGETICA","CAFE_TEA","CERVEZA","VINO","DESTILADO","COCTEL_PREMEZCLA"},
        "INSUMOS_COCINA": {"DESCARTABLES","ENVASES","UTENSILIOS","GAS_COCINA","HIELO"},
        "LIMPIEZA": {"DETERGENTES","DESINFECTANTES","UTENSILIOS_LIMPIEZA","PAPEL_SANITARIO","AMBIENTADORES"},
        "SUMINISTROS_MEDICOS": {"MEDICAMENTO","CURACION","EQUIPO_DIAGNOSTICO","EPP","INSTRUMENTAL","SOLUCION_IV"},
        "MANTENIMIENTO": {"PINTURA","LUBRICANTE","SELLADOR","ADHESIVO","ABRASIVO","FILTRO","ACEITE"},
        "REPUESTOS_TECNICOS": {"MOTOR","ELECTRICO","HVAC","NAVEGACION","ILUMINACION","BOMBAS","VALVULAS"},
        "EQUIPOS": {"ELECTRODOMESTICO","AUDIO_VIDEO","INFORMATICO","GIMNASIO","COCINA_INDUSTRIAL"},
        "TEXTILES": {"ROPA_CAMA","TOALLA","UNIFORME","CORTINA","TAPICERIA"},
        "OFICINA": {"PAPELERIA","IMPRESION","ESCRITORIO","CONSUMIBLE_IT"},
        "ENTRETENIMIENTO": {"JUEGO_MESA","JUEGO_VIDEO","LIBRO_REVISTA","EVENTO","SONIDO_LUZ"},
        "SPA_GYM": {"COSMETICO","ACEITE_MASAJE","SUPLEMENTO","ACC_FITNESS"},
        "SEGURIDAD": {"CHALECO_SALVAVIDAS","EXTINTOR","SENALIZACION","ARNES","BOTIQUIN","DETECTOR"},
        "MERCHANDISING": {"RECUERDO","PRENDA_LOGO","ACCESORIO_LOGO","BEBIDA_PREMIUM","DULCE_GOURMET"},
        "TECNOLOGIA": {"ROUTER","SWITCH","CABLEADO","CAMARA_SEGURIDAD","SENSOR","DISPOSITIVO_PORTATIL"},
    }

    nombre = models.CharField(max_length=100, db_index=True)
    tipo = models.CharField(max_length=25, choices=TIPOS_PRODUCTO)
    subtipo = models.CharField(max_length=25, choices=SUBTIPOS_PRODUCTO, blank=True, null=True)
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
        if cantidad_actual <= self.cantidad_ideal * 0.10:
            return 'CRITICO'
        if cantidad_actual <= self.cantidad_ideal * 0.30:
            return 'BAJO'
        if cantidad_actual <= self.cantidad_ideal * 0.70:
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
        # Validación de unicidad: nombre único (case-insensitive) dentro del mismo crucero
        if self.seccion_id:
            try:
                crucero_id = self.seccion.almacen.crucero_id
                if crucero_id:
                    existe = Producto.objects.filter(
                        seccion__almacen__crucero_id=crucero_id,
                        nombre__iexact=self.nombre
                    ).exclude(pk=self.pk).exists()
                    if existe:
                        raise ValidationError({
                            'nombre': 'Ya existe un producto con este nombre en el crucero.'
                        })
            except AttributeError:
                pass
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
        ("ADMINISTRACION", "Administración"),
        ("FUERA_BARCO", "Fuera del Barco")
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

#Ejemplo del modelo de compras. Esto se tiene que eliminar en la integración
class OrdenCompra(models.Model):
    ESTADOS_ORDEN = [
        ("PENDIENTE", "Pendiente"),
        ("APROBADA", "Aprobada"),
        ("POR_REGISTRAR", "Por registrar"),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="ordenes_compra")
    cantidad_productos = models.PositiveIntegerField()
    precio_lote = models.PositiveIntegerField(help_text="Precio total esperado del lote")
    estado = models.CharField(max_length=15, choices=ESTADOS_ORDEN, default="PENDIENTE")
    fecha_creacion = models.DateField(default=obtener_fecha_actual)

    class Meta:
        verbose_name = "Orden de Compra"
        verbose_name_plural = "Órdenes de Compra"
        ordering = ["-fecha_creacion", "-id"]

    def __str__(self):
        return f"OC#{self.id or ''} - {self.producto.nombre} x {self.cantidad_productos} ({self.get_estado_display()})"
        
    