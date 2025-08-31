from django.db import models
from datetime import timedelta
from django.core.exceptions import ValidationError

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
        PEQUENO = "pequeno", "Pequeño"
        MEDIANO = "mediano", "Mediano"
        GRANDE = "grande", "Grande"
        
    nombre = models.CharField(max_length=100)

    tipo_crucero = models.CharField(
        max_length=30,
        choices=TipoCrucero.choices,
    default=TipoCrucero.MEDIANO,
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
    altura = models.DecimalField(max_digits=7, decimal_places=2, help_text="Altura (m)")
    numero_cubiertas = models.PositiveIntegerField(default=0, help_text="Número de cubiertas")
    
    bandera = models.CharField(max_length=50)
    puerto_base = models.CharField(max_length=100)
    estado_operativo = models.CharField(
        max_length=20, 
        choices=EstadoOperativo.choices, 
        default=EstadoOperativo.ACTIVO
    )
    descripcion = models.TextField(blank=True, default="", help_text="Descripción general del crucero")

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

    @property
    def capacidad_total(self):
        return self.capacidad_pasajeros + self.capacidad_tripulacion
    
    @property
    def se_encuentra_en_planificacion(self) -> bool:
        viaje = self.viajes.filter(estado = "planificacion").first()
        if viaje is None:
            return False
        else:
            return True
        
    @property
    def se_encuentra_en_viaje(self) -> bool:
        viaje = self.viajes.filter(estado = "activo").first()
        if viaje is None:
            return False
        else:
            return True

    @property
    def dia_actual_de_viaje(self) -> int:
        viaje = self.viajes.filter(estado="activo").first()
        if not viaje:
            raise Exception("Error: El barco no está en un viaje")
        else: 
            hoy = FechaDelSistema.objects.first().fecha_actual
            dias_transcurridos = (hoy - viaje.fecha_inicio).days + 1
            return dias_transcurridos

    class Meta:
        verbose_name = "Crucero"
        verbose_name_plural = "Cruceros"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - ({self.codigo_identificacion})"


class TipoHabitacion(models.Model):
    nombre = models.CharField(max_length=50)
    capacidad = models.PositiveIntegerField()
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to="tipos_habitacion/", blank=True, null=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Tipo de Habitación"
        verbose_name_plural = "Tipos de habitaciones"
        ordering = ['nombre']


class Habitacion(models.Model):
    crucero = models.ForeignKey(Crucero, on_delete=models.CASCADE, related_name="habitaciones")
    tipo_habitacion = models.ForeignKey(TipoHabitacion, on_delete=models.PROTECT, related_name="habitaciones")
    cubierta = models.PositiveIntegerField(help_text="Número de cubierta")
    LADO_CHOICES = [
        ("babor", "Babor"),
        ("estribor", "Estribor"),
    ]
    lado = models.CharField(max_length=10, choices=LADO_CHOICES, help_text="Lado del barco")
    codigo_ubicacion = models.CharField(
        max_length=6,
        blank=True,
        help_text="Código UUAIII: UU=cubierta (2 dígitos), A=lado (0 babor / 1 estribor), III=consecutivo (001-999) por cubierta y lado"
    )
    numero = models.CharField(max_length=20)
    ocupada = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.crucero.nombre} - {self.tipo_habitacion} - cubierta {self.cubierta} - {self.lado} - {self.numero}"

    def _generar_codigo(self):
        """Genera un código en formato UUAIII (6 dígitos numéricos):

        - UU: cubierta (00-99)
        - A : lado (0=babor, 1=estribor)
        - III: consecutivo (001-999) reiniciado por (crucero, cubierta, lado)
        """
        lado_dig = '0' if self.lado == 'babor' else '1'
        prefijo = f"{int(self.cubierta):02d}{lado_dig}"
        existentes = Habitacion.objects.filter(
            crucero=self.crucero,
            codigo_ubicacion__startswith=prefijo
        ).values_list('codigo_ubicacion', flat=True)
        ids = []
        for cod in existentes:
            if len(cod) == 6 and cod.isdigit() and cod.startswith(prefijo):
                try:
                    ids.append(int(cod[-3:]))
                except ValueError:
                    continue
        siguiente = (max(ids) + 1) if ids else 1
        if siguiente > 999:
            raise ValidationError({
                "codigo_ubicacion": "Se alcanzó el límite (999) de habitaciones para esta cubierta y lado."
            })
        return f"{prefijo}{siguiente:03d}"

    def clean(self):
        errors = {}
        if self.crucero_id and self.cubierta and self.crucero.numero_cubiertas and self.cubierta > self.crucero.numero_cubiertas:
            errors['cubierta'] = "La cubierta excede el número de cubiertas del crucero"
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.codigo_ubicacion and self.crucero_id:
            self.codigo_ubicacion = self._generar_codigo()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"

