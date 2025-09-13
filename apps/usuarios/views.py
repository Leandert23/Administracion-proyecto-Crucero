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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.template.loader import render_to_string

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


@login_required
def create_user_simple(request):
    """Crea un usuario básico (sin rol ni crucero) y lo marca como staff.
    Responde JSON y está pensado para usarse desde un modal.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('Método no permitido')

    first_name = (request.POST.get('first_name') or '').strip()
    last_name = (request.POST.get('last_name') or '').strip()
    username = (request.POST.get('username') or '').strip()
    email = (request.POST.get('email') or '').strip()
    password = (request.POST.get('password') or '').strip()

    if not (first_name and last_name and username and email and password):
        return JsonResponse({'ok': False, 'error': 'Todos los campos son obligatorios'}, status=400)

    try:
        empleado = Empleado.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            activo=True
        )
        # mark as staff (but not superuser)
        empleado.is_staff = True
        empleado.is_superuser = True
        empleado.save()
        data = {'ok': True, 'id': empleado.id, 'username': empleado.username}
        return JsonResponse(data, status=201)
    except IntegrityError:
        return JsonResponse({'ok': False, 'error': 'Ya existe un usuario con ese nombre o email'}, status=400)
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
                    
                    # Registrar último acceso usando obtener_fecha_actual
                    if hasattr(user, 'actualizar_ultimo_acceso'):
                        user.actualizar_ultimo_acceso()

                    # Redireccionar según reglas:
                    # - usuario con username 'admin' -> vista de administración global
                    # - superusuario o administrativo -> raiz '/' (lista de cruceros)
                    # - si tiene crucero asignado -> '/<crucero_id>/'
                    # - en otro caso, respetar next o 'dashboard'
                    if user.username == 'admin':
                        return redirect('admin_superusers')
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


def roles_list(request):
    """Devuelve JSON con roles activos"""
    if request.method != 'GET':
        return HttpResponseBadRequest('Método no permitido')
    qs = Rol.objects.order_by('nombre')
    data = [{'id': r.id, 'nombre': r.nombre, 'descripcion': r.descripcion, 'activo': bool(r.activo)} for r in qs]
    return JsonResponse({'ok': True, 'roles': data})


def modules_list(request):
    """Devuelve JSON con módulos del sistema"""
    if request.method != 'GET':
        return HttpResponseBadRequest('Método no permitido')
    qs = ModuloSistema.objects.filter(activo=True).order_by('codigo')
    data = [{'id': m.id, 'codigo': m.codigo, 'label': str(m)} for m in qs]
    return JsonResponse({'ok': True, 'modulos': data})


@login_required
def admin_superusers(request):
    """Página que lista superusuarios sin crucero asignado. Solo accesible por el usuario con username 'admin'."""
    if request.user.username != 'admin':
        return HttpResponseForbidden('No autorizado')

    page_num = request.GET.get('page', '1')
    q = (request.GET.get('q') or '').strip()

    qs = Empleado.objects.filter(is_superuser=True, crucero__isnull=True).exclude(username='admin').order_by('username')
    if q:
        qs = qs.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q))

    data_list = []
    for u in qs:
        # pasar solo la fecha (date) o None
        ultimo_dt = getattr(u, 'fecha_ultimo_acceso', None)
        if ultimo_dt and hasattr(ultimo_dt, 'date'):
            ultimo_val = ultimo_dt.date()
        else:
            ultimo_val = None
        data_list.append({
            'id': u.id,
            'nombre': f"{u.first_name} {u.last_name}",
            'username': u.username,
            'email': u.email,
            'is_active': u.is_active,
            'ultimo_acceso': ultimo_val,
        })

    per_page = 10
    paginator = Paginator(data_list, per_page)
    try:
        page_obj = paginator.page(page_num)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    # If AJAX requested (from front-end fetch), render the partial similar to users table
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('partials/_admin_superusers_table.html', {'page_obj': page_obj}, request=request)
        return JsonResponse({'ok': True, 'html': html})

    return render(request, 'admin_superusers.html', {'page_obj': page_obj})


@login_required
def create_superuser_admin(request):
    """Crea un superusuario sin crucero asignado. Solo 'admin' puede ejecutar."""
    if request.user.username != 'admin':
        return HttpResponseForbidden('No autorizado')
    if request.method != 'POST':
        return HttpResponseBadRequest('Método no permitido')

    username = (request.POST.get('username') or '').strip()
    email = (request.POST.get('email') or '').strip()
    first_name = (request.POST.get('first_name') or '').strip()
    last_name = (request.POST.get('last_name') or '').strip()
    password = (request.POST.get('password') or '').strip()

    if not (username and email and first_name and last_name and password):
        return JsonResponse({'ok': False, 'error': 'Todos los campos son obligatorios'}, status=400)

    try:
        user = Empleado.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name, activo=True)
        # marcar como superuser/staff
        user.is_superuser = True
        user.is_staff = True
        user.crucero = None
        user.save()
        return JsonResponse({'ok': True, 'id': user.id, 'username': user.username}, status=201)
    except IntegrityError:
        return JsonResponse({'ok': False, 'error': 'Nombre de usuario o email ya en uso'}, status=400)
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)


def role_detail(request, role_id):
    """Devuelve JSON con detalles de un rol (incluye modulos asignados)"""
    if request.method != 'GET':
        return HttpResponseBadRequest('Método no permitido')
    try:
        rol = Rol.objects.get(pk=role_id)
    except Rol.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Rol no encontrado'}, status=404)
    mods = [m.id for m in rol.modulos_acceso.all()]
    data = {'id': rol.id, 'nombre': rol.nombre, 'descripcion': rol.descripcion, 'activo': bool(rol.activo), 'modulos': mods}
    return JsonResponse({'ok': True, 'role': data})


def users_by_crucero(request):
    """Devuelve JSON con usuarios del crucero actual (pasado por ?crucero_id=)"""
    if request.method != 'GET':
        return HttpResponseBadRequest('Método no permitido')
    crucero_id = request.GET.get('crucero_id')
    page_num = request.GET.get('page', '1')
    if crucero_id:
        usuarios_qs = Empleado.objects.filter(crucero_id=crucero_id).order_by('first_name', 'last_name')
    else:
        usuarios_qs = Empleado.objects.none()

    # Build a list of serializable dicts (used both for rendering and stats)
    data_list = []
    for u in usuarios_qs:
        rol_obj = getattr(u, 'rol', None)
        rol_nombre = rol_obj.nombre if rol_obj else ''
        ultimo = getattr(u, 'fecha_ultimo_acceso', None)
        data_list.append({
            'id': u.id,
            'nombre': f"{u.first_name} {u.last_name}",
            'username': u.username,
            'rol_nombre': rol_nombre,
            'is_active': u.is_active,
            'ultimo_acceso': ultimo,
        })

    # Paginate the serialized list
    per_page = 10
    paginator = Paginator(data_list, per_page)
    try:
        page_obj = paginator.page(page_num)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    # Totals for the sidebar
    totals = {
        'total': paginator.count,
        'activos': sum(1 for x in data_list if x.get('is_active')),
        'inactivos': sum(1 for x in data_list if not x.get('is_active')),
        'bloqueados': 0,
    }

    # If AJAX, render the partial and return HTML inside JSON
    html = render_to_string('partials/_users_table_pagination.html', {'page_obj': page_obj, 'totals': totals}, request=request)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'html': html})

    # For non-AJAX fallback, return the html directly
    return JsonResponse({'ok': True, 'html': html})


def search_users(request):
    """Busca usuarios por término (q). Renderiza la misma partial de tabla paginada.
    Parámetros GET: q (término de búsqueda), crucero_id (opcional), page (opcional)
    """
    if request.method != 'GET':
        return HttpResponseBadRequest('Método no permitido')

    q = (request.GET.get('q') or '').strip()
    page_num = request.GET.get('page', '1')
    crucero_id = request.GET.get('crucero_id')

    if not q:
        # si no hay término, devolver lista vacía (o la lista completa si no se quiere filtrar)
        usuarios_qs = Empleado.objects.none()
    else:
        # Buscar en username, first_name, last_name y combinación de nombres
        filtro = Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(first_name__icontains=q.split(' ')[0])
        usuarios_qs = Empleado.objects.filter(filtro).order_by('first_name', 'last_name')
        if crucero_id:
            usuarios_qs = usuarios_qs.filter(crucero_id=crucero_id)

    # Serializar como en users_by_crucero
    data_list = []
    for u in usuarios_qs:
        rol_obj = getattr(u, 'rol', None)
        rol_nombre = rol_obj.nombre if rol_obj else ''
        ultimo = getattr(u, 'fecha_ultimo_acceso', None)
        data_list.append({
            'id': u.id,
            'nombre': f"{u.first_name} {u.last_name}",
            'username': u.username,
            'rol_nombre': rol_nombre,
            'is_active': u.is_active,
            'ultimo_acceso': ultimo,
        })

    # Paginar
    per_page = 10
    paginator = Paginator(data_list, per_page)
    try:
        page_obj = paginator.page(page_num)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    totals = {
        'total': paginator.count,
        'activos': sum(1 for x in data_list if x.get('is_active')),
        'inactivos': sum(1 for x in data_list if not x.get('is_active')),
        'bloqueados': 0,
    }

    html = render_to_string('partials/_users_table_pagination.html', {'page_obj': page_obj, 'totals': totals}, request=request)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True, 'html': html})
    return JsonResponse({'ok': True, 'html': html})


@login_required
def deactivate_user(request, usuario_id):
    """Marca un usuario como inactivo (desactivar). Acepta POST (idealmente AJAX)."""
    if request.method != 'POST':
        return HttpResponseBadRequest('Método no permitido')
    try:
        user = Empleado.objects.get(pk=usuario_id)
        user.is_active = False
        user.save(update_fields=['is_active'])
        data = {'ok': True, 'id': user.id}
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(data)
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('login')
        return HttpResponseRedirect(next_url)
    except Empleado.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Usuario no encontrado'}, status=404)
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)


@login_required
def activate_user(request, usuario_id):
    """Marca un usuario como activo (reactivar)."""
    if request.method != 'POST':
        return HttpResponseBadRequest('Método no permitido')
    try:
        user = Empleado.objects.get(pk=usuario_id)
        user.is_active = True
        user.save(update_fields=['is_active'])
        data = {'ok': True, 'id': user.id}
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(data)
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('login')
        return HttpResponseRedirect(next_url)
    except Empleado.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Usuario no encontrado'}, status=404)
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)


@login_required
def edit_user(request, usuario_id):
    """Edita campos básicos de un Empleado: username, rol y (opcional) password.
    Responde JSON para solicitudes AJAX.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('Método no permitido')
    try:
        user = Empleado.objects.get(pk=usuario_id)
    except Empleado.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Usuario no encontrado'}, status=404)

    # Permisos básicos: sólo usuarios autenticados (decorador) pueden usar esto.
    # Puedes añadir comprobaciones más estrictas aquí (superuser/administrativo).

    username = (request.POST.get('username') or '').strip()
    rol_id = request.POST.get('rol')
    password = (request.POST.get('password') or '').strip()

    # Aplicar cambios
    try:
        changed = False
        if username and username != user.username:
            user.username = username
            changed = True
        if rol_id is not None and rol_id != '':
            # allow setting rol_id empty to detach? follow create_user pattern
            user.rol_id = rol_id
            changed = True
        if password:
            user.set_password(password)
            changed = True

        if changed:
            user.save()
            # si el usuario editado es el que está en sesión y cambió la contraseña, mantener la sesión
            if request.user.pk == user.pk and password:
                try:
                    update_session_auth_hash(request, user)
                except Exception:
                    pass

        data = {'ok': True, 'id': user.id}
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(data)
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('login')
        return HttpResponseRedirect(next_url)
    except IntegrityError:
        return JsonResponse({'ok': False, 'error': 'El nombre de usuario ya está en uso'}, status=400)
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)


