from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from apps.cruceros.models import Crucero
from .models import Dashboard, Alerta
from .forms import SolicitudMantenimientoHabitacionForm
from django.db.models import Count

#Obtener la distancia del recorrido de un crucero en particular
#Obtener las solicitudes de compra de un crucero en particualar
def cruceros_dashboard_data(request, crucero_id):
    """API endpoint para obtener datos del dashboard de un crucero en particular"""
    if crucero_id:
        try:
            crucero = Crucero.objects.get(id=crucero_id)
        except Crucero.DoesNotExist:
            # Si no existe el crucero, usar el primero disponible
            crucero = Crucero.objects.first()
    else:
        # Si no se proporciona ID, usar el primero disponible
        crucero = Crucero.objects.first()
    alertas = Alerta.objects.get(id=crucero_id)
    data = []

    # Obtener el objeto Dashboard para este crucero
    try:
        dashboard = Dashboard.objects.get(crucero=crucero)
        passengers = dashboard.num_pasajeros_actual
        employees = dashboard.num_empleados_actual
        budget = dashboard.presupuesto_estimado
        costs_total = dashboard.costos_totales
        earnings_total = dashboard.ganancias_totales
    except Dashboard.DoesNotExist:
        # Si no existe el dashboard para este crucero, usar valores por defecto
        passengers = 0
        employees = 0
        budget = 0
        costs_total = 0
        earnings_total = 0
        
    data.append({
        "name": crucero.nombre,
        "status": crucero.estado_operativo,
        "passengers": passengers,
        "employees": employees,
        "location": crucero.puerto_base,
        "days": getattr(crucero, "dia_actual_de_viaje", 0) if hasattr(crucero, "dia_actual_de_viaje") else 0,
        "distance": 0,
        "budget": budget,
        "costs": {
            "total": costs_total,
            "categories": {}
        },
        "earnings": {
            "total": earnings_total,
            "real": earnings_total - costs_total,
            "categories": {}
        },
        "alerts": [alertas.mensaje, alertas.fecha]
    })

    # Agregar datos de solicitudes de compra del modulo Compras
    purchase_requests = []
    
    return JsonResponse({
        "ships": data,
        "purchase_requests": purchase_requests
    })

#Obtener de alguna forma la ubicación actual de los barcos y no solo su puerto base 
def dashboard_empresa(request):
    """Dashboard principal de administración"""    
    dashboards = Dashboard.objects.select_related('crucero').all()
    cruceros_qs = Crucero.objects.all()

    costos_por_crucero = []
    ganancias_por_crucero = []
    total_costos = sum((d.costos_totales or 0) for d in dashboards)
    total_ganancias = sum((d.ganancias_totales or 0) for d in dashboards)

    ubicaciones = list(
        cruceros_qs.values('id', 'nombre', 'puerto_base', 'estado_operativo')
    )

    alertas = list(
        Alerta.objects.select_related('crucero')
        .values('id', 'mensaje', 'leida', 'fecha', 'crucero_id', 'crucero__nombre')
    )

    estados_counts = {
        'activo': 0,
        'inactivo': 0,
        'mantenimiento': 0,
        'viaje': 0,
    }
    for row in cruceros_qs.values('estado_operativo').annotate(cantidad=Count('id')):
        estado = row['estado_operativo']
        if estado in estados_counts:
            estados_counts[estado] = row['cantidad'] or 0

    for dashboard in dashboards:
        costos_por_crucero.append(dashboard.costos_totales or 0)
        ganancias_por_crucero.append(dashboard.ganancias_totales or 0)

    contexto = {
        'total_costos': total_costos,
        'costos_por_crucero': costos_por_crucero,
        'total_ganancias': total_ganancias,
        'ganancias_por_crucero': ganancias_por_crucero,
        'ubicaciones_cruceros': ubicaciones,
        'alertas': alertas,
        'conteo_cruceros_por_estado': estados_counts,
    }
    return render(request, 'dashboard_principal.html', contexto)


def solicitar_mantenimiento_habitacion(request):
    """Vista para crear una TareaMantenimiento desde administración para una habitación."""
    habitacion_id = request.GET.get('habitacion')
    form_kwargs = {}
    if habitacion_id:
        form_kwargs['habitacion'] = habitacion_id
    if request.method == 'POST':
        form = SolicitudMantenimientoHabitacionForm(request.POST, **form_kwargs)
        if form.is_valid():
            tarea = form.save(usuario=request.user)
            messages.success(request, 'Solicitud de mantenimiento creada correctamente.')
            try:
                crucero_id = tarea.crucero.id if tarea.crucero else None
                if crucero_id:
                    return redirect('dashboard', crucero_id=crucero_id)
            except Exception:
                pass
            return redirect('dashboard', crucero_id=1)
    else:
        form = SolicitudMantenimientoHabitacionForm(**form_kwargs)

    contexto = {
        'form': form,
        'titulo': 'Solicitar mantenimiento de habitación'
    }
    return render(request, 'administracion/solicitar_mantenimiento_habitacion.html', contexto)

# Agregar vistas para manejar solicitudes de compra
@csrf_exempt
@require_http_methods(["POST"])
def approve_purchase_request(request, request_id):
    # Agregar datos de solicitudes de compra del modulo Compras
    pass
    '''''''''
    try:
        solicitud = SolicitudCompra.objects.get(id=request_id)
        solicitud.estado = 'approved'
        solicitud.razon_rechazo = None
        solicitud.save()
        return JsonResponse({"status": "success"})
    except SolicitudCompra.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Solicitud no encontrada"}, status=404)
    '''''''''
        
@csrf_exempt
@require_http_methods(["POST"])
def reject_purchase_request(request, request_id):
    # Agregar datos de solicitudes de compra del modulo Compras
    pass
'''''''''
    try:
        data = json.loads(request.body)
        reason = data.get('reason', '')
        
        solicitud = SolicitudCompra.objects.get(id=request_id)
        solicitud.estado = 'rejected'
        solicitud.razon_rechazo = reason
        solicitud.save()
        return JsonResponse({"status": "success"})
    except SolicitudCompra.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Solicitud no encontrada"}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Datos inválidos"}, status=400)
'''''''''