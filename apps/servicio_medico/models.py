from django.db import models
from django.utils import timezone

# Create your models here.

from datetime import date

class Paciente(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    fecha_registro = models.DateTimeField(auto_now_add=True)
    nombres = models.CharField(max_length=100)
    primer_apellido = models.CharField(max_length=100)
    segundo_apellido = models.CharField(max_length=100, blank=True, null=True)
    documento_identidad = models.CharField(max_length=20, unique=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    fechade_nacimiento = models.DateField()
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=15)
    correo_electronico = models.EmailField(unique=True)
    motivo_consulta = models.TextField(max_length=100)
    descripcion_consulta = models.TextField(max_length=500)
    antecedentes_medicos = models.TextField(max_length=500)
    alergias = models.TextField(max_length=500, blank=True, null=True)
    medicamentos_actuales = models.TextField(max_length=500, blank=True, null=True)
    historial_familiar = models.TextField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.nombres} {self.apellido} - {self.documento_identidad}"

    @property
    def edad(self):
        today = date.today()
        return today.year - self.fechade_nacimiento.year - ((today.month, today.day) < (self.fechade_nacimiento.month, self.fechade_nacimiento.day))
    
class Insumo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=500) 
    fecha_vencimiento = models.DateField()

    


    def __str__(self):
        return self.nombre


class Inventario(models.Model):
    insumo = models.ForeignKey('Insumo', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    bajo_stockcantidad = models.IntegerField(default=10)
    ESTADOS_CHOICES = [
    ('S', 'Suficiente'),
    ('B', 'Bajo stock'),
    ('C', 'Crítico'),
    ]
    bajo_stock = models.CharField(max_length=1, choices=ESTADOS_CHOICES, default='S')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.insumo.nombre} - {self.cantidad}"
    
class Instrumentaria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=500)
    fecha_adquisicion = models.DateField()
    ESTADO_CHOICES = [
        ('O', 'Operativa'),
        ('N', 'No operativa'),
    ]
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='O')
    mantenimiento_programado = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    
class PacienteObservacion(models.Model):
    paciente = models.ForeignKey('Paciente', on_delete=models.CASCADE)
    fecha_observacion = models.DateTimeField(auto_now_add=True)
    fecha_alta = models.DateTimeField(blank=True, null=True)
    observacion = models.TextField(max_length=1000)
    tratamiento = models.TextField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return f"Observacion de {self.paciente.nombres} {self.paciente.apellido} - {self.fecha_observacion.strftime('%Y-%m-%d %H:%M:%S')}"
class Medico(models.Model):
    nombres = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100)
    numero_licencia = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=15)
    correo_electronico = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.nombres} {self.apellido} - {self.especialidad}"

