from django.db import models
from django.contrib.auth.models import User
from apps.cruceros.models import Crucero


class ConfiguracionSistema(models.Model):
    """Configuraciones generales del sistema"""
    nombre = models.CharField(max_length=100, unique=True)
    valor = models.TextField()
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
    
    def __str__(self):
        return self.nombre


class LogActividad(models.Model):
    """Registro de actividades del sistema"""
    TIPO_ACTIVIDAD_CHOICES = [
        ('login', 'Inicio de Sesión'),
        ('logout', 'Cierre de Sesión'),
        ('crear', 'Creación'),
        ('editar', 'Edición'),
        ('eliminar', 'Eliminación'),
        ('configurar', 'Configuración'),
        ('reporte', 'Generación de Reporte'),
        ('backup', 'Respaldo'),
        ('restore', 'Restauración'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    crucero = models.ForeignKey(Crucero, on_delete=models.SET_NULL, null=True, blank=True)
    tipo_actividad = models.CharField(max_length=20, choices=TIPO_ACTIVIDAD_CHOICES)
    descripcion = models.TextField()
    modulo = models.CharField(max_length=50)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Log de Actividad'
        verbose_name_plural = 'Logs de Actividad'
        ordering = ['-fecha_hora']
    
    def __str__(self):
        return f"{self.get_tipo_actividad_display()} - {self.descripcion[:50]}"


class BackupSistema(models.Model):
    """Registro de respaldos del sistema"""
    ESTADO_CHOICES = [
        ('iniciado', 'Iniciado'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
    ]
    
    nombre_archivo = models.CharField(max_length=255)
    ruta_archivo = models.CharField(max_length=500)
    tamaño_archivo = models.BigIntegerField(help_text="Tamaño en bytes")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='iniciado')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Respaldo del Sistema'
        verbose_name_plural = 'Respaldos del Sistema'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Backup {self.nombre_archivo} - {self.get_estado_display()}"


class ReporteSistema(models.Model):
    """Registro de reportes generados"""
    TIPO_REPORTE_CHOICES = [
        ('ventas', 'Reporte de Ventas'),
        ('inventario', 'Reporte de Inventario'),
        ('usuarios', 'Reporte de Usuarios'),
        ('actividades', 'Reporte de Actividades'),
        ('financiero', 'Reporte Financiero'),
        ('personalizado', 'Reporte Personalizado'),
    ]
    
    nombre = models.CharField(max_length=200)
    tipo_reporte = models.CharField(max_length=20, choices=TIPO_REPORTE_CHOICES)
    parametros = models.JSONField(default=dict, blank=True)
    archivo_generado = models.CharField(max_length=500, blank=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    crucero = models.ForeignKey(Crucero, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Reporte del Sistema'
        verbose_name_plural = 'Reportes del Sistema'
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.get_tipo_reporte_display()}"
