"""
Configuración optimizada del sistema
"""
from decimal import Decimal


class SystemConfig:
    """Configuración centralizada y optimizada"""
    
    # Tipos de crucero
    TIPOS_CRUCERO = [
        ('pequeño', 'Crucero Pequeño (2000 pasajeros)'),
        ('mediano', 'Crucero Mediano (4000 pasajeros)'),
        ('grande', 'Crucero Grande (6000 pasajeros)'),
    ]
    
    # Capacidades por tipo
    CAPACIDADES = {
        'pequeño': {'pasajeros': 2000, 'tripulantes': 800, 'cubiertas': 12},
        'mediano': {'pasajeros': 4000, 'tripulantes': 1200, 'cubiertas': 15},
        'grande': {'pasajeros': 6000, 'tripulantes': 1800, 'cubiertas': 18}
    }


    
    # Límites operacionales
    MAX_HORAS_TAREA = Decimal('24.0')
    MAX_HORAS_TURNO_PERSONAL = Decimal('12.0')
    MIN_HORAS_TAREA = Decimal('0.5')
    
    # Rangos de piscinas
    PH_RANGO_NORMAL = (Decimal('7.2'), Decimal('7.8'))
    CLORO_RANGO_NORMAL = (Decimal('1.0'), Decimal('3.0'))
    PH_RANGO_CRITICO = (Decimal('6.8'), Decimal('8.2'))
    CLORO_RANGO_CRITICO = (Decimal('0.5'), Decimal('5.0'))
    
    # Intervalos de actualización (segundos)
    INTERVALO_ACTUALIZACION_DASHBOARD = 30
    INTERVALO_ACTUALIZACION_PISCINAS = 60
    
    @classmethod
    def get_crucero_capacidad(cls, tipo: str):
        """Obtiene la capacidad de un tipo de crucero"""
        return cls.CAPACIDADES.get(tipo, {})
    
    @classmethod
    def is_ph_critical(cls, ph: Decimal) -> bool:
        """Verifica si el pH está en rango crítico"""
        return ph < cls.PH_RANGO_CRITICO[0] or ph > cls.PH_RANGO_CRITICO[1]
    
    @classmethod
    def is_cloro_critical(cls, cloro: Decimal) -> bool:
        """Verifica si el cloro está en rango crítico"""
        return cloro < cls.CLORO_RANGO_CRITICO[0] or cloro > cls.CLORO_RANGO_CRITICO[1]
