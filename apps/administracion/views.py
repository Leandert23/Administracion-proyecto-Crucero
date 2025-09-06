from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import ConfiguracionSistema, LogActividad, BackupSistema, ReporteSistema
from apps.cruceros.models import Crucero
from apps.ventas.models import Venta
from apps.almacen.models import Producto, Lote
import json


# @login_required  # Temporalmente comentado para pruebas
def dashboard_administracion(request, crucero_id):
    """Vista principal del dashboard de administración"""
    crucero = get_object_or_404(Crucero, id=crucero_id)
    
    # Estadísticas generales
    hoy = timezone.now().date()
    semana_pasada = hoy - timedelta(days=7)
    
    # Actividades recientes
    actividades_recientes = LogActividad.objects.filter(
        crucero=crucero
    ).order_by('-fecha_hora')[:10]
    
    # Estadísticas de ventas
    ventas_hoy = Venta.objects.filter(
        crucero_id=crucero_id,
        fecha_venta__date=hoy
    ).count()
    
    ventas_semana = Venta.objects.filter(
        crucero_id=crucero_id,
        fecha_venta__date__gte=semana_pasada
    ).count()
    
    # Estadísticas de inventario
    productos_total = Producto.objects.filter(
        seccion__almacen__crucero=crucero
    ).count()
    
    lotes_vencidos = Lote.objects.filter(
        producto__seccion__almacen__crucero=crucero,
        fecha_caducidad__lt=hoy
    ).count()
    
    # Actividades por módulo
    actividades_por_modulo = LogActividad.objects.filter(
        crucero=crucero,
        fecha_hora__gte=semana_pasada
    ).values('modulo').annotate(
        total=Count('id')
    ).order_by('-total')
    
    context = {
        'crucero': crucero,
        'crucero_id': crucero_id,
        'actividades_recientes': actividades_recientes,
        'ventas_hoy': ventas_hoy,
        'ventas_semana': ventas_semana,
        'productos_total': productos_total,
        'lotes_vencidos': lotes_vencidos,
        'actividades_por_modulo': actividades_por_modulo,
    }
    
    return render(request, 'administracion/dashboard.html', context)


# @login_required  # Temporalmente comentado para pruebas
def configuracion_sistema(request, crucero_id):
    """Vista para gestionar configuraciones del sistema"""
    crucero = get_object_or_404(Crucero, id=crucero_id)
    
    if request.method == 'POST':
        # Procesar cambios de configuración
        for key, value in request.POST.items():
            if key.startswith('config_'):
                config_name = key.replace('config_', '')
                try:
                    config = ConfiguracionSistema.objects.get(nombre=config_name)
                    config.valor = value
                    config.save()
                    
                    # Registrar actividad
                    LogActividad.objects.create(
                        usuario=request.user if request.user.is_authenticated else None,
                        crucero=crucero,
                        tipo_actividad='configurar',
                        descripcion=f'Configuración actualizada: {config_name}',
                        modulo='administracion',
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT', '')
                    )
                except ConfiguracionSistema.DoesNotExist:
                    pass
        
        messages.success(request, 'Configuraciones actualizadas exitosamente.')
        return redirect('administracion:configuracion', crucero_id=crucero_id)
    
    configuraciones = ConfiguracionSistema.objects.all()
    
    context = {
        'crucero': crucero,
        'crucero_id': crucero_id,
        'configuraciones': configuraciones,
    }
    
    return render(request, 'administracion/configuracion.html', context)


# @login_required  # Temporalmente comentado para pruebas
def logs_actividad(request, crucero_id):
    """Vista para ver logs de actividad"""
    crucero = get_object_or_404(Crucero, id=crucero_id)
    
    # Filtros
    tipo_actividad = request.GET.get('tipo_actividad')
    modulo = request.GET.get('modulo')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    usuario = request.GET.get('usuario')
    
    logs = LogActividad.objects.filter(crucero=crucero)
    
    if tipo_actividad:
        logs = logs.filter(tipo_actividad=tipo_actividad)
    if modulo:
        logs = logs.filter(modulo=modulo)
    if fecha_inicio:
        logs = logs.filter(fecha_hora__date__gte=fecha_inicio)
    if fecha_fin:
        logs = logs.filter(fecha_hora__date__lte=fecha_fin)
    if usuario:
        logs = logs.filter(usuario__username__icontains=usuario)
    
    # Paginación
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'crucero': crucero,
        'crucero_id': crucero_id,
        'page_obj': page_obj,
        'tipos_actividad': LogActividad.TIPO_ACTIVIDAD_CHOICES,
        'filtros': {
            'tipo_actividad': tipo_actividad,
            'modulo': modulo,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'usuario': usuario,
        }
    }
    
    return render(request, 'administracion/logs.html', context)


