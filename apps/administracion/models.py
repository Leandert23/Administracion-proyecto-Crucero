from django.db import models
from apps.cruceros.models import Crucero
from apps.compras.models import ProveedorMaterial, CompraLote
from apps.ventas.models import Venta
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal

class Administracion(models.Model):
    crucero = models.ForeignKey(Crucero, on_delete=models.CASCADE, related_name='finanzas')
    costos_totales = models.DecimalField(max_digits=12, 
                                         decimal_places=2, 
                                         validators=[MinValueValidator(Decimal('0'))])
    ganancias_totales = models.DecimalField(max_digits=12, decimal_places=2)
    presupuesto_estimado = models.DecimalField(max_digits=12, 
                                               decimal_places=2, 
                                               validators=[MinValueValidator(Decimal('0'))]) 
    precio_combustible = models.DecimalField(max_digits=10, 
                                             decimal_places=2, 
                                             validators=[MinValueValidator(Decimal('0'))])
    num_pasajeros_actual = models.PositiveIntegerField() #???
    num_empleados_actual = models.PositiveIntegerField() #Recursos humanos
    
    '''''''''
    # Agregar método para calcular presupuesto
    @property
    def presupuesto_estimado(self, pasajeros=None, empleados=None, dias=None, distancia=None):
        # Ecuación: [(Precio de los boletos + Estimado de los no incluidos) - Total*10%] * Capacidad del barco al 60%
        if not all([pasajeros, empleados, dias, distancia]):
            pasajeros = self.num_pasajeros_actual
            empleados = self.num_empleados_actual
            dias = 7  # valor por defecto
            distancia = 1000  # valor por defecto
        
        costo_combustible = distancia * 2.5
        costo_comida = (pasajeros + empleados) * dias * 45
        costo_mantenimiento = dias * 1200
        costo_operacional = empleados * dias * 80
        
        return costo_combustible + costo_comida + costo_mantenimiento + costo_operacional
    '''''''''

    @property
    def costos_totales(self):
        # Suma: para cada lote del crucero, suma cantidad * costo_unidad del material según el proveedor del lote
        total = Decimal('0.00')
        lotes = (
            CompraLote.objects
            .filter(crucero=self.crucero, estado='exitosa')
            .select_related('proveedor')
            .prefetch_related('items')
        )
        # Cache de costos por proveedor -> material_id -> costo
        for lote in lotes:
            costos_qs = ProveedorMaterial.objects.filter(proveedor=lote.proveedor).values_list('material_id', 'costo_unidad')
            costo_por_material = {material_id: costo for material_id, costo in costos_qs}
            for item in lote.items.all():
                costo_unitario = costo_por_material.get(item.producto_id)
                if costo_unitario is not None and item.cantidad is not None:
                    total += costo_unitario * item.cantidad
        return total
    
    @property
    def ganancias_totales(self):
        # Suma el monto_total de todas las ventas completadas del crucero
        total = Venta.objects.filter(
            crucero=self.crucero,
            estado='completada'
        ).aggregate(
            total=models.Sum('monto_total')
        )['total']
        return total if total is not None else Decimal('0.00')
    
    #Agregar para decidir el precio del combustible

    def clean(self):
        if self.costos_totales and self.costos_totales < 0:
            raise ValidationError("Los costos no pueden ser negativos.")
        if self.presupuesto_estimado and self.presupuesto_estimado < 0:
            raise ValidationError("El presupuesto no puede ser negativo.")
        if self.precio_combustible and self.precio_combustible < 0:
            raise ValidationError("El precio del combustible no puede ser negativo.")
        return super().clean() 

    class Meta:
        verbose_name = "Finanzas"
        verbose_name_plural = "Finanzas"

    def __str__(self):
        return f"{self.crucero.nombre} - Costos {self.costos_totales} - Ganancias {self.ganancias_totales}"

class Alerta(models.Model):
    crucero = models.ForeignKey(Administracion, on_delete=models.CASCADE, related_name='alertas')
    mensaje = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.crucero.nombre} - {self.mensaje} - {self.fecha}"

