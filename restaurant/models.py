from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Crucero(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del Crucero")
    description = models.TextField(blank=True, verbose_name="Descripción")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Crucero"
        verbose_name_plural = "Cruceros"
    
    def __str__(self):
        return self.name

class Restaurante(models.Model):
    # Normalizado a tres tipos funcionales
    RESTAURANT_TYPES = [
        ('buffet', 'Buffet'),
        ('main', 'Main Dining Room'),
        ('restaurant', 'Restaurante'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre del Restaurante")
    type = models.CharField(max_length=20, choices=RESTAURANT_TYPES, verbose_name="Tipo")
    crucero = models.ForeignKey(Crucero, on_delete=models.CASCADE, verbose_name="Crucero")
    capacity = models.IntegerField(default=100, verbose_name="Capacidad")
    # Nuevos campos para dimensiones y características
    largo = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Largo (metros)")
    ancho = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Ancho (metros)")
    area_total = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Área Total (m²)")
    ubicacion = models.CharField(max_length=200, blank=True, verbose_name="Ubicación en el Crucero")
    descripcion = models.TextField(blank=True, verbose_name="Descripción del Restaurante")
    horario_apertura = models.TimeField(null=True, blank=True, verbose_name="Horario de Apertura")
    horario_cierre = models.TimeField(null=True, blank=True, verbose_name="Horario de Cierre")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Restaurante"
        verbose_name_plural = "Restaurantes"
    
    def __str__(self):
        return f"{self.name} - {self.crucero.name}"
    
    def save(self, *args, **kwargs):
        # Calcular área total si se proporcionan largo y ancho
        if self.largo and self.ancho:
            self.area_total = self.largo * self.ancho
        super().save(*args, **kwargs)

class MenuItem(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre del Plato")
    description = models.TextField(blank=True, verbose_name="Descripción")
    restaurant = models.ForeignKey(Restaurante, on_delete=models.CASCADE, verbose_name="Restaurante")
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="Cantidad en Stock")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Precio")
    included = models.BooleanField(default=True, verbose_name="Incluido en el Paquete")
    min_stock_alert = models.IntegerField(default=10, verbose_name="Alerta de Stock Mínimo")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Item del Menú"
        verbose_name_plural = "Items del Menú"
    
    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"
    
    @property
    def is_low_stock(self):
        return self.quantity < self.min_stock_alert

class Employee(models.Model):
    POSITIONS = [
        ('executive', 'Chef Ejecutivo'),
        ('chef-partie', 'Jefe de estación'),
        ('maitre-d', 'Jefe de comedor'),
        ('bartender', 'Bartender'),
        ('pastelero', 'Pastelero'),
        ('cocinero', 'Cocinero'),
        ('auxiliar', 'Auxiliares de cocina'),
        ('mesero', 'Mesero'),
        ('jefe-mesero', 'Jefe de meseros'),
    ]
    
    SHIFTS = [
        ('mañana', 'Mañana (6:00-14:00)'),
        ('tarde', 'Tarde (14:00-22:00)'),
        ('noche', 'Noche (22:00-6:00)'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre Completo")
    position = models.CharField(max_length=20, choices=POSITIONS, verbose_name="Cargo")
    shift = models.CharField(max_length=10, choices=SHIFTS, verbose_name="Turno")
    restaurant = models.ForeignKey(Restaurante, on_delete=models.CASCADE, verbose_name="Restaurante")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    email = models.EmailField(blank=True, verbose_name="Email")
    hire_date = models.DateField(auto_now_add=True, verbose_name="Fecha de Contratación")
    active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
    
    def __str__(self):
        return f"{self.name} - {self.get_position_display()}"

class PersonalRRHH(models.Model):
    """Modelo para la tabla localRRHH_personal_PruebaABorrar"""
    
    CATEGORIAS = [
        ('Mantenimiento', 'Mantenimiento'),
        ('Culinario', 'Culinario'),
        ('Entretenimiento', 'Entretenimiento'),
        ('Administrativo', 'Administrativo'),
        ('Seguridad', 'Seguridad'),
        ('Limpieza', 'Limpieza'),
    ]
    
    STATUS_CHOICES = [
        (1, 'Activo'),
        (2, 'Inactivo'),
        (3, 'Suspendido'),
    ]
    
    nombre = models.CharField(max_length=10, verbose_name="Nombre")
    apellido = models.CharField(max_length=10, verbose_name="Apellido")
    salario = models.PositiveIntegerField(verbose_name="Salario")
    edad = models.PositiveIntegerField(verbose_name="Edad")
    anios_experiencia = models.PositiveIntegerField(verbose_name="Años de Experiencia")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, verbose_name="Categoría")
    puesto = models.CharField(max_length=30, verbose_name="Puesto")
    pStatus = models.IntegerField(choices=STATUS_CHOICES, verbose_name="Estado")
    
    class Meta:
        db_table = 'localRRHH_personal_PruebaABorrar'
        verbose_name = "Personal RRHH"
        verbose_name_plural = "Personal RRHH"
        ordering = ['categoria', 'puesto', 'apellido']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.puesto}"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    @property
    def is_active(self):
        return self.pStatus == 1

class MaintenanceItem(models.Model):
    AREAS = [
        ('cocina', 'Cocina'),
        ('comedor', 'Comedor'),
        ('bar', 'Bar'),
        ('almacen', 'Almacén'),
        ('equipos', 'Equipos'),
        ('refrigeracion', 'Refrigeración'),
        ('limpieza', 'Limpieza'),
    ]
    
    PRIORITIES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    
    area = models.CharField(max_length=20, choices=AREAS, verbose_name="Área")
    description = models.TextField(verbose_name="Descripción del Problema")
    priority = models.CharField(max_length=10, choices=PRIORITIES, verbose_name="Prioridad")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pendiente', verbose_name="Estado")
    restaurant = models.ForeignKey(Restaurante, on_delete=models.CASCADE, verbose_name="Restaurante")
    reported_by = models.CharField(max_length=100, verbose_name="Reportado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Reporte")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Completado")
    
    class Meta:
        verbose_name = "Item de Mantenimiento"
        verbose_name_plural = "Items de Mantenimiento"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_area_display()} - {self.get_priority_display()}"

class ConsumptionRecord(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, verbose_name="Item del Menú")
    cruise_day = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)], 
        verbose_name="Día del Crucero"
    )
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Total")
    is_included = models.BooleanField(verbose_name="Incluido en el Paquete")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Consumo")
    
    class Meta:
        verbose_name = "Registro de Consumo"
        verbose_name_plural = "Registros de Consumo"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.menu_item.name} - Día {self.cruise_day}"
    
    def save(self, *args, **kwargs):
        self.unit_price = self.menu_item.price
        self.total_price = self.unit_price * self.quantity if not self.is_included else 0
        self.is_included = self.menu_item.included
        super().save(*args, **kwargs)

