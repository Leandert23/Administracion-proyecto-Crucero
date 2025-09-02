from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone

from mantenimiento.models import ReporteIncidente
from mantenimiento.forms import ReporteIncidenteForm


def incidente_list(request):
    incidentes = ReporteIncidente.objects.select_related('ubicacion', 'equipo', 'reportado_por').all()

    severidad = request.GET.get('severidad')
    resuelto = request.GET.get('resuelto')

    if severidad:
        incidentes = incidentes.filter(severidad=severidad)
    if resuelto:
        incidentes = incidentes.filter(resuelto=resuelto == 'true')

    paginator = Paginator(incidentes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj, 'severidades': ReporteIncidente.SEVERIDADES}
    return render(request, 'mantenimiento/incidente_list.html', context)


def incidente_create(request):
    if request.method == 'POST':
        form = ReporteIncidenteForm(request.POST)
        if form.is_valid():
            incidente = form.save(commit=False)
            if hasattr(request, 'user') and request.user.is_authenticated:
                incidente.reportado_por = request.user
            incidente.save()

            if form.cleaned_data.get('generar_tarea', True):
                try:
                    tarea = incidente.generar_tarea_correctiva(
                        usuario=request.user if request.user.is_authenticated else None
                    )
                    messages.success(request, f'Incidente reportado y tarea correctiva #{tarea.id} generada automáticamente.')
                    return redirect('mantenimiento:tarea_detail', pk=tarea.pk)
                except Exception as e:
                    messages.warning(request, f'Incidente creado, pero no se pudo generar la tarea: {str(e)}')
            else:
                messages.success(request, 'Incidente reportado exitosamente.')

            return redirect('mantenimiento:incidente_detail', pk=incidente.pk)
    else:
        form = ReporteIncidenteForm()

    return render(request, 'mantenimiento/incidente_form.html', {'form': form, 'action': 'Crear'})


def incidente_detail(request, pk):
    incidente = get_object_or_404(ReporteIncidente, pk=pk)
    return render(request, 'mantenimiento/incidente_detail.html', {'incidente': incidente})


def incidente_update(request, pk):
    incidente = get_object_or_404(ReporteIncidente, pk=pk)
    if request.method == 'POST':
        form = ReporteIncidenteForm(request.POST, instance=incidente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Incidente actualizado exitosamente.')
            return redirect('mantenimiento:incidente_detail', pk=pk)
    else:
        form = ReporteIncidenteForm(instance=incidente)

    return render(request, 'mantenimiento/incidente_form.html', {'form': form, 'action': 'Editar', 'incidente': incidente})


def incidente_resolver(request, pk):
    incidente = get_object_or_404(ReporteIncidente, pk=pk)
    if not incidente.resuelto:
        incidente.resuelto = True
        incidente.fecha_resolucion = timezone.now()
        incidente.save()
        messages.success(request, 'Incidente resuelto exitosamente.')
    else:
        messages.error(request, 'El incidente ya está resuelto.')
    return redirect('mantenimiento:incidente_detail', pk=pk)


