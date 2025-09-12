# --- Crear usuario desde modal ---
from .models import Empleado
from ..cruceros.models import Crucero
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from .forms import CustomAuthenticationForm, CustomPasswordChangeForm
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.db import IntegrityError
from django.urls import reverse

from .models import Rol, ModuloSistema


def create_user(request):
    """Procesa el formulario del modal para crear un usuario Empleado."""
    if request.method != 'POST':
        return HttpResponseBadRequest('Método no permitido')

    first_name = (request.POST.get('first_name') or '').strip()
    last_name = (request.POST.get('last_name') or '').strip()
    username = (request.POST.get('username') or '').strip()
    email = (request.POST.get('email') or '').strip()
    password = (request.POST.get('password') or '').strip()
    rol_id = request.POST.get('rol')
    crucero_id = request.POST.get('crucero')

    if not (first_name and last_name and username and email and password and rol_id):
        return JsonResponse({'ok': False, 'error': 'Todos los campos son obligatorios excepto crucero.'}, status=400)

    try:
        empleado = Empleado.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            rol_id=rol_id,
            crucero_id=crucero_id or None,
            activo=True
        )
        data = {'ok': True, 'id': empleado.id, 'username': empleado.username}
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(data, status=201)
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('admin:index')
        return HttpResponseRedirect(next_url)
    except IntegrityError:
        return JsonResponse({'ok': False, 'error': 'Ya existe un usuario con ese nombre de usuario o email'}, status=400)
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)
# usuarios/views.py

def custom_login(request):
    # if request.user.is_authenticated:
    #     user = request.user
    #     # si es superuser o administrativo ir a lista de cruceros
    #     if user.is_superuser or getattr(user, 'is_administrativo', False):
    #         return redirect('/')
    #     # si tiene crucero asignado, ir a su crucero
    #     if getattr(user, 'crucero_id', None):
    #         return redirect(f'/{user.crucero_id}/')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Registrar último acceso
                    user.fecha_ultimo_acceso = timezone.now()
                    user.save(update_fields=['fecha_ultimo_acceso'])

                    # Redireccionar según reglas:
                    # - superusuario o administrativo -> raiz '/' (lista de cruceros)
                    # - si tiene crucero asignado -> '/<crucero_id>/'
                    # - en otro caso, respetar next o 'dashboard'
                    if user.is_superuser or getattr(user, 'is_administrativo', False):
                        return redirect('/')
                    if getattr(user, 'crucero_id', None):
                        return redirect(f'/{user.crucero_id}/')
                    next_url = request.GET.get('next', '/')
                    return redirect(next_url)
                else:
                    messages.error(request, "Cuenta desactivada")
            else:
                messages.error(request, "Credenciales inválidas")
    else:
        form = CustomAuthenticationForm()
    
    roles = Rol.objects.filter(activo=True)
    cruceros = Crucero.objects.all()
    return render(request, 'login.html', {'form': form, 'roles': roles, 'cruceros': cruceros})

@login_required
def custom_password_change(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña actualizada correctamente')
            return redirect('password_change_done')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'auth/password_change.html', {'form': form})

class LoginRequiredMixin:
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


#@login_required
def create_role(request):

    # user = request.user
    # if not (user.is_superuser or getattr(user, 'is_administrativo', False)):
    #     return HttpResponseForbidden('No tienes permisos para crear roles')

    print("[DEBUG] create_role llamada")
    if request.method != 'POST':
        print("[DEBUG] No es POST, es:", request.method)
        return HttpResponseBadRequest('Método no permitido')
    print("[DEBUG] Es POST")
    print("[DEBUG] Es AJAX?", request.headers.get('X-Requested-With'))
    nombre = (request.POST.get('nombre') or '').strip()
    descripcion = (request.POST.get('descripcion') or '').strip()
    activo = True
    modulos_values = request.POST.getlist('modulos_acceso')
    print("[DEBUG] Datos recibidos:", nombre, descripcion, modulos_values)

    if not nombre:
        print("[DEBUG] Falta nombre")
        return JsonResponse({'ok': False, 'error': 'El nombre es requerido'}, status=400)

    try:
        rol = Rol.objects.create(nombre=nombre, descripcion=descripcion, activo=activo)
        if modulos_values:
            modulos_qs = ModuloSistema.objects.filter(codigo__in=modulos_values)
            rol.modulos_acceso.set(modulos_qs)
        data = {'ok': True, 'id': rol.id, 'nombre': rol.nombre, 'message': 'Rol creado exitosamente.'}
        print("[DEBUG] Rol creado", data)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            print("[DEBUG] Respondiendo JSON AJAX")
            return JsonResponse(data, status=201)
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('admin:index')
        print("[DEBUG] Redirigiendo a", next_url)
        return HttpResponseRedirect(next_url)

    except IntegrityError:
        print("[DEBUG] Rol duplicado")
        return JsonResponse({'ok': False, 'error': 'Ya existe un rol con ese nombre'}, status=400)
    except Exception as exc:
        print("[DEBUG] Excepción:", exc)
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)