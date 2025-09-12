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
            '/cruceros/': 'cruceros',
            '/entretenimiento/': 'entretenimiento',
            '/ventas/': 'ventas',
            '/reservas/': 'reservas',
            '/restaurante/': 'restaurante',
            '/bares/': 'bares',
            '/compras/': 'compras',
            '/almacen/': 'almacen',
            '/rh/': 'rh',
            '/medico/': 'medico',
            '/mantenimiento/': 'mantenimiento',
        }
    
    def __call__(self, request):
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