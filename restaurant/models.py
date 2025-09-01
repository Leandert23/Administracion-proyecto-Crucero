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
        ('buffet', 'Buffet Principal'),
        ('gourmet', 'Restaurante Gourmet'),
        ('casual', 'Restaurante Casual'),
        ('roomservice', 'Room Service'),
        ('bar', 'Bar/Snacks'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre del Restaurante")
    type = models.CharField(max_length=20, choices=RESTAURANT_TYPES, verbose_name="Tipo")
    crucero = models.ForeignKey(Crucero, on_delete=models.CASCADE, verbose_name="Crucero")
    capacity = models.IntegerField(default=100, verbose_name="Capacidad")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Restaurante"
        verbose_name_plural = "Restaurantes"
    
    def __str__(self):
        return f"{self.name} - {self.crucero.name}"

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
        ('chef', 'Chef'),
        ('sous-chef', 'Sous Chef'),
        ('camarero', 'Camarero'),
        ('bartender', 'Bartender'),
        ('supervisor', 'Supervisor'),
        ('cocinero', 'Cocinero'),
        ('ayudante', 'Ayudante de Cocina'),
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