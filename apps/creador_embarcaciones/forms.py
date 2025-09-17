from django import forms
from django.core.exceptions import ValidationError
from .models import Dia, Embarcacion, Ruta, TipoEmbarcacion


class EmbarcacionForm(forms.ModelForm):
    """
    Formulario para crear y editar embarcaciones
    """
    # Campo adicional para añadir nuevo tipo de embarcación
    nuevo_tipo = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el nombre del nuevo tipo...'
        }),
        label="Nuevo tipo de embarcación"
    )

    # Checkbox para indicar si se quiere añadir un nuevo tipo
    agregar_nuevo_tipo = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label="¿Agregar nuevo tipo?"
    )

    class Meta:
        model = Embarcacion
        fields = [
            'nombre', 'tipo', 'nuevo_tipo', 'agregar_nuevo_tipo',
            'fecha_botadura', 'fecha_adquisicion',
            'capacidad_pasajeros', 'capacidad_tripulacion',
            'tonelaje', 'eslora', 'manga', 'altura', 'numero_cubiertas',
            'maximo_habitacion_pasajeros', 'maximo_habitacion_tripulantes',
            'bandera', 'puerto_base', 'estado_operativo', 'descripcion',
            'modelo_motor', 'velocidad_maxima',
            'ultimo_mantenimiento', 'proximo_mantenimiento',
            'tipo_combustible', 'consumo_combustible', 'capacidad_combustible',
            'ruta'
        ]
        widgets = {
            'fecha_botadura': forms.DateInput(attrs={
                'type': 'date',
                'placeholder': 'DD/MM/YYYY o YYYY-MM-DD'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha_adquisicion': forms.DateInput(attrs={
                'type': 'date',
                'placeholder': 'DD/MM/YYYY o YYYY-MM-DD'
            }),
            'ultimo_mantenimiento': forms.DateInput(attrs={
                'type': 'date',
                'placeholder': 'DD/MM/YYYY o YYYY-MM-DD'
            }),
            'proximo_mantenimiento': forms.DateInput(attrs={
                'type': 'date',
                'placeholder': 'DD/MM/YYYY o YYYY-MM-DD'
            }),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'estado_operativo': forms.Select(attrs={'class': 'form-control'}),
            'tipo_combustible': forms.Select(attrs={'class': 'form-control'}),
            'ruta': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que algunos campos no sean obligatorios inicialmente
        self.fields['ruta'].required = False
        self.fields['descripcion'].required = False

        # Configurar el campo tipo con opciones disponibles
        tipos_existentes = TipoEmbarcacion.objects.all()
        choices = [('', '-- Seleccionar tipo --')]
        choices.extend([(tipo.pk, tipo.nombre) for tipo in tipos_existentes])
        self.fields['tipo'].choices = choices
        self.fields['tipo'].required = False  # Será requerido condicionalmente

        # Configurar campos de nuevo tipo (visibilidad manejada por JavaScript)
        # El campo nuevo_tipo se oculta inicialmente por JavaScript
        # El checkbox se muestra si hay tipos existentes

        # Agregar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.Select) and not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'


    def clean_fecha_adquisicion(self):
        """
        Validar que la fecha de adquisición no sea posterior a hoy
        """
        fecha_adquisicion = self.cleaned_data.get('fecha_adquisicion')
        if fecha_adquisicion:
            from datetime import date
            today = date.today()
            if fecha_adquisicion > today:
                raise ValidationError("La fecha de adquisición no puede ser futura.")
        return fecha_adquisicion

    def clean_fecha_botadura(self):
        """
        Validar que la fecha de botadura no sea posterior a la fecha de adquisición
        """
        fecha_botadura = self.cleaned_data.get('fecha_botadura')
        fecha_adquisicion = self.cleaned_data.get('fecha_adquisicion')

        if fecha_botadura and fecha_adquisicion and fecha_botadura > fecha_adquisicion:
            raise ValidationError("La fecha de botadura no puede ser posterior a la fecha de adquisición.")
        return fecha_botadura

    def clean_proximo_mantenimiento(self):
        """
        Validar que el próximo mantenimiento sea posterior al último mantenimiento
        """
        ultimo_mantenimiento = self.cleaned_data.get('ultimo_mantenimiento')
        proximo_mantenimiento = self.cleaned_data.get('proximo_mantenimiento')

        if ultimo_mantenimiento and proximo_mantenimiento and proximo_mantenimiento <= ultimo_mantenimiento:
            raise ValidationError("El próximo mantenimiento debe ser posterior al último mantenimiento.")
        return proximo_mantenimiento

    def clean_consumo_combustible(self):
        """
        Validar que el consumo de combustible sea mayor que cero
        """
        consumo = self.cleaned_data.get('consumo_combustible')
        if consumo and consumo <= 0:
            raise ValidationError("El consumo de combustible debe ser mayor que cero.")
        return consumo

    def clean_capacidad_combustible(self):
        """
        Validar que la capacidad de combustible sea mayor que cero
        """
        capacidad = self.cleaned_data.get('capacidad_combustible')
        if capacidad and capacidad <= 0:
            raise ValidationError("La capacidad de combustible debe ser mayor que cero.")
        return capacidad

    def clean_velocidad_maxima(self):
        """
        Validar que la velocidad máxima sea razonable (mayor que cero y menor que 100 nudos)
        """
        velocidad = self.cleaned_data.get('velocidad_maxima')
        if velocidad and (velocidad <= 0 or velocidad > 100):
            raise ValidationError("La velocidad máxima debe estar entre 0.1 y 100 nudos.")
        return velocidad

    def clean(self):
        """
        Validaciones generales del formulario
        """
        cleaned_data = super().clean()
        capacidad_pasajeros = cleaned_data.get('capacidad_pasajeros')
        maximo_habitaciones = cleaned_data.get('maximo_habitacion_pasajeros')

        if capacidad_pasajeros and maximo_habitaciones and maximo_habitaciones > capacidad_pasajeros:
            raise ValidationError("El número máximo de habitaciones para pasajeros no puede ser mayor que la capacidad de pasajeros.")

        # Validación del tipo de embarcación
        tipo = cleaned_data.get('tipo')
        agregar_nuevo_tipo = cleaned_data.get('agregar_nuevo_tipo')
        nuevo_tipo = cleaned_data.get('nuevo_tipo')

        if agregar_nuevo_tipo:
            # Si se quiere añadir un nuevo tipo, validar que se proporcione el nombre
            if not nuevo_tipo:
                raise ValidationError("Debe proporcionar un nombre para el nuevo tipo de embarcación.")
            # Verificar que el nuevo tipo no exista ya
            if TipoEmbarcacion.objects.filter(nombre__iexact=nuevo_tipo).exists():
                raise ValidationError(f"El tipo de embarcación '{nuevo_tipo}' ya existe.")
        else:
            # Si no se quiere añadir nuevo tipo, debe seleccionar uno existente
            if not tipo:
                tipos_existentes = TipoEmbarcacion.objects.exists()
                if tipos_existentes:
                    raise ValidationError("Debe seleccionar un tipo de embarcación existente o marcar la opción para añadir uno nuevo.")
                else:
                    raise ValidationError("No hay tipos de embarcación registrados. Debe añadir un nuevo tipo.")

        return cleaned_data

    def save(self, commit=True):
        """
        Guardar el formulario, creando un nuevo tipo si es necesario
        """
        instance = super().save(commit=False)

        # Manejar la creación de nuevo tipo de embarcación
        agregar_nuevo_tipo = self.cleaned_data.get('agregar_nuevo_tipo')
        nuevo_tipo = self.cleaned_data.get('nuevo_tipo')

        if agregar_nuevo_tipo and nuevo_tipo:
            # Crear el nuevo tipo de embarcación
            tipo_embarcacion = TipoEmbarcacion.objects.create(
                nombre=nuevo_tipo,
                descripcion=f"Tipo de embarcación creado automáticamente al registrar {instance.nombre}"
            )
            instance.tipo = tipo_embarcacion

        if commit:
            instance.save()

        return instance


class RutaForm(forms.ModelForm):
    """
    Formulario para crear y editar rutas
    """

    class Meta:
        model = Ruta
        fields = ['titulo', 'numero_dias', 'fecha_inicio', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'DD/MM/YYYY'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean_numero_dias(self):
        """
        Validar que el número de días sea mayor que cero
        """
        numero_dias = self.cleaned_data.get('numero_dias')
        if numero_dias and numero_dias <= 0:
            raise ValidationError("El número de días debe ser mayor que cero.")
        return numero_dias

    def clean_fecha_inicio(self):
        """
        Validar que la fecha de inicio no sea anterior a hoy
        """
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        if fecha_inicio:
            from datetime import date
            today = date.today()
            if fecha_inicio < today:
                raise ValidationError("La fecha de inicio no puede ser anterior a hoy.")
        return fecha_inicio


class DiaForm(forms.ModelForm):
    """
    Formulario para crear y editar días de una ruta
    """

    class Meta:
        model = Dia
        fields = [
            'titulo_dia', 'ubicacion', 'descripcion',
            'hora_llegada', 'hora_salida', 'notas_especiales'
        ]
        widgets = {
            'titulo_dia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Día de navegación por el Caribe'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Puerto de Cartagena, Colombia'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe las características principales del día...'
            }),
            'hora_llegada': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'hora_salida': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'notas_especiales': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Información adicional importante...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer algunos campos opcionales inicialmente
        self.fields['descripcion'].required = False
        self.fields['notas_especiales'].required = False
        # Las horas ya tienen valores por defecto, así que no son requeridas

    def clean(self):
        """
        Validaciones del formulario
        """
        cleaned_data = super().clean()
        hora_llegada = cleaned_data.get('hora_llegada')
        hora_salida = cleaned_data.get('hora_salida')

        # Validar que la hora de salida sea posterior a la hora de llegada
        if hora_llegada and hora_salida and hora_salida <= hora_llegada:
            raise forms.ValidationError("La hora de salida debe ser posterior a la hora de llegada.")

        return cleaned_data

