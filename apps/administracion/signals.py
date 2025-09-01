from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Compra, Administracion, Alerta

@receiver(post_save, sender=Compra)
def actualizar_presupuesto(sender, instance, created, **kwargs):
    if created:
        admin = Administracion.objects.first()
        admin.presupuesto_estimado -= instance.monto
        admin.save()
        Alerta.objects.create(
            mensaje=f'Nueva compra registrada: {instance.descripcion}',
            administracion=admin
        )