# Nuevos modelos para la sección de Gestión
class ComidasPreviu(models.Model):
    """Modelo que apunta a la tabla comidasPreviu existente con estructura real"""
    # Estructura real de la tabla comidasPreviu
    ingredientes = models.CharField(max_length=200, verbose_name="Ingredientes", blank=True, null=True)
    tipo = models.CharField(max_length=100, verbose_name="Tipo", blank=True, null=True)
    subtipo = models.CharField(max_length=100, verbose_name="Subtipo", blank=True, null=True)
    clase_alimenticia = models.CharField(max_length=100, verbose_name="Clase Alimenticia", blank=True, null=True)
    detalle = models.TextField(verbose_name="Detalle", blank=True, null=True)
    platos = models.CharField(max_length=200, verbose_name="Platos", blank=True, null=True)
    origen = models.CharField(max_length=100, verbose_name="Origen", blank=True, null=True)
    fuente = models.CharField(max_length=100, verbose_name="Fuente", blank=True, null=True)

    class Meta:
        db_table = 'comidasPreviu'
        verbose_name = "Ingrediente Previu"
        verbose_name_plural = "Ingredientes Previu"
        managed = False  # No crear migraciones para esta tabla

    def __str__(self):
        return self.ingredientes or f"Ingrediente {self.pk}"

