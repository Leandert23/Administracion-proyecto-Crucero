from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.utils import timezone

from mantenimiento.models import (
    TareaMantenimiento,
    TipoCrucero,
    ProductoUtilizado,
    Personal,
    Producto,
    HistorialMantenimiento,
    CambioEstado,
)
from mantenimiento.forms import (
    TareaMantenimientoForm,
    AsignacionPersonalForm,
    ProductoUtilizadoForm,
    ChecklistItemForm,
    AdjuntoTareaForm,
)
from mantenimiento.services.personal_service import ocupar_personal, liberar_personal


def tarea_list(request):
    tareas = TareaMantenimiento.objects.select_related('equipo', 'ubicacion', 'asignado_a').all()
    if request.session.get('crucero_id'):
        tareas = tareas.filter(crucero_id=request.session['crucero_id'])

    tipo = request.GET.get('tipo')
    estado = request.GET.get('estado')
    prioridad = request.GET.get('prioridad')
    asignado = request.GET.get('asignado')
    tipo_crucero_id = request.GET.get('tipo_crucero')
    incluir_finalizadas = request.GET.get('incluir_finalizadas') == '1'

    if tipo:
        tareas = tareas.filter(tipo=tipo)
    if estado:
        tareas = tareas.filter(estado=estado)
    if prioridad:
        tareas = tareas.filter(prioridad=prioridad)
    if asignado:
        tareas = tareas.filter(asignado_a__id=asignado)
    if tipo_crucero_id:
        tareas = tareas.filter(tipo_crucero__id=tipo_crucero_id)
    # Ocultar tareas completadas/canceladas por defecto
    if not incluir_finalizadas:
        tareas = tareas.exclude(estado__in=['completada', 'cancelada'])

    paginator = Paginator(tareas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'tipos': TareaMantenimiento.TIPOS_TAREA,
        'estados': TareaMantenimiento.ESTADOS,
        'prioridades': TareaMantenimiento.PRIORIDADES,
        'usuarios': [],  # se llenará cuando agreguemos filtros por usuario
        'tipos_crucero': TipoCrucero.objects.all(),
        'incluir_finalizadas': incluir_finalizadas,
    }
    return render(request, 'mantenimiento/tarea_list.html', context)


def tarea_create(request):
    tipo_tarea = request.GET.get('tipo')
    # Preparar formularios auxiliares con prefijos para combinar en un único <form>
    asignacion_form = AsignacionPersonalForm(request.POST or None, prefix='asig')
    producto_form = ProductoUtilizadoForm(request.POST or None, prefix='prod')
    # Filtrar listas auxiliares
    personal_disponible = Personal.objects.filter(activo=True, disponible=True)
    asignacion_form.fields['personal'].queryset = personal_disponible
    productos_activos = Producto.objects.filter(activo=True)
    producto_form.fields['producto'].queryset = productos_activos

    if request.method == 'POST':
        form = TareaMantenimientoForm(request.POST)
        # Requerimos los tres formularios válidos
        if form.is_valid() and asignacion_form.is_valid() and producto_form.is_valid():
            tarea = form.save(commit=False)
            if tipo_tarea and not tarea.tipo:
                tarea.tipo = tipo_tarea
            if hasattr(request, 'user') and request.user.is_authenticated:
                tarea.creado_por = request.user
            # Si hay crucero seleccionado en la sesión y no se eligió en el form, úsalo
            if not tarea.crucero_id and request.session.get('crucero_id'):
                tarea.crucero_id = request.session['crucero_id']
            
            # Validaciones adicionales antes de guardar
            try:
                tarea.full_clean()  # Ejecutar todas las validaciones del modelo
                tarea.save()
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field if field != '__all__' else None, error)
                return render(request, 'mantenimiento/tarea_form.html', {
                    'form': form,
                    'action': 'Crear',
                    'tipo_tarea': tipo_tarea,
                    'asignacion_form': asignacion_form,
                    'producto_form': producto_form,
                })

            # Asignación inicial de personal (requerida)
            asignacion = asignacion_form.save(commit=False)
            asignacion.tarea = tarea
            if tarea.asignaciones.filter(personal=asignacion.personal).exists():
                messages.warning(request, 'Ese personal ya está asignado a esta tarea.')
            else:
                asignacion.save()

            # Registro inicial de producto (requerido)
            pu = producto_form.save(commit=False)
            pu.tarea = tarea
            try:
                if tarea.tipo_crucero is None:
                    raise ValidationError('Asigna primero el tipo de crucero a la tarea para poder registrar productos.')
                pu.save()
            except Exception as e:
                messages.error(request, f'No se pudo registrar el producto inicial: {e}')

            messages.success(request, 'Tarea creada exitosamente.')
            return redirect('mantenimiento:tarea_list')
        else:
            # Mantener formularios con errores para mostrarlos en la misma página
            pass
    else:
        form = TareaMantenimientoForm()
        if tipo_tarea:
            form.fields['tipo'].initial = tipo_tarea

    return render(request, 'mantenimiento/tarea_form.html', {
        'form': form,
        'action': 'Crear',
        'tipo_tarea': tipo_tarea,
        'asignacion_form': asignacion_form,
        'producto_form': producto_form,
    })


