from datetime import date, timedelta
from typing import Dict, Any
from ..models import FechaDelSistema, TipoHabitacion, Viaje
from apps.creador_embarcaciones.models import Embarcacion, Habitaciones
from apps.entretenimiento.utils import cargar_actividades_entretenimiento

# --- Fecha del sistema ---

def obtener_fecha_sistema() -> FechaDelSistema:
    fecha_sistema, _ = FechaDelSistema.objects.get_or_create(
        defaults={'fecha_actual': date.today()}
    )
    return fecha_sistema

def avanzar_dia(fecha_sistema: FechaDelSistema, embarcaciones):
    fecha_sistema.fecha_actual += timedelta(days=1)
    fecha_sistema.save()
    actualizar_estados_viajes(fecha_sistema, embarcaciones)

# --- Estados de viajes ---

def actualizar_estados_viajes(fecha_sistema: FechaDelSistema, embarcaciones):
    for embarcacion in embarcaciones:
        marcar_viajes_completados(fecha_sistema, embarcacion)
        activar_viajes_iniciados(fecha_sistema, embarcacion)

def marcar_viajes_completados(fecha_sistema: FechaDelSistema, embarcacion: Embarcacion):
    # Nota: El modelo Embarcacion no tiene viajes como el modelo Crucero
    # Esta funcionalidad está temporalmente deshabilitada
    pass


def activar_viajes_iniciados(fecha_sistema: FechaDelSistema, embarcacion: Embarcacion):
    # Nota: El modelo Embarcacion no tiene viajes como el modelo Crucero
    # Esta funcionalidad está temporalmente deshabilitada
    pass

# --- Construcción de contexto preview ---

def construir_contexto_preview(embarcacion: Embarcacion, viajes_embarcacion, primer_viaje, fecha_sistema: FechaDelSistema) -> Dict[str, Any]:
    hoy = fecha_sistema.fecha_actual
    datos_viaje = obtener_datos_viaje(primer_viaje, hoy)
    # Nota: El modelo Embarcacion no tiene instalaciones como el modelo Crucero
    # distribucion = obtener_distribucion_habitaciones(embarcacion)

    return {
        'crucero': embarcacion,
        'viajes': viajes_embarcacion,
        'primer_viaje': primer_viaje,
        'hoy': hoy,
        "instalaciones": [],  # Temporalmente vacío
        "distribucion_habitaciones": [],  # Temporalmente vacío
        **datos_viaje
    }

def obtener_datos_viaje(viaje, hoy):
    if viaje.estado == 'planificacion':
        return datos_viaje_planificacion(viaje, hoy)
    elif viaje.estado == 'activo':
        return datos_viaje_activo(viaje, hoy)
    return {}

def datos_viaje_planificacion(viaje, hoy):
    if not viaje.fecha_inicio:
        return {}
    dias_para_zarpe = max(0, (viaje.fecha_inicio - hoy).days)
    return {'dias_para_zarpe': dias_para_zarpe}

def datos_viaje_activo(viaje, hoy):
    if not viaje.fecha_inicio or not viaje.fecha_fin:
        return {}
    dias_totales = (viaje.fecha_fin - viaje.fecha_inicio).days + 1
    dias_transcurridos = calcular_dias_transcurridos(viaje, hoy, dias_totales)
    progreso_porcentaje = calcular_progreso(dias_transcurridos, dias_totales)
    etapas_datos = obtener_etapas_viaje(viaje, dias_transcurridos)
    return {
        'dias_transcurridos': dias_transcurridos,
        'dias_totales': dias_totales,
        'progreso_porcentaje': progreso_porcentaje,
        'etapas_datos': etapas_datos
    }

def calcular_dias_transcurridos(viaje, hoy, dias_totales):
    dias_transcurridos = (hoy - viaje.fecha_inicio).days + 1
    return max(0, min(dias_transcurridos, dias_totales))

def calcular_progreso(dias_transcurridos, dias_totales):
    if dias_totales <= 0:
        return 0
    return round(dias_transcurridos / dias_totales * 100, 1)

def obtener_etapas_viaje(viaje, dias_transcurridos):
    etapas = viaje.ruta.etapas.all().order_by('dia_llegada')
    return [procesar_etapa(etapa, dias_transcurridos) for etapa in etapas]

def procesar_etapa(etapa, dias_transcurridos):
    status = 'future'
    if dias_transcurridos is not None:
        if etapa.dia_llegada < dias_transcurridos:
            status = 'past'
        elif etapa.dia_llegada == dias_transcurridos:
            status = 'current'
    descripcion = etapa.descripcion or ('En el mar' if etapa.tipo == 'navegacion' else '')
    return {
        'dia': etapa.dia_llegada,
        'tipo': getattr(etapa, 'get_tipo_display', lambda: etapa.tipo)(),
        'nombre_lugar': etapa.nombre_lugar,
        'descripcion': descripcion,
        'status': status,
    }

def obtener_distribucion_habitaciones(embarcacion: Embarcacion):
    # Nota: El modelo Embarcacion no tiene habitaciones como el modelo Crucero
    # Esta funcionalidad está temporalmente deshabilitada
    return []