from django.db import models
from django.conf import settings
from apps.cruceros.models import Crucero

class Administracion(models.Model):
    crucero = models.ForeignKey(Crucero, on_delete=models.CASCADE, related_name='finanzas')
    costos_totales = models.DecimalField(max_digits=12, decimal_places=2)
    ganancias_totales = models.DecimalField(max_digits=12, decimal_places=2)
    presupuesto_estimado = models.DecimalField(max_digits=12, decimal_places=2)
    precio_combustible = models.DecimalField(max_digits=10, decimal_places=2)
    num_pasajeros_actual = models.PositiveIntegerField()
    num_empleados_actual = models.PositiveIntegerField()

    # Agregar método para calcular presupuesto
    def calcular_presupuesto_estimado(self, pasajeros=None, empleados=None, dias=None, distancia=None):
        # Ecuación: [(Precio de los boletos + Estimado de los no incluidos) - Total*10%] * Capacidad del barco al 60%
        """
        (Valores por defecto, tomar en cuenta una capacidad del barco al 60%)
        Fórmula de presupuesto:
        - Combustible: distancia * $2.5 por km
        - Comida: (pasajeros + empleados) * días * $45 por persona por día
        - Mantenimiento: días * $1200 por día
        - Operacional: empleados * días * $80 por empleado por día 
        """
        if not all([pasajeros, empleados, dias, distancia]):
            pasajeros = self.num_pasajeros_actual
            empleados = self.num_empleados_actual
            dias = 7  # valor por defecto
            distancia = 1000  # valor por defecto
        
        costo_combustible = distancia * 2.5
        costo_comida = (pasajeros + empleados) * dias * 45
        costo_mantenimiento = dias * 1200
        costo_operacional = empleados * dias * 80
        
        return costo_combustible + costo_comida + costo_mantenimiento + costo_operacional

    #Todas las conexiones se hacen a traves de señales
    def calcular_costos_totales(self):
        # Se conecta con el modulo compras para mostrar las ganancias
        return 0

    def calcular_ganancias_totales(self):
        # Aquí deberían conectar con el módulo de ventas mediante signals
        return 0 

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

# Agregar modelo para solicitudes de compra
class SolicitudCompra(models.Model):
    ESTADOS = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ]
    
    crucero = models.ForeignKey(Crucero, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pending')
    razon_rechazo = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Solicitud {self.id} - {self.crucero.nombre} - ${self.monto}"
    
# Modelos para el sistema de roles
class Modulo(models.Model):
    """Modelo para representar los diferentes módulos del sistema"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

class Rol(models.Model):
    """Modelo para representar los roles disponibles en cada módulo"""
    TIPOS_ROL = [
        ('admin', 'Administrador'),
        ('editor', 'Editor'),
        ('lector', 'Lector'),
        ('especialista', 'Especialista'),
    ]
    
    nombre = models.CharField(max_length=50)
    tipo = models.CharField(max_length=20, choices=TIPOS_ROL)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='roles')
    descripcion = models.TextField(blank=True)
    permisos = models.JSONField(default=dict, help_text="Permisos específicos del rol")
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        unique_together = ['nombre', 'modulo']
        ordering = ['modulo', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.modulo.nombre})"

class UsuarioRol(models.Model):
    """Modelo para asignar roles a usuarios en módulos específicos"""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='roles_asignados')
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='usuarios')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    asignado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='roles_asignados_por_mi')
    
    class Meta:
        verbose_name = "Rol de Usuario"
        verbose_name_plural = "Roles de Usuarios"
        unique_together = ['usuario', 'rol']
        ordering = ['-fecha_asignacion']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"
    
    @property
    def esta_activo(self):
        """Verifica si el rol está activo y no ha expirado"""
        if not self.activo:
            return False
        if self.fecha_expiracion:
            from django.utils import timezone
            return timezone.now() < self.fecha_expiracion
        return True