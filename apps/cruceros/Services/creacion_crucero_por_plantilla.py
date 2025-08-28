import json
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from django.db import transaction
from django.utils import timezone

from ..models import Crucero, Habitacion, Instalacion, TipoHabitacion

class PlantillaNoEncontrada(Exception):
    pass

DIRECTORIO_PLANTILLAS = Path(__file__).resolve().parent.parent / "config" / "cruceros"

def crear_crucero_desde_plantilla(
    tipo_crucero: str,
    codigo_identificacion: str,
    nombre: str,
    fecha_botadura,
    descripcion: Optional[str] = None,
) -> Crucero:
    
    plantilla = cargar_datos_plantilla(tipo_crucero)

    especificaciones = plantilla.get("especificaciones", {}).copy()

    if descripcion:
        especificaciones["descripcion"] = descripcion

    especificaciones_procesadas = convertir_especificaciones_numericas(especificaciones)
    fecha_adquisicion = timezone.now().date() 

    hab_config = plantilla.get("habitaciones", {})

    with transaction.atomic():
        crucero = Crucero.objects.create(
            nombre=nombre,
            tipo_crucero=tipo_crucero,
            codigo_identificacion=codigo_identificacion,
            fecha_botadura=fecha_botadura,
            fecha_adquisicion=fecha_adquisicion,
            capacidad_pasajeros=especificaciones_procesadas.get("capacidad_pasajeros", 0),
            capacidad_tripulacion=especificaciones_procesadas.get("capacidad_tripulacion", 0),
            tonelaje=especificaciones_procesadas.get("tonelaje", 0),
            eslora=especificaciones_procesadas.get("eslora", 0),
            manga=especificaciones_procesadas.get("manga", 0),
            altura=especificaciones_procesadas.get("altura", 0),
            numero_cubiertas=especificaciones_procesadas.get("numero_cubiertas", 0),
            bandera=especificaciones_procesadas.get("bandera", ""),
            puerto_base=especificaciones_procesadas.get("puerto_base", ""),
            estado_operativo=especificaciones_procesadas.get("estado_operativo", Crucero.EstadoOperativo.ACTIVO),
            descripcion=especificaciones_procesadas.get("descripcion", ""),
            modelo_motor=especificaciones_procesadas.get("modelo_motor", ""),
            velocidad_maxima=especificaciones_procesadas.get("velocidad_maxima", 0),
            tipo_combustible=especificaciones_procesadas.get("tipo_combustible", Crucero.TipoCombustible.DIESEL),
            consumo_combustible=especificaciones_procesadas.get("consumo_combustible", 0),
        )

        crear_habitaciones_crucero(crucero, hab_config)
        crear_instalaciones_crucero(crucero, plantilla.get("instalaciones", {}).get("items", []))

    return crucero

def cargar_datos_plantilla(tipo_crucero: str) -> Dict[str, Any]:
    ruta = obtener_ruta_plantilla(tipo_crucero)
    
    if not ruta.exists():
        raise PlantillaNoEncontrada(f"Plantilla no encontrada: {tipo_crucero} en {ruta}")
    
    with ruta.open(encoding="utf-8") as archivo:
        return json.load(archivo)

def obtener_ruta_plantilla(tipo_crucero: str) -> Path:
    return DIRECTORIO_PLANTILLAS / f"{tipo_crucero}.json"

def convertir_especificaciones_numericas(especificaciones: Dict[str, Any]) -> Dict[str, Any]:
    especificaciones_procesadas = especificaciones.copy()
    
    campos_numericos = {
        "capacidad_pasajeros": int,
        "capacidad_tripulacion": int,
        "numero_cubiertas": int,
        "tonelaje": float,
        "eslora": float,
        "manga": float,
        "altura": float,
        "velocidad_maxima": float,
        "consumo_combustible": float,
    }
    
    for campo, tipo_conversion in campos_numericos.items():
        if campo in especificaciones_procesadas and especificaciones_procesadas[campo] is not None:
            especificaciones_procesadas[campo] = tipo_conversion(especificaciones_procesadas[campo])
    
    return especificaciones_procesadas

def crear_instalaciones_crucero(crucero: Crucero, instalaciones_data: List[Dict[str, Any]]) -> None:
    
    for datos in instalaciones_data:
        Instalacion.objects.create(
            crucero=crucero,
            nombre=datos["nombre"],
            tipo=datos.get("tipo", "otro"),
            capacidad=int(datos.get("capacidad", 0)),
            cubierta=int(datos.get("cubierta", 1)),
            descripcion=datos.get("descripcion"),
        )

