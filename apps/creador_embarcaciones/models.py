from django.db import models
from datetime import timedelta

class Ruta(models.Model):
    """
    Modelo para representar rutas de navegación de las embarcaciones
    """
    numero_dias = models.IntegerField(verbose_name="Número de días")
    titulo = models.CharField(max_length=200, verbose_name="Título de la ruta")
    descripcion = models.TextField(blank=True, verbose_name="Descripción de la ruta")
    fecha_inicio = models.DateField(verbose_name="Fecha de inicio de la ruta", null=True, blank=True)
    fecha_fin = models.DateField(verbose_name="Fecha de fin de la ruta", null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Ruta"
        verbose_name_plural = "Rutas"
        ordering = ['titulo']

    def __str__(self):
        if self.fecha_inicio and self.fecha_fin:
            return f"{self.titulo} ({self.numero_dias} días) - {self.fecha_inicio.strftime('%d/%m/%Y')} al {self.fecha_fin.strftime('%d/%m/%Y')}"
        return f"{self.titulo} ({self.numero_dias} días)"

    @property
    def progreso_configuracion(self):
        """
        Propiedad que devuelve el porcentaje de configuración completada de todos los días
        """
        if self.numero_dias == 0:
            return 100

        dias_configurados = sum(1 for dia in self.dias.all() if dia.esta_configurado)
        return int((dias_configurados / self.numero_dias) * 100)

    @property
    def dias_configurados(self):
        """
        Propiedad que devuelve la cantidad de días configurados
        """
        return sum(1 for dia in self.dias.all() if dia.esta_configurado)

    @property
    def esta_completamente_configurada(self):
        """
        Propiedad que indica si toda la ruta está completamente configurada
        """
        return self.progreso_configuracion == 100

    def save(self, *args, **kwargs):
        """
        Sobreescribir save para calcular fecha_fin y crear automáticamente los días de la ruta
        """
        # Calcular fecha_fin automáticamente si se proporciona fecha_inicio
        if self.fecha_inicio and self.numero_dias:
            self.fecha_fin = self.fecha_inicio + timedelta(days=self.numero_dias - 1)
        
        is_new = self.pk is None  # Verificar si es una nueva instancia
        super().save(*args, **kwargs)

        # Solo crear días si es una nueva ruta
        if is_new and self.numero_dias > 0:
            # Eliminar días existentes si los hay (por si acaso)
            Dia.objects.filter(ruta=self).delete()

            # Crear un día por cada día especificado en numero_dias
            dias_creados = []
            for numero_dia in range(1, self.numero_dias + 1):
                dia = Dia.objects.create(
                    ruta=self,
                    numero_dia=numero_dia,
                    ubicacion=f"Día {numero_dia} - Ubicación pendiente",  # Ubicación por defecto editable
                    titulo_dia="Día pendiente de configuración",  # Título por defecto editable
                    hora_llegada="08:00:00",  # Hora fija de llegada
                    hora_salida="17:00:00"    # Hora fija de salida
                )
                dias_creados.append(dia)

            print(f"Se crearon {len(dias_creados)} días para la ruta '{self.titulo}' - Listos para ser configurados")


class TipoEmbarcacion(models.Model):
    """
    Modelo para representar los tipos de embarcación disponibles
    """
    nombre = models.CharField(max_length=50, unique=True, verbose_name="Nombre del tipo")
    descripcion = models.TextField(blank=True, verbose_name="Descripción del tipo")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Tipo de Embarcación"
        verbose_name_plural = "Tipos de Embarcación"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Dia(models.Model):
    """
    Modelo para representar cada día de una ruta - Permite construir itinerarios detallados
    """
    ruta = models.ForeignKey(
        Ruta,
        on_delete=models.CASCADE,
        verbose_name="Ruta",
        related_name="dias"
    )
    numero_dia = models.IntegerField(verbose_name="Número del día")

    # Información básica del día
    ubicacion = models.CharField(
        max_length=200,
        verbose_name="Ubicación",
        help_text="Lugar donde estará la embarcación este día",
        default="Ubicación pendiente"
    )
    titulo_dia = models.CharField(
        max_length=100,
        verbose_name="Título del día",
        help_text="Título descriptivo para este día",
        default="Día pendiente de configuración"
    )

    # Detalles del itinerario
    descripcion = models.TextField(
        verbose_name="Descripción del día",
        help_text="Actividades, atracciones y detalles del día",
        blank=True
    )

    # Información logística (horas fijas)
    hora_llegada = models.TimeField(
        verbose_name="Hora de llegada",
        default="08:00:00",
        help_text="Hora estimada de llegada al destino"
    )
    hora_salida = models.TimeField(
        verbose_name="Hora de salida",
        default="17:00:00",
        help_text="Hora estimada de salida del destino"
    )

    # Información adicional
    notas_especiales = models.TextField(
        verbose_name="Notas especiales",
        help_text="Información adicional importante para este día",
        blank=True
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Día"
        verbose_name_plural = "Días"
        ordering = ['ruta', 'numero_dia']
        unique_together = ['ruta', 'numero_dia']  # Evitar días duplicados para la misma ruta

    def __str__(self):
        if self.titulo_dia and self.titulo_dia != "Día pendiente de configuración":
            return f"Día {self.numero_dia}: {self.titulo_dia}"
        else:
            return f"Día {self.numero_dia} - {self.ubicacion}"

    @property
    def esta_configurado(self):
        """
        Propiedad que indica si el día está configurado
        """
        return (self.ubicacion != "Ubicación pendiente" and
                self.titulo_dia != "Día pendiente de configuración")

    @property
    def progreso_configuracion(self):
        """
        Propiedad que devuelve el porcentaje de configuración completada
        """
        campos_totales = 2  # ubicacion, titulo_dia (descripcion no es obligatoria)
        campos_completos = 0

        if self.ubicacion and self.ubicacion != "Ubicación pendiente":
            campos_completos += 1
        if self.titulo_dia and self.titulo_dia != "Día pendiente de configuración":
            campos_completos += 1
        # La descripción ya no es obligatoria para completar la configuración

        return int((campos_completos / campos_totales) * 100)

    def save(self, *args, **kwargs):
        """
        Validaciones adicionales al guardar un día
        """
        # Validar que el numero_dia no exceda el numero_dias de la ruta
        if self.numero_dia > self.ruta.numero_dias:
            raise ValueError(f"El número de día ({self.numero_dia}) no puede ser mayor que los días de la ruta ({self.ruta.numero_dias})")

        # Validar que el numero_dia sea positivo
        if self.numero_dia <= 0:
            raise ValueError("El número de día debe ser mayor que cero")

        # Establecer horas por defecto si no están definidas
        if not self.hora_llegada:
            self.hora_llegada = "08:00:00"
        if not self.hora_salida:
            self.hora_salida = "17:00:00"

        super().save(*args, **kwargs)


class Embarcacion(models.Model):
    """
    Modelo para representar embarcaciones del sistema
    """
    # Información básica
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la embarcación")
    tipo = models.ForeignKey(
        TipoEmbarcacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de embarcación"
    )
    identificador = models.CharField(max_length=20, unique=True, blank=True, verbose_name="Identificador único")

    # Fechas importantes
    fecha_botadura = models.DateField(verbose_name="Fecha de botadura")
    fecha_adquisicion = models.DateField(verbose_name="Fecha de adquisición")

    # Capacidades
    capacidad_pasajeros = models.IntegerField(verbose_name="Capacidad de pasajeros")
    capacidad_tripulacion = models.IntegerField(verbose_name="Capacidad de tripulación")

    # Dimensiones físicas
    tonelaje = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Tonelaje (toneladas)")
    eslora = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Eslora (metros)")
    manga = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Manga (metros)")
    altura = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Altura (metros)")
    numero_cubiertas = models.IntegerField(verbose_name="Número de cubiertas")

    # Campo calculado automáticamente
    area_utilizable = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Área utilizable (m²)",
        blank=True,
        null=True
    )

    # Alojamiento
    maximo_habitacion_pasajeros = models.IntegerField(verbose_name="Máximo habitaciones para pasajeros")
    maximo_habitacion_tripulantes = models.IntegerField(verbose_name="Máximo habitaciones para tripulantes")

    # Información de registro
    bandera = models.CharField(max_length=50, verbose_name="Bandera")
    puerto_base = models.CharField(max_length=100, verbose_name="Puerto base")

    # Estado y descripción
    ESTADO_CHOICES = [
        ('en_espera', 'En espera'),
        ('operativo', 'Operativo'),
        ('mantenimiento', 'En mantenimiento'),
        ('reparacion', 'En reparación'),
        ('inactivo', 'Inactivo'),
    ]
    estado_operativo = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='en_espera',
        verbose_name="Estado operativo"
    )

    descripcion = models.TextField(blank=True, verbose_name="Descripción")

    # Información técnica del motor
    modelo_motor = models.CharField(max_length=100, verbose_name="Modelo del motor")
    velocidad_maxima = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Velocidad máxima (nudos)")

    # Mantenimiento
    ultimo_mantenimiento = models.DateField(verbose_name="Último mantenimiento")
    proximo_mantenimiento = models.DateField(verbose_name="Próximo mantenimiento")

    # Información de combustible
    TIPO_COMBUSTIBLE_CHOICES = [
        ('diesel', 'Diésel'),
        ('gasolina', 'Gasolina'),
        ('gas_natural', 'Gas Natural'),
        ('electrico', 'Eléctrico'),
        ('hibrido', 'Híbrido'),
    ]
    tipo_combustible = models.CharField(
        max_length=20,
        choices=TIPO_COMBUSTIBLE_CHOICES,
        verbose_name="Tipo de combustible"
    )

    consumo_combustible = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Consumo de combustible (L/hora)"
    )
    capacidad_combustible = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Capacidad de combustible (litros)"
    )

    # Relaciones
    ruta = models.ForeignKey(
        Ruta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Ruta asignada"
    )

    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Embarcación"
        verbose_name_plural = "Embarcaciones"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.identificador} - {self.nombre}"

    @staticmethod
    def generar_identificador(tipo_embarcacion):
        """
        Genera un identificador único basado en el tipo de embarcación
        """
        # Mapa de tipos predefinidos
        tipos_predefinidos = {
            'Crucero': 'C',
            'Ferry': 'F',
            'Pesquero': 'P',
            'Remolcador': 'R',
            'Yate': 'Y'
        }

        # Determinar el prefijo
        if tipo_embarcacion.nombre in tipos_predefinidos:
            prefijo = tipos_predefinidos[tipo_embarcacion.nombre]
        else:
            # Tipo creado por usuario
            prefijo = 'US'

        # Generar número secuencial único
        contador = 1
        while True:
            identificador = f"{prefijo}{contador:04d}"
            if not Embarcacion.objects.filter(identificador=identificador).exists():
                return identificador
            contador += 1

    def save(self, *args, **kwargs):
        """
        Sobreescribir save para calcular automáticamente el área utilizable, generar identificador y crear cubiertas
        """
        is_new = self.pk is None  # Verificar si es una nueva instancia

        # Generar identificador si no existe
        if not self.identificador and self.tipo:
            self.identificador = self.generar_identificador(self.tipo)

        # Calcular área utilizable
        if self.eslora and self.manga and self.numero_cubiertas:
            from decimal import Decimal
            self.area_utilizable = self.eslora * self.manga * self.numero_cubiertas * Decimal('0.7')

        super().save(*args, **kwargs)

        # Solo crear cubiertas si es una nueva embarcación
        if is_new and self.numero_cubiertas and self.numero_cubiertas > 0:
            # Eliminar cubiertas existentes si las hay (por si acaso)
            Cubierta.objects.filter(embarcacion=self).delete()

            # Calcular área por cubierta
            area_por_cubierta = Decimal('0')
            if self.area_utilizable and self.numero_cubiertas > 0:
                area_por_cubierta = self.area_utilizable / self.numero_cubiertas

            # Crear una cubierta por cada cubierta especificada
            cubiertas_creadas = []
            for numero_cubierta in range(1, self.numero_cubiertas + 1):
                cubierta = Cubierta.objects.create(
                    embarcacion=self,
                    nombre=f"Cubierta {numero_cubierta}",
                    numero=numero_cubierta,
                    area_disponible=area_por_cubierta
                )
                cubiertas_creadas.append(cubierta)

            print(f"Se crearon {len(cubiertas_creadas)} cubiertas para la embarcación '{self.nombre}'")

    def autonomia(self):
        """
        Calcular la autonomía de la embarcación en horas
        """
        if self.consumo_combustible and self.consumo_combustible > 0:
            return self.capacidad_combustible / self.consumo_combustible
        return 0

    def autonomia_nautica(self):
        """
        Calcular la autonomía en millas náuticas
        """
        autonomia_horas = self.autonomia()
        return autonomia_horas * self.velocidad_maxima

    @property
    def capacidad_total_personas(self):
        """
        Propiedad que calcula la capacidad total de personas
        """
        return self.capacidad_pasajeros + self.capacidad_tripulacion


