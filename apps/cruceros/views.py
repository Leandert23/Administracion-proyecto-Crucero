from django.shortcuts import render, redirect, get_object_or_404
from .models import FechaDelSistema
from apps.creador_embarcaciones.models import Embarcacion
from apps.usuarios.models import ModuloSistema
from .forms import AsignarRutaForm, CruceroEditForm
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
    embarcaciones = Embarcacion.objects.all()

    if request.method == 'POST':
        if 'advance_day' in request.POST:
            avanzar_dia(fecha_sistema, embarcaciones)
            for embarcacion in embarcaciones:
                emitir_señal_si_falta_stock_general_en(embarcacion)
            return redirect('lista_cruceros')

    return _renderizar_lista_cruceros(request, embarcaciones, fecha_sistema)

def _renderizar_lista_cruceros(request, embarcaciones, fecha_sistema):
    return render(request, 'cruceros/lista_cruceros.html', {
        'cruceros': embarcaciones,
        'fecha_sistema': fecha_sistema.fecha_actual,
        'is_superuser': request.user.is_superuser if request.user.is_authenticated else False,
    })

def mostrar_inicio(request, crucero_id):
    crucero = get_object_or_404(Embarcacion, pk=crucero_id)
    
    if request.method == 'POST' and request.POST.get('accion') == 'editar_crucero':
        form_edit = CruceroEditForm(request.POST, instance=crucero)
        if form_edit.is_valid():
            form_edit.save()
            return redirect('gestion_crucero', crucero_id=crucero.id)
    else:
        form_edit = CruceroEditForm(instance=crucero)
    
    # El modelo Embarcacion no tiene viajes como el modelo Crucero
    # Verificar si tiene una ruta asignada
    if not crucero.ruta:
        return _manejar_embarcacion_sin_ruta(request, crucero)
    
    return _mostrar_vista_inicio(request, crucero, form_edit)

def _manejar_embarcacion_sin_ruta(request, embarcacion):
    # Para el modelo Embarcacion, no necesitamos cargar rutas desde JSON
    # Las rutas ya están disponibles en la base de datos

    if request.method == 'POST':
        return _procesar_asignacion_ruta(request, embarcacion)

    return _mostrar_formulario_asignacion(request, embarcacion)

def _procesar_asignacion_ruta(request, embarcacion):
    form = AsignarRutaForm(request.POST)
    if form.is_valid():
        # Para el modelo Embarcacion, simplemente asignamos la ruta directamente
        ruta = form.cleaned_data['ruta']
        embarcacion.ruta = ruta
        embarcacion.save()

        # Crear productos predeterminados según plantilla del tipo de embarcacion
        # Nota: Estas funciones pueden necesitar adaptación para trabajar con Embarcacion
        # crear_productos_predeterminados(embarcacion)
        # rellenar_entretenimiento(embarcacion)
        # rellenar_restaurantes(embarcacion)

        return redirect('gestion_crucero', crucero_id=embarcacion.id)
    # Volver a renderizar con errores
    return render(request, "inicio/inicio_sin_ruta.html", {
        'crucero': embarcacion,
        'form_asignar': form,
        'abrir_modal_asignar': True,
        'modulos_usuario': request.user.get_modulos_activos(),
    })

def _mostrar_formulario_asignacion(request, embarcacion):
    form = AsignarRutaForm()
    return render(request, "inicio/inicio_sin_ruta.html", {
        'crucero': embarcacion,
        'form_asignar': form,
        'modulos_usuario': request.user.get_modulos_activos(),
    })

def _mostrar_vista_inicio(request, embarcacion, form_edit):
    # Para el modelo Embarcacion, no hay viajes, solo una ruta asignada
    fecha_sistema = FechaDelSistema.objects.first()

    # Crear un contexto simplificado para la embarcación con ruta
    contexto = {
        'crucero': embarcacion,
        'viajes': [],  # Lista vacía ya que no hay viajes
        'primer_viaje': None,  # No hay viajes
        'hoy': fecha_sistema.fecha_actual if fecha_sistema else None,
        "instalaciones": [],  # Temporalmente vacío
        "distribucion_habitaciones": [],  # Temporalmente vacío
    }

    contexto['form_crucero_edit'] = form_edit
    contexto['modulos_usuario'] = request.user.get_modulos_activos()
    return render(request, 'inicio/inicio.html', contexto)
