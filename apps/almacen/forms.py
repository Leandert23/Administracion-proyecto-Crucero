from __future__ import annotations

from typing import Dict

from django import forms

from .models import Crucero
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
                descripcion=self.cleaned_data.get('descripcion') or None,
            )
        except PlantillaNoEncontrada as e:
            raise ValueError(str(e))
        return crucero

class cruceroEdicionParcialForm(forms.ModelForm):
    class Meta:
        model = Crucero
        fields = [
            'nombre', 'estado_operativo', 'ultimo_mantenimiento', 'proximo_mantenimiento',
            'seguro_vigente', 'fecha_vencimiento_seguro',
            'certificado_sanitario', 'certificado_seguridad',
            'foto_barco', 'plano_barco',
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'crucero-form__input'}),
            'estado_operativo': forms.Select(attrs={'class': 'crucero-form__input'}),
            'ultimo_mantenimiento': forms.DateInput(attrs={'type': 'date', 'class': 'crucero-form__input'}),
            'proximo_mantenimiento': forms.DateInput(attrs={'type': 'date', 'class': 'crucero-form__input'}),
            'fecha_vencimiento_seguro': forms.DateInput(attrs={'type': 'date', 'class': 'crucero-form__input'}),
        }

