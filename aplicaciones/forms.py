from django import forms
from .models import Medico, Paciente, Inventario, Solicitudmedicamento, Instrumentaria, Insumo

class MedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['nombres', 'apellido', 'especialidad', 'telefono', 'correo_electronico']
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombres', 'primer_apellido', 'segundo_apellido', 'fechade_nacimiento', 'documento_identidad', 'telefono', 'direccion', 'correo_electronico',  'sexo', 'motivo_consulta', 'descripcion_consulta', 'antecedentes_medicos', 'alergias', 'medicamentos_actuales', 'historial_familiar']
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'primer_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'segundo_apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'documento_identidad': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'motivo_consulta': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion_consulta': forms.Textarea(attrs={'class': 'form-control'}),
            'antecedentes_medicos': forms.Textarea(attrs={'class': 'form-control'}),
            'alergias': forms.Textarea(attrs={'class': 'form-control'}),
            'medicamentos_actuales': forms.Textarea(attrs={'class': 'form-control'}),
            'historial_familiar': forms.Textarea(attrs={'class': 'form-control'}),
            'correo_electronico': forms.EmailInput(attrs={'class': 'form-control'}),
            'fechade_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
        }

class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['insumo', 'cantidad']
        widgets = {
            'insumo': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SolicitudMedicamentoForm(forms.ModelForm):
    class Meta:
        model = Solicitudmedicamento
        fields = ['insumo', 'cantidad']
        widgets = {
            'insumo': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
        }
class InstrumentariaForm(forms.ModelForm):
    class Meta:
        model = Instrumentaria
        fields = ['nombre', 'descripcion', 'fecha_adquisicion', 'estado', 'mantenimiento_programado']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'fecha_adquisicion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'mantenimiento_programado': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ['nombre', 'descripcion', 'fecha_vencimiento']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class ModificarCuartoForm(forms.Form):
    numero_cuarto = forms.IntegerField(label='Número de Cuarto', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    nuevo_estado = forms.ChoiceField(label='Nuevo Estado', choices=[('disponible', 'Disponible'), ('ocupado', 'Ocupado'), ('mantenimiento', 'Mantenimiento')], widget=forms.Select(attrs={'class': 'form-control'}))
    

