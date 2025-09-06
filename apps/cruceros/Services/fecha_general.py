from ..models import FechaDelSistema

def obtener_fecha_actual():
    return FechaDelSistema.objects.first().fecha_actual