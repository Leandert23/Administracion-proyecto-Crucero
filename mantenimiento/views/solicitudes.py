from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta

from ..models import SolicitudMantenimiento, TareaMantenimiento, Crucero, TipoCrucero
from ..forms import (
    SolicitudMantenimientoForm, SolicitudMantenimientoPreventivoForm,
    SolicitudMantenimientoCorrectivoForm, SolicitudMantenimientoAdminForm,
    ConvertirSolicitudATareaForm
)


@login_required
def solicitar_mantenimiento(request, tipo=None):
    """
    Vista para solicitar mantenimiento desde cualquier módulo del crucero
    """
    # Detectar módulo solicitante desde parámetros GET
    modulo_solicitante = request.GET.get('modulo', 'mantenimiento')
    
    # Determinar formulario según el tipo
    if tipo == 'preventivo':
        form_class = SolicitudMantenimientoPreventivoForm
        titulo_base = 'Solicitar Mantenimiento Preventivo'
    elif tipo == 'correctivo':
        form_class = SolicitudMantenimientoCorrectivoForm
        titulo_base = 'Solicitar Mantenimiento Correctivo'
    else:
        form_class = SolicitudMantenimientoForm
        titulo_base = 'Solicitar Mantenimiento'
    
    # Títulos específicos por módulo
    modulo_display = {
        'servicios_medicos': 'Servicios Médicos',
        'almacen': 'Almacén',
        'recursos_humanos': 'Recursos Humanos',
        'ventas': 'Ventas',
        'reservas': 'Reservas',
        'restaurante': 'Restaurante',
        'bares': 'Bares',
        'entretenimiento': 'Entretenimiento',
        'compras': 'Compras',
        'mantenimiento': 'Mantenimiento'
    }.get(modulo_solicitante, 'Mantenimiento')
    
    titulo = f"{titulo_base} - {modulo_display}"
    
    if request.method == 'POST':
        form = form_class(
            request.POST,
            modulo_solicitante=modulo_solicitante,
            user=request.user
        )
        
        if form.is_valid():
            solicitud = form.save()
            
            # Mensaje de éxito
            messages.success(
                request,
                f'✅ Solicitud de mantenimiento {solicitud.get_tipo_display().lower()} '
                f'enviada exitosamente. ID: #{solicitud.id}'
            )
            
            # Redirigir según el módulo
            return redirect('mantenimiento:solicitud_enviada', solicitud_id=solicitud.id)
    else:
        form = form_class(
            modulo_solicitante=modulo_solicitante,
            user=request.user
        )
    
    # Obtener crucero activo para contexto
    crucero_activo = Crucero.objects.filter(activo=True).first()
    
    context = {
        'form': form,
        'titulo': titulo,
        'modulo_solicitante': modulo_solicitante,
        'tipo': tipo,
        'crucero_activo': crucero_activo,
    }
    
    return render(request, 'mantenimiento/solicitar_mantenimiento.html', context)


@login_required
def solicitud_enviada(request, solicitud_id):
    """
    Vista de confirmación después de enviar una solicitud
    """
    solicitud = get_object_or_404(SolicitudMantenimiento, id=solicitud_id)
    
    # Verificar que el usuario sea el que hizo la solicitud
    if solicitud.solicitado_por != request.user:
        messages.error(request, 'No tienes permisos para ver esta solicitud.')
        return redirect('mantenimiento:dashboard')
    
    context = {
        'solicitud': solicitud,
        'titulo': 'Solicitud Enviada',
    }
    
    return render(request, 'mantenimiento/solicitud_enviada.html', context)


