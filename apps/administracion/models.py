from django.db import models

class Crucero(models.Model):
    nombre = models.CharField(max_length=255)

class Administracion(models.Model):
    crucero = models.ForeignKey(Crucero, on_delete=models.CASCADE, related_name='finanzas')
    costos_totales = models.DecimalField(max_digits=12, decimal_places=2)
    ganancias_totales = models.DecimalField(max_digits=12, decimal_places=2)
    presupuesto_estimado = models.DecimalField(max_digits=12, decimal_places=2)
    precio_combustible = models.DecimalField(max_digits=10, decimal_places=2)
    num_pasajeros_actual = models.PositiveIntegerField()
    num_empleados_actual = models.PositiveIntegerField()
    fecha_creacion = models.DateField(auto_now_add=True)

    def calcular_costos_totales(self):
        # Suma de todas las compras asociadas al crucero
        return sum(compra.monto for compra in self.compras.all())

    def calcular_ganancias_totales(self):
        # Aquí deberían conectar con el módulo de ventas mediante signals
        # Ejemplo: return sum(venta.monto for venta in self.ventas.all())
        return 0 

    def calcular_presupuesto_estimado(self):
        # Ejemplo de cálculo: puedes sumar costos estimados y restar gastos
        return self.costos_totales + self.precio_combustible * self.num_pasajeros_actual

    def actualizar_campos_financieros(self):
        self.costos_totales = self.calcular_costos_totales()
        self.ganancias_totales = self.calcular_ganancias_totales()
        self.presupuesto_estimado = self.calcular_presupuesto_estimado()
        self.save()

    def actualizar_num_empleados_actual(self):
        self.num_empleados_actual = self.recursos_humanos.count()
        self.save()

    def actualizar_num_pasajeros_actual(self, nuevo_valor):
        self.num_pasajeros_actual = nuevo_valor
        self.save()

class Compra(models.Model):
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    administracion = models.ForeignKey(Administracion, on_delete=models.CASCADE, related_name='compras')

class RecursoHumano(models.Model):
    nombre = models.CharField(max_length=255)
    puesto = models.CharField(max_length=100)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    administracion = models.ForeignKey(Administracion, on_delete=models.CASCADE, related_name='recursos_humanos')

class Alerta(models.Model):
    mensaje = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    administracion = models.ForeignKey(Administracion, on_delete=models.CASCADE, related_name='alertas')
