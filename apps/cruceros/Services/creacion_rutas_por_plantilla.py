import json
from pathlib import Path
from typing import Tuple
from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import Ruta, EtapaRuta

RUTAS_JSON_PATH = Path(__file__).resolve().parent.parent / 'config' / 'rutas' / 'rutas_base.json'

class RutaJSONError(Exception):
    pass

def cargar_rutas_desde_json(ruta_archivo: Path = None, sobrescribir_existentes: bool = False):
    ruta_archivo = ruta_archivo or RUTAS_JSON_PATH
    
    if not ruta_archivo.exists():
        raise RutaJSONError(f"Archivo no encontrado: {ruta_archivo}")

    with ruta_archivo.open(encoding='utf-8') as archivo:
        datos_json = json.load(archivo)

    with transaction.atomic():
        for ruta_data in datos_json['rutas']:
            nombre_ruta = ruta_data['nombre']
            
            if Ruta.objects.filter(nombre=nombre_ruta).exists():
                if sobrescribir_existentes:
                    Ruta.objects.filter(nombre=nombre_ruta).delete()
                else:
                    continue

            ruta = Ruta.objects.create(
                nombre=nombre_ruta,
                descripcion=ruta_data.get('descripcion', ''),
                duracion_dias=ruta_data.get('duracion_dias', 1)
            )

            etapas_ordenadas = sorted(ruta_data['etapas'], key=lambda etapa: etapa.get('orden', 0))
            etapas_para_crear = [
                EtapaRuta(
                    ruta=ruta,
                    nombre_lugar=etapa['nombre_lugar'],
                    pais=etapa.get('pais', ''),
                    dia_llegada=etapa['dia_llegada'],
                    tipo=etapa['tipo'],
                    descripcion=etapa.get('descripcion', ''),
                )
                for etapa in etapas_ordenadas
            ]
            
            EtapaRuta.objects.bulk_create(etapas_para_crear)
