"""
Módulo para gestionar operaciones relacionadas con cruceros y sistema de inventario.

Este módulo proporciona funciones para obtener información sobre cruceros,
sus viajes activos, y gestionar el sistema de inventario de productos.
"""

from typing import Any, Optional
import datetime
from ..models import FechaDelSistema, Crucero


def obtener_fecha_actual() -> Optional[datetime.date]:
    """Obtiene la fecha actual del sistema.
    
    Returns:
        datetime.date o None: La fecha actual del sistema si existe, 
        None si no está configurada.
    """
    sistema_fecha = FechaDelSistema.objects.first()
    return sistema_fecha.fecha_actual if sistema_fecha else None


def obtener_dia_crucero(crucero_id: int) -> Optional[int]:
    """Obtiene el día actual de viaje para un crucero específico.
    
    Args:
        crucero_id (int): ID del crucero a consultar.
        
    Returns:
        int o None: El día actual de viaje del crucero si está en un viaje activo,
        None si el crucero no existe o no está en un viaje activo.
    """
    if not crucero_id:
        return None
        
    try:
        crucero = Crucero.objects.get(pk=crucero_id)
        return crucero.dia_actual_de_viaje
    except Crucero.DoesNotExist:
        return None
    except AttributeError:
        # Si no está en viaje activo retornamos None
        return None


def __obtener_viaje_activo(crucero: Crucero) -> Optional[Any]:
    """Obtiene el viaje activo de un crucero.
    
    Args:
        crucero (Crucero): Instancia del modelo Crucero.
        
    Returns:
        Viaje o None: El viaje activo del crucero si existe, None en caso contrario.
    """
    return crucero.viajes.filter(estado='activo').order_by('fecha_inicio').first()


def __calcular_dia_actual(viaje: Any, fecha_actual: datetime.date) -> int:
    """Calcula el día actual de un viaje basado en la fecha del sistema.
    
    Args:
        viaje (Viaje): Instancia del modelo Viaje.
        fecha_actual (datetime.date): Fecha actual del sistema.
        
    Returns:
        int: Día actual del viaje (mínimo 1).
    """
    if not viaje.fecha_inicio:
        return 1
        
    dia_actual = (fecha_actual - viaje.fecha_inicio).days + 1
    return max(dia_actual, 1)


def obtener_proximo_puerto(crucero_id: int) -> Optional[str]:
    """Obtiene el nombre del próximo puerto en el itinerario del crucero.
    
    Busca el siguiente puerto futuro en el viaje activo del crucero.
    
    Args:
        crucero_id (int): ID del crucero a consultar.
        
    Returns:
        str o None: Nombre del próximo puerto si existe, 
        None si no hay viaje activo o no hay más puertos pendientes.
        
    Raises:
        Crucero.DoesNotExist: Si el crucero no existe (manejado internamente).
    """
    if not crucero_id:
        return None
        
    try:
        crucero = Crucero.objects.get(pk=crucero_id)
    except Crucero.DoesNotExist:
        return None

    viaje = __obtener_viaje_activo(crucero)
    if not viaje or not viaje.fecha_inicio:
        return None

    fecha_actual = obtener_fecha_actual()
    if not fecha_actual:
        return None
        
    dia_actual = __calcular_dia_actual(viaje, fecha_actual)

    # Buscar la próxima etapa de tipo puerto
    etapa_futura = (viaje.ruta.etapas
                    .filter(dia_llegada__gt=dia_actual, tipo='puerto')
                    .order_by('dia_llegada')
                    .first())
                    
    return etapa_futura.nombre_lugar if etapa_futura else None


def obtener_puerto_actual(crucero_id: int) -> Optional[str]:
    """Obtiene el nombre del puerto/etapa actual del crucero.
    
    Prioriza la información del EstadoViaje.etapa_actual si existe;
    de lo contrario, calcula la etapa basándose en el día actual.
    
    Args:
        crucero_id (int): ID del crucero a consultar.
        
    Returns:
        str o None: Nombre del puerto/etapa actual si puede determinarse,
        None si no hay viaje activo o no se puede determinar la etapa.
    """
    if not crucero_id:
        return None
        
    try:
        crucero = Crucero.objects.get(pk=crucero_id)
    except Crucero.DoesNotExist:
        return None

    viaje = __obtener_viaje_activo(crucero)
    if not viaje or not viaje.fecha_inicio:
        return None

    # Intentar obtener del estado del viaje primero
    estado_viaje = getattr(viaje, 'estado_actual', None)
    if estado_viaje and estado_viaje.etapa_actual:
        return estado_viaje.etapa_actual.nombre_lugar

    # Calcular basándose en la fecha actual
    fecha_actual = obtener_fecha_actual()
    if not fecha_actual:
        return None
        
    dia_actual = __calcular_dia_actual(viaje, fecha_actual)
    if dia_actual < 1:
        return None
        
    etapa = viaje.ruta.etapas.filter(dia_llegada=dia_actual).first()
    return etapa.nombre_lugar if etapa else None

