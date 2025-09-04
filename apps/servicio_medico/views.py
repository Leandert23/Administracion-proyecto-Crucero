from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.http import HttpResponse
from .models import Medico, Paciente, Inventario, Solicitudmedicamento, cuarto
from .forms import MedicoForm, PacienteForm, InventarioForm, SolicitudMedicamentoForm
from django.shortcuts import render, redirect
from almacen.Services.products import save_product, remove_product




# Vista para editar un paciente
def editar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('historial_medico')
    else:
        form = PacienteForm(instance=paciente)
    return render(request, 'editar_paciente.html', {'form': form, 'paciente': paciente})

# Vista para eliminar un paciente (con confirmación por POST)
def eliminar_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    if request.method == 'POST':
        paciente.delete()
        return redirect('historial_medico')
    return render(request, 'eliminar_paciente.html', {'paciente': paciente})

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
    cuartos = cuarto.objects.all().order_by('numero')
    context = {
        'medico': medico or {'nombres': 'Nombre', 'apellido': 'Apellido'},
        'solicitudes': solicitudes,
        'pacientes': pacientes,
        'inventario': inventario,
        'cuartos': cuartos,
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

def comunicacion_mantenmiento(request):
    if request.method == 'POST':
        # Aquí puedes manejar el formulario enviado
        pass
    return render(request, 'comunicacion_mantenimiento.html')

def modificar_cuartos(request):
    if request.method == 'POST':
        cuarto_numero = request.POST.get('cuarto_numero')
        nuevo_estado = request.POST.get(f'estado_{cuarto_numero}')
        paciente_id = request.POST.get(f'paciente_{cuarto_numero}')
        try:
            cuarto_obj = cuarto.objects.get(numero=cuarto_numero)
            cuarto_obj.estado = nuevo_estado
            if nuevo_estado == 'O':
                if not paciente_id:
                    return HttpResponse("Debe seleccionar un paciente para ocupar el cuarto.", status=400)
                cuarto_obj.paciente_id = paciente_id
            else:
                cuarto_obj.paciente = None
            cuarto_obj.save()
            return redirect('panel_personal_medico')
        except cuarto.DoesNotExist:
            return HttpResponse("Cuarto no encontrado", status=404)
    else:
        cuartos = cuarto.objects.all().order_by('numero')
        pacientes = Paciente.objects.all()
        return render(request, 'modificar_cuartos.html', {'cuartos': cuartos, 'pacientes': pacientes})
    
# Vista para agregar un elemento al inventario
def agregar_inventario(request):
    if request.method == 'POST':
        form = InventarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('panel_inventario')
    else:
        form = InventarioForm()
    return render(request, 'agregar_inventario.html', {'form': form})

def editar_inventario(request, inventario_id):
    inventario = get_object_or_404(Inventario, id=inventario_id)
    if request.method == 'POST':
        form = InventarioForm(request.POST, instance=inventario)
        if form.is_valid():
            form.save()
            return redirect('panel_inventario')
    else:
        form = InventarioForm(instance=inventario)
    return render(request, 'editar_inventario.html', {'form': form, 'inventario': inventario})

