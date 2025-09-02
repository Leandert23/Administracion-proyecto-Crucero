from django.db import transaction
from django.core.exceptions import ValidationError

from mantenimiento.models import AsignacionPersonal


@transaction.atomic
def ocupar_personal(asignacion: AsignacionPersonal):
    """Marca una asignación en progreso y valida exclusividad por técnico."""
    if AsignacionPersonal.objects.filter(
        personal=asignacion.personal,
        estado='en_progreso',
    ).exclude(pk=asignacion.pk).exists():
        raise ValidationError('El técnico ya está ocupado en otra tarea.')

    asignacion.estado = 'en_progreso'
    asignacion.save(update_fields=['estado'])
    return asignacion


@transaction.atomic
def liberar_personal(asignacion: AsignacionPersonal):
    asignacion.estado = 'completado'
    asignacion.save(update_fields=['estado'])
    return asignacion


