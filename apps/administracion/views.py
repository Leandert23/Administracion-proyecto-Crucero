from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from apps.cruceros.models import Crucero
from .models import Administracion, Alerta, Modulo, Rol, UsuarioRol, SolicitudCompra
from .utils import requerir_administrador_modulo, usuario_tiene_rol, obtener_roles_usuario

@login_required
@requerir_administrador_modulo('administracion')
def cruceros_dashboard_data(request):
    """API endpoint para obtener datos del dashboard de cruceros - Solo administradores"""
    cruceros = Crucero.objects.all()
    data = []
    for c in cruceros:
        data.append({
            "id": c.id,
            "name": c.nombre,
            "status": c.estado_operativo,
            "passengers": c.capacidad_pasajeros,
            "employees": c.capacidad_tripulacion,
            "location": c.puerto_base,
            "days": getattr(c, "dia_actual_de_viaje", 0) if hasattr(c, "dia_actual_de_viaje") else 0,
            "distance": 0,
            "budget": 0,
            "costs": {
                "total": 0,
                "categories": {}
            },
            "earnings": {
                "total": 0,
                "real": 0,
                "categories": {}
            },
            "alerts": []
        })
    # Agregar datos de solicitudes de compra
    purchase_requests = []
    for solicitud in SolicitudCompra.objects.all():
        purchase_requests.append({
            "id": solicitud.id,
            "ship_name": solicitud.crucero.nombre,
            "amount": float(solicitud.monto),
            "description": solicitud.descripcion,
            "status": solicitud.estado,
            "rejection_reason": solicitud.razon_rechazo,
            "created_at": solicitud.fecha_creacion.strftime("%Y-%m-%d"),
        })
    
    return JsonResponse({
        "ships": data,
        "purchase_requests": purchase_requests
    })

@login_required
@requerir_administrador_modulo('administracion')
def dashboard_empresa(request):
    """Dashboard principal de administración - Solo administradores"""
    admin = Administracion.objects.first()
    contexto = {
        'presupuesto': admin.presupuesto_estimado if admin else 0,
        'alertas': Alerta.objects.filter(leida=False) if admin else [],
        'usuario_roles': obtener_roles_usuario(request.user),
        'es_administrador': usuario_tiene_rol(request.user, 'administracion', 'admin'),
    }
    return render(request, 'templates/index.html', contexto)

# Vistas para gestión de roles
@login_required
@requerir_administrador_modulo('administracion')
def gestion_roles(request):
    """Vista para gestionar roles de usuarios - Solo administradores"""
    if request.method == 'POST':
        # Aquí se manejarían las acciones de gestión de roles
        pass
    
    modulos = Modulo.objects.filter(activo=True)
    roles = Rol.objects.filter(activo=True).select_related('modulo')
    usuarios_roles = UsuarioRol.objects.filter(activo=True).select_related('usuario', 'rol', 'rol__modulo')
    
    contexto = {
        'modulos': modulos,
        'roles': roles,
        'usuarios_roles': usuarios_roles,
    }
    return render(request, 'administracion/gestion_roles.html', contexto)

@login_required
def mi_perfil_roles(request):
    """Vista para que el usuario vea sus propios roles"""
    roles_usuario = obtener_roles_usuario(request.user)
    
    contexto = {
        'roles_usuario': roles_usuario,
        'modulos_disponibles': Modulo.objects.filter(activo=True),
    }
    return render(request, 'administracion/mi_perfil_roles.html', contexto)

# Agregar vistas para manejar solicitudes de compra
@csrf_exempt
@require_http_methods(["POST"])
def approve_purchase_request(request, request_id):
    try:
        solicitud = SolicitudCompra.objects.get(id=request_id)
        solicitud.estado = 'approved'
        solicitud.razon_rechazo = None
        solicitud.save()
        return JsonResponse({"status": "success"})
    except SolicitudCompra.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Solicitud no encontrada"}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def reject_purchase_request(request, request_id):
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