from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator

from mantenimiento.models import Equipo
from mantenimiento.forms import EquipoForm


def equipo_list(request):
    equipos = Equipo.objects.select_related('tipo_equipo', 'ubicacion').all()
    paginator = Paginator(equipos, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'mantenimiento/equipo_list.html', {'page_obj': page_obj})


def equipo_create(request):
    if request.method == 'POST':
        form = EquipoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo creado correctamente.')
            return redirect('mantenimiento:equipo_list')
    else:
        form = EquipoForm()
    return render(request, 'mantenimiento/equipo_form.html', {'form': form, 'action': 'Crear'})


def equipo_detail(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    return render(request, 'mantenimiento/equipo_detail.html', {'equipo': equipo})


def equipo_update(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    if request.method == 'POST':
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipo actualizado.')
            return redirect('mantenimiento:equipo_detail', pk=pk)
    else:
        form = EquipoForm(instance=equipo)
    return render(request, 'mantenimiento/equipo_form.html', {'form': form, 'action': 'Editar', 'equipo': equipo})


def equipo_delete(request, pk):
    equipo = get_object_or_404(Equipo, pk=pk)
    if request.method == 'POST':
        equipo.delete()
        messages.success(request, 'Equipo eliminado.')
        return redirect('mantenimiento:equipo_list')
    return render(request, 'mantenimiento/equipo_confirm_delete.html', {'equipo': equipo})


