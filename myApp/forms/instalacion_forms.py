from django import forms
from ..models import Instalacion

class InstalacionForm(forms.ModelForm):
    class Meta:
        model = Instalacion
        fields = ['nombre', 'tipo', 'capacidad', 'ubicacion', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'style': 'text-transform: uppercase;'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
