from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps
from .models import Administracion, Alerta, Modulo, Rol, UsuarioRol

def calcular_presupuesto(administracion):
    compras = Administracion.compras.all()
    total_compras = sum([c.monto for c in compras])
    return Administracion.presupuesto_estimado - total_compras

def generar_alerta_si_excede_presupuesto(administracion):
    if calcular_presupuesto(administracion) < 0:
        Alerta.objects.create(
            mensaje='¡Presupuesto excedido!',
            administracion=administracion
        )

# Funciones para el sistema de roles
def usuario_tiene_rol(user, modulo_nombre, tipo_rol=None):
    """
    Verifica si un usuario tiene un rol específico en un módulo.
    
    Args:
        user: Usuario de Django
        modulo_nombre: Nombre del módulo
        tipo_rol: Tipo de rol específico (opcional)
    
    Returns:
        bool: True si el usuario tiene el rol, False en caso contrario
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        modulo = Modulo.objects.get(nombre=modulo_nombre, activo=True)
        roles_activos = UsuarioRol.objects.filter(
            usuario=user,
            rol__modulo=modulo,
            activo=True,
            rol__activo=True
        ).select_related('rol')
        
        # Verificar que los roles no hayan expirado
        roles_validos = [ur for ur in roles_activos if ur.esta_activo]
        
        if tipo_rol:
            return any(ur.rol.tipo == tipo_rol for ur in roles_validos)
        else:
            return len(roles_validos) > 0
            
    except Modulo.DoesNotExist:
        return False

def usuario_es_administrador_modulo(user, modulo_nombre):
    """
    Verifica si un usuario es administrador de un módulo específico.
    """
    return usuario_tiene_rol(user, modulo_nombre, 'admin')

def obtener_roles_usuario(user, modulo_nombre=None):
    """
    Obtiene todos los roles activos de un usuario.
    
    Args:
        user: Usuario de Django
        modulo_nombre: Nombre del módulo (opcional, si no se especifica devuelve todos)
    
    Returns:
        QuerySet: Roles activos del usuario
    """
    if not user or not user.is_authenticated:
        return UsuarioRol.objects.none()
    
    queryset = UsuarioRol.objects.filter(
        usuario=user,
        activo=True,
        rol__activo=True
    ).select_related('rol', 'rol__modulo')
    
    if modulo_nombre:
        queryset = queryset.filter(rol__modulo__nombre=modulo_nombre)
    
    # Filtrar roles no expirados
    return [ur for ur in queryset if ur.esta_activo]

def requerir_rol(modulo_nombre, tipo_rol=None):
    """
    Decorador para requerir un rol específico en una vista.
    
    Args:
        modulo_nombre: Nombre del módulo requerido
        tipo_rol: Tipo de rol específico (opcional)
    
    Usage:
        @requerir_rol('administracion', 'admin')
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            
            if not usuario_tiene_rol(request.user, modulo_nombre, tipo_rol):
                raise PermissionDenied(
                    f"No tienes permisos para acceder a esta sección. "
                    f"Se requiere rol de {tipo_rol or 'usuario'} en el módulo {modulo_nombre}."
                )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def requerir_administrador_modulo(modulo_nombre):
    """
    Decorador específico para requerir rol de administrador en un módulo.
    """
    return requerir_rol(modulo_nombre, 'admin')
