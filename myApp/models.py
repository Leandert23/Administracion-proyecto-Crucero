from django.db import models

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Crucero(models.Model):
    class EstadoOperativo(models.TextChoices):
        ACTIVO = "activo", "Activo"
        INACTIVO = "inactivo", "Inactivo"
        MANTENIMIENTO = "mantenimiento", "En mantenimiento"
        VIAJE = "viaje", "En viaje"
    
    class TipoCombustible(models.TextChoices):
        DIESEL = "diesel", "Diésel"
        GASOLINA = "gasolina", "Gasolina"
        GNL = "gnl", "Gas Natural Licuado"
        HIBRIDO = "hibrido", "Híbrido"

    class TipoCrucero(models.TextChoices):
        CONVENCIONAL = "convencional", "Barco Crucero Convencional"
        MEGA = "mega", "Mega Barco Crucero"
        OCEANICO = "oceanico", "Barco Crucero Oceanico"
        LUJO = "lujo", "Barco Crucero de Lujo"
        PEQUENO = "pequeno", "Barco Crucero de Pequeño Tamaño"
        AVENTURA = "aventura", "Barco Crucero de Aventura"
        EXPEDICIONARIO = "expedicionario", "Barco Crucero Expedicionario"
        FLUVIAL = "fluvial", "Barco Crucero Fluvial"
        
    # DATOS BÁSICOS
    nombre = models.CharField(max_length=100)

    tipo_crucero = models.CharField(
        max_length=30,
        choices=TipoCrucero.choices,
        default=TipoCrucero.CONVENCIONAL,
        help_text="Tipo de crucero"
    )
    codigo_identificacion = models.CharField(max_length=50, unique=True)
    fecha_botadura = models.DateField()
    fecha_adquisicion = models.DateField()
    
    capacidad_pasajeros = models.PositiveIntegerField()
    capacidad_tripulacion = models.PositiveIntegerField()
    
    tonelaje = models.DecimalField(max_digits=10, decimal_places=2, help_text="Toneladas de peso muerto")
    eslora = models.DecimalField(max_digits=7, decimal_places=2, help_text="Longitud total (m)")
    manga = models.DecimalField(max_digits=7, decimal_places=2, help_text="Ancho máximo (m)")
    puntal = models.DecimalField(max_digits=7, decimal_places=2, help_text="Altura desde quilla (m)")
    
    bandera = models.CharField(max_length=50)
    puerto_base = models.CharField(max_length=100)
    estado_operativo = models.CharField(
        max_length=20, 
        choices=EstadoOperativo.choices, 
        default=EstadoOperativo.ACTIVO
    )
    descripcion = models.TextField(blank=True, default="", help_text="Descripción general del crucero")

    # DATOS TÉCNICOS
    modelo_motor = models.CharField(max_length=100, blank=True)
    velocidad_maxima = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        help_text="Velocidad máxima en nudos"
    )
    ultimo_mantenimiento = models.DateField(blank=True, null=True)
    proximo_mantenimiento = models.DateField(blank=True, null=True)
    tipo_combustible = models.CharField(
        max_length=20, 
        choices=TipoCombustible.choices, 
        default=TipoCombustible.DIESEL
    )
    consumo_combustible = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        help_text="Consumo promedio en litros/hora",
        blank=True, 
        null=True
    )

    # DOCUMENTACIÓN 
    seguro_vigente = models.BooleanField(default=False, null=True, help_text="Indica si el seguro está vigente")
    fecha_vencimiento_seguro = models.DateField(blank=True, null=True)
    certificado_sanitario = models.FileField(
        upload_to="certificados/", 
        blank=True, 
        null=True,
        help_text="Certificado sanitario vigente"
    )
    certificado_seguridad = models.FileField(
    upload_to="certificados/seguridad/", 
    blank=True, 
    null=True,
    help_text="Certificado de seguridad del crucero"
)

    # MULTIMEDIA
    foto_barco = models.ImageField(
        upload_to="fotos_barco/", 
        blank=True, 
        null=True,
        help_text="Foto principal del crucero"
    )
    plano_barco = models.ImageField(
        upload_to="planos_barco/", 
        blank=True, 
        null=True,
        help_text="Plano de distribución del crucero"
    )

    # MÉTODOS  
    def clean(self):
        errors = {}
        
        if self.fecha_botadura and self.fecha_adquisicion:
            if self.fecha_botadura > self.fecha_adquisicion:
                errors['fecha_botadura'] = 'No puede ser posterior a la fecha de adquisición'
        
        if self.ultimo_mantenimiento and self.proximo_mantenimiento:
            if self.ultimo_mantenimiento > self.proximo_mantenimiento:
                errors['ultimo_mantenimiento'] = 'No puede ser posterior al próximo mantenimiento'
        
        if errors:
            raise ValidationError(errors)

    def necesita_mantenimiento(self):
        if self.proximo_mantenimiento:
            return self.proximo_mantenimiento <= timezone.now().date() + timezone.timedelta(days=30)
        return False

    def capacidad_total(self):
        return self.capacidad_pasajeros + self.capacidad_tripulacion

    # --- METADATOS ---
    class Meta:
        verbose_name = "Crucero"
        verbose_name_plural = "Cruceros"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.codigo_identificacion})"


class TipoHabitacion(models.Model):
    
	nombre = models.CharField(max_length=50)
	capacidad = models.PositiveIntegerField()
	precio_base = models.DecimalField(max_digits=10, decimal_places=2)
	descripcion = models.TextField(blank=True, null=True)
	imagen = models.ImageField(upload_to="tipos_habitacion/", blank=True, null=True)

	def __str__(self):
		return self.nombre


class Habitacion(models.Model):
    
	crucero = models.ForeignKey(Crucero, on_delete=models.CASCADE, related_name="habitaciones")
	tipo_habitacion = models.ForeignKey(TipoHabitacion, on_delete=models.PROTECT, related_name="habitaciones")
	cubierta = models.CharField(max_length=20)
	numero = models.CharField(max_length=20)
	ocupada = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.numero} - {self.crucero.nombre}"


class Instalacion(models.Model):
    
	TIPO_CHOICES = [
		("restaurante", "Restaurante"),
		("bar", "Bar"),
		("piscina", "Piscina"),
		("entretenimiento", "Zona de entretenimiento"),
		("gimnasio", "Gimnasio"),
		("enfermeria", "Enfermería"),
		("otro", "Otro"),
	]
	crucero = models.ForeignKey(Crucero, on_delete=models.CASCADE, related_name="instalaciones")
	nombre = models.CharField(max_length=100)
	tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
	capacidad = models.PositiveIntegerField()
	ubicacion = models.CharField(max_length=100)
	descripcion = models.TextField(blank=True, null=True)

	def __str__(self):
		return f"{self.nombre} - {self.crucero.nombre}"
