from django import forms
from django.contrib.auth.models import User
from .models import (
    SolicitudMantenimiento, TareaMantenimiento, Equipo, Ubicacion, 
    TipoCrucero, Crucero, Personal, Producto, InventarioProducto,
    Piscina, MedicionPiscina, ReporteIncidente, ProductoUtilizado,
    ChecklistItem, AdjuntoTarea, AsignacionPersonal
)
from django.utils import timezone
from datetime import datetime, timedelta


class SolicitudMantenimientoForm(forms.ModelForm):
    """Formulario para solicitar mantenimiento desde otros módulos"""
    
    class Meta:
        model = SolicitudMantenimiento
        fields = [
            'titulo', 'descripcion', 'tipo', 'prioridad', 
            'ubicacion_solicitud', 'equipo_afectado', 'materiales_necesarios',
            'tiempo_estimado', 'fecha_programada'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Limpieza de equipos médicos',
                'maxlength': 200
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe detalladamente qué necesita mantenimiento y por qué...'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_solicitud'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_prioridad'
            }),
            'ubicacion_solicitud': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Cubierta 5 - Consultorio Médico A',
                'maxlength': 100
            }),
            'equipo_afectado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Equipos de rayos X, camillas, etc.',
                'maxlength': 200
            }),
            'materiales_necesarios': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Lista los materiales, herramientas o suministros necesarios...'
            }),
            'tiempo_estimado': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tiempo en minutos',
                'min': 15,
                'max': 480
            }),
            'fecha_programada': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
            })
        }
        labels = {
            'titulo': 'Título de la Solicitud',
            'descripcion': 'Descripción Detallada',
            'tipo': 'Tipo de Mantenimiento',
            'prioridad': 'Prioridad',
            'ubicacion_solicitud': 'Ubicación',
            'equipo_afectado': 'Equipo/Área Afectada',
            'materiales_necesarios': 'Materiales Necesarios',
            'tiempo_estimado': 'Tiempo Estimado (minutos)',
            'fecha_programada': 'Fecha Programada'
        }
        help_texts = {
            'titulo': 'Un título claro y descriptivo de la solicitud',
            'descripcion': 'Explica detalladamente qué necesita mantenimiento y por qué',
            'tipo': 'Selecciona si es mantenimiento preventivo o correctivo',
            'prioridad': 'Nivel de urgencia de la solicitud',
            'ubicacion_solicitud': 'Ubicación específica donde se necesita el mantenimiento',
            'equipo_afectado': 'Equipo, máquina o área específica que necesita atención',
            'materiales_necesarios': 'Materiales, herramientas o suministros que podrían ser necesarios',
            'tiempo_estimado': 'Tiempo estimado que podría tomar el mantenimiento',
            'fecha_programada': 'Fecha y hora preferida para realizar el mantenimiento'
        }

    def __init__(self, *args, **kwargs):
        self.modulo_solicitante = kwargs.pop('modulo_solicitante', 'mantenimiento')
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configurar opciones de prioridad según el tipo
        if 'tipo' in self.data:
            tipo = self.data.get('tipo')
            if tipo == 'correctivo':
                self.fields['prioridad'].choices = [
                    ('media', 'Media'),
                    ('alta', 'Alta'),
                    ('critica', 'Crítica'),
                    ('emergencia', 'Emergencia Crítica'),
                ]
            else:
                self.fields['prioridad'].choices = [
                    ('baja', 'Baja'),
                    ('media', 'Media'),
                    ('alta', 'Alta'),
                ]

    def clean_fecha_programada(self):
        fecha = self.cleaned_data.get('fecha_programada')
        if fecha and fecha < timezone.now():
            raise forms.ValidationError("La fecha programada no puede ser en el pasado.")
        return fecha

    def clean_tiempo_estimado(self):
        tiempo = self.cleaned_data.get('tiempo_estimado')
        if tiempo and (tiempo < 15 or tiempo > 480):
            raise forms.ValidationError("El tiempo estimado debe estar entre 15 y 480 minutos.")
        return tiempo

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.modulo_solicitante = self.modulo_solicitante
        instance.solicitado_por = self.user
        
        # Obtener crucero activo (si existe)
        try:
            crucero_activo = Crucero.objects.filter(activo=True).first()
            if crucero_activo:
                instance.crucero = crucero_activo
                instance.tipo_crucero = crucero_activo.tipo
        except:
            pass
        
        if commit:
            instance.save()
        return instance


