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

    #Todas las conexiones se hacen a traves de señales
    def calcular_costos_totales(self):
        # Se conecta con el modulo compras para mostrar las ganancias
        return 0

    def calcular_ganancias_totales(self):
        # Aquí deberían conectar con el módulo de ventas mediante signals
        return 0 

    def calcular_presupuesto_estimado(self):
        # Ejemplo de cálculo: [(Precio de los boletos + Estimado de los no incluidos) - Total*10%] * Capacidad del barco al 60%
        return self.costos_totales + self.precio_combustible * self.num_pasajeros_actual

    def actualizar_num_empleados_actual(self):
        # Se conecta con recursos humanos para mostrar las los empleados
        return 0

    def actualizar_num_pasajeros_actual(self):
        # Se conecta con ventas para saber cuantos boletos se vendieron (boletos=cantidad de pasajeros)
        return 0

    def actualizar_campos_financieros(self):
        self.costos_totales = self.calcular_costos_totales()
        self.ganancias_totales = self.calcular_ganancias_totales()
        self.presupuesto_estimado = self.calcular_presupuesto_estimado()
        self.num_empleados_actual = self.actualizar_num_empleados_actual()
        self.num_pasajeros_actual = self.actualizar_num_pasajeros_actual()
        self.save()

class Alerta(models.Model):
    mensaje = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
    administracion = models.ForeignKey(Administracion, on_delete=models.CASCADE, related_name='alertas')

'''''''''''
Esto nos lo da otro modulo y no está conectado directamente a nosotros
class Compra(models.Model):
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField()
    administracion = models.ForeignKey(Administracion, on_delete=models.CASCADE, related_name='compras')
'''''''''''
'''''''''''
Esto nos lo da otro modulo y no está conectado directamente a nosotros
class RecursoHumano(models.Model):
    nombre = models.CharField(max_length=255)
    puesto = models.CharField(max_length=100)
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    administracion = models.ForeignKey(Administracion, on_delete=models.CASCADE, related_name='recursos_humanos')
'''''''''''