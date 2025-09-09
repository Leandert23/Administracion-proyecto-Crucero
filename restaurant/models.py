from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
    RESTAURANT_TYPES = [
        ('buffet', 'Buffet'),
        ('principal', 'Restaurante Principal'),
        ('tematico', 'Restaurante Temático'),
        ('roomservice', 'Room Service'),
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
class Ingrediente(models.Model):
    UNIDADES = [
        ('kg', 'Kilogramo'),
        ('g', 'Gramo'),
        ('l', 'Litro'),
        ('ml', 'Mililitro'),
        ('unidad', 'Unidad'),
        ('taza', 'Taza'),
        ('cucharada', 'Cucharada'),
        ('cucharadita', 'Cucharadita'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Ingrediente")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por Unidad")
    unidad = models.CharField(max_length=20, choices=UNIDADES, verbose_name="Unidad de Medida")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    stock_disponible = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Stock Disponible")
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Stock Mínimo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Ingrediente"
        verbose_name_plural = "Ingredientes"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_unidad_display()})"
    
    @property
    def is_low_stock(self):
        return self.stock_disponible < self.stock_minimo

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
    CATEGORIAS = [
        ('entrada', 'Entrada'),
        ('sopa', 'Sopa'),
        ('ensalada', 'Ensalada'),
        ('plato_principal', 'Plato Principal'),
        ('postre', 'Postre'),
        ('bebida', 'Bebida'),
        ('acompanamiento', 'Acompañamiento'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Platillo")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, verbose_name="Categoría")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    tiempo_preparacion = models.IntegerField(default=0, verbose_name="Tiempo de Preparación (minutos)")
    porciones = models.IntegerField(default=1, verbose_name="Número de Porciones")
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='platillos', verbose_name="Menú")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Platillo"
        verbose_name_plural = "Platillos"
        ordering = ['categoria', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.get_categoria_display()}"

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