@login_required
def mis_solicitudes(request):
    """
    Vista para ver las solicitudes realizadas por el usuario actual
    """
    solicitudes = SolicitudMantenimiento.objects.filter(
        solicitado_por=request.user
    ).order_by('-fecha_solicitud')
    
    # Filtros
    estado_filter = request.GET.get('estado')
    tipo_filter = request.GET.get('tipo')
    modulo_filter = request.GET.get('modulo')
    
    if estado_filter:
        solicitudes = solicitudes.filter(estado=estado_filter)
    if tipo_filter:
        solicitudes = solicitudes.filter(tipo=tipo_filter)
    if modulo_filter:
        solicitudes = solicitudes.filter(modulo_solicitante=modulo_filter)
    
    # Paginación
    paginator = Paginator(solicitudes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    stats = {
        'total': solicitudes.count(),
        'pendientes': solicitudes.filter(estado='pendiente').count(),
        'en_progreso': solicitudes.filter(estado='en_progreso').count(),
        'completadas': solicitudes.filter(estado='completada').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'estado_filter': estado_filter,
        'tipo_filter': tipo_filter,
        'modulo_filter': modulo_filter,
        'titulo': 'Mis Solicitudes de Mantenimiento',
    }
    
    return render(request, 'mantenimiento/mis_solicitudes.html', context)


@login_required
def solicitud_detail(request, solicitud_id):
    """
    Vista detallada de una solicitud
    """
    solicitud = get_object_or_404(SolicitudMantenimiento, id=solicitud_id)
    
    # Verificar permisos
    puede_ver = (
        solicitud.solicitado_por == request.user or
        request.user.has_perm('mantenimiento.view_solicitudmantenimiento') or
        request.user.personal.filter(activo=True).exists()
    )
    
    if not puede_ver:
        messages.error(request, 'No tienes permisos para ver esta solicitud.')
        return redirect('mantenimiento:dashboard')
    
    context = {
        'solicitud': solicitud,
        'titulo': f'Solicitud #{solicitud.id}',
    }
    
    return render(request, 'mantenimiento/solicitud_detail.html', context)


# ===== VISTAS PARA EL MÓDULO DE MANTENIMIENTO =====

@login_required
def gestionar_solicitudes(request):
    """
    Vista principal para gestionar todas las solicitudes desde el módulo de mantenimiento
    """
    # Verificar que el usuario sea del módulo de mantenimiento
    if not request.user.personal.filter(activo=True).exists():
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('mantenimiento:dashboard')
    
    solicitudes = SolicitudMantenimiento.objects.all().order_by('-fecha_solicitud')
    
    # Filtros
    estado_filter = request.GET.get('estado')
    tipo_filter = request.GET.get('tipo')
    modulo_filter = request.GET.get('modulo')
    prioridad_filter = request.GET.get('prioridad')
    
    if estado_filter:
        solicitudes = solicitudes.filter(estado=estado_filter)
    if tipo_filter:
        solicitudes = solicitudes.filter(tipo=tipo_filter)
    if modulo_filter:
        solicitudes = solicitudes.filter(modulo_solicitante=modulo_filter)
    if prioridad_filter:
        solicitudes = solicitudes.filter(prioridad=prioridad_filter)
    
    # Búsqueda
    search = request.GET.get('search')
    if search:
        solicitudes = solicitudes.filter(
            Q(titulo__icontains=search) |
            Q(descripcion__icontains=search) |
            Q(equipo_afectado__icontains=search) |
            Q(ubicacion_solicitud__icontains=search)
        )
    
    # Paginación
    paginator = Paginator(solicitudes, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    stats = {
        'total': SolicitudMantenimiento.objects.count(),
        'pendientes': SolicitudMantenimiento.objects.filter(estado='pendiente').count(),
        'en_revision': SolicitudMantenimiento.objects.filter(estado='en_revision').count(),
        'aprobadas': SolicitudMantenimiento.objects.filter(estado='aprobada').count(),
        'en_progreso': SolicitudMantenimiento.objects.filter(estado='en_progreso').count(),
        'completadas': SolicitudMantenimiento.objects.filter(estado='completada').count(),
    }
    
    # Solicitudes por módulo
    solicitudes_por_modulo = SolicitudMantenimiento.objects.values(
        'modulo_solicitante'
    ).annotate(
        total=Count('id')
    ).order_by('-total')
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'solicitudes_por_modulo': solicitudes_por_modulo,
        'estado_filter': estado_filter,
        'tipo_filter': tipo_filter,
        'modulo_filter': modulo_filter,
        'prioridad_filter': prioridad_filter,
        'search': search,
        'titulo': 'Gestionar Solicitudes de Mantenimiento',
    }
    
    return render(request, 'mantenimiento/gestionar_solicitudes.html', context)


@login_required
def editar_solicitud(request, solicitud_id):
    """
    Vista para editar una solicitud desde el módulo de mantenimiento
    """
    # Verificar permisos
    if not request.user.personal.filter(activo=True).exists():
        messages.error(request, 'No tienes permisos para editar solicitudes.')
        return redirect('mantenimiento:dashboard')
    
    solicitud = get_object_or_404(SolicitudMantenimiento, id=solicitud_id)
    
    if request.method == 'POST':
        form = SolicitudMantenimientoAdminForm(request.POST, instance=solicitud)
        
        if form.is_valid():
            solicitud_editada = form.save(commit=False)
            solicitud_editada.revisado_por = request.user
            
            # Actualizar fechas según el estado
            if solicitud_editada.estado == 'en_progreso' and not solicitud.fecha_inicio:
                solicitud_editada.fecha_inicio = timezone.now()
            elif solicitud_editada.estado == 'completada' and not solicitud.fecha_completado:
                solicitud_editada.fecha_completado = timezone.now()
            
            solicitud_editada.save()
            
            messages.success(
                request,
                f'✅ Solicitud #{solicitud.id} actualizada exitosamente.'
            )
            
            return redirect('mantenimiento:gestionar_solicitudes')
    else:
        form = SolicitudMantenimientoAdminForm(instance=solicitud)
    
    context = {
        'form': form,
        'solicitud': solicitud,
        'titulo': f'Editar Solicitud #{solicitud.id}',
    }
    
    return render(request, 'mantenimiento/editar_solicitud.html', context)


@login_required
def convertir_solicitud(request, solicitud_id):
    """
    Vista para convertir una solicitud en una tarea de mantenimiento
    """
    # Verificar permisos
    if not request.user.personal.filter(activo=True).exists():
        messages.error(request, 'No tienes permisos para convertir solicitudes.')
        return redirect('mantenimiento:dashboard')
    
    solicitud = get_object_or_404(SolicitudMantenimiento, id=solicitud_id)
    
    if request.method == 'POST':
        form = ConvertirSolicitudATareaForm(request.POST, solicitud=solicitud)
        
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.creado_por = request.user
            tarea.crucero = solicitud.crucero
            tarea.tipo_crucero = solicitud.tipo_crucero
            tarea.estado = 'planificada'
            tarea.save()
            
            # Actualizar la solicitud
            solicitud.tarea_mantenimiento = tarea
            solicitud.estado = 'aprobada'
            solicitud.revisado_por = request.user
            solicitud.save()
            
            messages.success(
                request,
                f'✅ Solicitud #{solicitud.id} convertida en tarea #{tarea.id} exitosamente.'
            )
            
            return redirect('mantenimiento:tarea_detail', pk=tarea.id)
    else:
        form = ConvertirSolicitudATareaForm(solicitud=solicitud)
    
    context = {
        'form': form,
        'solicitud': solicitud,
        'titulo': f'Convertir Solicitud #{solicitud.id} en Tarea',
    }
    
    return render(request, 'mantenimiento/convertir_solicitud.html', context)


# ===== VISTAS AJAX =====

@login_required
@require_http_methods(["POST"])
def cambiar_estado_solicitud(request, solicitud_id):
    """
    Vista AJAX para cambiar el estado de una solicitud
    """
    if not request.user.personal.filter(activo=True).exists():
        return JsonResponse({'success': False, 'error': 'Sin permisos'})
    
    solicitud = get_object_or_404(SolicitudMantenimiento, id=solicitud_id)
    nuevo_estado = request.POST.get('estado')
    
    if nuevo_estado not in dict(SolicitudMantenimiento.ESTADOS_SOLICITUD):
        return JsonResponse({'success': False, 'error': 'Estado inválido'})
    
    solicitud.estado = nuevo_estado
    solicitud.revisado_por = request.user
    
    # Actualizar fechas según el estado
    if nuevo_estado == 'en_progreso' and not solicitud.fecha_inicio:
        solicitud.fecha_inicio = timezone.now()
    elif nuevo_estado == 'completada' and not solicitud.fecha_completado:
        solicitud.fecha_completado = timezone.now()
    
    solicitud.save()
    
    return JsonResponse({
        'success': True,
        'estado': solicitud.get_estado_display(),
        'fecha_actualizacion': solicitud.fecha_solicitud.strftime('%d/%m/%Y %H:%M')
    })


# ===== FUNCIONES AUXILIARES =====

def detectar_modulo_solicitante(request):
    """
    Detecta el módulo desde el cual se está haciendo la solicitud
    """
    path = request.path
    referer = request.META.get('HTTP_REFERER', '')
    
    # Detectar por URL
    if '/mantenimiento' in path:
        return 'mantenimiento'
    elif '/servicios-medicos' in path or '/medical' in path:
        return 'servicios_medicos'
    elif '/almacen' in path or '/warehouse' in path:
        return 'almacen'
    elif '/recursos-humanos' in path or '/hr' in path:
        return 'recursos_humanos'
    elif '/ventas' in path or '/sales' in path:
        return 'ventas'
    elif '/reservas' in path or '/reservations' in path:
        return 'reservas'
    elif '/restaurante' in path or '/restaurant' in path:
        return 'restaurante'
    elif '/bares' in path or '/bars' in path:
        return 'bares'
    elif '/entretenimiento' in path or '/entertainment' in path:
        return 'entretenimiento'
    elif '/compras' in path or '/purchases' in path:
        return 'compras'
    
    # Detectar por referer
    if 'servicios-medicos' in referer:
        return 'servicios_medicos'
    elif 'almacen' in referer:
        return 'almacen'
    elif 'recursos-humanos' in referer:
        return 'recursos_humanos'
    elif 'ventas' in referer:
        return 'ventas'
    elif 'reservas' in referer:
        return 'reservas'
    elif 'restaurante' in referer:
        return 'restaurante'
    elif 'bares' in referer:
        return 'bares'
    elif 'entretenimiento' in referer:
        return 'entretenimiento'
    elif 'compras' in referer:
        return 'compras'
    
    # Por defecto, mantenimiento
    return 'mantenimiento'
