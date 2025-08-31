import json
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from django.db import transaction
from django.utils import timezone

from ..models import Crucero, Habitacion, Instalacion, TipoHabitacion
try:
    # import SeccionAlmacen desde la app almacen (si la app está disponible en el path)
    from apps.almacen.models import SeccionAlmacen
except Exception:
    # Fallback a import relativo si la estructura de paquetes lo requiere
    try:
        from ...almacen.models import SeccionAlmacen
    except Exception:
        SeccionAlmacen = None

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
        # manejar capacidad nula en plantillas (JSON null -> Python None)
        capacidad_raw = datos.get("capacidad", None)
        capacidad = None if capacidad_raw is None else int(capacidad_raw)

        cubierta_raw = datos.get("cubierta", 1)
        cubierta = 1 if cubierta_raw is None else int(cubierta_raw)

        instalacion = Instalacion.objects.create(
            crucero=crucero,
            nombre=datos["nombre"],
            tipo=datos.get("tipo", "otro"),
            capacidad=capacidad,
            cubierta=cubierta,
            descripcion=datos.get("descripcion"),
        )

        # Si la instalación es de tipo 'almacen', crear secciones.
        # Preferimos las secciones definidas en la plantilla (datos['secciones']).
        if instalacion and instalacion.tipo == 'almacen' and SeccionAlmacen is not None:
            secciones_definidas = datos.get('secciones')

            if secciones_definidas and isinstance(secciones_definidas, list):
                # Crear/obtener cada sección provista en la plantilla
                for sec in secciones_definidas:
                    nombre_sec = sec.get('nombre') or sec.get('nombre_seccion') or 'Sección'
                    tipo_cod = sec.get('tipo') or 'SECO'
                    capacidad_sec_raw = sec.get('capacidad', None)
                    try:
                        capacidad_sec = None if capacidad_sec_raw is None else int(capacidad_sec_raw)
                    except Exception:
                        capacidad_sec = 0

                    temperatura = sec.get('temperatura', None)
                    humedad = sec.get('humedad', None)
                    esta_activa = sec.get('esta_activa', True)

                    try:
                        SeccionAlmacen.objects.get_or_create(
                            almacen=instalacion,
                            nombre=nombre_sec,
                            defaults={
                                'tipo': tipo_cod,
                                'capacidad': capacidad_sec or 0,
                                'temperatura': temperatura,
                                'humedad': humedad,
                                'esta_activa': esta_activa,
                            }
                        )
                    except Exception:
                        continue
            else:
                # Si no hay secciones en la plantilla, creamos secciones por defecto.
                default_sections = [
                    ("SECO", "Sección Seco"),
                    ("REFRIGERACION", "Cámara de Refrigeración"),
                    ("CONGELACION", "Cámara de Congelación"),
                    ("ESTANTERIAS", "Estanterías"),
                ]

                n = len(default_sections)
                capacidad_por_seccion = 0
                if isinstance(capacidad, int) and capacidad > 0:
                    capacidad_por_seccion = max(0, capacidad // n)

                for tipo_cod, nombre_seccion in default_sections:
                    try:
                        SeccionAlmacen.objects.get_or_create(
                            almacen=instalacion,
                            nombre=nombre_seccion,
                            defaults={
                                'tipo': tipo_cod,
                                'capacidad': capacidad_por_seccion,
                                'temperatura': None,
                                'humedad': None,
                            }
                        )
                    except Exception:
                        continue

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
        # Calcular contadores iniciales por lado (se hace una sola consulta por lado)
        from ..models import Habitacion as _Habitacion  # local alias para evitar sombras

        def _prefijo(p):
            return f"{int(p):02d}"

        pref_babor = f"{_prefijo(piso)}0"
        pref_estribor = f"{_prefijo(piso)}1"

        existentes_babor = _Habitacion.objects.filter(crucero=crucero, codigo_ubicacion__startswith=pref_babor).values_list('codigo_ubicacion', flat=True)
        existentes_estribor = _Habitacion.objects.filter(crucero=crucero, codigo_ubicacion__startswith=pref_estribor).values_list('codigo_ubicacion', flat=True)

        def _max_from_existentes(iterable, pref):
            maxn = 0
            for cod in iterable:
                if len(cod) >= 6 and cod.isdigit() and cod.startswith(pref):
                    try:
                        n = int(cod[-3:])
                        if n > maxn:
                            maxn = n
                    except ValueError:
                        continue
            return maxn

        contadores_lado = {
            'babor': _max_from_existentes(existentes_babor, pref_babor),
            'estribor': _max_from_existentes(existentes_estribor, pref_estribor),
        }

        # alternador para repartir entre babor/estribor sin recalcular prefix cada vez
        alternador_lado = 0

        for cantidad, clave_tipo in distribucion:
            if cantidad <= 0 or clave_tipo not in tipos_map:
                continue

            tipo_habitacion = tipos_map[clave_tipo]
            habitaciones_creadas, nuevo_consecutivo, contadores_lado, alternador_lado = crear_lote_habitaciones(
                crucero, piso, cantidad, tipo_habitacion, contadores_lado, alternador_lado
            )

            total_habitaciones += habitaciones_creadas
    
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
                            contadores_lado: Dict[str, int], alternador_lado: int) -> Tuple[int, int, Dict[str, int], int]:
    """Crea `cantidad` habitaciones en memoria y las inserta en bloque.

    - contadores_lado: diccionario con los últimos números usados por lado (enteros).
    - alternador_lado: 0 para empezar por babor, 1 por estribor. Se mantiene entre llamadas por piso.

    Retorna: (habitaciones_creadas, nuevo_consecutivo_estimado, contadores_lado, alternador_lado)
    """
    habitaciones_a_insertar: List[Habitacion] = []
    habitaciones_creadas = 0

    for _ in range(cantidad):
        lado = 'babor' if alternador_lado == 0 else 'estribor'
        alternador_lado = 1 - alternador_lado

        # incrementar contador local y preparar número y código de ubicación
        contadores_lado[lado] += 1
        numero_simple = f"{contadores_lado[lado]}"
        lado_dig = '0' if lado == 'babor' else '1'
        codigo = f"{int(piso):02d}{lado_dig}{contadores_lado[lado]:03d}"

        habitacion = Habitacion(
            crucero=crucero,
            tipo_habitacion=tipo_habitacion,
            cubierta=piso,
            lado=lado,
            numero=numero_simple,
            codigo_ubicacion=codigo,
        )

        habitaciones_a_insertar.append(habitacion)
        habitaciones_creadas += 1

    # Insertar en bloque para reducir round-trips a la base de datos
    if habitaciones_a_insertar:
        # bulk_create no llama a save(), por eso ya establecimos codigo_ubicacion
        Habitacion.objects.bulk_create(habitaciones_a_insertar, batch_size=500)

    # nuevo_consecutivo es útil si la interfaz lo requiere; retornamos el total creado + 1
    nuevo_consecutivo = sum(contadores_lado.values())

    return habitaciones_creadas, nuevo_consecutivo, contadores_lado, alternador_lado