class Cubierta(models.Model):
    """
    Modelo para representar las cubiertas de una embarcación
    """
    embarcacion = models.ForeignKey(
        Embarcacion,
        on_delete=models.CASCADE,
        verbose_name="Embarcación",
        related_name="cubiertas"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la cubierta")
    numero = models.IntegerField(verbose_name="Número de cubierta")
    area_disponible = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Área disponible (m²)"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Cubierta"
        verbose_name_plural = "Cubiertas"
        ordering = ['embarcacion', 'numero']
        unique_together = ['embarcacion', 'numero']  # Una embarcación no puede tener dos cubiertas con el mismo número

    def __str__(self):
        return f"{self.embarcacion.nombre} - Cubierta {self.numero}: {self.nombre}"


class Locales(models.Model):
    """
    Modelo para representar locales comerciales en las embarcaciones
    """
    # Tipos de locales disponibles
    TIPO_CHOICES = [
        ('restaurante', 'Restaurante'),
        ('bar', 'Bar'),
        ('piscina', 'Piscina'),
        ('entretenimientos', 'Entretenimientos'),
        ('oficinas', 'Oficinas'),
        ('almacen', 'Almacén'),
        ('servicio_medico', 'Servicio Médico'),
        ('lobby', 'Lobby'),
    ]

    # Estados disponibles
    ESTADO_CHOICES = [
        ('operativo', 'Operativo'),
        ('mantenimiento', 'En mantenimiento'),
        ('cerrado', 'Cerrado'),
        ('construccion', 'En construcción'),
    ]

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de local"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre del local")
    ID_local = models.CharField(max_length=20, unique=True, verbose_name="ID único del local")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='operativo',
        verbose_name="Estado"
    )
    area_metros_cuadrados = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Área (m²)"
    )
    cubierta = models.ForeignKey(
        Cubierta,
        on_delete=models.CASCADE,
        verbose_name="Cubierta",
        related_name="locales"
    )
    n_cubierta = models.IntegerField(verbose_name="Número de cubierta")
    ultimo_mantenimiento = models.DateField(verbose_name="Último mantenimiento")
    proximo_mantenimiento = models.DateField(verbose_name="Próximo mantenimiento")
    ubicacion = models.CharField(max_length=50, unique=True, verbose_name="Ubicación única")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Local"
        verbose_name_plural = "Locales"
        ordering = ['cubierta', 'tipo', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.ID_local}) - {self.get_tipo_display()}"

    def save(self, *args, **kwargs):
        """
        Sobreescribir save para generar ubicación única si no existe
        """
        if not self.ubicacion:
            self.ubicacion = self.generar_ubicacion()
        super().save(*args, **kwargs)

    def generar_ubicacion(self):
        """
        Genera una ubicación única basada en cubierta, tipo e ID con formato XCIII
        X = número de cubierta
        C = código del tipo de local
        III = ID del local proporcionado por el usuario
        """
        # Mapa de códigos para tipos de locales
        codigos_tipo = {
            'restaurante': '2',
            'bar': '3',
            'piscina': 'P',
            'entretenimientos': '4',
            'oficinas': '5',
            'almacen': '6',
            'servicio_medico': '7',
            'lobby': 'L',
        }

        # Obtener código del tipo
        codigo_tipo = codigos_tipo.get(self.tipo, 'X')

        # Generar ubicación con formato XCIII
        ubicacion_base = f"{self.n_cubierta}{codigo_tipo}{self.ID_local}"

        # Verificar unicidad y añadir sufijo si es necesario
        contador = 1
        ubicacion = ubicacion_base
        while Locales.objects.filter(ubicacion=ubicacion).exclude(pk=self.pk).exists() or \
              Habitaciones.objects.filter(ubicacion=ubicacion).exists():
            ubicacion = f"{ubicacion_base}-{contador}"
            contador += 1

        return ubicacion


