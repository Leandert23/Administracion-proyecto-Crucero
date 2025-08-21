from django import forms
from .models import Crucero, Instalacion


class CruceroForm(forms.ModelForm):
    class Meta:
        model = Crucero
        # Incluir todos los campos del modelo para poder editar/mostrar todo
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'crucero-form__input'}),
            'tipo_crucero': forms.Select(attrs={'class': 'crucero-form__input'}),
            'codigo_identificacion': forms.TextInput(attrs={'class': 'crucero-form__input'}),
            'fecha_botadura': forms.DateInput(attrs={'type': 'date', 'class': 'crucero-form__input'}),
            'fecha_adquisicion': forms.DateInput(attrs={'type': 'date', 'class': 'crucero-form__input'}),
            'capacidad_pasajeros': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'capacidad_tripulacion': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'tonelaje': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'puntal': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'eslora': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'manga': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'bandera': forms.TextInput(attrs={'class': 'crucero-form__input'}),
            'puerto_base': forms.TextInput(attrs={'class': 'crucero-form__input'}),
            'estado_operativo': forms.Select(attrs={'class': 'crucero-form__input'}),
            'descripcion': forms.Textarea(attrs={'class': 'crucero-form__input'}),
            'modelo_motor': forms.TextInput(attrs={'class': 'crucero-form__input'}),
            'velocidad_maxima': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'ultimo_mantenimiento': forms.DateInput(attrs={'type': 'date', 'class': 'crucero-form__input'}),
            'proximo_mantenimiento': forms.DateInput(attrs={'type': 'date', 'class': 'crucero-form__input'}),
            'tipo_combustible': forms.Select(attrs={'class': 'crucero-form__input'}),
            'consumo_combustible': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'fecha_vencimiento_seguro': forms.DateInput(attrs={'type': 'date', 'class': 'crucero-form__input'}),
            'seguro_vigente': forms.CheckboxInput(attrs={'class': 'crucero-form__checkbox'}),
            # File/Image fields will use default ClearableFileInput; add classes if desired
            'certificado_sanitario': forms.ClearableFileInput(attrs={'class': 'crucero-form__input'}),
            'certificado_seguridad': forms.ClearableFileInput(attrs={'class': 'crucero-form__input'}),
            'foto_barco': forms.ClearableFileInput(attrs={'class': 'crucero-form__input'}),
            'plano_barco': forms.ClearableFileInput(attrs={'class': 'crucero-form__input'}),
        }


class CruceroCreateForm(forms.ModelForm):
    """Formulario para crear un crucero: solo datos básicos y técnicos.
    Los demás campos (documentación, multimedia, etc.) se dejarán en null/default
    y podrán editarse posteriormente desde la vista de edición completa.
    """
    class Meta:
        model = Crucero
        fields = [
            'nombre',
            'tipo_crucero',
            'codigo_identificacion',
            'fecha_botadura',
            'fecha_adquisicion',
            'capacidad_pasajeros',
            'capacidad_tripulacion',
            'tonelaje',
            'eslora',
            'manga',
            'puntal',
            'bandera',
            'puerto_base',
            'estado_operativo',
            'descripcion',
            'modelo_motor',
            'velocidad_maxima',
            'ultimo_mantenimiento',
            'proximo_mantenimiento',
            'tipo_combustible',
            'consumo_combustible',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'crucero-form__input'}),
            'tipo_crucero': forms.Select(attrs={'class': 'crucero-form__input'}),
            'codigo_identificacion': forms.TextInput(attrs={'class': 'crucero-form__input'}),
            'fecha_botadura': forms.DateInput(attrs={'type': 'date', 'class': 'crucero-form__input'}),
            'fecha_adquisicion': forms.DateInput(attrs={'type': 'date', 'class': 'crucero-form__input'}),
            'capacidad_pasajeros': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'capacidad_tripulacion': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'tonelaje': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'eslora': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'manga': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'puntal': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'bandera': forms.TextInput(attrs={'class': 'crucero-form__input'}),
            'puerto_base': forms.TextInput(attrs={'class': 'crucero-form__input'}),
            'estado_operativo': forms.Select(attrs={'class': 'crucero-form__input'}),
            'descripcion': forms.Textarea(attrs={'class': 'crucero-form__input'}),
            'modelo_motor': forms.TextInput(attrs={'class': 'crucero-form__input'}),
            'velocidad_maxima': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
            'ultimo_mantenimiento': forms.DateInput(attrs={'type': 'date', 'class': 'crucero-form__input'}),
            'proximo_mantenimiento': forms.DateInput(attrs={'type': 'date', 'class': 'crucero-form__input'}),
            'tipo_combustible': forms.Select(attrs={'class': 'crucero-form__input'}),
            'consumo_combustible': forms.NumberInput(attrs={'class': 'crucero-form__input'}),
        }


class InstalacionForm(forms.ModelForm):
    class Meta:
        model = Instalacion
        fields = ['nombre', 'tipo', 'capacidad', 'ubicacion', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
