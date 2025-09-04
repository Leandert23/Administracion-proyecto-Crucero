from django.db import models

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
    NUMEROS_CUARTO = [
        ('1', 'Cuarto 1'),
        ('2', 'Cuarto 2'),
        ('3', 'Cuarto 3'),
    ]
    numero = models.CharField(max_length=1, unique=True, choices=NUMEROS_CUARTO, editable=False)
    ESTADO_CHOICES = [
        ('D', 'Disponible'),
        ('O', 'Ocupado'),
    ]
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='D')
    paciente = models.ForeignKey('Paciente', null=True, blank=True, on_delete=models.SET_NULL)
    

    def __str__(self):
        return f"Cuarto {self.numero} - {'Disponible' if self.estado == 'D' else 'Ocupado'}"
    
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


