from django.contrib.auth.models import AbstractUser, Permission
from django.db import models

class ModuloSistema(models.Model):
    # Sólo almacenamos el código; las etiquetas quedan en las opciones
    MODULOS = [
        ('administracion', 'Administración'),
        ('cruceros', 'Gestión de Cruceros'),
        ('entretenimiento', 'Entretenimiento'),
        ('ventas', 'Ventas'),
        ('reservas', 'Reservas'),
        ('restaurante', 'Restaurante'),
        ('bares', 'Bares'),
        ('compras', 'Compras'),
        ('almacen', 'Almacén'),
        ('rh', 'Recursos Humanos'),
        ('medico', 'Servicio Médico'),
        ('mantenimiento', 'Mantenimiento'),
    ]

    codigo = models.CharField(max_length=20, choices=MODULOS, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['codigo']

    def __str__(self):
        # Mostrar la etiqueta legible en lugar del código
        return self.get_codigo_display()


# Crear entradas por defecto tras migraciones usando las opciones definidas en MODULOS
def _crear_modulos_por_defecto(sender, **kwargs):
    app_config = kwargs.get('app_config')
    if not app_config or app_config.label != 'usuarios':
        return
    for code, label in ModuloSistema.MODULOS:
        ModuloSistema.objects.get_or_create(codigo=code)


from django.db.models.signals import post_migrate
post_migrate.connect(_crear_modulos_por_defecto)

class Rol(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    modulos_acceso = models.ManyToManyField(ModuloSistema, blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Roles"
    
    def __str__(self):
        return self.nombre

class Empleado(AbstractUser):
    # Campos básicos
    telefono = models.CharField(max_length=15, blank=True)
    fecha_contratacion = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_ultimo_acceso = models.DateTimeField(null=True, blank=True)
    
    # Relación con rol
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    # Posible enlace a un crucero (puede ser null para empleados administrativos que gestionan todos)
    crucero = models.ForeignKey('cruceros.Crucero', on_delete=models.SET_NULL, null=True, blank=True, related_name='empleados')
    
    def save(self, *args, **kwargs):
        self.is_staff = True
        super().save(*args, **kwargs)
    
    def tiene_acceso_modulo(self, codigo_modulo):
        if self.is_superuser:
            return True
        if self.rol and self.rol.modulos_acceso.filter(codigo=codigo_modulo, activo=True).exists():
            return True
        return self.has_perm(f'acceso_{codigo_modulo}')

    @property
    def is_administrativo(self):
        """Heurística para determinar si un rol es administrativo.

        Comprueba el nombre del rol buscando palabras clave como 'admin' o 'administración'.
        Ajusta la heurística si tu proyecto usa otros nombres de rol.
        """
        if self.is_superuser:
            return True
        if not self.rol or not self.rol.nombre:
            return False
        nombre = self.rol.nombre.lower()
        keywords = ['admin', 'administración', 'administrativo']
        return any(k in nombre for k in keywords)

    def puede_acceder_crucero(self, crucero_obj):
        """Devuelve True si el empleado puede acceder al crucero pasado.

        Reglas:
        - superusuarios: acceso completo
        - si el empleado tiene asignado un `crucero`, solo puede acceder a ese crucero
        - si no tiene `crucero` asignado y es administrativo (según heurística), puede acceder a todos
        - en cualquier otro caso, False
        """
        if self.is_superuser:
            return True
        # Si tiene crucero asignado, sólo a ese
        if self.crucero_id:
            return self.crucero_id == getattr(crucero_obj, 'id', getattr(crucero_obj, 'pk', None))
        # Si no tiene crucero asignado, los administrativos pueden acceder a todos
        if not self.crucero_id and self.is_administrativo():
            return True
        return False
    
    def get_modulos_activos(self):
        if self.is_superuser:
            return ModuloSistema.objects.filter(activo=True)
        if self.rol:
            return self.rol.modulos_acceso.filter(activo=True)
        return ModuloSistema.objects.none()