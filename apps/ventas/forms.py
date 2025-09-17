from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import Cliente, Venta, DetalleVenta, VentaHabitacion
from apps.creador_embarcaciones.models import Embarcacion, Habitaciones

class ClienteForm(forms.ModelForm):
    """Formulario para crear y editar clientes"""
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'email', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

class VentaForm(forms.ModelForm):
    """Formulario para crear y editar ventas"""
    class Meta:
        model = Venta
        fields = ['cliente', 'tipo_venta', 'descripcion', 'estado', 'notas']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'tipo_venta': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class DetalleVentaForm(forms.ModelForm):
    """Formulario para los detalles de venta"""
    class Meta:
        model = DetalleVenta
        fields = ['concepto', 'cantidad', 'precio_unitario']
        widgets = {
            'concepto': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# Formset para manejar múltiples detalles de venta
DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    extra=1,
    can_delete=True,
    fields=['concepto', 'cantidad', 'precio_unitario']
)


class VentaHabitacionForm(forms.ModelForm):
    """Formulario para vender habitaciones"""
    
    class Meta:
        model = VentaHabitacion
        fields = [
            'habitacion', 'nombre_cliente', 'apellido_cliente', 
            'numero_pasaporte', 'precio_venta', 'fecha_checkin', 
            'fecha_checkout', 'notas'
        ]
        widgets = {
            'habitacion': forms.Select(attrs={'class': 'form-control'}),
            'nombre_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre del cliente'
            }),
            'apellido_cliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el apellido del cliente'
            }),
            'numero_pasaporte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de pasaporte'
            }),
            'precio_venta': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'fecha_checkin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'fecha_checkout': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notas adicionales (opcional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        embarcacion_id = kwargs.pop('embarcacion_id', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar habitaciones por embarcación si se proporciona
        if embarcacion_id:
            self.fields['habitacion'].queryset = Habitaciones.objects.filter(
                cubierta__embarcacion_id=embarcacion_id,
                estado='disponible'
            ).select_related('cubierta')
            
            # Obtener la embarcación para verificar si tiene ruta con fechas
            try:
                from apps.creador_embarcaciones.models import Embarcacion
                embarcacion = Embarcacion.objects.get(id=embarcacion_id)
                if embarcacion.ruta and embarcacion.ruta.fecha_inicio and embarcacion.ruta.fecha_fin:
                    # Si hay ruta con fechas, hacer los campos de fecha de solo lectura
                    self.fields['fecha_checkin'].widget.attrs['readonly'] = True
                    self.fields['fecha_checkout'].widget.attrs['readonly'] = True
                    self.fields['fecha_checkin'].help_text = f"Fecha automática de la ruta: {embarcacion.ruta.titulo}"
                    self.fields['fecha_checkout'].help_text = f"Fecha automática de la ruta: {embarcacion.ruta.titulo}"
            except:
                pass
        else:
            self.fields['habitacion'].queryset = Habitaciones.objects.filter(
                estado='disponible'
            ).select_related('cubierta', 'cubierta__embarcacion')
        
        # Personalizar las opciones del campo habitación
        self.fields['habitacion'].empty_label = "-- Seleccionar habitación --"
        
        # Hacer algunos campos opcionales
        self.fields['notas'].required = False
        self.fields['fecha_checkin'].required = False
        self.fields['fecha_checkout'].required = False
    
    def clean_numero_pasaporte(self):
        """Validar que el número de pasaporte no esté vacío y tenga formato válido"""
        numero_pasaporte = self.cleaned_data.get('numero_pasaporte')
        if not numero_pasaporte:
            raise ValidationError("El número de pasaporte es obligatorio.")
        
        # Validar formato básico (al menos 6 caracteres alfanuméricos)
        if len(numero_pasaporte) < 6:
            raise ValidationError("El número de pasaporte debe tener al menos 6 caracteres.")
        
        return numero_pasaporte.upper()
    
    def clean_precio_venta(self):
        """Validar que el precio de venta sea mayor que cero"""
        precio_venta = self.cleaned_data.get('precio_venta')
        if precio_venta and precio_venta <= 0:
            raise ValidationError("El precio de venta debe ser mayor que cero.")
        return precio_venta
    
    def clean(self):
        """Validaciones adicionales del formulario"""
        cleaned_data = super().clean()
        fecha_checkin = cleaned_data.get('fecha_checkin')
        fecha_checkout = cleaned_data.get('fecha_checkout')
        habitacion = cleaned_data.get('habitacion')
        
        # Validar fechas si ambas están presentes
        if fecha_checkin and fecha_checkout:
            if fecha_checkout <= fecha_checkin:
                raise ValidationError("La fecha de checkout debe ser posterior a la fecha de checkin.")
        
        # Validar disponibilidad de habitación para las fechas seleccionadas
        if habitacion and fecha_checkin:
            ventas_existentes = VentaHabitacion.objects.filter(
                habitacion=habitacion,
                fecha_checkin=fecha_checkin,
                estado__in=['reservada', 'ocupada']
            )
            
            if self.instance.pk:
                ventas_existentes = ventas_existentes.exclude(pk=self.instance.pk)
            
            if ventas_existentes.exists():
                raise ValidationError(f"La habitación {habitacion.numero} ya está reservada para la fecha {fecha_checkin}.")
        
        return cleaned_data


class FiltroEmbarcacionForm(forms.Form):
    """Formulario para filtrar habitaciones por embarcación"""
    embarcacion = forms.ModelChoiceField(
        queryset=Embarcacion.objects.all(),
        empty_label="-- Seleccionar embarcación --",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar embarcaciones que tengan habitaciones
        self.fields['embarcacion'].queryset = Embarcacion.objects.filter(
            cubiertas__habitaciones__isnull=False
        ).distinct()
