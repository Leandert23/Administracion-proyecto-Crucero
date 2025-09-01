from django import forms
from django.contrib.auth.models import User
from .models import (
    Ubicacion, Producto, InventarioProducto, Equipo, TareaMantenimiento, 
    ReporteIncidente, TipoCrucero, TipoEquipo, CategoriaProducto
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
        fields = ['titulo', 'descripcion', 'tipo', 'prioridad', 'equipo', 'ubicacion', 'asignado_a', 'fecha_programada', 'tiempo_estimado_horas', 'observaciones']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'equipo': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion': forms.Select(attrs={'class': 'form-control'}),
            'asignado_a': forms.Select(attrs={'class': 'form-control'}),
            'fecha_programada': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'tiempo_estimado_horas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0.5'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar usuarios que pueden ser asignados (staff o superuser)
        self.fields['asignado_a'].queryset = User.objects.filter(is_staff=True)
        self.fields['equipo'].queryset = Equipo.objects.filter(estado__in=['operativo', 'mantenimiento'])
        self.fields['ubicacion'].queryset = Ubicacion.objects.filter(activa=True)


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


# Formularios adicionales para funcionalidades específicas
class FiltroUbicacionForm(forms.Form):
    """Formulario de filtros para ubicaciones"""
    cubierta = forms.ChoiceField(
        choices=[('', 'Todas las cubiertas')] + [(i, f'Cubierta {i}') for i in range(1, 19)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    uso = forms.ChoiceField(
        choices=[('', 'Todos los usos')] + Ubicacion.USOS_UBICACION,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    activa = forms.ChoiceField(
        choices=[('', 'Todas'), ('true', 'Activas'), ('false', 'Inactivas')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class FiltroProductoForm(forms.Form):
    """Formulario de filtros para productos"""
    categoria = forms.ModelChoiceField(
        queryset=CategoriaProducto.objects.all(),
        empty_label="Todas las categorías",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    activo = forms.ChoiceField(
        choices=[('', 'Todos'), ('true', 'Activos'), ('false', 'Inactivos')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class FiltroInventarioForm(forms.Form):
    """Formulario de filtros para inventario"""
    tipo_crucero = forms.ModelChoiceField(
        queryset=TipoCrucero.objects.all(),
        empty_label="Todos los tipos de crucero",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    categoria = forms.ModelChoiceField(
        queryset=CategoriaProducto.objects.all(),
        empty_label="Todas las categorías",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    estado_stock = forms.ChoiceField(
        choices=[('', 'Todos'), ('critico', 'Crítico'), ('bajo', 'Bajo'), ('normal', 'Normal')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class FiltroEquipoForm(forms.Form):
    """Formulario de filtros para equipos"""
    tipo_equipo = forms.ModelChoiceField(
        queryset=TipoEquipo.objects.all(),
        empty_label="Todos los tipos de equipo",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Equipo.ESTADOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cubierta = forms.ChoiceField(
        choices=[('', 'Todas las cubiertas')] + [(i, f'Cubierta {i}') for i in range(1, 19)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class FiltroTareaForm(forms.Form):
    """Formulario de filtros para tareas"""
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + TareaMantenimiento.TIPOS_TAREA,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + TareaMantenimiento.ESTADOS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    prioridad = forms.ChoiceField(
        choices=[('', 'Todas las prioridades')] + TareaMantenimiento.PRIORIDADES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    asignado = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),
        empty_label="Todos los usuarios",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class FiltroIncidenteForm(forms.Form):
    """Formulario de filtros para incidentes"""
    severidad = forms.ChoiceField(
        choices=[('', 'Todas las severidades')] + ReporteIncidente.SEVERIDADES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    resuelto = forms.ChoiceField(
        choices=[('', 'Todos'), ('true', 'Resueltos'), ('false', 'Pendientes')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


# Formularios para búsqueda
class BusquedaForm(forms.Form):
    """Formulario de búsqueda general"""
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar...',
            'aria-label': 'Buscar'
        })
    )
    tipo = forms.ChoiceField(
        choices=[
            ('', 'Todos'),
            ('ubicacion', 'Ubicaciones'),
            ('producto', 'Productos'),
            ('equipo', 'Equipos'),
            ('tarea', 'Tareas'),
            ('incidente', 'Incidentes'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
