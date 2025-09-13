from django.db import models
from django.core.validators import RegexValidator, MaxLengthValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

# Validadores para texto sin números, máximo 10 caracteres, inicial mayúscula
def validate_name(value):
    if any(char.isdigit() for char in value):
        raise ValidationError('No se permiten números en este campo.')
    if not value:
        raise ValidationError('Este campo no puede estar vacío.')
    if len(value) > 10:
        raise ValidationError('Máximo 10 caracteres permitidos.')
    if value[0] != value[0].upper():
        raise ValidationError('La primera letra debe estar en mayúscula.')

# Opciones de categoría
CATEGORIA_CHOICES = [
    ('Culinario', 'Culinario'),
    ('Medico', 'Medico'),
    ('Administrativo', 'Administrativo'),
    ('Mantenimiento', 'Mantenimiento'),
    ('Entretenimiento', 'Entretenimiento'),
    ('Personal Extra', 'Personal Extra'),
]

# Puestos ligados a categorías
PUESTO_CHOICES = {
    'Culinario': [
        ('Cocinero', 'Cocinero'), ('Mesero', 'Mesero'), ('Chef', 'Chef'), ('Barista', 'Barista'),
        ('Repostero', 'Repostero'), ('Bartender', 'Bartender'), ('Chef Ejecutivo', 'Chef Ejecutivo'),
        ('Chef de Partie', 'Chef de Partie'), ('Auxiliares de cocina', 'Auxiliares de cocina'),
        ('Maitre d’', 'Maitre d’'), ('Jefe de meseros', 'Jefe de meseros'), ('Mesero', 'Mesero'),
        ('Sous chef', 'Sous chef'), ('Sommelier', 'Sommelier'), ('Jefe de Alimentos', 'Jefe de Alimentos')
    ],
    'Administrativo': [
        ('Gerente', 'Gerente'), ('Cajero', 'Cajero')
    ],
    'Medico': [
        ('Enfermero', 'Enfermero'), ('Medico General', 'Medico General'), ('Medico en Jefe', 'Medico en Jefe'),
        ('Paramedico', 'Paramedico')
    ],
    'Entretenimiento': [
        ('Animadores', 'Animadores'), ("DJ's", "DJ's"), ('Musicos', 'Musicos'), ('Bailarines', 'Bailarines'),
        ('Guias Turisticos', 'Guias Turisticos')
    ],
    'Mantenimiento': [
        ('Plomero', 'Plomero'), ('Ingeniero', 'Ingeniero'), ('Conserje', 'Conserje'), ('Tecnico', 'Tecnico')
    ],
    'Personal Extra': [
        ('No Ocupado', 'No Ocupado'),
    ]
}

# Estado del personal
STATUS_CHOICES = [
    (1, 'Activo'),
    (2, 'Inactivo'),
    (3, 'De baja'),
]

class Personal(models.Model):
    id = models.AutoField(primary_key=True)  # Identificativo autoincremental

    nombre = models.CharField(max_length=10, validators=[validate_name])
    apellido = models.CharField(max_length=10, validators=[validate_name])

    salario = models.PositiveIntegerField(validators=[MaxValueValidator(99999999)])

    edad = models.PositiveIntegerField(validators=[MinValueValidator(21)], help_text='Mayor o igual 21 años')

    anios_experiencia = models.PositiveIntegerField()

    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)

    puesto = models.CharField(max_length=30)

    pStatus = models.IntegerField(choices=STATUS_CHOICES, default=1)

    # Campos unificados de amonestación (antes en modelo Amonestacion)
    amon_estado = models.BooleanField(default=False)
    amon_detalle = models.CharField(max_length=50, blank=True, null=True)

    def clean(self):
    # Edad debe ser mayor o igual a 21
     if self.edad < 21:
        raise ValidationError('La edad debe ser mayor o igual a 21 años.')

    # Años de experiencia no puede ser mayor a la mitad de la edad
     if self.anios_experiencia > (self.edad / 2):
        raise ValidationError('Los años de experiencia no pueden ser mayores a la mitad de la edad.')

    # Validar que el puesto esté en la lista correspondiente por categoria
     puestos_opciones = [p[0] for p in PUESTO_CHOICES.get(self.categoria, [])]

     if self.categoria == 'Personal Extra':
        if self.puesto not in puestos_opciones and self.puesto != 'No Ocupado':
            raise ValidationError('Puesto inválido para Personal Extra.')
     else:
        if self.puesto not in puestos_opciones:
            raise ValidationError(f'Puesto inválido para la categoría {self.categoria}.')

    def save(self, *args, **kwargs):
        # Forzar primer letra mayúscula en nombre y apellido
        self.nombre = self.nombre.capitalize()
        self.apellido = self.apellido.capitalize()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


# Nota: El modelo Amonestacion se ha consolidado dentro de Personal (amon_estado, amon_detalle)
# La tabla antigua `localRRHH_amonestacion` será migrada y luego eliminada mediante una migración.


# Modelos auxiliares para pools de generación (nombres, apellidos y salarios)
class MainPool(models.Model):
    """
    Pool unificado para nombres, apellidos y salarios.
    campo 'tipo' puede ser: 'nombre', 'apellido', 'salario'
    valor guarda el texto o número (como string). Para salarios se guarda el número en texto.
    """
    TIPO_CHOICES = [
        ('nombre', 'Nombre'),
        ('apellido', 'Apellido'),
        ('salario', 'Salario'),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    valor = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Main Pool'
        verbose_name_plural = 'Main Pools'
        indexes = [models.Index(fields=['tipo', 'valor'])]

    def __str__(self):
        return f"{self.tipo}: {self.valor}"