class cuarto(models.Model):
    ESTADO_CHOICES = [
        ('D', 'Disponible'),
        ('O', 'Ocupado'),
        ('M', 'Mantenimiento'),
    ]
    
    # Relación con crucero
    crucero = models.ForeignKey('cruceros.Crucero', on_delete=models.CASCADE, related_name='cuartos_medicos', default=1)
    numero = models.CharField(max_length=10, help_text="Número del cuarto médico")
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='D')
    paciente = models.ForeignKey('Paciente', null=True, blank=True, on_delete=models.SET_NULL)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_ultima_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['crucero', 'numero']
        ordering = ['crucero', 'numero']

    def __str__(self):
        return f"{self.crucero.nombre} - Cuarto {self.numero} - {'Disponible' if self.estado == 'D' else 'Ocupado' if self.estado == 'O' else 'Mantenimiento'}"
    
    @property
    def get_estado_display(self):
        return dict(self.ESTADO_CHOICES)[self.estado]
    
    def clean(self):
        """
        Validación personalizada para asegurar que un paciente no ocupe múltiples cuartos
        """
        from django.core.exceptions import ValidationError
        
        # Si el cuarto está ocupado y tiene un paciente asignado
        if self.estado == 'O' and self.paciente:
            # Verificar si el paciente ya está ocupando otro cuarto
            cuartos_ocupados_por_paciente = cuarto.objects.filter(
                paciente=self.paciente,
                estado='O'
            ).exclude(id=self.id)  # Excluir el cuarto actual si se está editando
            
            if cuartos_ocupados_por_paciente.exists():
                cuarto_existente = cuartos_ocupados_por_paciente.first()
                raise ValidationError({
                    'paciente': f'El paciente {self.paciente.nombres} {self.paciente.primer_apellido} ya está ocupando el cuarto {cuarto_existente.numero} del crucero {cuarto_existente.crucero.nombre}. Un paciente no puede ocupar múltiples cuartos simultáneamente.'
                })
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir save para ejecutar validaciones personalizadas
        """
        self.clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def generar_cuartos_por_crucero(cls, crucero):
        """
        Genera cuartos médicos según el tamaño del crucero:
        - Pequeño: 5 cuartos
        - Mediano: 10 cuartos  
        - Grande: 20 cuartos
        """
        # Mapeo de tamaños a cantidad de cuartos
        cuartos_por_tamaño = {
            'pequeno': 5,
            'mediano': 10,
            'grande': 20
        }
        
        cantidad_cuartos = cuartos_por_tamaño.get(crucero.tipo_crucero, 10)  # Default mediano
        
        # Verificar si ya existen cuartos para este crucero
        cuartos_existentes = cls.objects.filter(crucero=crucero).count()
        
        if cuartos_existentes == 0:
            # Crear los cuartos
            cuartos_creados = []
            for i in range(1, cantidad_cuartos + 1):
                cuarto_obj = cls.objects.create(
                    crucero=crucero,
                    numero=str(i),
                    estado='D'
                )
                cuartos_creados.append(cuarto_obj)
            
            return cuartos_creados
        else:
            # Retornar cuartos existentes
            return cls.objects.filter(crucero=crucero).order_by('numero')
    
ESTADOS = [
    ('E', 'En espera'),
    ('A', 'Atendido'),
    ('C', 'Cancelado'),
    ('F', 'Finalizado'),
]


from django.core.exceptions import ValidationError

class Solicitudmedicamento(models.Model):
    camarote = models.CharField(max_length=10)
    insumo = models.ForeignKey('insumo', on_delete=models.CASCADE)
    razon = models.TextField(max_length=500, blank=True, null=True)  # Razón de solicitud
    cantidad = models.IntegerField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=1, choices=ESTADOS, default='E')
    fecha_aprobacion = models.DateTimeField(blank=True, null=True)

    def clean(self):
        if self.fecha_aprobacion and self.estado not in ['A', 'F']:
            raise ValidationError('La fecha de aprobación solo puede asignarse si el estado es Atendido o Finalizado.')

class Producto(models.Model):
    TIPOS_PRODUCTO = [
        ("COMIDA", "Comida"),
        ("BIENES", "Bienes"),
    ]

    SUBTIPOS_PRODUCTO = [
        ("CADUCABLE", "Caducable"),
        ("NO_CADUCABLE", "No caducable"),
        ("REFRIGERADO", "Refrigerado"),
        ("NO_REFRIGERADO", "No refrigerado"),
        ("BEBIDA", "Bebida"),
        ("LICOR", "Licor"),
        ("REPUESTOS", "Repuestos"),
        ("LIMPIEZA", "Materiales de limpieza"),
        ("MEDICOS", "Materiales médicos"),
        ("ACTIVOS", "Bienes activos"),
    ]

    UNIDADES_MEDIDA = [
        ("L", "Litros"),
        ("M", "Metros"),
        ("K", "Kilogramos"),
        ("U", "Unidades"),
    ]

    SUBTIPOS_POR_TIPO = {
        "COMIDA": {"CADUCABLE", "NO_CADUCABLE", "REFRIGERADO", "NO_REFRIGERADO", "BEBIDA", "LICOR"},
        "BIENES": {"REPUESTOS", "LIMPIEZA", "MEDICOS", "ACTIVOS"},
    }

class NotificacionUrgencia(models.Model):
    """
    Modelo para notificaciones de urgencia médica desde otros módulos
    """
    ESTADO_CHOICES = [
        ('P', 'Pendiente'),
        ('A', 'Atendida'),
    ]
    
    # Información básica
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    modulo_origen = models.CharField(max_length=50, help_text="Módulo que envía la notificación")
    solicitante = models.CharField(max_length=100, help_text="Nombre de quien solicita ayuda")
    ubicacion = models.CharField(max_length=200, help_text="Ubicación exacta")
    tipo_urgencia = models.CharField(max_length=100, help_text="Tipo de urgencia")
    descripcion = models.TextField(max_length=1000, help_text="Descripción detallada")
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P')
    
    # Información de respuesta
    fecha_atendida = models.DateTimeField(blank=True, null=True)
    observaciones_medicas = models.TextField(max_length=1000, blank=True, null=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Notificación de Urgencia"
        verbose_name_plural = "Notificaciones de Urgencia"
    
    def __str__(self):
        return f"Urgencia - {self.ubicacion} - {self.fecha_creacion.strftime('%d/%m/%Y %H:%M')}"