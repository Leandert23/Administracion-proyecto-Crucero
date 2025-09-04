from django.shortcuts import render
from django.http import HttpResponse
from .models import Medico, Paciente, Inventario, Solicitudmedicamento, cuarto
from .forms import MedicoForm, PacienteForm, InventarioForm, SolicitudMedicamentoForm
from django.shortcuts import render, redirect



# Create your views here.

def panel_personal_medico(request):
    # Datos de ejemplo, reemplazar por consultas reales
    medico = Medico.objects.first()
    solicitudes = Solicitudmedicamento.objects.all()[:5]
    pacientes = Paciente.objects.all()[:5]
    inventario = Inventario.objects.all()[:5]
    context = {
        'medico': medico or {'nombres': 'Nombre', 'apellido': 'Apellido'},
        'solicitudes': solicitudes,
        'pacientes': pacientes,
        'inventario': inventario,
    }
    return render(request, 'personal_medico_v2.html', context)

def panel_servicio_medico(request):
    # Datos de ejemplo, reemplazar por consultas reales
    medico = Medico.objects.first()
    solicitudes = Solicitudmedicamento.objects.all()[:5]
    pacientes = Paciente.objects.all()[:5]
    inventario = Inventario.objects.all()[:5]
    context = {
        'medico': medico or {'nombres': 'Nombre', 'apellido': 'Apellido'},
        'solicitudes': solicitudes,
        'pacientes': pacientes,
        'inventario': inventario,
    }
    return render(request, 'servicio_medico.html', context)

def panel_inicio(request):
    return render(request, 'index.html')

def panel_inventario(request):
    inventario = Inventario.objects.all()
    context = {
        'inventario': inventario,
    }
    return render(request, 'inventario.html', context)

def agregar_historial(request):
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('panel_inicio')
    else:
        form = PacienteForm()
    return render(request, 'agregar_historial.html', {'form': form})

def historial_medico(request):
    from .models import Paciente
    pacientes = Paciente.objects.all()
    return render(request, 'historial_medico.html', {'pacientes': pacientes})

def prueba(request):
    return render(request, 'layouts/basetest.html')

def tu_vista_servicio_medico(request):
    cuartos_disponibles = cuarto.objects.filter(estado='D')
    return render(request, 'servicio_medico.html', {'cuartos_disponibles': cuartos_disponibles})



