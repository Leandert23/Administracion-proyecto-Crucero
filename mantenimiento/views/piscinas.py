from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from mantenimiento.models import Piscina
from mantenimiento.forms import PiscinaForm, MedicionPiscinaForm


def piscina_list(request):
    piscinas = Piscina.objects.select_related('ubicacion', 'tipo_crucero').prefetch_related('mediciones')

    piscinas_con_alertas = []
    for piscina in piscinas:
        ultima_medicion = piscina.mediciones.first()
        alerta_info = {
            'piscina': piscina,
            'ultima_medicion': ultima_medicion,
            'tiene_alerta': False,
            'tipo_alerta': '',
            'dias_sin_medicion': None,
        }
        if ultima_medicion:
            if ultima_medicion.necesita_alerta:
                alerta_info['tiene_alerta'] = True
                alerta_info['tipo_alerta'] = ultima_medicion.tipo_alerta
            dias_sin_medicion = (timezone.now().date() - ultima_medicion.fecha_hora.date()).days
            alerta_info['dias_sin_medicion'] = dias_sin_medicion
            if dias_sin_medicion > 1:
                alerta_info['tiene_alerta'] = True
                if alerta_info['tipo_alerta']:
                    alerta_info['tipo_alerta'] += ' / '
                alerta_info['tipo_alerta'] += f'SIN MEDICIÓN ({dias_sin_medicion} días)'
        else:
            alerta_info['tiene_alerta'] = True
            alerta_info['tipo_alerta'] = 'SIN MEDICIONES'
        piscinas_con_alertas.append(alerta_info)

    total_piscinas = len(piscinas_con_alertas)
    piscinas_con_alerta = sum(1 for p in piscinas_con_alertas if p['tiene_alerta'])

    return render(request, 'mantenimiento/piscina_list.html', {
        'piscinas_con_alertas': piscinas_con_alertas,
        'total_piscinas': total_piscinas,
        'piscinas_con_alerta': piscinas_con_alerta,
        'piscinas_normales': total_piscinas - piscinas_con_alerta,
    })


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
    piscina = get_object_or_404(Piscina, pk=pk)
    fecha_limite = timezone.now() - timedelta(days=14)
    mediciones = piscina.mediciones.filter(fecha_hora__gte=fecha_limite).order_by('fecha_hora')

    fechas, ph_values, cloro_values, temperatura_values = [], [], [], []
    for m in mediciones:
        fechas.append(m.fecha_hora.strftime('%Y-%m-%d %H:%M'))
        ph_values.append(float(m.ph) if m.ph else None)
        cloro_values.append(float(m.cloro_mg_l) if m.cloro_mg_l else None)
        temperatura_values.append(float(m.temperatura_c) if m.temperatura_c else None)

    ultima_medicion = mediciones.last()
    recomendaciones = []
    if ultima_medicion:
        if ultima_medicion.necesita_alerta:
            recomendaciones.append(f"🚨 ALERTA: {ultima_medicion.tipo_alerta}")
        recomendaciones.append(f"💡 {ultima_medicion.recomendacion}")

    return render(request, 'mantenimiento/piscina_trends.html', {
        'piscina': piscina,
        'mediciones': mediciones,
        'fechas': fechas,
        'ph_values': ph_values,
        'cloro_values': cloro_values,
        'temperatura_values': temperatura_values,
        'ultima_medicion': ultima_medicion,
        'recomendaciones': recomendaciones,
        'dias_datos': 14,
    })


