from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from apps.administracion.models import Habitaciones
from apps.mantenimiento.mantenimiento.models import TareaMantenimiento, Ubicacion

class SolicitudMantenimientoHabitacionForm(forms.Form):
    """Formulario para crear una TareaMantenimiento asociada a una habitación."""

    habitacion = forms.ModelChoiceField(
        queryset=Habitaciones.objects.select_related('crucero').all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Habitación'
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
            except Habitaciones.DoesNotExist:
                pass

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
        if habitacion and not ubicacion:
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
        # Opcional: marcar la habitación en mantenimiento
        try:
            if habitacion.estado != 'maintenance':
                habitacion.estado = 'maintenance'
                habitacion.save(update_fields=['estado'])
        except Exception:
            pass
        return tarea
