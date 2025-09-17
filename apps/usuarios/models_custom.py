from django.db import models

class RolCustom(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    # Guardamos los módulos como una lista de strings
    modulos = models.JSONField(default=list)  # requiere Django 3.1+

    def __str__(self):
        return self.nombre

class UsuarioCustom(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # Hasheado en implementación real
    rol = models.ForeignKey(RolCustom, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.username})"