class Cubierta(models.Model):
    crucero = models.ForeignKey(Crucero, on_delete=models.CASCADE, related_name='cubierta')
    nombre = models.CharField(max_length=25)
    numero = models.PositiveIntegerField()
    area_disponible = models.DecimalField(max_digits=5, 
                                          decimal_places=2, 
                                          validators=[MinValueValidator(Decimal('0'))])
    area_restante = models.DecimalField(max_digits=5, 
                                        decimal_places=2, 
                                        validators=[MinValueValidator(Decimal('0'))])

    def _validar_area_cubierta(self):
        """Valida que el total de áreas de la cubierta no exceda el área del crucero."""
        if self.crucero and self.area_disponible and self.area_restante:
            # Calcular área aproximada del crucero usando eslora y manga 
            area_crucero = self.crucero.eslora * self.crucero.manga
            total_area_cubierta = self.area_disponible + self.area_restante
            
            if total_area_cubierta > area_crucero:
                raise ValidationError(
                    f"El total del área disponible ({self.area_disponible}) y área restante "
                    f"({self.area_restante}) = {total_area_cubierta} m² no puede ser mayor "
                    f"al área del crucero ({area_crucero} m²)."
                )

    def _validar_uso_area_cubierta(self):
        """Valida que el total de áreas usadas por instalaciones y habitaciones no exceda el área disponible."""
        if self.area_disponible:
            # Calcular área total usada por instalaciones
            total_instalaciones = Instalaciones.objects.filter(cubierta=self).aggregate(
                total=models.Sum('espacio_area')
            )['total']
            # Calcular área total usada por habitaciones
            total_habitaciones = Habitaciones.objects.filter(cubierta=self).aggregate(
                total=models.Sum('espacio_area')
            )['total']
            
            # Total de área usada
            total_area_usada = total_instalaciones + total_habitaciones
            
            if total_area_usada > self.area_disponible:
                raise ValidationError(
                    f"El área total usada por instalaciones ({total_instalaciones} m²) y habitaciones "
                    f"({total_habitaciones} m²) = {total_area_usada} m² excede el área disponible "
                    f"de la cubierta ({self.area_disponible} m²)."
                )

    def clean(self):
        # Validación: el total de área_disponible y area_restante debe ser menor o igual al área del crucero
        self._validar_area_cubierta()
        # Validación: el total de áreas usadas no debe exceder el área disponible
        self._validar_uso_area_cubierta()

        return super().clean()

    def save(self, *args, **kwargs):
        """Sobrescribe save para asegurar validación en cada guardado."""
        # Validar antes de guardar
        self._validar_area_cubierta()
        self._validar_uso_area_cubierta()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Cubierta"
        verbose_name_plural = "Cubiertas"

    def __str__(self):
        return f"Cubierta {self.nombre} - Numero {self.numero}"

class Instalaciones(models.Model):
    ESTADOS = [
        ('active', 'Activa'),
        ('reserved', 'Reservada'),
        ('occupied', 'Ocupada'),
        ('maintenance', 'En mantenimiento')
    ]
    TIPOS = [
        ('restaurant', 'Restaurante'),
        ('bar', 'Bar'),
        ('pool', 'Piscina'),
        ('theater', 'Teatro'),
        ('lobby', 'Recepción'),
        ('warehouse', 'Almacén'),
        ('nursery', 'Enfermería'),
        ('employee_restroom', 'Área de empleados'),
        ('event_room', 'Espacio de eventos'),
        ('navigation_bridge', 'Puente de navegación'),
    ]

    cubierta = models.ForeignKey(Cubierta, on_delete=models.PROTECT, related_name='instalaciones')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    capacidad = models.PositiveIntegerField()
    espacio_area = models.DecimalField(max_digits=5, 
                                       decimal_places=2, 
                                       validators=[MinValueValidator(Decimal('0'))])
    id_instalacion = models.PositiveIntegerField() 
    ubicacion = models.CharField(max_length=25)
    estado = models.CharField(max_length=20, 
                              default='active', 
                              choices=ESTADOS)
    ultimo_mantenimiento = models.DateField()
    proximo_mantenimiento = models.DateField()

    def clean(self):
        if self.cubierta:
            self.cubierta._validar_uso_area_cubierta()

        return super().clean()

    def save(self, *args, **kwargs):
        """Sobrescribe save para asegurar validación en cada guardado."""
        # Validar antes de guardar
        if self.cubierta:
            self.cubierta._validar_uso_area_cubierta()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Instalación"
        verbose_name_plural = "Instalaciones"

    def __str__(self):
        return f"Instalación {self.tipo} - Ubicación {self.ubicacion} - {self.estado}"

