from django.shortcuts import render, get_object_or_404
from apps.cruceros.models import Crucero, Instalacion
from apps.almacen.models import SeccionAlmacen

def mostrar_vista_almacen(request, crucero_id):
    crucero = get_object_or_404(Crucero, pk=crucero_id)
    instalaciones = Instalacion.objects.filter(crucero=crucero, tipo='almacen')
    secciones = SeccionAlmacen.objects.filter(almacen__in=instalaciones, esta_activa=True).select_related('almacen')
    return render(request, "almacen.html", {"crucero": crucero, 'secciones': secciones})