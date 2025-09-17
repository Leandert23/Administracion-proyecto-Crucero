# mi_proyecto/middleware/access_control.py
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings

class ModuleAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_paths = [
            '/login/',
            '/logout/',
            '/admin/login/',
            '/static/',
            '/media/',
            '/acceso-denegado/',
            '/usuarios/roles/create/', 
            '/usuarios/create/'  
        ]
        
        # Mapeo de paths a módulos
        self.path_modulo_mapping = {
            '/admin/': 'administracion',
            '/dashboard/': 'administracion',
            '/cruceros/': 'cruceros',
            '/entretenimiento/': 'entretenimiento',
            '/ventas/': 'ventas',
            '/reservas/': 'reservas',
            '/restaurante/': 'restaurante',
            '/bares/': 'bares',
            '/compras/': 'compras',
            '/almacen/': 'almacen',
            '/rh/': 'rh',
            '/recursos-humanos/': 'rh',
            '/medico/': 'medico',
            '/mantenimiento/': 'mantenimiento',
        }
    
    def __call__(self, request):
        # Actualizar fecha_ultimo_acceso si el usuario está autenticado y es un Empleado
        user = getattr(request, 'user', None)
        if user and user.is_authenticated and hasattr(user, 'actualizar_ultimo_acceso'):
            # Evitar actualizar en peticiones AJAX, static, media y public_paths
            if not (
                request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                any(request.path.startswith(path) for path in self.public_paths) or
                request.path.startswith('/static/') or
                request.path.startswith('/media/')
            ):
                try:
                    user.actualizar_ultimo_acceso()
                except Exception as e:
                    pass  # No romper el flujo si hay error
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Permitir acceso a paths públicos sin necesidad de autenticación
        if any(request.path.startswith(path) for path in self.public_paths):
            return None

        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return HttpResponseForbidden("Authentication required")
            try:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path(), login_url=settings.LOGIN_URL)
            except Exception:
                return HttpResponseRedirect(f"{settings.LOGIN_URL}?next={request.path}")
            
        # Si el usuario está autenticado y es el usuario administrador 'admin', redireccionar
        # a la vista de administración de superusuarios. Evitar bucles: permitir el acceso
        # a la propia ruta de administración y a peticiones AJAX, static, media y public_paths.
        try:
            is_admin_user = getattr(request.user, 'username', None) == 'admin'
        except Exception:
            is_admin_user = False

        admin_prefix = '/usuarios/admin/superusers'
        # Si el usuario literal 'admin' está autenticado, restringir sus accesos
        if request.user.is_authenticated and is_admin_user:
            # Permitir AJAX y recursos públicos
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return None
            if any(request.path.startswith(p) for p in self.public_paths) or request.path.startswith('/static/') or request.path.startswith('/media/'):
                return None
            # Permitir acceso al panel de superusuarios y al admin de Django
            if request.path.startswith(admin_prefix) or request.path.startswith('/admin/'):
                return None
            # En cualquier otro caso, redirigir al panel de superusuarios
            return HttpResponseRedirect(reverse('admin_superusers'))
        if request.user.is_superuser:
            return None
            
        for path_prefix, modulo in self.path_modulo_mapping.items():
            if request.path.startswith(path_prefix):
                if not request.user.tiene_acceso_modulo(modulo):
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return HttpResponseForbidden("Acceso denegado")
                    else:
                        return HttpResponseRedirect(reverse('acceso_denegado'))
        
        return None