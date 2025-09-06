from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from ..models import Piscina
from ..forms import PiscinaForm, MedicionPiscinaForm
from ..core.services import PiscinaService, ValidationService


def piscina_list(request):
    """Lista de piscinas optimizada"""
    try:
        piscinas_info = PiscinaService.get_piscinas_with_alerts()
        
        total_piscinas = len(piscinas_info)
        piscinas_con_alerta = sum(1 for p in piscinas_info if p['tiene_alerta'])
        
        return render(request, 'mantenimiento/piscina_list.html', {
            'piscinas_con_alertas': piscinas_info,
            'total_piscinas': total_piscinas,
            'piscinas_con_alerta': piscinas_con_alerta,
            'piscinas_normales': total_piscinas - piscinas_con_alerta,
        })
    except Exception as e:
        messages.error(request, f'Error al cargar piscinas: {str(e)}')
        return render(request, 'mantenimiento/piscina_list.html', {})


def piscina_create(request):
    if request.method == 'POST':
        form = PiscinaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Piscina creada exitosamente.')
            return redirect('mantenimiento:piscina_list')
    else:
        form = PiscinaForm()
    return render(request, 'mantenimiento/piscina_form.html', {'form': form, 'action': 'Crear'})


def piscina_update(request, pk):
    piscina = get_object_or_404(Piscina, pk=pk)
    if request.method == 'POST':
        form = PiscinaForm(request.POST, instance=piscina)
        if form.is_valid():
            form.save()
            messages.success(request, 'Piscina actualizada exitosamente.')
            return redirect('mantenimiento:piscina_list')
    else:
        form = PiscinaForm(instance=piscina)
    return render(request, 'mantenimiento/piscina_form.html', {'form': form, 'action': 'Editar', 'piscina': piscina})


def piscina_detail(request, pk):
    piscina = get_object_or_404(Piscina, pk=pk)
    mediciones = piscina.mediciones.all()[:20]
    return render(request, 'mantenimiento/piscina_detail.html', {'piscina': piscina, 'mediciones': mediciones})


def medicion_piscina_create(request):
    if request.method == 'POST':
        form = MedicionPiscinaForm(request.POST)
        if form.is_valid():
            medicion = form.save()
            if medicion.necesita_alerta:
                try:
                    messages.warning(request, f'Medición registrada. ALERTA: {medicion.tipo_alerta}.')
                except Exception:
                    messages.warning(request, f'Medición registrada con alerta: {medicion.tipo_alerta}.')
            else:
                messages.success(request, 'Medición registrada exitosamente - Parámetros normales.')
            return redirect('mantenimiento:piscina_detail', pk=medicion.piscina.pk)
    else:
        form = MedicionPiscinaForm()
    return render(request, 'mantenimiento/medicion_piscina_form.html', {'form': form})


def piscina_trends(request, pk):
    """Tendencias de piscina optimizada"""
    try:
        data = PiscinaService.get_trends_data(pk, days=14)
        if not data:
            messages.error(request, 'Piscina no encontrada')
            return redirect('mantenimiento:piscina_list')
        
        return render(request, 'mantenimiento/piscina_trends.html', {
            **data,
            'dias_datos': 14,
        })
    except Exception as e:
        messages.error(request, f'Error al cargar tendencias: {str(e)}')
        return redirect('mantenimiento:piscina_list')


@require_GET
def piscina_update_data(request, pk):
    """Actualización AJAX de datos de piscina"""
    try:
        data = PiscinaService.get_trends_data(pk, days=14)
        if not data:
            return JsonResponse({'success': False, 'error': 'Piscina no encontrada'})
        
        return JsonResponse({
            'success': True,
            'data': {
                'fechas': data['fechas'],
                'ph_values': data['ph_values'],
                'cloro_values': data['cloro_values'],
                'temperatura_values': data['temperatura_values']
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