def tarea_detail(request, pk):
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    productos_utilizados = ProductoUtilizado.objects.filter(tarea=tarea)
    personal_asignado = tarea.personal_asignado
    cambios_estado = tarea.cambios_estado.all()[:10]

    estados_posibles = [
        (code, name) for code, name in TareaMantenimiento.ESTADOS if tarea.puede_cambiar_estado(code)
    ]

    asignacion_form = AsignacionPersonalForm()
    producto_form = ProductoUtilizadoForm()

    personal_disponible = Personal.objects.filter(activo=True, disponible=True)
    asignacion_form.fields['personal'].queryset = personal_disponible

    productos_activos = Producto.objects.filter(activo=True)
    producto_form.fields['producto'].queryset = productos_activos

    try:
        historial = HistorialMantenimiento.objects.get(tarea=tarea)
    except HistorialMantenimiento.DoesNotExist:
        historial = None

    context = {
        'tarea': tarea,
        'productos_utilizados': productos_utilizados,
        'personal_asignado': personal_asignado,
        'cambios_estado': cambios_estado,
        'estados_posibles': estados_posibles,
        'historial': historial,
        'asignacion_form': asignacion_form,
        'producto_form': producto_form,
        'puede_iniciar': tarea.puede_iniciar,
        'materiales_necesarios': tarea.materiales_necesarios,
        'puede_finalizar': tarea.puede_cambiar_estado('completada'),
    }
    return render(request, 'mantenimiento/tarea_detail.html', context)


def tarea_update(request, pk):
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    if request.method == 'POST':
        form = TareaMantenimientoForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarea actualizada exitosamente.')
            return redirect('mantenimiento:tarea_detail', pk=pk)
    else:
        form = TareaMantenimientoForm(instance=tarea)

    return render(request, 'mantenimiento/tarea_form.html', {
        'form': form,
        'action': 'Editar',
        'tarea': tarea,
    })


def tarea_delete(request, pk):
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    if request.method == 'POST':
        tarea.delete()
        messages.success(request, 'Tarea eliminada exitosamente.')
        return redirect('mantenimiento:tarea_list')
    return render(request, 'mantenimiento/tarea_confirm_delete.html', {'tarea': tarea})


@require_POST
def tarea_asignar_personal(request, pk):
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    form = AsignacionPersonalForm(request.POST)
    if form.is_valid():
        asignacion = form.save(commit=False)
        asignacion.tarea = tarea
        # Evitar duplicados por validación de aplicación
        if tarea.asignaciones.filter(personal=asignacion.personal).exists():
            messages.warning(request, 'Ese personal ya está asignado a esta tarea.')
        else:
            asignacion.save()
            messages.success(request, 'Personal asignado a la tarea.')
    else:
        messages.error(request, 'Error al asignar personal.')
    return redirect('mantenimiento:tarea_detail', pk=pk)


@require_POST
def tarea_registrar_producto(request, pk):
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    form = ProductoUtilizadoForm(request.POST)
    if form.is_valid():
        pu = form.save(commit=False)
        pu.tarea = tarea
        try:
            if tarea.tipo_crucero is None:
                raise ValidationError('Asigna primero el tipo de crucero a la tarea para poder registrar productos.')
            pu.save()
            messages.success(request, 'Producto registrado y stock actualizado.')
        except Exception as e:
            messages.error(request, f'No se pudo registrar el producto: {e}')
    else:
        messages.error(request, 'Datos inválidos del producto.')
    return redirect('mantenimiento:tarea_detail', pk=pk)


