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
    prefijo = PREFIJOS_TIPO.get(tipo_crucero, 'CR')
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
    return f"{prefijo}-{(max_num + 1):03d}"

class creacionCruceroForm(forms.Form):
    nombre = forms.CharField(max_length=100, label="Nombre")
    tipo_crucero = forms.ChoiceField(choices=Crucero.TipoCrucero.choices, label="Tipo de crucero")
    fecha_botadura = forms.DateField(label="Fecha de botadura", widget=forms.DateInput(attrs={'type': 'date'}))
    descripcion = forms.CharField(label="Descripción", required=False, widget=forms.Textarea)

    def crear_crucero(self) -> Crucero:
        if not self.is_valid():
            raise ValueError("Formulario no válido")
        tipo = self.cleaned_data['tipo_crucero']
        codigo = generar_codigo_identificacion(tipo)
        try:
            crucero = crear_crucero_desde_plantilla(
                tipo_crucero=tipo,
                codigo_identificacion=codigo,
                nombre=self.cleaned_data['nombre'],
                fecha_botadura=self.cleaned_data['fecha_botadura'],
                descripcion=self.cleaned_data.get('descripcion'),
            )
        except PlantillaNoEncontrada as e:
            raise ValueError(str(e))
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
