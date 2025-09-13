from django.db import models
from ..cruceros.models import Crucero
# Modelo para registrar compras por lote
class CompraLote(models.Model):
    ESTADO_CHOICES = [
        ('registrada', 'Registrada'),
        ('espera_revision', 'En espera por revisión'),
        ('exitosa', 'Exitosa'),
        ('defectuosa', 'Defectuosa'),
        ('cancelada', 'Cancelada'),
    ]
    empresa_nombre = models.CharField(max_length=100)
    empresa_contacto = models.CharField(max_length=100)
    empresa_ubicacion = models.CharField(max_length=100)
    proveedor = models.ForeignKey('Proveedores', on_delete=models.PROTECT)
    crucero = models.ForeignKey(Crucero, on_delete=models.CASCADE, related_name="compras_por_lote")
    puerto_entrega = models.CharField(max_length=100)
    notas_compra = models.TextField(blank=True)
    presupuesto_lote = models.DecimalField(max_digits=15, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='registrada')
    fecha = models.DateTimeField(auto_now_add=True)
    solicitud = models.ForeignKey('SolicitudSubtipo', null=True, blank=True, on_delete=models.SET_NULL, related_name='lotes')

# Modelo para los artículos de la compra por lote
class CompraLoteItem(models.Model):
    compra_lote = models.ForeignKey(CompraLote, related_name='items', on_delete=models.CASCADE)
    producto_id = models.IntegerField()
    nombre = models.CharField(max_length=100)
    medida = models.CharField(max_length=20)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

from django.db import models
from django.core.validators import MaxValueValidator

# Create your models here.


# Nueva estructura para solicitudes agrupadas por subtipo
class SolicitudSubtipo(models.Model):
    id = models.AutoField(primary_key=True)
    crucero = models.ForeignKey(Crucero, on_delete=models.CASCADE, related_name="solicitudes_de_compra")
    tipo = models.CharField(max_length=50)
    subtipo = models.CharField(max_length=50)
    procesada = models.BooleanField(default=False)

class SolicitudSubtipoItem(models.Model):
    id = models.AutoField(primary_key=True)
    solicitud = models.ForeignKey(SolicitudSubtipo, related_name='items', on_delete=models.CASCADE)
    producto_id = models.IntegerField()
    nombre = models.CharField(max_length=200)
    cantidad_a_comprar = models.IntegerField(validators=[MaxValueValidator(10000)])
    medida = models.CharField(max_length=20)
    tipo = models.CharField(max_length=50)
    subtipo = models.CharField(max_length=50)

class Material(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre

# Relación intermedia para asociar proveedor, material y costo
class ProveedorMaterial(models.Model):
    proveedor = models.ForeignKey('Proveedores', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    costo_unidad = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        unique_together = ('proveedor', 'material')
    def __str__(self):
        return f"{self.proveedor.name} - {self.material.nombre} (${self.costo_unidad})"

class Paises(models.Model):
    nombre = models.CharField(max_length=100)

class Proveedores(models.Model):
    # Diccionario de países, editable por el usuario
    paises= [
        
    ]
    TIPO_CHOICES = [
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
    SUBTIPO_CHOICES = [
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
    name = models.CharField(max_length=100)
    service_or_product = models.CharField(max_length=100)
    categorie = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    countries = models.ManyToManyField(Paises)
    sucursal = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    subtipo = models.CharField(max_length=20, choices=SUBTIPO_CHOICES, blank=True, null=True)
