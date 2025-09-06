from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
import json
from apps.cruceros.models import Crucero
from .models import Administracion, Alerta, Modulo, Rol, UsuarioRol, SolicitudCompra
from .utils import requerir_administrador_modulo, usuario_tiene_rol, obtener_roles_usuario
from .forms import RegistroUsuarioForm

@login_required
@requerir_administrador_modulo('administracion')
def cruceros_dashboard_data(request):
    """API endpoint para obtener datos del dashboard de cruceros - Solo administradores"""
    cruceros = Crucero.objects.all()
    data = []
    for c in cruceros:
        # Generar datos simulados más realistas
        import random
        base_cost = random.randint(50000, 200000)
        base_earnings = random.randint(300000, 800000)
        
        data.append({
            "id": c.id,
            "name": c.nombre,
            "status": c.estado_operativo,
            "passengers": c.capacidad_pasajeros,
            "employees": {
                "total": c.capacidad_tripulacion,
                "status": {
                    "active_employees": int(c.capacidad_tripulacion * 0.85),
                    "inactive_employees": int(c.capacidad_tripulacion * 0.10),
                    "de_baja_employees": int(c.capacidad_tripulacion * 0.05)
                },
                "work_site": {
                    "restaurante": int(c.capacidad_tripulacion * 0.25),
                    "bares": int(c.capacidad_tripulacion * 0.15),
                    "mantenimiento": int(c.capacidad_tripulacion * 0.20),
                    "servicio_medico": int(c.capacidad_tripulacion * 0.05),
                    "entretenimiento": int(c.capacidad_tripulacion * 0.10),
                    "almacen": int(c.capacidad_tripulacion * 0.10),
                    "ventas": int(c.capacidad_tripulacion * 0.08),
                    "compras": int(c.capacidad_tripulacion * 0.05),
                    "administracion": int(c.capacidad_tripulacion * 0.02)
                }
            },
            "location": c.puerto_base,
            "days": random.randint(1, 7),  # Días simulados para evitar errores
            "distance": random.randint(500, 2000),
            "budget": base_earnings * 0.6,
            "gasPrice": round(random.uniform(2.0, 3.5), 2),
            "costs": {
                "total": base_cost,
                "categories": {
                    "combustible": int(base_cost * 0.4),
                    "comida": int(base_cost * 0.25),
                    "mantenimiento": int(base_cost * 0.20),
                    "personal": int(base_cost * 0.15)
                }
            },
            "earnings": {
                "total": base_earnings,
                "real": int(base_earnings * random.uniform(0.7, 0.95)),
                "categories": {
                    "boletos": int(base_earnings * 0.6),
                    "restaurantes": int(base_earnings * 0.15),
                    "bares": int(base_earnings * 0.10),
                    "tiendas": int(base_earnings * 0.10),
                    "servicios": int(base_earnings * 0.05)
                }
            },
            "alerts": [alert for alert in [
                "Mantenimiento programado para próxima semana" if c.estado_operativo == 'mantenimiento' else None,
                "Verificar certificados de seguridad" if not c.seguro_vigente else None,
                "Revisar inventario de combustible" if random.random() < 0.3 else None
            ] if alert is not None]
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
def dashboard_empresa(request, crucero_id=None):
    """Dashboard principal de administración"""
    # Verificación simplificada de permisos
    # Permitir acceso si es superusuario O si tiene rol de administrador
    es_administrador = request.user.is_superuser or usuario_tiene_rol(request.user, 'administracion', 'admin')
    
    if not es_administrador:
        # Para usuarios sin permisos, mostrar mensaje informativo
        from django.contrib import messages
        messages.warning(request, 'No tienes permisos de administrador. Contacta al administrador del sistema.')
        return render(request, 'administracion/sin_permisos.html', {
            'usuario_roles': obtener_roles_usuario(request.user),
            'es_administrador': False,
        })
    
    # Obtener el crucero si se proporciona el ID
    crucero = None
    if crucero_id:
        try:
            crucero = Crucero.objects.get(id=crucero_id)
        except Crucero.DoesNotExist:
            # Si no existe el crucero, usar el primero disponible
            crucero = Crucero.objects.first()
    else:
        # Si no se proporciona ID, usar el primero disponible
        crucero = Crucero.objects.first()
    
    admin = Administracion.objects.first()
    contexto = {
        'crucero': crucero,
        'presupuesto': admin.presupuesto_estimado if admin else 0,
        'costos': admin.costos_totales if admin else 0,
        'ganancias': admin.ganancias_totales if admin else 0,
        'alertas': Alerta.objects.filter(leida=False) if admin else [],
        'usuario_roles': obtener_roles_usuario(request.user),
        'es_administrador': es_administrador,
    }
    return render(request, 'index.html', contexto)

@login_required
def dashboard_crucero_individual(request, crucero_id):
    """Dashboard individual de un crucero específico"""
    # Verificación simplificada de permisos
    es_administrador = request.user.is_superuser or usuario_tiene_rol(request.user, 'administracion', 'admin')
    
    if not es_administrador:
        from django.contrib import messages
        messages.warning(request, 'No tienes permisos de administrador. Contacta al administrador del sistema.')
        return render(request, 'administracion/sin_permisos.html', {
            'usuario_roles': obtener_roles_usuario(request.user),
            'es_administrador': False,
        })
    
    # Obtener el crucero específico
    try:
        crucero = Crucero.objects.get(id=crucero_id)
    except Crucero.DoesNotExist:
        from django.contrib import messages
        messages.error(request, 'El crucero solicitado no existe.')
        return redirect('dashboard_empresa')
    
    # Obtener datos específicos del crucero
    admin = Administracion.objects.first()
    contexto = {
        'crucero': crucero,
        'presupuesto': admin.presupuesto_estimado if admin else 0,
        'costos': admin.costos_totales if admin else 0,
        'ganancias': admin.ganancias_totales if admin else 0,
        'alertas': Alerta.objects.filter(leida=False) if admin else [],
        'usuario_roles': obtener_roles_usuario(request.user),
        'es_administrador': es_administrador,
        'crucero_individual': True,  # Flag para indicar que es vista individual
    }
    return render(request, 'administracion/dashboard_crucero.html', contexto)

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
    usuarios = User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username')

    contexto = {
        'modulos': modulos,
        'roles': roles,
        'usuarios_roles': usuarios_roles,
        'usuarios': usuarios,
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
    
# Vistas de autenticación
def registro_usuario(request):
    """Vista para registro de nuevos usuarios"""
    if request.user.is_authenticated:
        # Redirigir al dashboard del primer crucero disponible
        crucero = Crucero.objects.first()
        if crucero:
            return redirect('dashboard', crucero_id=crucero.id)
        return redirect('dashboard', crucero_id=1)
    
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Iniciar sesión automáticamente después del registro
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.first_name}! Tu cuenta ha sido creada exitosamente.')
            # Redirigir al dashboard del primer crucero disponible
            crucero = Crucero.objects.first()
            if crucero:
                return redirect('dashboard', crucero_id=crucero.id)
            return redirect('dashboard', crucero_id=1)
    else:
        form = RegistroUsuarioForm()
    
    contexto = {
        'form': form,
        'titulo': 'Registro de Usuario'
    }
    return render(request, 'administracion/registro.html', contexto)

class LoginPersonalizado(LoginView):
    """Vista personalizada de login"""
    template_name = 'administracion/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Redirigir al dashboard del primer crucero disponible
        crucero = Crucero.objects.first()
        if crucero:
            return f'/dashboard/{crucero.id}'
        return '/dashboard/1'
    
    def form_valid(self, form):
        messages.success(self.request, f'¡Bienvenido de vuelta, {form.get_user().first_name}!')
        return super().form_valid(form)

def logout_usuario(request):
    """Vista personalizada de logout que maneja peticiones GET"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')