def crear_habitaciones_crucero(crucero: Crucero, config_habitaciones: Dict[str, Any]) -> None:
    reglas = config_habitaciones.get("reglas", [])
    definiciones_tipos = config_habitaciones.get("tipos_habitacion", {})
    
    tipos_map = crear_mapa_tipos_habitacion(definiciones_tipos)
    
    for regla in reglas:
        procesar_regla_habitaciones(crucero, regla, tipos_map)
    

def crear_mapa_tipos_habitacion(definiciones_tipos: Dict[str, Any]) -> Dict[str, TipoHabitacion]:
    tipos_map = {}
    
    for clave, datos in definiciones_tipos.items():
        nombre = datos.get("nombre")
        if not nombre:
            continue
        
        capacidad = int(datos.get("capacidad", 0))
        precio_base = Decimal(str(datos.get("precio_base", "0.00")))
        descripcion = datos.get("descripcion", "Generado desde plantilla")
        
        tipo, creado = TipoHabitacion.objects.get_or_create(
            nombre=nombre,
            defaults={"capacidad": capacidad, "precio_base": precio_base, "descripcion": descripcion}
        )
        
        if not creado and capacidad > 0 and tipo.capacidad != capacidad:
            tipo.capacidad = capacidad
            tipo.save(update_fields=["capacidad"])
        
        tipos_map[clave] = tipo
    
    return tipos_map

def procesar_regla_habitaciones(crucero: Crucero, regla: Dict[str, Any], tipos_map: Dict[str, TipoHabitacion]) -> int:
    total_habitaciones = 0
    pisos = regla["pisos"]
    categoria = regla["categoria"]
    sencillos = int(regla.get("sencillos_por_piso", 0))
    dobles = int(regla.get("dobles_por_piso", 0))
    porcentaje_vista = float(regla.get("porcentaje_vista", 0))
    
    distribucion = calcular_distribucion_habitaciones(categoria, sencillos, dobles, porcentaje_vista)
    
    for piso in pisos:
        consecutivo_piso = 1
        
        for cantidad, clave_tipo in distribucion:
            if cantidad <= 0 or clave_tipo not in tipos_map:
                continue
            
            tipo_habitacion = tipos_map[clave_tipo]
            habitaciones_creadas, nuevo_consecutivo = crear_lote_habitaciones(
                crucero, piso, cantidad, tipo_habitacion, consecutivo_piso
            )
            
            total_habitaciones += habitaciones_creadas
            consecutivo_piso = nuevo_consecutivo
    
    return total_habitaciones

def calcular_distribucion_habitaciones(categoria: str, sencillos: int, dobles: int, porcentaje_vista: float) -> List[Tuple[int, str, int]]:
    vista_sencillas = round(sencillos * porcentaje_vista)
    interior_sencillas = sencillos - vista_sencillas
    vista_dobles = round(dobles * porcentaje_vista)
    interior_dobles = dobles - vista_dobles
    
    return [
        (vista_sencillas, f"{categoria}_sencillo_vista"),
        (interior_sencillas, f"{categoria}_sencillo_interior"),
        (vista_dobles, f"{categoria}_doble_vista"),
        (interior_dobles, f"{categoria}_doble_interior"),
    ]

def crear_lote_habitaciones(crucero: Crucero, piso: int, cantidad: int, tipo_habitacion: TipoHabitacion, 
                            consecutivo_inicio: int) -> Tuple[int, int]:
    habitaciones_creadas = 0
    consecutivo_actual = consecutivo_inicio
    alternador_lado = 0
    contadores_lado = {"babor": 0, "estribor": 0}

    for _ in range(cantidad):
        lado = "babor" if alternador_lado == 0 else "estribor"
        alternador_lado = 1 - alternador_lado
        contadores_lado[lado] += 1

        numero_simple = f"{contadores_lado[lado]}"

        Habitacion.objects.create(
            crucero=crucero,
            tipo_habitacion=tipo_habitacion,
            cubierta=piso,
            lado=lado,
            numero=numero_simple,
        )

        consecutivo_actual += 1
        habitaciones_creadas += 1

    return habitaciones_creadas, consecutivo_actual