from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Administracion, Alerta
'''''''''
from apps.compras.compras.signals import compra_defectosa
from apps.compras.compras.signals import solicitud_compra_administracion_signal

@receiver(solicitud_compra_administracion_signal)
def manejar_solicitud_compra_administracion(sender, id, monto, mensaje, **kwargs):
    print(f"Solicitud recibida: id={id}, monto={monto}, mensaje={mensaje}")
    # Aquí puedes agregar la lógica que necesites para procesar la solicitud
    Administracion(id=id).costos_totales += monto

@receiver(compra_defectosa)
def manejar_compra_defectuosa(sender, presupuesto_lote, mensaje, **kwargs):
    # Aquí va la lógica que deseas ejecutar cuando se emite el signal
    print(f"Compra defectuosa detectada. Presupuesto: {presupuesto_lote}, Mensaje: {mensaje}")
'''''''''

'''''''''
@receiver(post_save, sender=Compras)
def actualizar_costos_totales(sender, **kwargs):
    admin = Administracion.objects.get(id=kwargs.get('cruceroId'))
    admin.costos_totales += kwargs.get('monto')
    admin.save()
    Alerta.objects.create(
        mensaje=f'Nueva compra registrada: {kwargs.get('description')}',
        administracion=admin)
'''''''''

'''''''''
Envio del presupuesto por administración
def procesar_pago(request):
    monto = 1000
    mensaje = 'Presupuesto por parada'
    monto_mensaje_signal.send(sender=procesar_pago, monto=monto, mensaje=mensaje)

    return HttpResponse("Presupuesto procesado")
'''''''''

'''''''''
Encontrar la señal en apps.py para administración->Compras
from django.apps import AppConfig

class ComprasConfig(AppConfig):
    name='apps.compras'
    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        import apps.compras.compras.signals
'''''''''

'''''''''
Recibir mensaje de que se pasa del presupuesto para dashboard
@overBudgetSignal.connect
def overBudgetReceiver(sender, **kwargs):
    monto = kwargs.get('monto')
    mensaje = kwargs.get('mensaje')
    print(f"Signal recibido: Monto={monto}, Mensaje={mensaje}")
'''''''''