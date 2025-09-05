from django.db import models
from pytz import timezone
from almacen import *
from django.core.validators import MinValueValidator, MaxValueValidator

class Categoria(models.Model):
    nombre = models.CharField(max_length=50) 
    descripcion=models.CharField(max_length=100, default='')
    def __str__(self):
        return self.nombre, self.descripcion

    class Menu(models.Model):
     nombre = models.CharField(max_length=50)
     descripcion = models.CharField(max_length=100)
     instruccion = models.CharField(max_length=800)
     precio_vta = models.DecimalField(max_digits=10, decimal_places=2) 
     categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL,  # Si se borra la categoría, el campo queda NULL
        null=True,
        blank=True,
        related_name='menus',  # Para acceder: categoria.menus.all()
        verbose_name='Categoría'
    )
     
    # La tabla intermedia IngredientesReceta conecta Menu con Producto
     ingredientes = models.ManyToManyField(
        'almacen.Producto', 
        through='IngredientesReceta',
        through_fields=('receta', 'producto')
    )

    def __str__(self):
        return self.nombre
     
    class IngredientesReceta(models.Model):
    # Enlaza a Menu
     receta = models.ForeignKey('Menu', on_delete=models.CASCADE, related_name='ingredientes_detalle')
    # Enlaza a Producto de la app 'almacen'
     producto = models.ForeignKey('almacen.Producto', on_delete=models.CASCADE, related_name='producto_enrecetas')
     cantidad = models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(99)], default=0)
     medida = models.CharField(max_length=10,choices=[
    ('unidades', 'Unidades'),
    ('gramos', 'Gramos'),
    ('litros', 'Litros'),
    ('ml', 'Mililitros'),
    ('kg', 'Kilogramos'),
],  default='unidades')  # Ejemplo: gramos, litros, unidades
     class Meta:
        unique_together = ['receta', 'producto']
    def __str__(self):
        return f"{self.cantidad} {self.medida} de {self.producto} para {self.receta}" 

#Puntos de venta de los distintos bares del crucero
class Bar(models.Model):
    nombre = models.CharField(max_length=50)
    ubicacion = models.ForeignKey('cruceros.Instalacion', 
        on_delete=models.CASCADE,
        related_name='bares',
        help_text="Ubicacion del bar dentro del crucero")
    hora_aper=models.DateTimeField(null=False, default=timezone.now) #YYYY-MM-DD HH:MM:SS
    hora_cierre=models.DateTimeField(null=False, default=timezone.now)
    
    class Meta:
        constraints = [
        models.CheckConstraint(
            check=models.Q(hora_cierre__gt=models.F('hora_aper')),  # Condición
            name='hcierre_mayorqueapertura'  
        )
    ]
    def __str__(self):
     return f"{self.nombre} - {self.ubicacion} // Apertura: {self.hora_aper} - Cierre: {self.hora_cierre}"

    
class Clientes(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
class Pedidos(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    id = models.AutoField(primary_key=True)
    ptoventa=models.ForeignKey(Bar, on_delete=models.CASCADE, related_name='pedidos')
    fecha=models.DateTimeField(null=False, default=timezone.now)
    empleado=models.ForeignKey('recursos_humanos.Personal', default=1, on_delete=models.PROTECT, related_name='pedidos_atendidos')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    cliente=models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='pedidos')
    lugar_consumo=models.CharField(max_length=20, default="Bar") #Si sera consumido en el bar o camarote
    
    
    def __str__(self):
      return f"Pedido #{self.id} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def total(self):
        return sum(detalle.subtotal for detalle in self.detalles.all())
    
class DetallePedido(models.Model):
    pedido=models.ForeignKey(Pedidos, on_delete=models.CASCADE, related_name='detalles')
    menu=models.ForeignKey('Menu', on_delete=models.CASCADE, related_name='detalles_pedido')
    cantidad=models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(50)], default=0)
    
    @property
    def subtotal(self):
        return self.cantidad * self.menu.precio
    
    def __str__(self):
        return f"{self.cantidad} x {self.menu.nombre} (Pedido #{self.pedido.id})"