class Habitaciones(models.Model):
    ESTADOS = [
        ('free', 'Libre'),
        ('reserved', 'Reservada'),
        ('occupied', 'Ocupada'),
        ('maintenance', 'Mantenimiento')
    ]
    TIPOS = [
        ('indivual', 'Individual'),
        ('double', 'Doble'),
        ('triple', 'Triple'),
        ('quadruple', 'Cuadruple'),
        ('penthouse', 'Penthouse'),
        ('suite', 'Suite'),
        ('ship_crew', 'De tripulación'),
    ]
    cubierta = models.ForeignKey(Cubierta, on_delete=models.PROTECT, related_name='habitaciones')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    id_room = models.PositiveIntegerField() 
    precio_base = models.DecimalField(max_digits=20, 
                                      decimal_places=2, 
                                      validators=[MinValueValidator(Decimal('0'))])
    ubicacion = models.CharField(max_length=25)
    aumento_ubicacion = models.DecimalField(max_digits=20, 
                                      decimal_places=2,
                                      default=0)
    estado = models.CharField(max_length=20, default='free', choices=ESTADOS)
    espacio_area = models.DecimalField(max_digits=5, 
                                       decimal_places=2, 
                                       validators=[MinValueValidator(Decimal('0'))]) #En m^2
    nombre_usuario = models.CharField(max_length=25,  
                                      default='free') 
    capacidad = models.PositiveIntegerField() #El límite es de 1 persona por cada 0.4645 m^2
    vista_mar = models.BooleanField(default=False)
    aumento_vista_mar = models.DecimalField(max_digits=20, 
                                      decimal_places=2,
                                      default=0)
    costo_extra = models.DecimalField(max_digits=20, 
                                      decimal_places=2,
                                      default=0)
    ultimo_mantenimiento = models.DateField()
    proximo_mantenimiento = models.DateField()
    costo_final = models.DecimalField(max_digits=10, 
                                      decimal_places=2, 
                                      validators=[MinValueValidator(Decimal('0'))])

    def calcular_costo_final(self):
        """Calcula el costo final basado en precio_base, aumento_ubicacion, capacidad y opcionalmente aumento_vista_mar."""
        if not self.precio_base or not self.capacidad:
            return Decimal('0.00')
        
        # Calcular el costo base con el aumento de ubicación
        costo_final = self.precio_base + (self.precio_base * self.aumento_ubicacion)
        
        # Aplicar el aumento por vista al mar si está habilitado
        if self.vista_mar and self.aumento_vista_mar:
            costo_final = costo_final + (costo_final * self.aumento_vista_mar)

        return costo_final

    def clean(self):
        if self.cubierta:
            self.cubierta._validar_uso_area_cubierta()

        return super().clean()

    def save(self, *args, **kwargs):
        """Sobrescribe save para asegurar validación en cada guardado y calcular costo_final."""
        # Calcular el costo final antes de guardar
        self.costo_final = self.calcular_costo_final()
        
        # Validar antes de guardar
        if self.cubierta:
            self.cubierta._validar_uso_area_cubierta()
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"

    def __str__(self):
        return f"Habitación {self.nombre_usuario} - Ubicación {self.ubicacion} - {self.tipo}"