@require_POST
def tarea_cambiar_estado(request, pk):
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    nuevo_estado = request.POST.get('nuevo_estado')
    observaciones = request.POST.get('observaciones', '')
    next_url = request.POST.get('next')

    if not nuevo_estado:
        messages.error(request, 'Debe seleccionar un estado.')
        return redirect('mantenimiento:tarea_detail', pk=pk)

    try:
        if nuevo_estado == 'en_progreso':
            if not tarea.personal_asignado.exists():
                messages.error(request, 'No se puede iniciar una tarea sin personal asignado.')
                return redirect('mantenimiento:tarea_detail', pk=pk)
            
            # Verificar disponibilidad real del personal
            personal_no_disponible = []
            for asignacion in tarea.asignaciones.filter(estado='asignado'):
                if not asignacion.personal.disponible:
                    personal_no_disponible.append(asignacion.personal.nombre)
                # Verificar si el personal ya está en otra tarea activa
                otras_tareas = asignacion.personal.asignacionpersonal_set.filter(
                    estado='en_progreso',
                    tarea__estado='en_progreso'
                ).exclude(tarea=tarea)
                if otras_tareas.exists():
                    personal_no_disponible.append(f"{asignacion.personal.nombre} (en otra tarea)")
            
            if personal_no_disponible:
                messages.error(request, f'Personal no disponible: {", ".join(personal_no_disponible)}')
                return redirect('mantenimiento:tarea_detail', pk=pk)
            
            # Marcar ocupación del personal asignado (exclusividad)
            for asignacion in tarea.asignaciones.all():
                if asignacion.estado == 'asignado':
                    ocupar_personal(asignacion)

        if nuevo_estado == 'completada' and tarea.productos_utilizados.count() == 0:
            messages.warning(request, 'Se completó la tarea sin registrar productos utilizados.')

        estado_anterior = tarea.estado
        tarea.cambiar_estado(nuevo_estado, observaciones=observaciones)

        CambioEstado.objects.create(
            tarea=tarea,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            observaciones=observaciones,
            usuario=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
        )

        # Liberar personal al completar o cancelar
        if nuevo_estado in ['revision', 'completada', 'cancelada']:
            for asignacion in tarea.asignaciones.all():
                if asignacion.estado == 'en_progreso':
                    liberar_personal(asignacion)

        messages.success(request, f'Estado cambiado a: {dict(TareaMantenimiento.ESTADOS)[nuevo_estado]}')

    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f'Error al cambiar estado: {e}')

    if next_url:
        return redirect(next_url)
    return redirect('mantenimiento:tarea_detail', pk=pk)


def tarea_crear_preventiva(request):
    return redirect(f"{reverse('mantenimiento:tarea_create')}?tipo=preventivo")


def tarea_crear_correctiva(request):
    return redirect(f"{reverse('mantenimiento:tarea_create')}?tipo=correctivo")


def tarea_workflow(request, pk):
    # Reusar la vista detallada por ahora; la versión avanzada quedará en otro módulo
    return redirect('mantenimiento:tarea_detail', pk=pk)


