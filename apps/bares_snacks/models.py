from django.db import models
import datetime
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Categoria(models.Model):
    nombre = models.CharField(max_length=50) 
    def __str__(self):
        return self.nombre 

class Productos(models.Model): 
    nombre = models.CharField(max_length=50) 
    descripcion=models.CharField(max_length=100)
    precio=models.DecimalField(max_digits=10, decimal_places=2)
    categoria=models.ForeignKey(Categoria, on_delete=models.CASCADE)
    stock_act=models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(9999)], default=0)
    stock_minimo=models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(999)], default=0)
    def __str__(self):
        return self.nombre 
    
class Menu(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion=models.CharField(max_length=100)
    instruccion=models.CharField(max_length=800)
    precio_vta=models.DecimalField(max_digits=10, decimal_places=2)
    ingredientes = models.ManyToManyField(
        Productos,
        through='IngredientesReceta',  # Tabla intermedia
        through_fields=('receta', 'producto')
    )  
    
    def __str__(self):
        return self.nombre
    
 #Tabla para unir los productos y la receta 
class IngredientesReceta(models.Model):
    receta = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='lista_ingredientes')
    producto=models.ForeignKey(Productos, on_delete=models.CASCADE, related_name='ingrediente_enreceta')
    cantidad=models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(99)], default=0)
    und_medida=models.CharField(max_length=20) #gr, kg
    class Meta:
        unique_together = ['receta', 'producto']
    def __str__(self):
        return f"{self.cantidad} {self.und_medida} de {self.producto} para {self.receta}"    

#Puntos de venta de los distintos bares del crucero
class PuntoVenta(models.Model):
    nombre = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=150)
    hora_aper=models.DateTimeField(null=False)
    hora_cierre=models.DateTimeField(null=False)
    
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
    ptoventa=models.ForeignKey(PuntoVenta, on_delete=models.CASCADE, related_name='pedidos')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
   # empleado=models.ForeignKey(Empleados, on_delete=models.CASCADE, related_name='pedidos_atendidos')
    cliente=models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='pedidos')
    
    def __str__(self):
      return f"Pedido #{self.id} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def total(self):
        return sum(detalle.subtotal for detalle in self.detalles.all())
    
class DetallePedido(models.Model):
    pedido=models.ForeignKey(Pedidos, on_delete=models.CASCADE, related_name='detalles')
    menu=models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='detalles_pedido')
    cantidad=models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(50)], default=0)
    
    def __str__(self):
        return f"{self.cantidad} x {self.menu.nombre} (Pedido #{self.pedido.id})"
    