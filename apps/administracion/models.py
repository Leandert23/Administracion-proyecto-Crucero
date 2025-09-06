from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Modulo(models.Model):
    """Modelo para representar módulos del sistema"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Rol(models.Model):
    """Modelo para representar roles del sistema"""

    TIPO_CHOICES = [
        ('admin', 'Administrador'),
        ('editor', 'Editor'),
        ('lector', 'Lector'),
        ('especialista', 'Especialista'),
    ]

    nombre = models.CharField(max_length=100)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='roles')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='lector')
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['modulo', 'nombre']
        unique_together = ['nombre', 'modulo']

    def __str__(self):
        return f"{self.nombre} ({self.modulo.nombre})"


class UsuarioRol(models.Model):
    """Modelo para asignar roles a usuarios"""

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles_asignados')
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='asignaciones')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    esta_activo = models.BooleanField(default=True)
    asignado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roles_asignados_por'
    )

    class Meta:
        verbose_name = "Asignación de Rol"
        verbose_name_plural = "Asignaciones de Roles"
        ordering = ['-fecha_asignacion']
        unique_together = ['usuario', 'rol']

    def __str__(self):
        return f"{self.usuario.username} - {self.rol.nombre}"

    def esta_vigente(self):
        """Verifica si la asignación de rol está vigente"""
        if not self.esta_activo:
            return False
        if self.fecha_expiracion and self.fecha_expiracion < timezone.now():
            return False
        return True


class SolicitudCompra(models.Model):
    """Modelo para solicitudes de compra"""

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('completada', 'Completada'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes')
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    costo_estimado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    aprobado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_aprobadas'
    )

    class Meta:
        verbose_name = "Solicitud de Compra"
        verbose_name_plural = "Solicitudes de Compra"
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"{self.titulo} - {self.solicitante.username}"
