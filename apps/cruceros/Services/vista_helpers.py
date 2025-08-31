from datetime import date, timedelta
from typing import Dict, Any
from ..models import FechaDelSistema, Crucero, Habitacion, TipoHabitacion

# --- Fecha del sistema ---

def obtener_fecha_sistema() -> FechaDelSistema:
    fecha_sistema, _ = FechaDelSistema.objects.get_or_create(
        defaults={'fecha_actual': date.today()}
    )
    return fecha_sistema

def avanzar_dia(fecha_sistema: FechaDelSistema, cruceros):
    fecha_sistema.fecha_actual += timedelta(days=1)
    fecha_sistema.save()
    actualizar_estados_viajes(fecha_sistema, cruceros)

# --- Estados de viajes ---

def actualizar_estados_viajes(fecha_sistema: FechaDelSistema, cruceros):
    for crucero in cruceros:
        marcar_viajes_completados(fecha_sistema, crucero)
        activar_viajes_iniciados(fecha_sistema, crucero)

def marcar_viajes_completados(fecha_sistema: FechaDelSistema, crucero: Crucero):
    viaje = crucero.viajes.filter(estado='activo', fecha_fin__lte=fecha_sistema.fecha_actual).first()

    if viaje is None:
        return
    
    viaje.estado = 'completado'
    viaje.save()
    crucero.viajes.create(
        estado='activo',
        ruta = viaje.ruta,
        fecha_inicio=fecha_sistema.fecha_actual)

def activar_viajes_iniciados(fecha_sistema: FechaDelSistema, crucero: Crucero):
    crucero.viajes.filter(
        estado='planificacion',
        fecha_inicio=fecha_sistema.fecha_actual
    ).update(estado='activo')

# --- Construcción de contexto preview ---

def construir_contexto_preview(crucero: Crucero, viajes_crucero, primer_viaje, fecha_sistema: FechaDelSistema) -> Dict[str, Any]:
    hoy = fecha_sistema.fecha_actual
    datos_viaje = obtener_datos_viaje(primer_viaje, hoy)
    instalaciones = crucero.instalaciones.all()
    distribucion = obtener_distribucion_habitaciones(crucero)
        
    return {
        'crucero': crucero,
        'viajes': viajes_crucero,
        'primer_viaje': primer_viaje,
        'hoy': hoy,
        "instalaciones": instalaciones,
        "distribucion_habitaciones": distribucion,
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

def obtener_distribucion_habitaciones(crucero: Crucero):
    tipos = (TipoHabitacion.objects.filter(habitaciones__crucero=crucero).distinct().order_by('nombre'))
    distribucion = []
    for tipo in tipos:
        total = Habitacion.objects.filter(crucero=crucero, tipo_habitacion=tipo).count()
        distribucion.append({
            'nombre': tipo.nombre,
            'capacidad_tipo': tipo.capacidad,
            'cantidad_habitaciones': total,
            'capacidad_total': total * tipo.capacidad,
            'descripcion': tipo.descripcion,
        })
    return distribucion