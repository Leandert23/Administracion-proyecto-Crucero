from django import forms
from django.forms import inlineformset_factory
from .models import Cliente, Venta, DetalleVenta

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
            'tipo_venta': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DetalleVentaForm(forms.ModelForm):
    """Formulario para los detalles de venta"""
    class Meta:
        model = DetalleVenta
        fields = ['concepto', 'cantidad', 'precio_unitario']
        widgets = {
            'concepto': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
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