@require_POST
def tarea_finalizar(request, pk):
    """Implementa el flujo lógico de estados: Pendiente → En Progreso → Completada"""
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    next_url = request.POST.get('next') or reverse('mantenimiento:tarea_list')

    if tarea.estado in ['completada', 'cancelada']:
        messages.info(request, 'La tarea ya está finalizada o cancelada.')
        return redirect(next_url)

    estado_anterior = tarea.estado
    cambios_realizados = []

    try:
        # Flujo lógico de estados
        if tarea.estado in ['creada', 'planificada', 'asignada']:
            # Si está pendiente, primero iniciarla (en_progreso)
            if tarea.estado != 'en_progreso':
                if not tarea.personal_asignado.exists():
                    messages.error(request, 'No se puede iniciar la tarea sin personal asignado.')
                    return redirect('mantenimiento:tarea_detail', pk=pk)
                
                if not tarea.materiales_necesarios:
                    messages.error(request, 'No se puede iniciar la tarea sin materiales necesarios.')
                    return redirect('mantenimiento:tarea_detail', pk=pk)
                
                # Cambiar a en_progreso
                tarea.estado = 'en_progreso'
                if not tarea.fecha_inicio:
                    tarea.fecha_inicio = timezone.now()
                tarea.save()
                
                # Marcar personal como ocupado
                for asignacion in tarea.asignaciones.filter(estado='asignado'):
                    ocupar_personal(asignacion)
                
                cambios_realizados.append('en_progreso')
                messages.info(request, 'Tarea iniciada (en progreso).')
                
                # Registrar cambio de estado
                CambioEstado.objects.create(
                    tarea=tarea,
                    estado_anterior=estado_anterior,
                    estado_nuevo='en_progreso',
                    observaciones='Iniciada automáticamente al finalizar',
                    usuario=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
                )
                
                estado_anterior = 'en_progreso'

        # Ahora completar la tarea
        if tarea.estado == 'en_progreso':
            tarea.estado = 'completada'
            tarea.fecha_completada = timezone.now()
            tarea.save()
            
            if tarea.equipo:
                tarea.equipo.ultima_revision = timezone.now()
                tarea.equipo.save()

            # Registrar cambio a completada
            CambioEstado.objects.create(
                tarea=tarea,
                estado_anterior=estado_anterior,
                estado_nuevo='completada',
                observaciones='Completada siguiendo flujo lógico',
                usuario=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
            )

            # Liberar personal
            for asignacion in tarea.asignaciones.all():
                if asignacion.estado in ['asignado', 'en_progreso']:
                    liberar_personal(asignacion)

            cambios_realizados.append('completada')
            messages.success(request, 'Tarea completada siguiendo el flujo lógico de estados.')
        else:
            messages.warning(request, f'La tarea está en estado "{tarea.get_estado_display()}" y no puede completarse directamente.')

    except Exception as e:
        messages.error(request, f'Error al procesar la tarea: {e}')
        return redirect('mantenimiento:tarea_detail', pk=pk)

    return redirect(next_url)


# Flujo simplificado: Pendiente -> En Progreso -> Completada
@require_POST
def tarea_siguiente_estado(request, pk):
    """Avanza la tarea al siguiente estado lógico con validaciones mínimas.

    - Si está en creada/planificada/asignada => pasa a en_progreso
    - Si está en en_progreso => pasa a completada
    Otros estados muestran mensaje informativo.
    """
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    next_url = request.POST.get('next') or reverse('mantenimiento:tarea_detail', kwargs={'pk': pk})

    try:
        if tarea.estado in ['creada', 'planificada', 'asignada']:
            if not tarea.personal_asignado.exists():
                messages.error(request, 'No se puede iniciar: asigne personal primero.')
                return redirect(next_url)
            if not tarea.materiales_necesarios:
                messages.error(request, 'No se puede iniciar: faltan materiales requeridos.')
                return redirect(next_url)

            estado_anterior = tarea.estado
            tarea.cambiar_estado('en_progreso', observaciones='Inicio rápido (flujo simplificado)')
            for asignacion in tarea.asignaciones.filter(estado='asignado'):
                ocupar_personal(asignacion)
            CambioEstado.objects.create(
                tarea=tarea,
                estado_anterior=estado_anterior,
                estado_nuevo='en_progreso',
                observaciones='Inicio rápido (flujo simplificado)',
                usuario=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
            )
            messages.success(request, 'Tarea iniciada (en progreso).')
        elif tarea.estado == 'en_progreso':
            estado_anterior = tarea.estado
            tarea.cambiar_estado('completada', observaciones='Finalización rápida (flujo simplificado)')
            for asignacion in tarea.asignaciones.all():
                if asignacion.estado in ['asignado', 'en_progreso']:
                    liberar_personal(asignacion)
            CambioEstado.objects.create(
                tarea=tarea,
                estado_anterior=estado_anterior,
                estado_nuevo='completada',
                observaciones='Finalización rápida (flujo simplificado)',
                usuario=request.user if getattr(request, 'user', None) and request.user.is_authenticated else None,
            )
            messages.success(request, 'Tarea completada.')
        else:
            messages.info(request, f'La tarea está en estado "{tarea.get_estado_display()}" y no tiene siguiente estado automático.')
    except ValidationError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f'No se pudo avanzar la tarea: {e}')

    return redirect(next_url)