class Instalacion(models.Model):
    TIPO_CHOICES = [
        ("restaurantes", "Restaurantes"),
        ("bares_cafes", "Bares y Cafés"),
        ("almacenes", "Almacenes"),
        ("entretenimiento", "Sitios de Entretenimiento"),
        ("otro", "Otro"),
    ]
    crucero = models.ForeignKey(Crucero, on_delete=models.CASCADE, related_name="instalaciones")
    cubierta = models.PositiveIntegerField(default=1, help_text="Número de cubierta")
    codigo_ubicacion = models.CharField(
        max_length=5,
        blank=True,
        help_text="Código XXABC: XX=cubierta (2 dígitos), A=uso (2=rest.,3=bares/cafés,4=almacenes,5=entretenimiento,6=otros), BC=consecutivo (01-99)"
    )
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    capacidad = models.PositiveIntegerField()
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.crucero.nombre}"

    USO_MAP = {
        'restaurantes': '2',
        'bares_cafes': '3',
        'almacenes': '4',
        'entretenimiento': '5',
        'otro': '6',
    }

    def _generar_codigo(self):
        uso = self.USO_MAP.get(self.tipo, '6')
        existentes = Instalacion.objects.filter(
            crucero=self.crucero,
            codigo_ubicacion__regex=rf'^\d{{2}}{uso}\d{{2}}$'
        ).values_list('codigo_ubicacion', flat=True)
        ids = []
        for cod in existentes:
            if len(cod) == 5 and cod.isdigit():
                try:
                    ids.append(int(cod[-2:]))
                except ValueError:
                    continue
        siguiente = (max(ids) + 1) if ids else 1
        if siguiente > 99:
            raise ValidationError({
                "codigo_ubicacion": "Se alcanzó el límite (99) de identificadores para este uso en el crucero."
            })
        return f"{int(self.cubierta):02d}{uso}{siguiente:02d}"

    def clean(self):
        errors = {}
        if self.crucero_id and self.cubierta and self.crucero.numero_cubiertas and self.cubierta > self.crucero.numero_cubiertas:
            errors['cubierta'] = "La cubierta excede el número de cubiertas del crucero"
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.codigo_ubicacion and self.crucero_id:
            self.codigo_ubicacion = self._generar_codigo()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Instalación"
        verbose_name_plural = "Instalaciones"
        ordering = ['nombre']

class FechaDelSistema(models.Model):
    fecha_actual = models.DateField()
    
    

class Ruta(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    duracion_dias = models.IntegerField(help_text="Duración total del ciclo de la ruta")
    
    def __str__(self):
        return self.nombre

class EtapaRuta(models.Model):
    TIPO_ETAPA = (
        ('puerto', 'Puerto'),
        ('navegacion', 'Navegación'),
    )
    
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='etapas')
    nombre_lugar = models.CharField(max_length=100, help_text="Nombre del puerto o 'Navegación'")
    pais = models.CharField(max_length=100, blank=True)
    dia_llegada = models.IntegerField(help_text="Día en que se llega a esta etapa")
    tipo = models.CharField(max_length=20, choices=TIPO_ETAPA)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        ordering = ['dia_llegada']
        unique_together = ['ruta', 'dia_llegada']
    
    def __str__(self):
        return f"{self.ruta.nombre} - Día {self.dia_llegada}: {self.nombre_lugar}"

class Viaje(models.Model):
    ESTADOS = (
        ('planificacion', 'En Planificación'),
        ('activo', 'Activo'),
        ('completado', 'Completado'),
    )
    
    crucero = models.ForeignKey(Crucero, on_delete=models.CASCADE, related_name='viajes')
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='planificacion')
    
    class Meta:
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.crucero.nombre} - {self.ruta.nombre} - {self.estado}"

    def calcular_fecha_fin(self):
        if self.fecha_inicio and self.ruta and self.ruta.duracion_dias is not None:
            dias = self.ruta.duracion_dias - 1
            return self.fecha_inicio + timedelta(days=dias)
        return None

    def save(self, *args, **kwargs):
        nueva_fecha_fin = self.calcular_fecha_fin()
        if nueva_fecha_fin:
            self.fecha_fin = nueva_fecha_fin
        super().save(*args, **kwargs)

class EstadoViaje(models.Model):
    viaje = models.OneToOneField(Viaje, on_delete=models.CASCADE, related_name='estado_actual')
    dia_actual = models.IntegerField(default=1)
    etapa_actual = models.ForeignKey(EtapaRuta, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        ubicacion = self.etapa_actual.nombre_lugar if self.en_puerto else "Navegación"
        return f"{self.viaje} - Día {self.dia_actual}: {ubicacion}"