# @login_required  # Temporalmente comentado para pruebas
def respaldos(request, crucero_id):
    """Vista para gestionar respaldos del sistema"""
    crucero = get_object_or_404(Crucero, id=crucero_id)
    
    if request.method == 'POST':
        if 'crear_backup' in request.POST:
            # Crear nuevo respaldo
            backup = BackupSistema.objects.create(
                nombre_archivo=f"backup_{crucero.nombre}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql",
                ruta_archivo="/backups/",
                tamaño_archivo=0,
                estado='iniciado',
                usuario=request.user if request.user.is_authenticated else None,
                descripcion=f"Respaldo manual del crucero {crucero.nombre}"
            )
            
            # Registrar actividad
            LogActividad.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                crucero=crucero,
                tipo_actividad='backup',
                descripcion=f'Iniciado respaldo: {backup.nombre_archivo}',
                modulo='administracion',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Respaldo iniciado exitosamente.')
            return redirect('administracion:respaldos', crucero_id=crucero_id)
    
    respaldos = BackupSistema.objects.all().order_by('-fecha_creacion')
    
    context = {
        'crucero': crucero,
        'crucero_id': crucero_id,
        'respaldos': respaldos,
    }
    
    return render(request, 'administracion/respaldos.html', context)


# @login_required  # Temporalmente comentado para pruebas
def reportes(request, crucero_id):
    """Vista para generar y gestionar reportes"""
    crucero = get_object_or_404(Crucero, id=crucero_id)
    
    if request.method == 'POST':
        tipo_reporte = request.POST.get('tipo_reporte')
        nombre_reporte = request.POST.get('nombre_reporte')
        
        if tipo_reporte and nombre_reporte:
            # Crear registro de reporte
            reporte = ReporteSistema.objects.create(
                nombre=nombre_reporte,
                tipo_reporte=tipo_reporte,
                parametros=request.POST.dict(),
                usuario=request.user if request.user.is_authenticated else None,
                crucero=crucero
            )
            
            # Registrar actividad
            LogActividad.objects.create(
                usuario=request.user if request.user.is_authenticated else None,
                crucero=crucero,
                tipo_actividad='reporte',
                descripcion=f'Reporte generado: {nombre_reporte}',
                modulo='administracion',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, 'Reporte generado exitosamente.')
            return redirect('administracion:reportes', crucero_id=crucero_id)
    
    reportes_generados = ReporteSistema.objects.filter(
        crucero=crucero
    ).order_by('-fecha_generacion')
    
    context = {
        'crucero': crucero,
        'crucero_id': crucero_id,
        'reportes_generados': reportes_generados,
        'tipos_reporte': ReporteSistema.TIPO_REPORTE_CHOICES,
    }
    
    return render(request, 'administracion/reportes.html', context)


# @login_required  # Temporalmente comentado para pruebas
def estadisticas_sistema(request, crucero_id):
    """Vista para mostrar estadísticas del sistema"""
    crucero = get_object_or_404(Crucero, id=crucero_id)
    
    # Estadísticas por período
    hoy = timezone.now().date()
    semana_pasada = hoy - timedelta(days=7)
    mes_pasado = hoy - timedelta(days=30)
    
    # Actividades por día (últimos 7 días)
    actividades_por_dia = []
    for i in range(7):
        fecha = hoy - timedelta(days=i)
        count = LogActividad.objects.filter(
            crucero=crucero,
            fecha_hora__date=fecha
        ).count()
        actividades_por_dia.append({
            'fecha': fecha.strftime('%d/%m'),
            'cantidad': count
        })
    
    # Usuarios más activos
    usuarios_activos = LogActividad.objects.filter(
        crucero=crucero,
        fecha_hora__gte=semana_pasada
    ).values('usuario__username').annotate(
        total=Count('id')
    ).order_by('-total')[:10]
    
    context = {
        'crucero': crucero,
        'crucero_id': crucero_id,
        'actividades_por_dia': actividades_por_dia,
        'usuarios_activos': usuarios_activos,
    }
    
    return render(request, 'administracion/estadisticas.html', context)
