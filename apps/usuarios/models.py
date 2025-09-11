from django.db import models
from django.contrib.auth.models import AbstractBaseUser

# Create your models here.

class Modulo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"Módulo de {self.nombre}"

class TipoEmpleado(models.Model):
    nombre = models.CharField(max_length=100)
    nivel_acceso = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.nombre}"

class UsuarioEmpleado(AbstractBaseUser):
    pass