from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages

from ..models import Ubicacion
from ..forms import UbicacionForm


def ubicacion_list(request):
    ubicaciones = Ubicacion.objects.all().order_by('cubierta', 'uso', 'identificador', 'numero')

    cubierta = request.GET.get('cubierta')
    uso = request.GET.get('uso')
    activa = request.GET.get('activa')

    if cubierta:
        ubicaciones = ubicaciones.filter(cubierta=cubierta)
    if uso:
        ubicaciones = ubicaciones.filter(uso=uso)
    if activa:
        ubicaciones = ubicaciones.filter(activa=activa == 'true')

    paginator = Paginator(ubicaciones, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'cubiertas': range(1, 19),
        'usos': Ubicacion.USOS_UBICACION,
    }
    return render(request, 'mantenimiento/ubicacion_list.html', context)


def ubicacion_create(request):
    if request.method == 'POST':
        form = UbicacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ubicación creada correctamente.')
            return redirect('mantenimiento:ubicacion_list')
    else:
        form = UbicacionForm()
    return render(request, 'mantenimiento/ubicacion_form.html', {'form': form, 'action': 'Crear'})


def ubicacion_detail(request, pk):
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    return render(request, 'mantenimiento/ubicacion_detail.html', {'ubicacion': ubicacion})


def ubicacion_update(request, pk):
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    if request.method == 'POST':
        form = UbicacionForm(request.POST, instance=ubicacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ubicación actualizada.')
            return redirect('mantenimiento:ubicacion_detail', pk=pk)
    else:
        form = UbicacionForm(instance=ubicacion)
    return render(request, 'mantenimiento/ubicacion_form.html', {'form': form, 'action': 'Editar', 'ubicacion': ubicacion})


def ubicacion_delete(request, pk):
    ubicacion = get_object_or_404(Ubicacion, pk=pk)
    if request.method == 'POST':
        ubicacion.delete()
        messages.success(request, 'Ubicación eliminada.')
        return redirect('mantenimiento:ubicacion_list')
    return render(request, 'mantenimiento/ubicacion_confirm_delete.html', {'ubicacion': ubicacion})


