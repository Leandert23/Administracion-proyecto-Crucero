from django.dispatch import receiver, Signal
from .models import Administracion
from apps.compras.signals import solicitud_compra_administracion_signal

@receiver(solicitud_compra_administracion_signal)
def manejar_solicitud_compra_administracion(sender, id, monto, mensaje, **kwargs):
    # Actualizar/registrar información administrativa si aplica
    try:
        print(f"Solicitud recibida: id={id}, monto={monto}, mensaje={mensaje}")
        admin = Administracion.objects.filter(id=id).first()
        if admin is not None and monto is not None:
            admin.costos_totales = (admin.costos_totales or 0) + monto
            admin.save()
    except Exception as e:
        print(f"[ADMIN] No se pudo actualizar costos_totales para id={id}: {e}")

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

# Helpers explícitos para uso desde administración (UI/Views/Forms)
def aprobar_solicitud_compra(id, mensaje=None):
    """Aprueba una solicitud de compra desde administración."""
    decision_solicitud(id=id, aceptado=True, mensaje=mensaje or "Aprobado por administración")

def rechazar_solicitud_compra(id, mensaje=None):
    """Rechaza una solicitud de compra desde administración."""
    decision_solicitud(id=id, aceptado=False, mensaje=mensaje or "Rechazado por administración")