class Ingrediente(models.Model):
    UNIDADES = [
        ('g', 'Gramos'),
        ('ml', 'Mililitros'),
    ]
    SUBTIPOS = [
        ('caducable', 'Caducable'),
        ('no_caducable', 'No Caducable'),
        ('refrigerable', 'Refrigerable'),
        ('no_refrigerable', 'No Refrigerable'),
    ]

    nombre = models.CharField(max_length=120, unique=True, verbose_name="Nombre")
    unidad = models.CharField(max_length=5, choices=UNIDADES, verbose_name="Unidad")
    subtipo = models.CharField(max_length=20, choices=SUBTIPOS, default='no_caducable', verbose_name="Subtipo")
    # tipo fijo 'comida' según requerimiento (no se modela tabla aparte aún)
    tipo = models.CharField(max_length=20, default='comida', editable=False, verbose_name="Tipo")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Creado")

    class Meta:
        verbose_name = "Ingrediente"
        verbose_name_plural = "Ingredientes"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Menu(models.Model):
    TIPOS_MENU = [
        ('desayuno', 'Desayuno'),
        ('almuerzo', 'Almuerzo'),
        ('cena', 'Cena'),
        ('snack', 'Snack'),
        ('especial', 'Especial'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Menú")
    tipo = models.CharField(max_length=20, choices=TIPOS_MENU, verbose_name="Tipo de Menú")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, verbose_name="Restaurante")
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Precio Total")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    is_temporary = models.BooleanField(default=False, verbose_name="Temporal / Ad-hoc")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Menú"
        verbose_name_plural = "Menús"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.restaurante.name}"
    
    def calcular_precio_total(self):
        """Calcula el precio total del menú basado en sus platillos"""
        total = sum(platillo.precio for platillo in self.platillos.all())
        self.precio_total = total
        self.save()
        return total

class Platillo(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Platillo")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='platillos', verbose_name="Menú")
    # Se elimina la asociación directa a múltiples restaurantes; queda implícita vía Menu.restaurante
    # restaurantes = models.ManyToManyField(Restaurante, related_name='platillos', verbose_name="Restaurantes", blank=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Platillo"
        verbose_name_plural = "Platillos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

# ---------------------
# Inventario (Almacén y Despensa)
# ---------------------

class WarehouseStock(models.Model):
    ingrediente = models.OneToOneField(Ingrediente, on_delete=models.CASCADE, related_name='warehouse_stock', verbose_name="Ingrediente")
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Cantidad Disponible")
    actualizado = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        verbose_name = "Stock Almacén"
        verbose_name_plural = "Stocks Almacén"

    def __str__(self):
        return f"{self.ingrediente.nombre} {self.cantidad}{self.ingrediente.unidad}"

class PantryItem(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='despensa', verbose_name="Restaurante")
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, related_name='pantry_items', verbose_name="Ingrediente")
    cantidad = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Cantidad")
    actualizado = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        verbose_name = "Item Despensa"
        verbose_name_plural = "Items Despensa"
        unique_together = ('restaurante', 'ingrediente')

    def __str__(self):
        return f"{self.restaurante.name} - {self.ingrediente.nombre}: {self.cantidad}{self.ingrediente.unidad}"

# ---------------------
# Pedidos (Restaurant -> Almacén)
# ---------------------

class Request(models.Model):
    STATUS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('parcial', 'Parcial'),
        ('entregado', 'Entregado'),
        ('rechazado', 'Rechazado'),
    ]
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='pedidos', verbose_name="Restaurante")
    creado_por = models.CharField(max_length=120, verbose_name="Creado por")  # Más adelante FK a User
    status = models.CharField(max_length=12, choices=STATUS, default='pendiente', verbose_name="Estado")
    notas = models.TextField(blank=True, verbose_name="Notas")
    creado = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    actualizado = models.DateTimeField(auto_now=True, verbose_name="Actualizado")

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-creado']

    def __str__(self):
        return f"Pedido {self.id} {self.restaurante.name} ({self.status})"

