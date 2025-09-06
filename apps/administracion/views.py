from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q
from django.utils import timezone
from datetime import datetime

from .models import Modulo, Rol, UsuarioRol, SolicitudCompra


def dashboard(request):
    """Vista principal del dashboard de administración"""
    # Obtener datos para el dashboard
    modulos = Modulo.objects.filter(activo=True)
    roles = Rol.objects.filter(activo=True).select_related('modulo')

    # Estadísticas generales
    total_modulos = modulos.count()
    total_roles = roles.count()
    total_usuarios = 0  # Sin sistema de usuarios, mostrar 0
    solicitudes_pendientes = SolicitudCompra.objects.filter(estado='pendiente').count()

    context = {
        'modulos': modulos,
        'roles': roles,
        'total_modulos': total_modulos,
        'total_roles': total_roles,
        'total_usuarios': total_usuarios,
        'solicitudes_pendientes': solicitudes_pendientes,
    }

    return render(request, 'administracion/dashboard.html', context)


def dashboard_empresa(request):
    """Vista del dashboard general de la empresa"""
    # Estadísticas de la empresa
    from apps.cruceros.models import Crucero
    cruceros = Crucero.objects.all()
    total_cruceros = cruceros.count()
    cruceros_activos = cruceros.filter(estado_operativo='activo').count()

    context = {
        'total_cruceros': total_cruceros,
        'cruceros_activos': cruceros_activos,
        'cruceros': cruceros,
    }

    return render(request, 'administracion/dashboard_empresa.html', context)


def dashboard_crucero(request, crucero_id):
    """Vista del dashboard específico de un crucero"""
    from apps.cruceros.models import Crucero
    crucero = get_object_or_404(Crucero, id=crucero_id)

    # Datos del crucero para el dashboard
    presupuesto = 1000000  # Esto debería calcularse dinámicamente
    ganancias = 750000    # Esto debería calcularse dinámicamente
    costos = 250000      # Esto debería calcularse dinámicamente

    # Alertas del crucero
    alertas = []
    if crucero.fecha_ultimo_mantenimiento:
        dias_sin_mantenimiento = (timezone.now().date() - crucero.fecha_ultimo_mantenimiento).days
        if dias_sin_mantenimiento > 365:
            alertas.append({
                'mensaje': f'El crucero necesita mantenimiento. Último mantenimiento: {crucero.fecha_ultimo_mantenimiento}',
                'fecha': timezone.now()
            })

    context = {
        'crucero': crucero,
        'presupuesto': presupuesto,
        'ganancias': ganancias,
        'costos': costos,
        'alertas': alertas,
    }

    return render(request, 'administracion/dashboard_crucero.html', context)


def gestion_roles(request):
    """Vista para gestión de roles y permisos"""
    if request.method == 'POST':
        if 'usuario' in request.POST and 'rol' in request.POST:
            # Asignar rol a usuario
            usuario_id = request.POST.get('usuario')
            rol_id = request.POST.get('rol')
            fecha_expiracion = request.POST.get('fecha_expiracion')

            try:
                from django.contrib.auth.models import User
                usuario = User.objects.get(id=usuario_id)
                rol = Rol.objects.get(id=rol_id)

                # Verificar que no exista ya la asignación
                if not UsuarioRol.objects.filter(usuario=usuario, rol=rol).exists():
                    UsuarioRol.objects.create(
                        usuario=usuario,
                        rol=rol,
                        fecha_expiracion=fecha_expiracion if fecha_expiracion else None,
                        asignado_por=usuario
                    )
                    messages.success(request, f'Rol {rol.nombre} asignado a {usuario.username} exitosamente.')
                else:
                    messages.warning(request, 'Este rol ya está asignado a este usuario.')

            except (User.DoesNotExist, Rol.DoesNotExist):
                messages.error(request, 'Usuario o rol no encontrado.')

        elif 'nombre_rol' in request.POST:
            # Crear nuevo rol
            nombre = request.POST.get('nombre_rol')
            modulo_id = request.POST.get('modulo_rol')
            tipo = request.POST.get('tipo_rol')
            descripcion = request.POST.get('descripcion_rol')

            try:
                modulo = Modulo.objects.get(id=modulo_id)

                # Verificar que no exista un rol con el mismo nombre en el módulo
                if not Rol.objects.filter(nombre=nombre, modulo=modulo).exists():
                    Rol.objects.create(
                        nombre=nombre,
                        modulo=modulo,
                        tipo=tipo,
                        descripcion=descripcion
                    )
                    messages.success(request, f'Rol {nombre} creado exitosamente.')
                else:
                    messages.warning(request, 'Ya existe un rol con este nombre en este módulo.')

            except Modulo.DoesNotExist:
                messages.error(request, 'Módulo no encontrado.')

        return redirect('gestion_roles')

    # Datos para los templates
    from django.contrib.auth.models import User
    modulos = Modulo.objects.filter(activo=True)
    roles = Rol.objects.filter(activo=True).select_related('modulo')
    usuarios_roles = UsuarioRol.objects.filter(esta_activo=True).select_related('usuario', 'rol__modulo')
    usuarios = User.objects.all()

    context = {
        'modulos': modulos,
        'roles': roles,
        'usuarios_roles': usuarios_roles,
        'usuarios': usuarios,
    }

    return render(request, 'administracion/gestion_roles.html', context)


def sin_permisos(request):
    """Vista para usuarios sin permisos"""
    return render(request, 'administracion/sin_permisos.html')
