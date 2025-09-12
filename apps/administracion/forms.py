from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from apps.administracion.models import Habitaciones, Cubierta
from apps.mantenimiento.mantenimiento.models import TareaMantenimiento, Ubicacion

class SolicitudMantenimientoHabitacionForm(forms.Form):
    """Formulario para crear una TareaMantenimiento asociada a una habitación."""

    habitacion = forms.ModelChoiceField(
        queryset=Habitaciones.objects.select_related('crucero').all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Habitación'
    )
    cambiar_habitacion = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'cambiar_habitacion'}),
        label='¿Cambiar usuario a otra habitación?'
    )
    habitacion_reemplazo = forms.ModelChoiceField(
        queryset=Habitaciones.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'habitacion_reemplazo', 'disabled': True}),
        label='Habitación de reemplazo'
    )
    titulo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título de la solicitud'}),
        label='Título'
    )
    descripcion = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describa el problema o la necesidad'}),
        label='Descripción'
    )
    tipo = forms.ChoiceField(
        choices=TareaMantenimiento.TIPOS_TAREA,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Tipo de tarea'
    )
    prioridad = forms.ChoiceField(
        choices=TareaMantenimiento.PRIORIDADES,
        initial='media',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Prioridad'
    )
    fecha_programada = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        label='Fecha programada'
    )
    tiempo_estimado_horas = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=Decimal('0.5'),
        max_value=Decimal('24'),
        initial=Decimal('1.0'),
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.25'}),
        label='Tiempo estimado (horas)'
    )
    ubicacion = forms.ModelChoiceField(
        queryset=Ubicacion.objects.select_related('crucero').all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Ubicación (opcional)'
    )

    def __init__(self, *args, **kwargs):
        habitacion_inicial = kwargs.pop('habitacion', None)
        super().__init__(*args, **kwargs)
        # Si llega una habitación preseleccionada, fijarla por defecto
        if habitacion_inicial is not None:
            self.fields['habitacion'].initial = habitacion_inicial.pk if hasattr(habitacion_inicial, 'pk') else habitacion_inicial
            # Filtrar ubicaciones por el mismo crucero de la habitación
            try:
                hab = habitacion_inicial if hasattr(habitacion_inicial, 'pk') else Habitaciones.objects.get(pk=habitacion_inicial)
                self.fields['ubicacion'].queryset = Ubicacion.objects.filter(crucero=hab.crucero)
                # Configurar habitaciones de reemplazo disponibles
                self._configurar_habitaciones_reemplazo(hab)
            except Habitaciones.DoesNotExist:
                pass
        else:
            # Si no hay habitación inicial, configurar queryset vacío para habitaciones de reemplazo
            self.fields['habitacion_reemplazo'].queryset = Habitaciones.objects.none()

    def _configurar_habitaciones_reemplazo(self, habitacion_original):
        """Configura las habitaciones de reemplazo disponibles del mismo tipo y crucero."""
        habitaciones_disponibles = Habitaciones.objects.filter(
            crucero=habitacion_original.crucero,
            tipo=habitacion_original.tipo,
            estado='free'
        ).exclude(pk=habitacion_original.pk)
        
        self.fields['habitacion_reemplazo'].queryset = habitaciones_disponibles

    def clean_fecha_programada(self):
        fecha = self.cleaned_data['fecha_programada']
        # Permitir programaciones futuras o inmediatas según validación del modelo
        if fecha < timezone.now():
            raise ValidationError('La fecha programada no puede estar en el pasado.')
        return fecha

    def clean(self):
        cleaned = super().clean()
        habitacion = cleaned.get('habitacion')
        ubicacion = cleaned.get('ubicacion')
        cambiar_habitacion = cleaned.get('cambiar_habitacion')
        habitacion_reemplazo = cleaned.get('habitacion_reemplazo')
        
        # Validaciones para el cambio de habitación
        if cambiar_habitacion and not habitacion_reemplazo:
            raise ValidationError('Debe seleccionar una habitación de reemplazo si desea cambiar al usuario.')
        
        if habitacion_reemplazo and not cambiar_habitacion:
            raise ValidationError('Debe marcar la opción de cambiar habitación si selecciona una habitación de reemplazo.')
        
        if habitacion and habitacion_reemplazo and habitacion.pk == habitacion_reemplazo.pk:
            raise ValidationError('La habitación de reemplazo debe ser diferente a la habitación original.')
        
        if habitacion and ubicacion and not ubicacion:
            # Intento de deducir la ubicación automáticamente:
            # 1) Buscar ubicaciones del mismo crucero cuya descripción contenga el identificador de la habitación
            posibles = Ubicacion.objects.filter(crucero=habitacion.crucero, descripcion__icontains=str(habitacion.nombre_usuario))
            if not posibles.exists():
                # 2) Intentar por coincidencia en la descripción con el campo ubicacion (texto) de la habitación
                if habitacion.ubicacion:
                    posibles = Ubicacion.objects.filter(crucero=habitacion.crucero, descripcion__icontains=str(habitacion.ubicacion))
            if posibles.count() == 1:
                cleaned['ubicacion'] = posibles.first()
            elif posibles.count() > 1:
                raise ValidationError('Se encontraron múltiples ubicaciones posibles. Seleccione una explícitamente.')
            else:
                raise ValidationError('No se pudo inferir la ubicación. Seleccione una explícitamente.')
        return cleaned

    def save(self, usuario=None):
        data = self.cleaned_data
        habitacion = data['habitacion']
        cambiar_habitacion = data.get('cambiar_habitacion', False)
        habitacion_reemplazo = data.get('habitacion_reemplazo')
        
        tarea = TareaMantenimiento.objects.create(
            titulo=data['titulo'],
            descripcion=data['descripcion'],
            tipo=data['tipo'],
            prioridad=data['prioridad'],
            ubicacion=data['ubicacion'],
            tipo_crucero=habitacion.crucero.tipo,
            crucero=habitacion.crucero,
            fecha_programada=data['fecha_programada'],
            tiempo_estimado_horas=data['tiempo_estimado_horas'],
            creado_por=usuario,
        )
        
        # Marcar la habitación en mantenimiento
        try:
            if habitacion.estado != 'maintenance':
                habitacion.estado = 'maintenance'
                habitacion.save(update_fields=['estado'])
        except Exception:
            pass
        
        # Si se solicita cambio de habitación, mover al usuario
        if cambiar_habitacion and habitacion_reemplazo:
            try:
                # Verificar que la habitación de reemplazo esté disponible
                if habitacion_reemplazo.estado == 'free':
                    # Mover el usuario a la nueva habitación
                    habitacion_reemplazo.nombre_usuario = habitacion.nombre_usuario
                    habitacion_reemplazo.estado = 'occupied'
                    habitacion_reemplazo.save(update_fields=['nombre_usuario', 'estado'])
                    
                    # Limpiar la habitación original
                    habitacion.nombre_usuario = 'free'
                    habitacion.save(update_fields=['nombre_usuario'])
            except Exception as e:
                # Si hay error en el cambio, revertir el estado de la habitación original
                habitacion.estado = 'occupied'
                habitacion.save(update_fields=['estado'])
                raise ValidationError(f'Error al cambiar la habitación: {str(e)}')
        
        return tarea

