from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Reserva, ServicioReserva
from ventas.models import Venta, DetalleVenta


@receiver(post_save, sender=Reserva)
def crear_venta_desde_reserva(sender, instance, created, **kwargs):
    """
    Señal que se ejecuta cuando se crea o actualiza una reserva.
    Si la reserva se confirma, crea automáticamente una venta en la app de Ventas.
    """
    if instance.estado == 'confirmada':
        # Verificar si ya existe una venta para esta reserva
        venta_existente = Venta.objects.filter(
            tipo_venta='reserva',
            descripcion__contains=f'Reserva #{instance.id}'
        ).first()
        
        if not venta_existente:
            # Crear nueva venta
            venta = Venta.objects.create(
                cliente=instance.cliente,
                tipo_venta='reserva',
                descripcion=f'Reserva #{instance.id} - {instance.viaje.barco.nombre} - {instance.viaje.ruta.nombre}',
                monto_total=instance.precio_total,
                estado='confirmada',
                vendedor=instance.agente,
                notas=f'Reserva automática generada desde el sistema de reservas. Viaje: {instance.viaje.fecha_salida.strftime("%d/%m/%Y")}'
            )
            
            # Crear detalle de venta para la cabina
            DetalleVenta.objects.create(
                venta=venta,
                concepto=f'Cabina {instance.cabina.numero} - {instance.cabina.tipo_cabina.nombre}',
                cantidad=1,
                precio_unitario=instance.precio_total,
                subtotal=instance.precio_total
            )
            
            # Crear detalles para servicios adicionales si los hay
            servicios = instance.servicios.all()
            for servicio in servicios:
                DetalleVenta.objects.create(
                    venta=venta,
                    concepto=f'Servicio: {servicio.servicio.nombre}',
                    cantidad=servicio.cantidad,
                    precio_unitario=servicio.precio_unitario,
                    subtotal=servicio.subtotal
                )
                
                # Actualizar monto total de la venta
                venta.monto_total += servicio.subtotal
                venta.save()
        
        elif venta_existente and instance.precio_total != venta_existente.monto_total:
            # Actualizar monto total si cambió
            venta_existente.monto_total = instance.precio_total
            venta_existente.save()
            
            # Actualizar o crear detalle de la cabina
            detalle_cabina, created = DetalleVenta.objects.get_or_create(
                venta=venta_existente,
                concepto__contains='Cabina',
                defaults={
                    'concepto': f'Cabina {instance.cabina.numero} - {instance.cabina.tipo_cabina.nombre}',
                    'cantidad': 1,
                    'precio_unitario': instance.precio_total,
                    'subtotal': instance.precio_total
                }
            )
            
            if not created:
                detalle_cabina.precio_unitario = instance.precio_total
                detalle_cabina.subtotal = instance.precio_total
                detalle_cabina.save()


@receiver(post_save, sender=ServicioReserva)
def actualizar_venta_por_servicio(sender, instance, created, **kwargs):
    """
    Señal que se ejecuta cuando se agrega o modifica un servicio en una reserva.
    Actualiza la venta correspondiente.
    """
    if instance.reserva.estado == 'confirmada':
        # Buscar la venta correspondiente
        venta = Venta.objects.filter(
            tipo_venta='reserva',
            descripcion__contains=f'Reserva #{instance.reserva.id}'
        ).first()
        
        if venta:
            if created:
                # Agregar nuevo detalle de servicio
                DetalleVenta.objects.create(
                    venta=venta,
                    concepto=f'Servicio: {instance.servicio.nombre}',
                    cantidad=instance.cantidad,
                    precio_unitario=instance.precio_unitario,
                    subtotal=instance.subtotal
                )
                
                # Actualizar monto total
                venta.monto_total += instance.subtotal
                venta.save()
            else:
                # Actualizar detalle existente
                detalle = DetalleVenta.objects.filter(
                    venta=venta,
                    concepto__contains=f'Servicio: {instance.servicio.nombre}'
                ).first()
                
                if detalle:
                    # Calcular diferencia para actualizar monto total
                    diferencia = instance.subtotal - detalle.subtotal
                    detalle.cantidad = instance.cantidad
                    detalle.precio_unitario = instance.precio_unitario
                    detalle.subtotal = instance.subtotal
                    detalle.save()
                    
                    venta.monto_total += diferencia
                    venta.save()


@receiver(post_delete, sender=ServicioReserva)
def eliminar_servicio_de_venta(sender, instance, **kwargs):
    """
    Señal que se ejecuta cuando se elimina un servicio de una reserva.
    Actualiza la venta correspondiente.
    """
    if instance.reserva.estado == 'confirmada':
        venta = Venta.objects.filter(
            tipo_venta='reserva',
            descripcion__contains=f'Reserva #{instance.reserva.id}'
        ).first()
        
        if venta:
            # Buscar y eliminar el detalle del servicio
            detalle = DetalleVenta.objects.filter(
                venta=venta,
                concepto__contains=f'Servicio: {instance.servicio.nombre}'
            ).first()
            
            if detalle:
                # Restar del monto total
                venta.monto_total -= detalle.subtotal
                venta.save()
                detalle.delete()


@receiver(post_save, sender=Reserva)
def cancelar_venta_si_reserva_cancelada(sender, instance, **kwargs):
    """
    Señal que se ejecuta cuando se cancela una reserva.
    Cancela la venta correspondiente.
    """
    if instance.estado == 'cancelada':
        venta = Venta.objects.filter(
            tipo_venta='reserva',
            descripcion__contains=f'Reserva #{instance.id}'
        ).first()
        
        if venta:
            venta.estado = 'cancelada'
            venta.save()