class Habitaciones(models.Model):
    """
    Modelo para representar habitaciones de las embarcaciones
    """
    # Posición de la habitación
    POSICION_CHOICES = [
        ('babor', 'Babor'),
        ('estribor', 'Estribor'),
    ]

    # Estados disponibles
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('mantenimiento', 'En mantenimiento'),
        ('cerrada', 'Cerrada'),
        ('construccion', 'En construcción'),
    ]

    # Tipo de habitación estándar (referencia)
    tipo_habitacion_estandar = models.ForeignKey(
        'TipoHabitacion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de habitación estándar",
        related_name="habitaciones"
    )

    numero = models.IntegerField(verbose_name="Número de habitación")
    ID_local = models.CharField(max_length=20, unique=True, verbose_name="ID único de la habitación")
    posicion = models.CharField(
        max_length=20,
        choices=POSICION_CHOICES,
        default='babor',
        verbose_name="Posición"
    )
    area_metros_cuadrados = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Área (m²)"
    )
    cubierta = models.ForeignKey(
        Cubierta,
        on_delete=models.CASCADE,
        verbose_name="Cubierta",
        related_name="habitaciones"
    )
    n_cubierta = models.IntegerField(verbose_name="Número de cubierta")
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='disponible',
        verbose_name="Estado"
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio por noche (€)"
    )
    id_persona = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="ID de persona asignada"
    )
    ultimo_mantenimiento = models.DateField(verbose_name="Último mantenimiento")
    proximo_mantenimiento = models.DateField(verbose_name="Próximo mantenimiento")
    ubicacion = models.CharField(max_length=50, unique=True, verbose_name="Ubicación única")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"
        ordering = ['cubierta', 'numero']

    def __str__(self):
        return f"Habitación {self.numero} ({self.ID_local}) - {self.get_posicion_display()}"

    def save(self, *args, **kwargs):
        """
        Sobreescribir save para generar ID_local y ubicación única si no existen
        """
        if not self.ID_local:
            self.ID_local = self.generar_id_local()
        if not self.ubicacion:
            self.ubicacion = self.generar_ubicacion()
        super().save(*args, **kwargs)

    def generar_id_local(self):
        """
        Genera ID único con formato XACCC
        X = número de cubierta
        A = 0 (babor) o 1 (estribor)
        CCC = número de habitación (3 dígitos)
        """
        # Código de posición
        codigo_posicion = '0' if self.posicion == 'babor' else '1'

        # Número de habitación con 3 dígitos
        numero_formateado = str(self.numero).zfill(3)

        # Generar ID
        id_local = f"{self.n_cubierta}{codigo_posicion}{numero_formateado}"

        # Verificar unicidad
        contador = 1
        id_base = id_local
        while Habitaciones.objects.filter(ID_local=id_local).exclude(pk=self.pk).exists():
            id_local = f"{id_base}-{contador}"
            contador += 1

        return id_local

    def generar_ubicacion(self):
        """
        Genera una ubicación única basada en cubierta, posición e ID
        """
        # Generar ubicación tentativa
        ubicacion_base = f"C{self.n_cubierta}-{self.posicion}-{self.ID_local}"

        # Verificar unicidad y añadir sufijo si es necesario
        contador = 1
        ubicacion = ubicacion_base
        while Habitaciones.objects.filter(ubicacion=ubicacion).exclude(pk=self.pk).exists() or \
              Locales.objects.filter(ubicacion=ubicacion).exists():
            ubicacion = f"{ubicacion_base}-{contador}"
            contador += 1

        return ubicacion


