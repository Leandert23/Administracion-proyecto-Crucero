from django.dispatch import receiver, Signal
from .models import Administracion
from apps.compras.signals import solicitud_compra_administracion_signal
import threading

# Arreglo global para almacenar las solicitudes de compra
solicitudes_compra = []
lock = threading.Lock()

@receiver(solicitud_compra_administracion_signal)
def manejar_solicitud_compra_administracion(sender, id, monto, mensaje, **kwargs):
    # Actualizar/registrar información administrativa si aplica
    try:
        print(f"Solicitud recibida: id={id}, monto={monto}, mensaje={mensaje}")
        
        # Obtener el dashboard asociado al crucero
        admin = Administracion.objects.get(id=id)
        
        # Crear el objeto de solicitud
        solicitud_data = {
            'id': id,
            'monto': monto,
            'mensaje': mensaje,
            'crucero_id': admin.crucero.id,
            'crucero_nombre': admin.crucero.nombre,
            'fecha': admin.crucero.fecha_creacion if hasattr(admin.crucero, 'fecha_creacion') else None,
            'estado': 'Pendiente'
        }
        
        # Agregar la solicitud al arreglo de forma thread-safe
        with lock:
            solicitudes_compra.append(solicitud_data)
            print(f"[ADMIN] Solicitud agregada al arreglo: {solicitud_data}")
            
    except Exception as e:
        print(f"[ADMIN] No se pudo procesar solicitud para id={id}: {e}")

def obtener_solicitudes_compra(crucero_id=None):
    """
    Obtiene las solicitudes de compra, opcionalmente filtradas por crucero_id
    """
    with lock:
        if crucero_id:
            return [s for s in solicitudes_compra if s.get('crucero_id') == crucero_id]
        return solicitudes_compra.copy()

## Sender: decisión de solicitud hacia Compras
# Señal que será recibida por el receiver en apps/compras/signals.py
decision_solicitud_signal = Signal()

def decision_solicitud(id, aceptado, mensaje=None):
    """
    Envía la decisión administrativa de una solicitud de compra hacia Compras.

    Parámetros:
    - id: identificador de la CompraLote / solicitud
    - aceptado: bool que indica si se aprueba o rechaza
    - mensaje: texto opcional con notas/razón
    """
    if mensaje is None:
        mensaje = "Sin comentarios"
    if mensaje is None and not aceptado:
        return "Se debe dar una razón del rechazo de la orden"
    decision_solicitud_signal.send(sender=None, id=id, aceptado=aceptado, mensaje=mensaje)