from django.shortcuts import render, redirect, get_object_or_404
from .models import Crucero, FechaDelSistema
from apps.usuarios.models import ModuloSistema
from .forms import creacionCruceroForm, AsignarRutaForm, CruceroEditForm
from ..reservaciones.utils import rellenar_entretenimiento, rellenar_restaurantes
from .Services.creacion_rutas_por_plantilla import cargar_rutas_desde_json
from .Services.creacion_productos_predeterminados import crear_productos_predeterminados
from .Services.vista_helpers import (
    obtener_fecha_sistema,
    avanzar_dia,
    construir_contexto_preview,
)
from apps.almacen.signals import emitir_señal_si_falta_stock_general_en

def lista_cruceros(request):
    fecha_sistema = obtener_fecha_sistema()
    cruceros = Crucero.objects.all()

    if request.method == 'POST':
        if 'advance_day' in request.POST:
            avanzar_dia(fecha_sistema, cruceros)
            for crucero in cruceros:
                emitir_señal_si_falta_stock_general_en(crucero)
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
    # Guardar datos en sesión para reconstruir el formulario tras redirect (PRG)
    request.session['form_crucero_data'] = request.POST.dict()
    return redirect('lista_cruceros')

def _renderizar_lista_cruceros(request, cruceros, fecha_sistema):
    session_data = request.session.pop('form_crucero_data', None)
    if session_data:
        form = creacionCruceroForm(session_data)
        # Forzar validación para que se generen los errores que se mostraran en la plantilla
        form.is_valid()  # no importa si es inválido, solo pobla form.errors
    else:
        form = creacionCruceroForm()
    return render(request, 'cruceros/lista_cruceros.html', {
        'cruceros': cruceros,
        'form': form,
        'fecha_sistema': fecha_sistema.fecha_actual,
    })

def mostrar_inicio(request, crucero_id):
    crucero = get_object_or_404(Crucero, pk=crucero_id)

    # obtener módulos accesibles por el usuario para renderizar el sidebar
    if request.user.is_authenticated and hasattr(request.user, 'get_modulos_activos'):
        modulos_usuario = request.user.get_modulos_activos()
    else:
        modulos_usuario = ModuloSistema.objects.filter(activo=True)
    
    if request.method == 'POST' and request.POST.get('accion') == 'editar_crucero':
        form_edit = CruceroEditForm(request.POST, instance=crucero)
        if form_edit.is_valid():
            form_edit.save()
            return redirect('gestion_crucero', crucero_id=crucero.id)
    else:
        form_edit = CruceroEditForm(instance=crucero)
    
    if crucero.viajes.filter(estado="activo").count() == 0 and crucero.viajes.filter(estado = "planificacion").count() == 0:
        return _manejar_crucero_sin_viajes(request, crucero, modulos_usuario)

    return _mostrar_vista_inicio(request, crucero, form_edit, modulos_usuario)

def _manejar_crucero_sin_viajes(request, crucero, modulos_usuario):
    cargar_rutas_desde_json()

    if request.method == 'POST':
        return _procesar_asignacion_ruta(request, crucero, modulos_usuario)

    return _mostrar_formulario_asignacion(request, crucero, modulos_usuario)

def _procesar_asignacion_ruta(request, crucero, modulos_usuario):
    form = AsignarRutaForm(request.POST)
    if form.is_valid():
        viaje = form.save(commit=False)
        viaje.crucero = crucero
        viaje.estado = 'planificacion'
        viaje.save()
    # Crear productos predeterminados según plantilla del tipo de crucero
        crear_productos_predeterminados(crucero)
        rellenar_entretenimiento(crucero)
        rellenar_restaurantes(crucero)
        return redirect('gestion_crucero', crucero_id=crucero.id)
    # Volver a renderizar con errores
    return render(request, "inicio/inicio_sin_ruta.html", {
        'crucero': crucero,
        'form_asignar': form,
        'abrir_modal_asignar': True,
        'modulos_usuario': modulos_usuario,
    })

def _mostrar_formulario_asignacion(request, crucero, modulos_usuario):
    form = AsignarRutaForm()
    return render(request, "inicio/inicio_sin_ruta.html", {
        'crucero': crucero,
        'form_asignar': form,
        'modulos_usuario': modulos_usuario,
    })

def _mostrar_vista_inicio(request, crucero, form_edit, modulos_usuario):
    viajes_crucero = crucero.viajes.filter(estado__in = ["activo", "planificacion"]).order_by('fecha_inicio')
    primer_viaje = viajes_crucero.first()
    fecha_sistema = FechaDelSistema.objects.first()
    contexto = construir_contexto_preview(crucero, viajes_crucero, primer_viaje, fecha_sistema)
    contexto['form_crucero_edit'] = form_edit
    contexto['modulos_usuario'] = modulos_usuario
    return render(request, 'inicio/inicio.html', contexto)