class HabitacionForm(forms.ModelForm):
    """Formulario para registrar habitaciones."""
    
    class Meta:
        model = Habitaciones
        fields = [
            'cubierta', 'tipo', 'id', 'precio_base', 'ubicacion', 'aumento_ubicacion',
            'estado', 'espacio_area', 'nombre_usuario', 'capacidad', 'vista_mar',
            'aumento_vista_mar', 'ultimo_mantenimiento', 'proximo_mantenimiento'
        ]
        widgets = {
            'cubierta': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'id_room': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'required': True,
                'placeholder': 'ID único de la habitación'
            }),
            'precio_base': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '25',
                'required': True,
                'placeholder': 'Ej: A-101, B-205'
            }),
            'aumento_ubicacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'required': True,
                'placeholder': 'Porcentaje de aumento por la ubicación'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'espacio_area': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'required': True,
                'placeholder': 'En m²'
            }),
            'nombre_usuario': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '25',
                'required': True,
                'placeholder': 'Nombre del usuario'
            }),
            'capacidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'required': True,
                'placeholder': 'Número de personas'
            }),
            'vista_mar': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'aumento_vista_mar': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'required': True,
                'placeholder': 'Porcentaje de aumento por vista al mar'
            }),
            'ultimo_mantenimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            }),
            'proximo_mantenimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            })
        }
        labels = {
            'cubierta': 'Cubierta',
            'tipo': 'Tipo de habitación',
            'id_room': 'ID de habitación',
            'precio_base': 'Precio base ($)',
            'ubicacion': 'Ubicación',
            'aumento_ubicacion': 'Porcentaje de aumento por la ubicación',
            'estado': 'Estado',
            'espacio_area': 'Área (m²)',
            'nombre_usuario': 'Nombre del usuario',
            'capacidad': 'Capacidad (personas)',
            'vista_mar': 'Vista al mar',
            'aumento_vista_mar': 'Porcentaje de aumento por vista al mar',
            'ultimo_mantenimiento': 'Último mantenimiento',
            'proximo_mantenimiento': 'Próximo mantenimiento'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar cubiertas que tengan área disponible
        self.fields['cubierta'].queryset = Cubierta.objects.filter(
            area_disponible__gt=0
        ).select_related('crucero')
        
        # Establecer valores por defecto
        self.fields['estado'].initial = 'free'
        self.fields['vista_mar'].initial = False
        self.fields['aumento_ubicacion'].initial = 1.0
        self.fields['aumento_vista_mar'].initial = 1.0

    def clean_capacidad(self):
        capacidad = self.cleaned_data.get('capacidad')
        espacio_area = self.cleaned_data.get('espacio_area')
        
        if capacidad and espacio_area:
            # Validar que la capacidad no exceda el límite de 1 persona por cada 0.4645 m²
            capacidad_maxima = int(espacio_area / Decimal('0.4645'))
            if capacidad > capacidad_maxima:
                raise ValidationError(
                    f'La capacidad máxima permitida es {capacidad_maxima} personas '
                    f'para un área de {espacio_area} m² (1 persona por cada 0.4645 m²).'
                )
        
        return capacidad

    def clean_espacio_area(self):
        espacio_area = self.cleaned_data.get('espacio_area')
        cubierta = self.cleaned_data.get('cubierta')
        
        if espacio_area and cubierta:
            # Verificar que el área de la habitación no exceda el área disponible de la cubierta
            if espacio_area > cubierta.area_disponible:
                raise ValidationError(
                    f'El área de la habitación ({espacio_area} m²) excede el área disponible '
                    f'de la cubierta ({cubierta.area_disponible} m²).'
                )
        
        return espacio_area

    def clean_proximo_mantenimiento(self):
        proximo_mantenimiento = self.cleaned_data.get('proximo_mantenimiento')
        ultimo_mantenimiento = self.cleaned_data.get('ultimo_mantenimiento')
        
        
        if proximo_mantenimiento <= ultimo_mantenimiento:
            raise ValidationError(
                'La fecha del próximo mantenimiento debe ser posterior '
                'a la fecha del último mantenimiento.'
            )
        
        return proximo_mantenimiento

    def clean_id(self):
        id_habitacion = self.cleaned_data.get('id')
        
        if id_habitacion:
            # Verificar que el ID sea único
            queryset = Habitaciones.objects.filter(id=id_habitacion)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError(
                    f'Ya existe una habitación con el ID "{id_habitacion}". '
                    'Elija un ID diferente.'
                )
        
        return id_habitacion

    def clean_aumento_ubicacion(self):
        aumento_ubicacion = self.cleaned_data.get('aumento_ubicacion')
        
        if aumento_ubicacion is not None and aumento_ubicacion < 0:
            raise ValidationError(
                'El factor de aumento por ubicación no puede ser negativo.'
            )
        
        return aumento_ubicacion

    def clean_aumento_vista_mar(self):
        aumento_vista_mar = self.cleaned_data.get('aumento_vista_mar')
        
        if aumento_vista_mar is not None and aumento_vista_mar < 0:
            raise ValidationError(
                'El factor de aumento por vista al mar no puede ser negativo.'
            )
        
        return aumento_vista_mar

    def clean(self):
        """Validación general del formulario."""
        cleaned_data = super().clean()
        
        # Verificar que todos los campos requeridos estén presentes
        campos_requeridos = [
            'cubierta', 'tipo', 'id', 'precio_base', 'ubicacion', 
            'aumento_ubicacion', 'estado', 'espacio_area', 'nombre_usuario', 
            'capacidad', 'ultimo_mantenimiento', 'proximo_mantenimiento'
        ]
        
        for campo in campos_requeridos:
            if campo not in cleaned_data or cleaned_data[campo] is None:
                raise ValidationError(f'El campo {self.fields[campo].label} es requerido.')
        
        # Validación adicional para asegurar coherencia de datos
        if cleaned_data.get('precio_base') and cleaned_data.get('precio_base') <= 0:
            raise ValidationError('El precio base debe ser mayor a 0.')
        
        if cleaned_data.get('capacidad') and cleaned_data.get('capacidad') <= 0:
            raise ValidationError('La capacidad debe ser mayor a 0.')
        
        return cleaned_data