class SolicitudMantenimientoPreventivoForm(SolicitudMantenimientoForm):
    """Formulario específico para solicitudes de mantenimiento preventivo"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].initial = 'preventivo'
        self.fields['tipo'].widget.attrs['readonly'] = True
        self.fields['prioridad'].initial = 'baja'
        
        # Para preventivo, limitar prioridades
        self.fields['prioridad'].choices = [
            ('baja', 'Baja'),
            ('media', 'Media'),
            ('alta', 'Alta'),
        ]


class SolicitudMantenimientoCorrectivoForm(SolicitudMantenimientoForm):
    """Formulario específico para solicitudes de mantenimiento correctivo"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].initial = 'correctivo'
        self.fields['tipo'].widget.attrs['readonly'] = True
        self.fields['prioridad'].initial = 'media'
        
        # Para correctivo, permitir todas las prioridades
        self.fields['prioridad'].choices = [
            ('media', 'Media'),
            ('alta', 'Alta'),
            ('critica', 'Crítica'),
            ('emergencia', 'Emergencia Crítica'),
        ]


class SolicitudMantenimientoAdminForm(forms.ModelForm):
    """Formulario para administrar solicitudes desde el módulo de mantenimiento"""
    
    class Meta:
        model = SolicitudMantenimiento
        fields = [
            'estado', 'asignado_a', 'revisado_por', 'observaciones',
            'fecha_programada', 'fecha_inicio', 'fecha_completado'
        ]
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'asignado_a': forms.Select(attrs={'class': 'form-select'}),
            'revisado_por': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observaciones del personal de mantenimiento...'
            }),
            'fecha_programada': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'fecha_inicio': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'fecha_completado': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }
        labels = {
            'estado': 'Estado de la Solicitud',
            'asignado_a': 'Asignado a',
            'revisado_por': 'Revisado por',
            'observaciones': 'Observaciones',
            'fecha_programada': 'Fecha Programada',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_completado': 'Fecha de Completado'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar usuarios que pueden ser asignados (personal de mantenimiento)
        self.fields['asignado_a'].queryset = User.objects.filter(
            personal__tipo='mantenimiento'
        ).order_by('first_name', 'last_name')
        
        self.fields['revisado_por'].queryset = User.objects.filter(
            personal__tipo='mantenimiento'
        ).order_by('first_name', 'last_name')


class ConvertirSolicitudATareaForm(forms.ModelForm):
    """Formulario para convertir una solicitud en una tarea de mantenimiento"""
    
    class Meta:
        model = TareaMantenimiento
        fields = [
            'titulo', 'descripcion', 'tipo', 'prioridad', 'equipo', 'ubicacion',
            'asignado_a', 'fecha_programada'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'equipo': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion': forms.Select(attrs={'class': 'form-select'}),
            'asignado_a': forms.Select(attrs={'class': 'form-select'}),
            'fecha_programada': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }

    def __init__(self, *args, **kwargs):
        self.solicitud = kwargs.pop('solicitud', None)
        super().__init__(*args, **kwargs)
        
        if self.solicitud:
            # Pre-llenar campos con datos de la solicitud
            self.fields['titulo'].initial = self.solicitud.titulo
            self.fields['descripcion'].initial = self.solicitud.descripcion
            self.fields['tipo'].initial = self.solicitud.tipo
            self.fields['prioridad'].initial = self.solicitud.prioridad
            self.fields['fecha_programada'].initial = self.solicitud.fecha_programada
            
            # Filtrar ubicaciones según el crucero
            if self.solicitud.crucero:
                self.fields['ubicacion'].queryset = Ubicacion.objects.filter(
                    crucero=self.solicitud.crucero,
                    activa=True
                )
            
            # Filtrar personal de mantenimiento
            self.fields['asignado_a'].queryset = User.objects.filter(
                personal__activo=True
            ).order_by('first_name', 'last_name')


# Formularios adicionales necesarios para el sistema existente
class UbicacionForm(forms.ModelForm):
    """Formulario para ubicaciones"""
    class Meta:
        model = Ubicacion
        fields = ['cubierta', 'uso', 'identificador', 'numero', 'descripcion', 'crucero', 'activa']
        widgets = {
            'cubierta': forms.NumberInput(attrs={'class': 'form-control'}),
            'uso': forms.Select(attrs={'class': 'form-select'}),
            'identificador': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 1}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 2}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'crucero': forms.Select(attrs={'class': 'form-select'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class ProductoForm(forms.ModelForm):
    """Formulario para productos"""
    class Meta:
        model = Producto
        fields = ['nombre', 'categoria', 'unidad', 'descripcion', 'notas', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'unidad': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class PiscinaForm(forms.ModelForm):
    """Formulario para piscinas"""
    class Meta:
        model = Piscina
        fields = ['nombre', 'ubicacion', 'tipo_crucero', 'volumen_m3', 'en_servicio', 'fecha_ultima_limpieza', 'observaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.Select(attrs={'class': 'form-select'}),
            'tipo_crucero': forms.Select(attrs={'class': 'form-select'}),
            'volumen_m3': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.1'}),
            'en_servicio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_ultima_limpieza': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }


class MedicionPiscinaForm(forms.ModelForm):
    """Formulario para mediciones de piscina"""
    class Meta:
        model = MedicionPiscina
        fields = ['piscina', 'ph', 'cloro_mg_l', 'temperatura_c', 'turbidez_ntu', 'presion_filtro_bar', 'estado_filtro', 'retrolavado_realizado']
        widgets = {
            'piscina': forms.Select(attrs={'class': 'form-select'}),
            'ph': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '14'}),
            'cloro_mg_l': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '10'}),
            'temperatura_c': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'turbidez_ntu': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'presion_filtro_bar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado_filtro': forms.Select(attrs={'class': 'form-select'}),
            'retrolavado_realizado': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class InventarioProductoForm(forms.ModelForm):
    """Formulario para inventario de productos"""
    class Meta:
        model = InventarioProducto
        fields = ['producto', 'tipo_crucero', 'crucero', 'cantidad_requerida', 'stock_minimo', 'stock_actual', 'ubicacion']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'tipo_crucero': forms.Select(attrs={'class': 'form-select'}),
            'crucero': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_requerida': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'ubicacion': forms.Select(attrs={'class': 'form-select'})
        }


