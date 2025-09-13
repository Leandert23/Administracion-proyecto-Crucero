from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Categoria(models.Model):
    nombre = models.CharField(max_length=50) 
    descripcion=models.CharField(max_length=100, default='')

    def __str__(self):
        return f"{self.nombre}, {self.descripcion}"

# Modelo de Menú (producto vendible)
class Menu(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=100)
    instruccion = models.CharField(max_length=800)
    precio_vta = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='menus',
        verbose_name='Categoría'
    )

    def __str__(self):
        return self.nombre

# Modelo intermedio para ingredientes de la receta

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

    
class Pedidos(models.Model):
    def descontar_stock_ingredientes(self):
        """
        Descuenta el stock de los ingredientes usados en los productos del pedido,
        registrando el egreso en MovimientoAlmacen por cada ingrediente y lote utilizado.
        """
        from almacen.models import Producto, Lote, MovimientoAlmacen
        for detalle in self.detalles.all():
            producto_bar = detalle.producto
            if not producto_bar:
                continue
            for receta_item in producto_bar.receta_items.all():
                ingrediente = receta_item.ingrediente
                cantidad_necesaria = receta_item.cantidad * detalle.cantidad
                # Buscar lotes disponibles (FIFO)
                lotes = ingrediente.lotes.order_by('fecha_ingreso', 'numero_lote')
                cantidad_restante = cantidad_necesaria
                for lote in lotes:
                    # Calcular stock actual del lote
                    ingresos = lote.cantidad_productos
                    egresos = lote.movimientos.filter(tipo='OUT').aggregate(models.Sum('cantidad'))['cantidad__sum'] or 0
                    disponible = ingresos - egresos
                    if disponible <= 0:
                        continue
                    descontar = min(disponible, cantidad_restante)
                    if descontar > 0:
                        MovimientoAlmacen.objects.create(
                            tipo='OUT',
                            producto=ingrediente,
                            lote=lote,
                            cantidad=descontar,
                            fecha=self.fecha_hora.date(),
                            modulo='BARES_SNACKS',
                            descripcion=f"Pedido #{self.id} - {producto_bar.nombre}"
                        )
                        cantidad_restante -= descontar
                    if cantidad_restante <= 0:
                        break
                if cantidad_restante > 0:
                    # Si no hay suficiente stock, podrías lanzar una excepción o registrar un error
                    pass
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]
    id = models.AutoField(primary_key=True)
    # ptoventa eliminado: ahora se usa sólo lugarentrega (Instalación)
    empleado=models.ForeignKey(
        'recursos_humanos.Personal',
        on_delete=models.PROTECT,
        related_name='pedidos_atendidos',
        null=True,
        blank=True,
    )
    fecha_hora = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    cliente=models.ForeignKey(
        'ventas.Cliente',
        on_delete=models.SET_NULL,
        related_name='pedidos',
        null=True,
        blank=True,
    )
    # Nueva FK principal a la instalación donde se entregará / consumirá
    lugarentrega = models.ForeignKey(
        'cruceros.Instalacion',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='pedidos_entregados',
        help_text='Instalación física de entrega o consumo (bar, restaurante, etc.)'
    )

    numero_factura = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        null=True,
        help_text='Número de factura generado para el pedido (formato BR-XXX-0001[-PR])'
    )
    # Si el consumo es en camarote, guardamos la habitación
    habitacion = models.ForeignKey(
        'cruceros.Habitacion',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='pedidos_servicio',
        help_text='Habitación destino si el consumo es en camarote'
    )
    
    
    def __str__(self):
      return f"Pedido #{self.id} - {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def total(self):
        return sum(detalle.subtotal for detalle in self.detalles.all())

    @property
    def fecha(self):
        """Compatibilidad: devuelve sólo la parte de fecha de fecha_hora al remover el campo fecha."""
        return self.fecha_hora.date()
    
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedidos, on_delete=models.CASCADE, related_name='detalles')
    # Nuevo vínculo directo a ProductoBar (reemplaza a 'menu')
    producto = models.ForeignKey('ProductoBar', on_delete=models.CASCADE, related_name='detalles_pedido', null=True, blank=True)
    cantidad = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)], default=0)

    @property
    def subtotal(self):
       precio = 0
       if self.producto and getattr(self.producto, 'precio_vta', None) is not None:
           try:
               precio = self.producto.precio_vta or 0
           except Exception:
               precio = 0
       return self.cantidad * precio

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (Pedido #{self.pedido.id})"

# ProductoBar: producto creado en interfaz de gestión (separado del Menu final)
class ProductoBar(models.Model):
    PLANES = [
        ('gratis', 'All Inclusive'),
        ('pago', 'Premium')
    ]
    nombre = models.CharField(max_length=50)
    categoria = models.CharField(max_length=60)  # Corresponde al select "categoria_filtro"
    tipo_almacen = models.CharField(max_length=40)  # tipo almacen (id tipo)
    subtipo_almacen = models.CharField(max_length=40)  # subtipo almacen (id subtipo)
    plan = models.CharField(max_length=10, choices=PLANES, default='gratis')
    receta = models.TextField(blank=True, default='')  # JSON / texto libre para preparación futura
    precio_vta = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # si plan=pago
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.nombre} ({self.get_plan_display()})"


class IngredienteReceta(models.Model):
    producto_bar = models.ForeignKey('ProductoBar', on_delete=models.CASCADE, related_name='receta_items')
    ingrediente = models.ForeignKey('almacen.Producto', on_delete=models.PROTECT, related_name='usos_bares')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unidad = models.CharField(max_length=20, blank=True, default='')

    class Meta:
        unique_together = (('producto_bar', 'ingrediente'),)
        verbose_name = 'Ingrediente de Receta'
        verbose_name_plural = 'Ingredientes de Receta'

    def __str__(self):
        return f"{self.producto_bar.nombre} -> {self.ingrediente.nombre} ({self.cantidad} {self.unidad})"