from django.shortcuts import render, redirect, get_object_or_404
from .models import Crucero, FechaDelSistema, Habitacion, TipoHabitacion
from .forms import creacionCruceroForm, AsignarRutaForm, CruceroEditForm
from .Services.creacion_rutas_por_plantilla import cargar_rutas_desde_json
from .Services.vista_helpers import (
    obtener_fecha_sistema,
    avanzar_dia,
    construir_contexto_preview,
)

def lista_cruceros(request):
    fecha_sistema = obtener_fecha_sistema()
    cruceros = Crucero.objects.all()

    if request.method == 'POST':
        if 'advance_day' in request.POST:
            avanzar_dia(fecha_sistema, cruceros)
            return redirect('lista_cruceros')
        else:
            respuesta = _procesar_formulario_crucero(request)
            if respuesta:
                return respuesta

    return _renderizar_lista_cruceros(request, cruceros, fecha_sistema)

def _procesar_formulario_crucero(request):
    form = creacionCruceroForm(request.POST)
    if form.is_valid():
        form.crear_crucero()
        return redirect('lista_cruceros')
    return None

def _renderizar_lista_cruceros(request, cruceros, fecha_sistema):
    form = creacionCruceroForm()
    return render(request, 'cruceros/lista_cruceros.html', {
        'cruceros': cruceros,
        'form': form,
        'fecha_sistema': fecha_sistema.fecha_actual,
    })

def mostrar_inicio(request, crucero_id):
    crucero = get_object_or_404(Crucero, pk=crucero_id)
    
    if request.method == 'POST' and request.POST.get('accion') == 'editar_crucero':
        form_edit = CruceroEditForm(request.POST, instance=crucero)
        if form_edit.is_valid():
            form_edit.save()
            return redirect('gestion_crucero', crucero_id=crucero.id)
    else:
        form_edit = CruceroEditForm(instance=crucero)
    
    if crucero.viajes.filter(estado="activo").count() == 0 and crucero.viajes.filter(estado = "planificacion").count() == 0:
        return _manejar_crucero_sin_viajes(request, crucero)
    
    return _mostrar_vista_inicio(request, crucero, form_edit)

def _manejar_crucero_sin_viajes(request, crucero):
    cargar_rutas_desde_json()
    
    if request.method == 'POST':
        return _procesar_asignacion_ruta(request, crucero)
    
    return _mostrar_formulario_asignacion(request, crucero)

def _procesar_asignacion_ruta(request, crucero):
    form = AsignarRutaForm(request.POST)
    if form.is_valid():
        viaje = form.save(commit=False)
        viaje.crucero = crucero
        viaje.estado = 'planificacion'
        viaje.save()
        return redirect('gestion_crucero', crucero_id=crucero.id)
    return None

def _mostrar_formulario_asignacion(request, crucero):
    form = AsignarRutaForm()
    return render(request, "inicio/inicio_sin_ruta.html", {
        'crucero': crucero,
        'form_asignar': form,
    })

def _mostrar_vista_inicio(request, crucero, form_edit):
    viajes_crucero = crucero.viajes.filter(estado__in = ["activo", "planificacion"]).order_by('fecha_inicio')
    primer_viaje = viajes_crucero.first()
    fecha_sistema = FechaDelSistema.objects.first()
    contexto = construir_contexto_preview(crucero, viajes_crucero, primer_viaje, fecha_sistema)
    contexto['form_crucero_edit'] = form_edit
    return render(request, 'inicio/inicio.html', contexto)
