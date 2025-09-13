from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import JsonResponse
from apps.cruceros.models import Crucero
from .models import Dashboard, Alerta
from .forms import SolicitudMantenimientoHabitacionForm, HabitacionForm
from .signals import decision_solicitud, obtener_solicitudes_compra
from django.db.models import Count

#Obtener la distancia del recorrido de un crucero en particular
def cruceros_dashboard_data(request, crucero_id):
    """API endpoint para obtener datos del dashboard de un crucero en particular"""
    crucero = get_object_or_404(Crucero, pk=crucero_id)

    try:
        dashboard = Dashboard.objects.get(pk=crucero_id)
    except Dashboard.DoesNotExist:
        # Si no existe un registro de administración para este crucero, crear uno con valores por defecto
        dashboard = Dashboard.objects.create(
            crucero=crucero,
            costos_totales=0.00,
            ganancias_totales=0.00,
            presupuesto_estimado=0.00,
            precio_combustible=0.00,
            num_pasajeros_actual=0,
            num_empleados_actual=0
        )
    # Alertas asociadas al crucero seleccionado
    alertas_list = list(
        Alerta.objects.filter(crucero=dashboard)
        .values('id', 'mensaje', 'leida', 'fecha', 'crucero_id', 'crucero__crucero__nombre')
    )
    passengers = dashboard.num_pasajeros_actual
    employees = dashboard.num_empleados_actual
    budget = dashboard.presupuesto_estimado
    costs_total = dashboard.costos_totales
    precio_gasolina = dashboard.precio_combustible
    earnings_total = dashboard.ganancias_totales
    purchase_requests = obtener_solicitudes_compra(crucero_id)
        
    context = {
        "crucero": crucero,
        "name": crucero.nombre,
        "status": crucero.estado_operativo,
        "passengers": passengers,
        "employees": {
            "total": employees,
            "status" : {
                "active_employees": 0,
                "inactive_employees": 0,
                "de_baja_employees": 0,
            },
        },
        "location": crucero.puerto_base,
        "days": getattr(crucero, "dia_actual_de_viaje", 0) if hasattr(crucero, "dia_actual_de_viaje") else 0,
        "distance": 0,
        "gas_price": precio_gasolina,
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
        "alerts": alertas_list,
        "purchase_requests": purchase_requests
    }

    return render(request, 'dashboard_crucero.html', context)

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
        Alerta.objects.select_related('crucero__crucero')
        .values('id', 'mensaje', 'leida', 'fecha', 'crucero_id', 'crucero__crucero__nombre')
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
    cruceros = Crucero.objects.all()
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
        'titulo': 'Solicitar mantenimiento de habitación',
        'crucero': cruceros
    }
    return render(request, 'administracion/solicitar_mantenimiento_habitacion.html', contexto)

# Agregar vista para manejar solicitudes de compra
@csrf_exempt
@require_http_methods(["POST"])
def decision_solicitud_view(request):
    """
    Vista para procesar la decisión de una solicitud de compra enviada desde crucero.js
    URL: /administracion/decision-solicitud/
    """
    try:
        # Obtener los datos del FormData enviado desde JavaScript
        request_id = request.POST.get('id')
        aceptado_str = request.POST.get('aceptado')
        mensaje = request.POST.get('mensaje', '')
        
        # Validar que se proporcionen los datos requeridos
        if not request_id:
            return JsonResponse({
                'success': False,
                'message': 'ID de solicitud requerido'
            }, status=400)
        
        if aceptado_str is None:
            return JsonResponse({
                'success': False,
                'message': 'Estado de decisión requerido'
            }, status=400)
        
        # Convertir el string a boolean
        aceptado = aceptado_str.lower() in ['true', '1', 'yes', 'si', 'sí'] 
        
        # Procesar la decisión usando la función de utils
        decision_solicitud(request_id, aceptado, mensaje)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error interno del servidor: {str(e)}'
        }, status=500)

def registrar_habitacion(request):
    """Vista para registrar una nueva habitación."""
    cruceros = Crucero.objects.all()
    if request.method == 'POST':
        form = HabitacionForm(request.POST)
        if form.is_valid():
            try:
                # Guardar la habitación en la base de datos
                habitacion = form.save()
                
                # Mensaje de éxito con información detallada
                messages.success(
                    request, 
                    f'¡Habitación registrada exitosamente! '
                    f'ID: {habitacion.id}, Nombre: "{habitacion.nombre_usuario}", '
                    f'Ubicación: {habitacion.ubicacion}, Tipo: {habitacion.get_tipo_display()}, '
                    f'Costo final: ${habitacion.costo_final:,.2f}'
                )
                
                # Redirigir para limpiar el formulario
                return redirect('registrar_habitacion')
            except Exception as e:
                # Manejar otros errores
                messages.error(
                    request, 
                    f'Error al registrar la habitación: {str(e)}. '
                    'Por favor, verifique los datos e intente nuevamente.'
                )
        else:
            # El formulario no es válido, mostrar errores
            messages.error(
                request, 
                'Por favor, corrija los errores en el formulario antes de continuar.'
            )
    else:
        form = HabitacionForm()
    
    contexto = {
        'form': form,
        'titulo': 'Registrar Nueva Habitación',
        'crucero': cruceros
    }
    return render(request, 'administracion/registrar_habitacion.html', contexto)

def listar_habitaciones(request):
    """Vista para listar todas las habitaciones registradas."""
    cruceros = Crucero.objects.all()
    from .models import Habitaciones
    
    habitaciones = Habitaciones.objects.select_related('cubierta', 'cubierta__crucero').all().order_by('-id')
    
    contexto = {
        'habitaciones': habitaciones,
        'titulo': 'Lista de Habitaciones Registradas',
        'crucero': cruceros
    }
    return render(request, 'administracion/listar_habitaciones.html', contexto)
