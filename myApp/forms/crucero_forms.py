from django import forms
from ..models import Crucero

class CruceroForm(forms.ModelForm):
    class Meta:
        model = Crucero
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'style': 'text-transform: uppercase;'}),
            # ...existing widgets...
        }

class CruceroCreateForm(forms.ModelForm):
    class Meta:
        model = Crucero
        fields = [
            'nombre', 'tipo_crucero', 'codigo_identificacion', 'fecha_botadura',
            'fecha_adquisicion', 'capacidad_pasajeros', 'capacidad_tripulacion',
            'tonelaje', 'eslora', 'manga', 'puntal', 'bandera', 'puerto_base',
            'estado_operativo', 'descripcion', 'modelo_motor', 'velocidad_maxima',
            'ultimo_mantenimiento', 'proximo_mantenimiento', 'tipo_combustible',
            'consumo_combustible'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'style': 'text-transform: uppercase;'}),
            # ...existing widgets...
        }