class ReporteIncidenteForm(forms.ModelForm):
    """Formulario para reportes de incidentes"""
    class Meta:
        model = ReporteIncidente
        fields = ['titulo', 'descripcion', 'severidad', 'ubicacion', 'equipo', 'tipo_crucero']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'severidad': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion': forms.Select(attrs={'class': 'form-select'}),
            'equipo': forms.Select(attrs={'class': 'form-select'}),
            'tipo_crucero': forms.Select(attrs={'class': 'form-select'})
        }


class EquipoForm(forms.ModelForm):
    """Formulario para equipos"""
    class Meta:
        model = Equipo
        fields = ['codigo', 'nombre', 'tipo_equipo', 'ubicacion', 'estado', 'fecha_instalacion', 'ultima_revision', 'proxima_revision', 'observaciones']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_equipo': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'fecha_instalacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ultima_revision': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'proxima_revision': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }


class AsignacionPersonalForm(forms.ModelForm):
    """Formulario para asignar personal a tareas"""
    
    class Meta:
        model = AsignacionPersonal
        fields = ['personal', 'horas_asignadas']
        widgets = {
            'personal': forms.Select(attrs={'class': 'form-select'}),
            'horas_asignadas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.5',
                'step': '0.5',
                'value': '1.0'
            })
        }
        labels = {
            'personal': 'Personal de Mantenimiento',
            'horas_asignadas': 'Horas Asignadas'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['personal'].queryset = Personal.objects.filter(activo=True)


class ProductoUtilizadoForm(forms.ModelForm):
    """Formulario para productos utilizados en tareas"""
    class Meta:
        model = ProductoUtilizado
        fields = ['producto', 'cantidad_utilizada']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_utilizada': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'})
        }


class ChecklistItemForm(forms.ModelForm):
    """Formulario para items de checklist"""
    class Meta:
        model = ChecklistItem
        fields = ['descripcion', 'completado', 'orden', 'obligatorio']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'completado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'obligatorio': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class AdjuntoTareaForm(forms.ModelForm):
    """Formulario para adjuntos de tareas"""
    class Meta:
        model = AdjuntoTarea
        fields = ['archivo', 'descripcion']
        widgets = {
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'})
        }


class TareaMantenimientoForm(forms.ModelForm):
    """Formulario para crear y editar tareas de mantenimiento"""
    
    class Meta:
        model = TareaMantenimiento
        fields = [
            'titulo', 'descripcion', 'tipo', 'prioridad', 'equipo', 'ubicacion',
            'asignado_a', 'fecha_programada'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'equipo': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion': forms.Select(attrs={'class': 'form-select'}),
            'asignado_a': forms.Select(attrs={'class': 'form-select'}),
            'fecha_programada': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }