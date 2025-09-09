from .models import Crucero


def crucero_context(request):
    """Expone el crucero seleccionado y el listado para el selector global."""
    crucero_id = request.session.get('crucero_id')
    crucero_actual = None
    if crucero_id:
        try:
            crucero_actual = Crucero.objects.get(pk=crucero_id)
        except Crucero.DoesNotExist:
            crucero_actual = None

    return {
        'cruceros': Crucero.objects.filter(activo=True).order_by('nombre'),
        'crucero_actual': crucero_actual,
    }


