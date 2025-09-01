from django import forms
from django.contrib.auth.models import User
from .models import (
    Ubicacion, Producto, InventarioProducto, Equipo, TareaMantenimiento, 
    ReporteIncidente, TipoCrucero, TipoEquipo, CategoriaProducto, Personal, AsignacionPersonal, ProductoUtilizado
)


class UbicacionForm(forms.ModelForm):
    """Formulario para ubicaciones"""
    class Meta:
        model = Ubicacion
        fields = ['cubierta', 'uso', 'identificador', 'numero', 'descripcion', 'activa']
        widgets = {
            'cubierta': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '18'}),
            'uso': forms.Select(attrs={'class': 'form-control'}),
            'identificador': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '1'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_identificador(self):
        identificador = self.cleaned_data['identificador']
        if identificador and not identificador.isalpha():
            raise forms.ValidationError('El identificador debe ser una letra.')
        return identificador.upper()
    
    def clean_numero(self):
        numero = self.cleaned_data['numero']
        if numero and not numero.isdigit():
            raise forms.ValidationError('El número debe ser un valor numérico.')
        return numero


class ProductoForm(forms.ModelForm):
    """Formulario para productos"""
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'unidad', 'descripcion', 'notas', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'unidad': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class InventarioProductoForm(forms.ModelForm):
    """Formulario para inventario de productos"""
    class Meta:
        model = InventarioProducto
        fields = ['cantidad_requerida', 'stock_minimo', 'stock_actual', 'ubicacion']
        widgets = {
            'cantidad_requerida': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'ubicacion': forms.Select(attrs={'class': 'form-control'}),
        }


class EquipoForm(forms.ModelForm):
    """Formulario para equipos"""
    class Meta:
        model = Equipo
        fields = ['codigo', 'nombre', 'tipo_equipo', 'ubicacion', 'estado', 'fecha_instalacion', 'proxima_revision', 'observaciones']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_equipo': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_instalacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proxima_revision': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class TareaMantenimientoForm(forms.ModelForm):
    """Formulario para tareas de mantenimiento"""
    class Meta:
        model = TareaMantenimiento
        fields = ['titulo', 'descripcion', 'tipo', 'prioridad', 'equipo', 'ubicacion', 'tipo_crucero', 'asignado_a', 'fecha_programada', 'tiempo_estimado_horas', 'observaciones']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'equipo': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion': forms.Select(attrs={'class': 'form-control'}),
            'tipo_crucero': forms.Select(attrs={'class': 'form-control'}),
            'asignado_a': forms.Select(attrs={'class': 'form-control'}),
            'fecha_programada': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'tiempo_estimado_horas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0.5'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar listas
        self.fields['asignado_a'].required = False
        self.fields['equipo'].queryset = Equipo.objects.filter(estado__in=['operativo', 'mantenimiento'])
        self.fields['ubicacion'].queryset = Ubicacion.objects.filter(activa=True)
        self.fields['tipo_crucero'].queryset = TipoCrucero.objects.all()


class ReporteIncidenteForm(forms.ModelForm):
    """Formulario para reportes de incidentes"""
    class Meta:
        model = ReporteIncidente
        fields = ['titulo', 'descripcion', 'ubicacion', 'equipo', 'severidad']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'ubicacion': forms.Select(attrs={'class': 'form-control'}),
            'equipo': forms.Select(attrs={'class': 'form-control'}),
            'severidad': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipo'].queryset = Equipo.objects.all()
        self.fields['ubicacion'].queryset = Ubicacion.objects.filter(activa=True)


class PersonalForm(forms.ModelForm):
    class Meta:
        model = Personal
        fields = ['nombre', 'rol', 'nivel', 'activo', 'disponible', 'horas_turno']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'nivel': forms.Select(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'horas_turno': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0.5'}),
        }


class AsignacionPersonalForm(forms.ModelForm):
    class Meta:
        model = AsignacionPersonal
        fields = ['personal', 'horas_asignadas', 'estado']
        widgets = {
            'personal': forms.Select(attrs={'class': 'form-control'}),
            'horas_asignadas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0.5'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }


class ProductoUtilizadoForm(forms.ModelForm):
    class Meta:
        model = ProductoUtilizado
        fields = ['producto', 'cantidad_utilizada']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_utilizada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }



