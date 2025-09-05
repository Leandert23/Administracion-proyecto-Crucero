"""Servicio para creación de productos predeterminados al asignar una ruta a un crucero.

Lee un archivo JSON (basado en el tipo de crucero) y crea productos iniciales
asociados a las secciones de almacén existentes del crucero.

Convención de archivo (nueva prioridad):
1. apps/cruceros/config/productos/<tipo>.json
2. (Fallback legacy) apps/cruceros/config/cruceros/<tipo>.json
(Si ninguno existe, no crea nada y retorna resultado con success False.)
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.cruceros.models import Crucero, Instalacion
from apps.almacen.models import SeccionAlmacen, Producto

BASE_CONFIG_PRODUCTOS = Path(__file__).resolve().parent.parent / 'config' / 'productos'
BASE_CONFIG_CRUCEROS = Path(__file__).resolve().parent.parent / 'config' / 'cruceros'

# Estructura esperada (ejemplo sugerido) dentro del JSON en clave 'productos_iniciales':
# {
#   "productos_iniciales": [
#       {
#          "nombre": "Arroz",
#          "tipo": "COMIDA",
#          "subtipo": "CADUCABLE",
#          "medida": "K",
#          "cantidad_ideal": 500,
#          "seccion_nombre": "Almacén Seco"  # Se busca case-insensitive dentro de las secciones del crucero
#       },
#       ...
#   ]
# }

RESULT_OK: Dict[str, Any] = {"success": True}


def _cargar_json_tipo(tipo: str) -> Dict[str, Any] | None:
    """Carga el JSON de configuración para un tipo de crucero.

    Prioridad:
    1. config/productos/<tipo>_productos.json (nuevo esquema)
    2. config/productos/<tipo>.json (anterior en carpeta productos)
    3. config/cruceros/<tipo>.json (soporte retrocompatible)
    """
    posibles = [
        BASE_CONFIG_PRODUCTOS / f'{tipo}_productos.json',
        BASE_CONFIG_PRODUCTOS / f'{tipo}.json',
        BASE_CONFIG_CRUCEROS / f'{tipo}.json'
    ]
    for path in posibles:
        if not path.exists():
            continue
        try:
            with path.open('r', encoding='utf-8') as fh:
                return json.load(fh)
        except json.JSONDecodeError:
            return None
    return None


def _indexar_secciones(crucero: Crucero) -> Dict[str, SeccionAlmacen]:
    index: Dict[str, SeccionAlmacen] = {}
    secciones = SeccionAlmacen.objects.filter(almacen__crucero=crucero)
    for s in secciones:
        index[s.nombre.strip().lower()] = s
    return index


def crear_productos_predeterminados(crucero: Crucero) -> Dict[str, Any]:
    """Crea productos base para un crucero según plantilla JSON.

    Idempotente a nivel de nombre de producto dentro del crucero: si ya existe (case-insensitive) se omite.
    """
    if not isinstance(crucero, Crucero):
        return {"success": False, "error": "parametro_invalido", "mensaje": "crucero inválido"}

    data = _cargar_json_tipo(crucero.tipo_crucero)
    if not data:
        return {"success": False, "error": "config_no_encontrada", "mensaje": "No se encontró JSON de tipo de crucero"}

    productos_cfg: List[Dict[str, Any]] = data.get('productos_iniciales') or []
    if not productos_cfg:
        return {"success": False, "error": "sin_productos", "mensaje": "La plantilla no define productos_iniciales"}

    index_secciones = _indexar_secciones(crucero)

    creados: List[int] = []
    omitidos: List[str] = []
    errores: List[Dict[str, str]] = []

    with transaction.atomic():
        for cfg in productos_cfg:
            try:
                nombre = (cfg.get('nombre') or '').strip()
                if not nombre:
                    continue
                key_nombre = nombre.lower()
                # Verificar existencia en cualquier seccion del mismo crucero
                existe = Producto.objects.filter(
                    seccion__almacen__crucero=crucero,
                    nombre__iexact=nombre
                ).exists()
                if existe:
                    omitidos.append(nombre)
                    continue

                seccion_nombre = (cfg.get('seccion_nombre') or '').strip().lower()
                seccion = index_secciones.get(seccion_nombre)
                if not seccion:
                    errores.append({"producto": nombre, "error": "seccion_no_encontrada"})
                    continue

                producto = Producto(
                    nombre=nombre,
                    tipo=cfg.get('tipo') or 'COMIDA',
                    subtipo=cfg.get('subtipo'),
                    medida=cfg.get('medida') or 'U',
                    cantidad_ideal=cfg.get('cantidad_ideal') or 0,
                    seccion=seccion
                )
                producto.save()
                creados.append(producto.id)
            except ValidationError as ve:  # VALIDACIÓN DE MODELO
                errores.append({"producto": cfg.get('nombre', ''), "error": "validacion", "detalle": str(ve)})
            except Exception as e:  # CUALQUIER OTRO ERROR
                errores.append({"producto": cfg.get('nombre', ''), "error": "excepcion", "detalle": str(e)})

    return {
        "success": True,
        "creados": creados,
        "omitidos": omitidos,
        "errores": errores
    }