# ========== MODELOS PARA ESTÁNDARES/CREADORES ==========

class TipoHabitacion(models.Model):
    """
    Modelo para definir tipos/estándares de habitaciones que pueden ser reutilizados
    """
    # Posición de la habitación (duplicado para evitar referencia circular)
    POSICION_CHOICES = [
        ('babor', 'Babor'),
        ('estribor', 'Estribor'),
    ]

    # Estados disponibles (duplicado para evitar referencia circular)
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('ocupada', 'Ocupada'),
        ('mantenimiento', 'En mantenimiento'),
        ('cerrada', 'Cerrada'),
        ('construccion', 'En construcción'),
    ]

    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del tipo")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    tipo = models.CharField(max_length=20, choices=POSICION_CHOICES, verbose_name="Tipo de habitación")
    area_metros_cuadrados = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Área estándar (m²)")
    precio_base = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, verbose_name="Precio base (€)")
    estado_default = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible', verbose_name="Estado por defecto")

    # Información de mantenimiento
    ultimo_mantenimiento_dias = models.IntegerField(default=30, verbose_name="Días para último mantenimiento")
    proximo_mantenimiento_dias = models.IntegerField(default=180, verbose_name="Días para próximo mantenimiento")

    # Especificaciones adicionales
    capacidad_personas = models.IntegerField(default=2, verbose_name="Capacidad de personas")
    numero_camas = models.IntegerField(default=1, verbose_name="Número de camas")
    tiene_bano_privado = models.BooleanField(default=True, verbose_name="Tiene baño privado")
    tiene_balcon = models.BooleanField(default=False, verbose_name="Tiene balcón")
    tiene_vista_mar = models.BooleanField(default=False, verbose_name="Tiene vista al mar")

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Tipo de Habitación"
        verbose_name_plural = "Tipos de Habitación"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_display()} ({self.area_metros_cuadrados} m²)"


class TipoLocal(models.Model):
    """
    Modelo para definir tipos/estándares de locales que pueden ser reutilizados
    """
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del tipo")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    tipo = models.CharField(max_length=20, choices=Locales.TIPO_CHOICES, verbose_name="Tipo de local")
    area_metros_cuadrados = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Área estándar (m²)")
    estado_default = models.CharField(max_length=20, choices=Locales.ESTADO_CHOICES, default='operativo', verbose_name="Estado por defecto")

    # Información de mantenimiento
    ultimo_mantenimiento_dias = models.IntegerField(default=30, verbose_name="Días para último mantenimiento")
    proximo_mantenimiento_dias = models.IntegerField(default=90, verbose_name="Días para próximo mantenimiento")

    # Especificaciones adicionales
    capacidad_personas = models.IntegerField(default=50, verbose_name="Capacidad de personas")
    tiene_ventilacion = models.BooleanField(default=True, verbose_name="Tiene ventilación")
    tiene_iluminacion_especial = models.BooleanField(default=False, verbose_name="Tiene iluminación especial")

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Tipo de Local"
        verbose_name_plural = "Tipos de Local"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_display()} ({self.area_metros_cuadrados} m²)"
