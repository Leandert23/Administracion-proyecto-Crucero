from django import forms
from .models import Proveedores, Material

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedores
        fields = ['name', 'service_or_product', 'categorie', 'contact', 'sucursal', 'tipo', 'subtipo']
