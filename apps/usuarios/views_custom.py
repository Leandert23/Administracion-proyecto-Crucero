from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from .models_custom import RolCustom, UsuarioCustom
import json

@csrf_exempt
@require_GET
def listar_usuarios_custom(request):
    usuarios = []
    for u in UsuarioCustom.objects.select_related('rol').all():
        usuarios.append({
            'id': u.id,
            'username': u.username,
            'nombre': u.nombre,
            'apellido': u.apellido,
            'rol_nombre': u.rol.nombre if u.rol else ''
        })
    return JsonResponse({'ok': True, 'usuarios': usuarios})

@csrf_exempt
@require_POST
def crear_rol_custom(request):
    nombre = request.POST.get('nombre', '').strip()
    descripcion = request.POST.get('descripcion', '').strip()
    modulos = request.POST.getlist('modulos')
    
    if not nombre:
        return JsonResponse({'ok': False, 'error': 'El nombre es requerido'})
    
    # Verificar si ya existe un rol con ese nombre
    if RolCustom.objects.filter(nombre=nombre).exists():
        return JsonResponse({'ok': False, 'error': f'Ya existe un rol con el nombre "{nombre}". Por favor, elige un nombre diferente.'})
    
    try:
        rol = RolCustom.objects.create(nombre=nombre, descripcion=descripcion, modulos=modulos)
        return JsonResponse({'ok': True, 'id': rol.id})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})

@csrf_exempt
@require_GET
def listar_roles_custom(request):
    roles = []
    for rol in RolCustom.objects.all():
        roles.append({
            'id': rol.id,
            'nombre': rol.nombre,
            'modulos': rol.modulos if rol.modulos else []
        })
    return JsonResponse({'ok': True, 'roles': roles})

@csrf_exempt
@require_GET
def verificar_nombre_rol(request):
    nombre = request.GET.get('nombre', '').strip()
    if not nombre:
        return JsonResponse({'ok': True, 'exists': False})
    
    exists = RolCustom.objects.filter(nombre=nombre).exists()
    return JsonResponse({'ok': True, 'exists': exists})

from .models import Empleado, Rol

@csrf_exempt
@require_POST
def eliminar_usuario_custom(request):
    user_id = request.POST.get('id')
    from .models import Empleado
    try:
        usuario = UsuarioCustom.objects.get(id=user_id)
        # Eliminar también el usuario Django (Empleado) asociado por username
        Empleado.objects.filter(username=usuario.username).delete()
        usuario.delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})

@csrf_exempt
@require_POST
def eliminar_rol_custom(request):
    rol_id = request.POST.get('id')
    from .models import Rol
    try:
        rol = RolCustom.objects.get(id=rol_id)
        # Eliminar también el rol Django asociado por nombre
        Rol.objects.filter(nombre=rol.nombre).delete()
        rol.delete()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})

@csrf_exempt
@require_POST
def crear_usuario_custom(request):
    nombre = request.POST.get('nombre', '').strip()
    apellido = request.POST.get('apellido', '').strip()
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '').strip()
    rol_id = request.POST.get('rol')
    if not (nombre and apellido and username and password and rol_id):
        return JsonResponse({'ok': False, 'error': 'Todos los campos son obligatorios'})
    try:
        # Crear usuario custom
        usuario = UsuarioCustom.objects.create(
            nombre=nombre,
            apellido=apellido,
            username=username,
            password=password,
            rol_id=rol_id
        )
        # Crear usuario Django/Empleado
        rol_django = None
        try:
            rol_custom = RolCustom.objects.get(id=rol_id)
            rol_django = Rol.objects.filter(nombre=rol_custom.nombre).first()
            if not rol_django:
                rol_django = Rol.objects.create(nombre=rol_custom.nombre, descripcion=rol_custom.descripcion)
            # Sincronizar módulos de acceso
            modulos_codigos = rol_custom.modulos if rol_custom.modulos else []
            from .models import ModuloSistema
            modulos = ModuloSistema.objects.filter(codigo__in=modulos_codigos)
            rol_django.modulos_acceso.set(modulos)
            rol_django.save()
        except Exception as e:
            return JsonResponse({'ok': False, 'error': f'Error al sincronizar rol: {str(e)}'})
        empleado = Empleado.objects.create_user(
            username=username,
            password=password,
            first_name=nombre,
            last_name=apellido,
            rol=rol_django
        )
        return JsonResponse({'ok': True, 'id': usuario.id})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)})
