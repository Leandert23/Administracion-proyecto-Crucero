from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Administracion, Alerta
#from apps.compras.models import Compras

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
Recibe la señal el modulo compras
ese es el receiver de la señal de alerta de que les pasaron el presupuesto

@monto_mensaje_signal.connect
def monto_mensaje_receiver(sender, **kwargs):
    monto = kwargs.get('monto')
    mensaje = kwargs.get('mensaje')
    print(f"Signal recibido: Monto={monto}, Mensaje={mensaje}")
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