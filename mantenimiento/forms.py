from django import forms
from django.contrib.auth.models import User
from .models import (
    Ubicacion, Producto, InventarioProducto, Equipo, TareaMantenimiento, 
    ReporteIncidente, TipoCrucero, TipoEquipo, CategoriaProducto, Personal, AsignacionPersonal, ProductoUtilizado,
    Piscina, MedicionPiscina, PlantillaTarea, ChecklistItem, AdjuntoTarea, MantenimientoRecurrente, FiltroGuardado
)


class UbicacionForm(forms.ModelForm):
    """Formulario para ubicaciones"""
    class Meta:
        model = Ubicacion
        fields = ['cubierta', 'uso', 'identificador', 'numero', 'descripcion', 'activa', 'crucero']
        widgets = {
            'cubierta': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '18'}),
            'uso': forms.Select(attrs={'class': 'form-control'}),
            'identificador': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '1'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'crucero': forms.Select(attrs={'class': 'form-control'}),
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
        fields = ['cantidad_requerida', 'stock_minimo', 'stock_actual', 'ubicacion', 'crucero']
        widgets = {
            'cantidad_requerida': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'ubicacion': forms.Select(attrs={'class': 'form-control'}),
            'crucero': forms.Select(attrs={'class': 'form-control'}),
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
        fields = ['titulo', 'descripcion', 'tipo', 'prioridad', 'equipo', 'ubicacion', 'tipo_crucero', 'crucero', 'asignado_a', 'fecha_programada', 'tiempo_estimado_horas', 'observaciones']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'equipo': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion': forms.Select(attrs={'class': 'form-control'}),
            'tipo_crucero': forms.Select(attrs={'class': 'form-control'}),
            'crucero': forms.Select(attrs={'class': 'form-control'}),
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
        # crucero se selecciona manualmente, sin autocompletar


class ReporteIncidenteForm(forms.ModelForm):
    """Formulario para reportes de incidentes"""
    generar_tarea = forms.BooleanField(
        required=False, 
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text="Generar automáticamente una tarea correctiva"
    )
    
    class Meta:
        model = ReporteIncidente
        fields = ['titulo', 'descripcion', 'ubicacion', 'equipo', 'tipo_crucero', 'severidad']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'ubicacion': forms.Select(attrs={'class': 'form-control'}),
            'equipo': forms.Select(attrs={'class': 'form-control'}),
            'tipo_crucero': forms.Select(attrs={'class': 'form-control'}),
            'severidad': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipo'].queryset = Equipo.objects.all()
        self.fields['ubicacion'].queryset = Ubicacion.objects.filter(activa=True)
        self.fields['tipo_crucero'].queryset = TipoCrucero.objects.all()
        self.fields['tipo_crucero'].required = True


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


class PiscinaForm(forms.ModelForm):
    class Meta:
        model = Piscina
        fields = ['nombre', 'ubicacion', 'tipo_crucero', 'volumen_m3', 'en_servicio', 'fecha_ultima_limpieza', 'observaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.Select(attrs={'class': 'form-control'}),
            'tipo_crucero': forms.Select(attrs={'class': 'form-control'}),
            'volumen_m3': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.1'}),
            'en_servicio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_ultima_limpieza': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class MedicionPiscinaForm(forms.ModelForm):
    class Meta:
        model = MedicionPiscina
        fields = ['piscina', 'ph', 'cloro_mg_l', 'temperatura_c', 'turbidez_ntu', 'presion_filtro_bar', 'estado_filtro', 'retrolavado_realizado', 'observaciones']
        widgets = {
            'piscina': forms.Select(attrs={'class': 'form-control'}),
            'ph': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '14'}),
            'cloro_mg_l': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '10'}),
            'temperatura_c': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'turbidez_ntu': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'presion_filtro_bar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado_filtro': forms.Select(attrs={'class': 'form-control'}),
            'retrolavado_realizado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# Formularios para nuevas funcionalidades

class TipoTareaForm(forms.Form):
    """Formulario para seleccionar tipo de crucero antes de crear tarea"""
    tipo_crucero = forms.ModelChoiceField(
        queryset=TipoCrucero.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Selecciona el tipo de crucero donde se realizará la tarea"
    )
    tipo_tarea = forms.ChoiceField(
        choices=[('', 'Selecciona tipo de tarea')] + TareaMantenimiento.TIPOS_TAREA,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )


class TareaRapidaForm(forms.ModelForm):
    """Formulario simplificado para crear tareas rápidas"""
    class Meta:
        model = TareaMantenimiento
        fields = ['titulo', 'descripcion', 'ubicacion', 'equipo', 'prioridad', 'fecha_programada']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ubicacion': forms.Select(attrs={'class': 'form-control'}),
            'equipo': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'fecha_programada': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class PlantillaTareaForm(forms.ModelForm):
    """Formulario para plantillas de tareas"""
    class Meta:
        model = PlantillaTarea
        fields = ['nombre', 'descripcion', 'tipo_equipo', 'ubicacion', 'tipo_tarea', 'tiempo_estimado_horas', 'prioridad_default', 'instrucciones', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo_equipo': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion': forms.Select(attrs={'class': 'form-control'}),
            'tipo_tarea': forms.Select(attrs={'class': 'form-control'}),
            'tiempo_estimado_horas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0.5'}),
            'prioridad_default': forms.Select(attrs={'class': 'form-control'}),
            'instrucciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ChecklistItemForm(forms.ModelForm):
    """Formulario para items de checklist"""
    class Meta:
        model = ChecklistItem
        fields = ['descripcion', 'obligatorio', 'orden']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'obligatorio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }


class AdjuntoTareaForm(forms.ModelForm):
    """Formulario para adjuntos de tareas"""
    class Meta:
        model = AdjuntoTarea
        fields = ['archivo', 'nombre', 'tipo', 'descripcion']
        widgets = {
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class MantenimientoRecurrenteForm(forms.ModelForm):
    """Formulario para mantenimientos recurrentes"""
    class Meta:
        model = MantenimientoRecurrente
        fields = ['nombre', 'descripcion', 'tipo_equipo', 'tipo_crucero', 'plantilla_tarea', 'frecuencia', 'dias_adelanto', 'fecha_inicio', 'fecha_fin', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo_equipo': forms.Select(attrs={'class': 'form-control'}),
            'tipo_crucero': forms.Select(attrs={'class': 'form-control'}),
            'plantilla_tarea': forms.Select(attrs={'class': 'form-control'}),
            'frecuencia': forms.Select(attrs={'class': 'form-control'}),
            'dias_adelanto': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FiltroGuardadoForm(forms.ModelForm):
    """Formulario para filtros guardados"""
    class Meta:
        model = FiltroGuardado
        fields = ['nombre', 'publico']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'publico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FiltroTareasForm(forms.Form):
    """Formulario avanzado para filtrar tareas"""
    estado = forms.MultipleChoiceField(
        choices=TareaMantenimiento.ESTADOS,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    tipo = forms.MultipleChoiceField(
        choices=TareaMantenimiento.TIPOS_TAREA,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    prioridad = forms.MultipleChoiceField(
        choices=TareaMantenimiento.PRIORIDADES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    tipo_crucero = forms.ModelMultipleChoiceField(
        queryset=TipoCrucero.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    fecha_desde = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    fecha_hasta = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    buscar_texto = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar en título o descripción...'}),
        required=False
    )



