from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import JsonResponse
from apps.cruceros.models import Crucero
from .models import Dashboard, Alerta
from .signals import decision_solicitud, obtener_solicitudes_compra
from apps.compras.models import CompraLote, Proveedores
from apps.ventas.models import Venta
from django.db.models import Count, Sum

def obtener_totales_compras_por_tipo(crucero_id):
    """
    Obtiene el total de compras agrupadas por tipo de proveedor para un crucero específico.
    
    Args:
        crucero_id (int): ID del crucero
        
    Returns:
        list: Lista de diccionarios con el tipo de proveedor y su total de compras
    """
    # Obtener todas las compras del crucero con sus proveedores
    compras = CompraLote.objects.filter(
        crucero_id=crucero_id
    ).select_related('proveedor').values(
        'proveedor__tipo',
        'presupuesto_lote'
    )
    
    # Agrupar por tipo de proveedor y sumar los presupuestos
    totales_por_tipo = {}
    for compra in compras:
        tipo = compra['proveedor__tipo']
        presupuesto = compra['presupuesto_lote'] or 0
        
        if tipo in totales_por_tipo:
            totales_por_tipo[tipo] += presupuesto
        else:
            totales_por_tipo[tipo] = presupuesto
    
    # Convertir a lista de diccionarios para facilitar el uso en el template
    lista_totales = []
    for tipo, total in totales_por_tipo.items():
        # Obtener el nombre legible del tipo
        tipo_nombre = dict(Proveedores.TIPO_CHOICES).get(tipo, tipo)
        lista_totales.append({
            'tipo': tipo,
            'tipo_nombre': tipo_nombre,
            'total': float(total)
        })
    
    # Ordenar por total descendente
    lista_totales.sort(key=lambda x: x['total'], reverse=True)
    
    return lista_totales

def obtener_totales_ventas_por_tipo(crucero_id=None):
    """
    Obtiene una lista con el total de ventas por cada tipo de venta
    Retorna una lista de diccionarios con: tipo_venta, total, cantidad, porcentaje
    
    Args:
        crucero_id (int, optional): ID del crucero. Si no se proporciona, obtiene de todos los cruceros
        
    Returns:
        list: Lista de diccionarios con información detallada por tipo de venta
    """
    queryset = Venta.objects.all()
    if crucero_id:
        queryset = queryset.filter(crucero_id=crucero_id)
    
    # Obtener totales por tipo
    totales_por_tipo = queryset.values('tipo_venta').annotate(
        total=Sum('monto_total'),
        cantidad=Count('id')
    ).order_by('-total')
    
    # Calcular total general para porcentajes
    total_general = queryset.aggregate(total=Sum('monto_total'))['total'] or 0
    
    # Crear lista con información completa
    lista_totales = []
    for item in totales_por_tipo:
        tipo_venta = item['tipo_venta']
        total = item['total'] or 0
        cantidad = item['cantidad']
        
        # Obtener el nombre legible del tipo de venta
        tipo_display = dict(Venta.TIPO_VENTA_CHOICES).get(tipo_venta, tipo_venta)
        
        # Calcular porcentaje
        porcentaje = (total / total_general * 100) if total_general > 0 else 0
        
        lista_totales.append({
            'tipo_venta': tipo_venta,
            'tipo_display': tipo_display,
            'total': total,
            'cantidad': cantidad,
            'porcentaje': round(porcentaje, 2)
        })
    
    return lista_totales

#Obtener la distancia del recorrido de un crucero en particular
def cruceros_dashboard_data(request, crucero_id):
    """API endpoint para obtener datos del dashboard de un crucero en particular"""
    crucero = get_object_or_404(Crucero, pk=crucero_id)

    try:
        dashboard = Dashboard.objects.get(crucero=crucero)
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
    
    # Obtener totales de compras por tipo de proveedor
    compras_por_tipo = obtener_totales_compras_por_tipo(crucero_id)
    ventas_por_tipo = obtener_totales_ventas_por_tipo(crucero_id)

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
        "days": getattr(crucero, "dia_actual_de_viaje", 0) if (hasattr(crucero, "dia_actual_de_viaje") and 
                                                               isinstance(getattr(crucero, "dia_actual_de_viaje", 0), int)) 
                                                            else 0,
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
        "purchase_requests": purchase_requests,
        "compras_por_tipo": compras_por_tipo,
        "ventas_por_tipo": ventas_por_tipo,
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
        'real_ganancias': total_ganancias - total_costos,
        'ganancias_por_crucero': ganancias_por_crucero,
        'ubicaciones_cruceros': ubicaciones,
        'alertas': alertas,
        'conteo_cruceros_por_estado': estados_counts,
    }
    return render(request, 'dashboard_principal.html', contexto)

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