@login_required
def edit_role(request, role_id):
    """Edita un Rol: nombre, descripcion y activo. Responde JSON para AJAX."""
    if request.method != 'POST':
        return HttpResponseBadRequest('Método no permitido')
    try:
        rol = Rol.objects.get(pk=role_id)
    except Rol.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Rol no encontrado'}, status=404)

    nombre = (request.POST.get('nombre') or '').strip()
    descripcion = (request.POST.get('descripcion') or '').strip()
    activo = request.POST.get('activo') in ('true', 'on', '1')
    modulos_values = request.POST.getlist('modulos')

    if not nombre:
        return JsonResponse({'ok': False, 'error': 'El nombre es obligatorio'}, status=400)

    try:
        rol.nombre = nombre
        rol.descripcion = descripcion
        rol.activo = activo
        rol.save()
        # actualizar modulos de acceso si se enviaron
        if modulos_values is not None:
            try:
                mod_qs = ModuloSistema.objects.filter(id__in=[int(x) for x in modulos_values])
                rol.modulos_acceso.set(mod_qs)
            except Exception:
                # ignorar si valores no son válidos
                rol.modulos_acceso.clear()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'ok': True, 'id': rol.id})
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    except IntegrityError:
        return JsonResponse({'ok': False, 'error': 'Nombre de rol duplicado'}, status=400)
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)