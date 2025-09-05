from __future__ import annotations

from typing import Dict

from django import forms

from .models import Crucero, Viaje, FechaDelSistema
from .Services.creacion_crucero_por_plantilla import crear_crucero_desde_plantilla, PlantillaNoEncontrada

PREFIJOS_TIPO: Dict[str, str] = {
    'pequeno': 'SM',
    'mediano': 'MD',
    'grande': 'LG',
}

def generar_codigo_identificacion(tipo_crucero: str) -> str:
    """
    Genera un código de identificación único para un crucero.
    Maneja condiciones de carrera y códigos duplicados.
    """
    prefijo = PREFIJOS_TIPO.get(tipo_crucero, 'CR')
    max_intentos = 100  # Límite de intentos para evitar bucles infinitos
    
    for intento in range(max_intentos):
        # Obtener el siguiente número disponible
        existentes = (
            Crucero.objects
            .filter(codigo_identificacion__startswith=f"{prefijo}-")
            .values_list('codigo_identificacion', flat=True)
        )
        
        max_num = 0
        for cod in existentes:
            try:
                sufijo = cod.split('-', 1)[1]
                if sufijo.isdigit():
                    max_num = max(max_num, int(sufijo))
            except (IndexError, ValueError):
                continue
        
        codigo_candidato = f"{prefijo}-{(max_num + 1):03d}"
        
        # Verificar si el código ya existe (manejo de condición de carrera)
        if not Crucero.objects.filter(codigo_identificacion=codigo_candidato).exists():
            return codigo_candidato
        
        # Si existe, incrementar y probar de nuevo
        max_num += 1
    
    # Si llegamos aquí, algo está muy mal
    raise ValueError(f"No se pudo generar un código único después de {max_intentos} intentos")

class creacionCruceroForm(forms.Form):
    nombre = forms.CharField(max_length=100, label="Nombre")
    tipo_crucero = forms.ChoiceField(choices=Crucero.TipoCrucero.choices, label="Tipo de crucero")
    fecha_botadura = forms.DateField(label="Fecha de botadura", widget=forms.DateInput(attrs={'type': 'date'}))
    descripcion = forms.CharField(label="Descripción", required=False, widget=forms.Textarea)

    def crear_crucero(self) -> Crucero:
        if not self.is_valid():
            raise ValueError("Formulario no válido")
        
        tipo = self.cleaned_data['tipo_crucero']
        nombre = self.cleaned_data['nombre']
        
        # Verificar si ya existe un crucero con el mismo nombre
        if Crucero.objects.filter(nombre=nombre).exists():
            raise ValueError(f"Ya existe un crucero con el nombre '{nombre}'. Por favor, elige un nombre diferente.")
        
        try:
            codigo = generar_codigo_identificacion(tipo)
        except ValueError as e:
            raise ValueError(f"Error al generar código de identificación: {str(e)}")
        
        try:
            crucero = crear_crucero_desde_plantilla(
                tipo_crucero=tipo,
                codigo_identificacion=codigo,
                nombre=nombre,
                fecha_botadura=self.cleaned_data['fecha_botadura'],
                descripcion=self.cleaned_data.get('descripcion'),
            )
        except PlantillaNoEncontrada as e:
            raise ValueError(f"Error de plantilla: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error inesperado al crear el crucero: {str(e)}")
        
        return crucero

class AsignarRutaForm(forms.ModelForm):
    class Meta:
        model = Viaje
        fields = ["ruta", "fecha_inicio"]
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "ruta": "Ruta",
            "fecha_inicio": "Fecha de inicio",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fs = FechaDelSistema.objects.first()
        if fs:
            self.fields["fecha_inicio"].initial = fs.fecha_actual


class CruceroEditForm(forms.ModelForm):
    class Meta:
        model = Crucero
        fields = [
            'nombre', 'fecha_botadura', 'bandera', 'puerto_base', 'estado_operativo',
            'descripcion', 'ultimo_mantenimiento', 'proximo_mantenimiento'
        ]
        widgets = {
            'fecha_botadura': forms.DateInput(attrs={'type': 'date'}),
            'ultimo_mantenimiento': forms.DateInput(attrs={'type': 'date'}),
            'proximo_mantenimiento': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