class RequestLine(models.Model):
    pedido = models.ForeignKey(Request, on_delete=models.CASCADE, related_name='lineas', verbose_name="Pedido")
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, verbose_name="Ingrediente")
    cantidad_solicitada = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Cant. Solicitada")
    cantidad_aprobada = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Cant. Aprobada")
    cantidad_entregada = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Cant. Entregada")

    class Meta:
        verbose_name = "Línea Pedido"
        verbose_name_plural = "Líneas Pedido"
        unique_together = ('pedido', 'ingrediente')

    def __str__(self):
        return f"{self.ingrediente.nombre} ({self.cantidad_solicitada}{self.ingrediente.unidad})"

# ---------------------
# Facturación y registros buffet
# ---------------------

class ServiceInvoice(models.Model):
    code = models.CharField(max_length=10, unique=True, editable=False, verbose_name="Código")
    restaurant = models.ForeignKey(Restaurante, on_delete=models.CASCADE, verbose_name="Restaurante")
    cruise = models.ForeignKey(Crucero, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Crucero")
    cruise_day = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Día Crucero")
    room_number = models.CharField(max_length=10, verbose_name="Habitación")
    date = models.DateField(auto_now_add=True, verbose_name="Fecha")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")

    class Meta:
        verbose_name = "Factura Restaurante"
        verbose_name_plural = "Facturas Restaurante"
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.code:
            last = ServiceInvoice.objects.order_by('-id').first()
            next_num = 1 if not last else last.id + 1
            self.code = f"R{next_num:05d}"
        super().save(*args, **kwargs)

    def recalc_total(self):
        total = sum(item.line_total for item in self.items.all())
        self.total_amount = total
        super().save(update_fields=['total_amount'])

class ServiceInvoiceItem(models.Model):
    invoice = models.ForeignKey(ServiceInvoice, related_name='items', on_delete=models.CASCADE, verbose_name="Factura")
    platillo = models.ForeignKey(Platillo, on_delete=models.CASCADE, verbose_name="Platillo")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Cantidad")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    line_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Subtotal")
    included = models.BooleanField(default=False, verbose_name="Incluido")

    class Meta:
        verbose_name = "Item Factura"
        verbose_name_plural = "Items Factura"

    def __str__(self):
        return f"{self.platillo.nombre} x{self.quantity}"

    def save(self, *args, **kwargs):
        # Unit price tomado del platillo salvo que included (0)
        if not self.pk:  # primera vez
            self.unit_price = self.platillo.precio
        if self.included:
            self.line_total = 0
        else:
            self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)
        # Recalcular total factura
        self.invoice.recalc_total()

class BuffetBulkRecord(models.Model):
    restaurant = models.ForeignKey(Restaurante, on_delete=models.CASCADE, limit_choices_to={'type': 'buffet'}, verbose_name="Buffet")
    cruise = models.ForeignKey(Crucero, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Crucero")
    cruise_day = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Día Crucero")
    date = models.DateField(auto_now_add=True, verbose_name="Fecha")
    platillo = models.ForeignKey(Platillo, on_delete=models.CASCADE, verbose_name="Platillo")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Cantidad")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")

    class Meta:
        verbose_name = "Registro Buffet"
        verbose_name_plural = "Registros Buffet"
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.restaurant.name} {self.date} {self.platillo.nombre} ({self.quantity})"

class IngredientePlatillo(models.Model):
    platillo = models.ForeignKey(Platillo, on_delete=models.CASCADE, related_name='ingredientes', verbose_name="Platillo")
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, verbose_name="Ingrediente")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cantidad")
    unidad = models.CharField(max_length=20, choices=Ingrediente.UNIDADES, verbose_name="Unidad")
    
    class Meta:
        verbose_name = "Ingrediente del Platillo"
        verbose_name_plural = "Ingredientes de Platillos"
        unique_together = ['platillo', 'ingrediente']
    
    def __str__(self):
        return f"{self.platillo.nombre} - {self.ingrediente.nombre} ({self.cantidad} {self.get_unidad_display()})"