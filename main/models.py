from django.db import models

class Personal(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    edad = models.IntegerField()
    experiencia = models.IntegerField()
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=50)
    puesto = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"