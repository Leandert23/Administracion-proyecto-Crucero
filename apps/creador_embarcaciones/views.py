from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views.generic import ListView, CreateView
from .models import Embarcacion, Ruta, Dia, Cubierta, Locales, Habitaciones, TipoEmbarcacion, TipoHabitacion, TipoLocal
from .forms import EmbarcacionForm, RutaForm, DiaForm


class EmbarcacionListView(ListView):
    """
    Vista para listar todas las embarcaciones
    """
    model = Embarcacion
    template_name = 'creador_embarcaciones/embarcacion_list.html'
    context_object_name = 'embarcaciones'
    paginate_by = 10
    ordering = ['-fecha_creacion']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtros opcionales por URL parameters
        estado = self.request.GET.get('estado')
        tipo = self.request.GET.get('tipo')

        if estado:
            queryset = queryset.filter(estado_operativo=estado)
        if tipo:
            queryset = queryset.filter(tipo__icontains=tipo)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estado_choices'] = Embarcacion.ESTADO_CHOICES
        context['total_embarcaciones'] = Embarcacion.objects.count()
        context['total_rutas'] = Ruta.objects.count()
        context['embarcaciones_operativas'] = Embarcacion.objects.filter(estado_operativo='operativo').count()
        return context


class EmbarcacionCreateView(CreateView):
    """
    Vista para crear una nueva embarcación
    """
    model = Embarcacion
    form_class = EmbarcacionForm
    template_name = 'creador_embarcaciones/embarcacion_form.html'
    success_url = '/embarcaciones/'

    def dispatch(self, request, *args, **kwargs):
        """
        Verificar que existan rutas antes de permitir crear embarcaciones
        """
        if not Ruta.objects.exists():
            messages.warning(request, 'No hay rutas disponibles. Debe crear al menos una ruta antes de poder crear embarcaciones.')
            return redirect('creador_embarcaciones:ruta_create')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, f'Embarcación "{form.instance.nombre}" creada exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear la embarcación. Verifica los datos e intenta nuevamente.')
        return super().form_invalid(form)


def embarcacion_detail(request, pk):
    """
    Vista para ver los detalles de una embarcación específica
    """
    embarcacion = get_object_or_404(Embarcacion, pk=pk)
    context = {
        'embarcacion': embarcacion,
    }
    return render(request, 'creador_embarcaciones/embarcacion_detail.html', context)


def embarcacion_update(request, pk):
    """
    Vista para actualizar una embarcación existente
    """
    embarcacion = get_object_or_404(Embarcacion, pk=pk)

    if request.method == 'POST':
        form = EmbarcacionForm(request.POST, instance=embarcacion)
        if form.is_valid():
            form.save()
            messages.success(request, f'Embarcación "{embarcacion.nombre}" actualizada exitosamente.')
            return redirect('creador_embarcaciones:embarcacion_detail', pk=embarcacion.pk)
    else:
        form = EmbarcacionForm(instance=embarcacion)

    context = {
        'form': form,
        'embarcacion': embarcacion,
    }
    return render(request, 'creador_embarcaciones/embarcacion_form.html', context)


def embarcacion_delete(request, pk):
    """
    Vista para eliminar una embarcación
    """
    embarcacion = get_object_or_404(Embarcacion, pk=pk)

    if request.method == 'POST':
        nombre = embarcacion.nombre
        embarcacion.delete()
        messages.success(request, f'Embarcación "{nombre}" eliminada exitosamente.')
        return redirect('creador_embarcaciones:embarcacion_list')

    context = {
        'embarcacion': embarcacion,
    }
    return render(request, 'creador_embarcaciones/embarcacion_confirm_delete.html', context)


# ========== VISTAS PARA RUTAS ==========

class RutaListView(ListView):
    """
    Vista para listar todas las rutas
    """
    model = Ruta
    template_name = 'creador_embarcaciones/ruta_list.html'
    context_object_name = 'rutas'
    paginate_by = 10
    ordering = ['-fecha_creacion']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtros opcionales por URL parameters
        crucero = self.request.GET.get('crucero')
        titulo = self.request.GET.get('titulo')

        if crucero:
            queryset = queryset.filter(crucero__icontains=crucero)
        if titulo:
            queryset = queryset.filter(titulo__icontains=titulo)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_rutas'] = Ruta.objects.count()
        return context


class RutaCreateView(CreateView):
    """
    Vista para crear una nueva ruta
    """
    model = Ruta
    form_class = RutaForm
    template_name = 'creador_embarcaciones/ruta_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Ruta "{form.instance.titulo}" creada exitosamente con {form.instance.numero_dias} días generados automáticamente.')
        messages.info(self.request, f'Los días están listos para ser configurados individualmente desde la página de detalles de la ruta.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear la ruta. Verifica los datos e intenta nuevamente.')
        return super().form_invalid(form)

    def get_success_url(self):
        """
        Redirigir a los detalles de la ruta recién creada
        """
        return reverse('creador_embarcaciones:ruta_detail', kwargs={'pk': self.object.pk})


def ruta_detail(request, pk):
    """
    Vista para ver los detalles de una ruta específica
    """
    ruta = get_object_or_404(Ruta, pk=pk)
    context = {
        'ruta': ruta,
    }
    return render(request, 'creador_embarcaciones/ruta_detail.html', context)


def ruta_update(request, pk):
    """
    Vista para actualizar una ruta existente
    """
    ruta = get_object_or_404(Ruta, pk=pk)

    if request.method == 'POST':
        form = RutaForm(request.POST, instance=ruta)
        if form.is_valid():
            form.save()
            messages.success(request, f'Ruta "{ruta.titulo}" actualizada exitosamente.')
            return redirect('creador_embarcaciones:ruta_detail', pk=ruta.pk)
    else:
        form = RutaForm(instance=ruta)

    context = {
        'form': form,
        'ruta': ruta,
    }
    return render(request, 'creador_embarcaciones/ruta_form.html', context)


def ruta_delete(request, pk):
    """
    Vista para eliminar una ruta
    """
    ruta = get_object_or_404(Ruta, pk=pk)

    if request.method == 'POST':
        titulo = ruta.titulo
        ruta.delete()
        messages.success(request, f'Ruta "{titulo}" eliminada exitosamente.')
        return redirect('creador_embarcaciones:ruta_list')

    context = {
        'ruta': ruta,
    }
    return render(request, 'creador_embarcaciones/ruta_confirm_delete.html', context)


# ========== VISTAS PARA DÍAS ==========

def dia_update(request, pk):
    """
    Vista para editar un día específico de una ruta
    """
    dia = get_object_or_404(Dia, pk=pk)

    if request.method == 'POST':
        form = DiaForm(request.POST, instance=dia)
        if form.is_valid():
            form.save()
            messages.success(request, f'Día {dia.numero_dia} actualizado exitosamente.')
            # Redirigir de vuelta a los detalles de la ruta
            return redirect('creador_embarcaciones:ruta_detail', pk=dia.ruta.pk)
    else:
        form = DiaForm(instance=dia)

    # Calcular días anterior y siguiente
    dias = list(dia.ruta.dias.all().order_by('numero_dia'))
    dia_index = dia.numero_dia - 1  # Los índices empiezan en 0

    dia_anterior = None
    dia_siguiente = None

    if dia_index > 0:
        dia_anterior = dias[dia_index - 1]
    if dia_index < len(dias) - 1:
        dia_siguiente = dias[dia_index + 1]

    context = {
        'form': form,
        'dia': dia,
        'ruta': dia.ruta,
        'dia_anterior': dia_anterior,
        'dia_siguiente': dia_siguiente,
    }
    return render(request, 'creador_embarcaciones/dia_form.html', context)


def dia_detail(request, pk):
    """
    Vista para ver los detalles de un día específico
    """
    dia = get_object_or_404(Dia, pk=pk)

    context = {
        'dia': dia,
        'ruta': dia.ruta,
    }
    return render(request, 'creador_embarcaciones/dia_detail.html', context)


# ========== VISTA DE INICIO ==========

def delete_all_embarcaciones(request):
    """
    Vista para eliminar todas las embarcaciones del sistema
    """
    if request.method == 'POST':
        # Eliminar todas las embarcaciones
        total_eliminadas = Embarcacion.objects.count()
        Embarcacion.objects.all().delete()

        messages.success(
            request,
            f'¡Todas las embarcaciones han sido eliminadas exitosamente! ({total_eliminadas} embarcaciones)'
        )
        return redirect('creador_embarcaciones:home')

    # Si no es POST, redirigir a home
    return redirect('creador_embarcaciones:home')


def delete_all_rutas(request):
    """
    Vista para eliminar todas las rutas y sus días conectados
    """
    if request.method == 'POST':
        # Eliminar todas las rutas (esto automáticamente elimina los días por CASCADE)
        total_rutas = Ruta.objects.count()
        total_dias = Dia.objects.count()

        Ruta.objects.all().delete()

        messages.success(
            request,
            f'¡Todas las rutas y días han sido eliminados exitosamente! ({total_rutas} rutas y {total_dias} días)'
        )
        return redirect('creador_embarcaciones:home')

    # Si no es POST, redirigir a home
    return redirect('creador_embarcaciones:home')


def delete_all_tipos_habitacion(request):
    """
    Vista para eliminar todos los tipos de habitación del sistema
    """
    if request.method == 'POST':
        # Eliminar todos los tipos de habitación
        total_eliminados = TipoHabitacion.objects.count()
        TipoHabitacion.objects.all().delete()

        messages.success(
            request,
            f'¡Todos los tipos de habitación han sido eliminados exitosamente! ({total_eliminados} tipos)'
        )
        return redirect('creador_embarcaciones:home')

    # Si no es POST, redirigir a home
    return redirect('creador_embarcaciones:home')


def delete_all_tipos_local(request):
    """
    Vista para eliminar todos los tipos de local del sistema
    """
    if request.method == 'POST':
        # Eliminar todos los tipos de local
        total_eliminados = TipoLocal.objects.count()
        TipoLocal.objects.all().delete()

        messages.success(
            request,
            f'¡Todos los tipos de local han sido eliminados exitosamente! ({total_eliminados} tipos)'
        )
        return redirect('creador_embarcaciones:home')

    # Si no es POST, redirigir a home
    return redirect('creador_embarcaciones:home')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def home(request):
    """
    Vista de inicio que muestra ambas tablas (embarcaciones y rutas), solo para superusuarios, administracion o compras
    """
    user = request.user
    if not (user.is_superuser or user.tiene_acceso_modulo('administracion') or user.tiene_acceso_modulo('compras')):
        return render(request, 'administracion/sin_permisos.html', status=403)
    # Obtener las primeras 10 embarcaciones y rutas para mostrar en la página de inicio
    embarcaciones = Embarcacion.objects.all()[:10]
    rutas = Ruta.objects.all()[:10]

    context = {
        'embarcaciones': embarcaciones,
        'rutas': rutas,
        'total_embarcaciones': Embarcacion.objects.count(),
        'total_rutas': Ruta.objects.count(),
        'embarcaciones_operativas': Embarcacion.objects.filter(estado_operativo='operativo').count(),
        'total_tipos_habitacion': TipoHabitacion.objects.count(),
        'total_tipos_local': TipoLocal.objects.count(),
        'estado_choices': Embarcacion.ESTADO_CHOICES,
    }
    return render(request, 'creador_embarcaciones/home.html', context)


# ========== VISTAS PARA GESTIÓN DE ESTRUCTURA DE EMBARCACIONES ==========

def embarcacion_detail(request, pk):
    """
    Vista para mostrar detalles de una embarcación con sus cubiertas
    """
    embarcacion = get_object_or_404(Embarcacion, pk=pk)
    cubiertas = embarcacion.cubiertas.all().order_by('numero')

    context = {
        'embarcacion': embarcacion,
        'cubiertas': cubiertas,
        'total_cubiertas': cubiertas.count(),
        'total_locales': sum(cubierta.locales.count() for cubierta in cubiertas),
        'total_habitaciones': sum(cubierta.habitaciones.count() for cubierta in cubiertas),
    }

    return render(request, 'creador_embarcaciones/embarcacion_detail.html', context)


def cubierta_detail(request, embarcacion_pk, cubierta_pk):
    """
    Vista para mostrar detalles de una cubierta específica con sus locales y habitaciones
    """
    embarcacion = get_object_or_404(Embarcacion, pk=embarcacion_pk)
    cubierta = get_object_or_404(Cubierta, pk=cubierta_pk, embarcacion=embarcacion)

    locales = cubierta.locales.all().order_by('tipo', 'nombre')
    habitaciones = cubierta.habitaciones.all().order_by('numero')

    context = {
        'embarcacion': embarcacion,
        'cubierta': cubierta,
        'locales': locales,
        'habitaciones': habitaciones,
        'total_locales': locales.count(),
        'total_habitaciones': habitaciones.count(),
    }

    return render(request, 'creador_embarcaciones/cubierta_detail.html', context)


# ========== VISTAS PARA GESTIÓN DE LOCALES ==========

def local_create(request, embarcacion_pk, cubierta_pk):
    """
    Vista para crear un nuevo local en una cubierta específica
    """
    embarcacion = get_object_or_404(Embarcacion, pk=embarcacion_pk)
    cubierta = get_object_or_404(Cubierta, pk=cubierta_pk, embarcacion=embarcacion)

    if request.method == 'POST':
        tipo_seleccionado = request.POST.get('tipo')

        # Verificar si se seleccionó un tipo estándar
        if tipo_seleccionado and tipo_seleccionado.startswith('estandar_'):
            # Extraer el ID del tipo estándar
            tipo_estandar_id = tipo_seleccionado.replace('estandar_', '')
            try:
                tipo_estandar = TipoLocal.objects.get(pk=tipo_estandar_id)
                tipo_real = tipo_estandar.tipo  # Obtener el tipo real del modelo TipoLocal
            except TipoLocal.DoesNotExist:
                messages.error(request, 'Tipo de local estándar no encontrado.')
                return redirect('creador_embarcaciones:cubierta_detail', embarcacion_pk=embarcacion.pk, cubierta_pk=cubierta.pk)
        else:
            tipo_real = tipo_seleccionado

        # Crear el local con los datos del POST
        local = Locales(
            tipo=tipo_real,
            nombre=request.POST.get('nombre'),
            ID_local=request.POST.get('ID_local'),
            estado=request.POST.get('estado', 'operativo'),
            area_metros_cuadrados=request.POST.get('area_metros_cuadrados'),
            cubierta=cubierta,
            n_cubierta=cubierta.numero,
            ultimo_mantenimiento=request.POST.get('ultimo_mantenimiento'),
            proximo_mantenimiento=request.POST.get('proximo_mantenimiento'),
        )
        local.save()

        messages.success(request, f'Local "{local.nombre}" creado exitosamente.')
        return redirect('creador_embarcaciones:cubierta_detail', embarcacion_pk=embarcacion.pk, cubierta_pk=cubierta.pk)

    context = {
        'embarcacion': embarcacion,
        'cubierta': cubierta,
        'tipo_choices': Locales.TIPO_CHOICES,
        'estado_choices': Locales.ESTADO_CHOICES,
    }

    return render(request, 'creador_embarcaciones/local_form.html', context)


def local_update(request, pk):
    """
    Vista para editar un local existente
    """
    local = get_object_or_404(Locales, pk=pk)
    cubierta = local.cubierta
    embarcacion = cubierta.embarcacion

    if request.method == 'POST':
        tipo_seleccionado = request.POST.get('tipo')

        # Verificar si se seleccionó un tipo estándar
        if tipo_seleccionado and tipo_seleccionado.startswith('estandar_'):
            # Extraer el ID del tipo estándar
            tipo_estandar_id = tipo_seleccionado.replace('estandar_', '')
            try:
                tipo_estandar = TipoLocal.objects.get(pk=tipo_estandar_id)
                tipo_real = tipo_estandar.tipo  # Obtener el tipo real del modelo TipoLocal
            except TipoLocal.DoesNotExist:
                messages.error(request, 'Tipo de local estándar no encontrado.')
                return redirect('creador_embarcaciones:cubierta_detail', embarcacion_pk=embarcacion.pk, cubierta_pk=cubierta.pk)
        else:
            tipo_real = tipo_seleccionado

        # Actualizar el local con los datos del POST
        local.tipo = tipo_real
        local.nombre = request.POST.get('nombre')
        local.ID_local = request.POST.get('ID_local')
        local.estado = request.POST.get('estado', 'operativo')
        local.area_metros_cuadrados = request.POST.get('area_metros_cuadrados')
        local.ultimo_mantenimiento = request.POST.get('ultimo_mantenimiento')
        local.proximo_mantenimiento = request.POST.get('proximo_mantenimiento')
        local.save()

        messages.success(request, f'Local "{local.nombre}" actualizado exitosamente.')
        return redirect('creador_embarcaciones:cubierta_detail', embarcacion_pk=embarcacion.pk, cubierta_pk=cubierta.pk)

    context = {
        'embarcacion': embarcacion,
        'cubierta': cubierta,
        'local': local,
        'tipo_choices': Locales.TIPO_CHOICES,
        'estado_choices': Locales.ESTADO_CHOICES,
    }

    return render(request, 'creador_embarcaciones/local_form.html', context)


def local_delete(request, pk):
    """
    Vista para eliminar un local
    """
    local = get_object_or_404(Locales, pk=pk)
    cubierta = local.cubierta
    embarcacion = cubierta.embarcacion

    if request.method == 'POST':
        nombre_local = local.nombre
        local.delete()
        messages.success(request, f'Local "{nombre_local}" eliminado exitosamente.')
        return redirect('creador_embarcaciones:cubierta_detail', embarcacion_pk=embarcacion.pk, cubierta_pk=cubierta.pk)

    context = {
        'embarcacion': embarcacion,
        'cubierta': cubierta,
        'local': local,
    }

    return render(request, 'creador_embarcaciones/local_confirm_delete.html', context)


# ========== VISTAS PARA GESTIÓN DE HABITACIONES ==========

# ========== VISTAS PARA DETALLES ESPECÍFICOS ==========

def local_detail(request, pk):
    """
    Vista para mostrar detalles específicos de un local
    """
    local = get_object_or_404(Locales, pk=pk)
    cubierta = local.cubierta
    embarcacion = cubierta.embarcacion

    context = {
        'embarcacion': embarcacion,
        'cubierta': cubierta,
        'local': local,
    }

    return render(request, 'creador_embarcaciones/local_detail.html', context)


# ========== VISTAS PARA GESTIÓN DE HABITACIONES ==========

def habitacion_create(request, embarcacion_pk, cubierta_pk):
    """
    Vista para crear una nueva habitación en una cubierta específica
    """
    embarcacion = get_object_or_404(Embarcacion, pk=embarcacion_pk)
    cubierta = get_object_or_404(Cubierta, pk=cubierta_pk, embarcacion=embarcacion)

    if request.method == 'POST':
        # Obtener el tipo de habitación estándar seleccionado
        tipo_habitacion_id = request.POST.get('tipo_habitacion_id')
        tipo_estandar = None
        if tipo_habitacion_id:
            from .models import TipoHabitacion
            try:
                tipo_estandar = TipoHabitacion.objects.get(pk=tipo_habitacion_id)
            except TipoHabitacion.DoesNotExist:
                pass

        # Obtener datos del formulario
        numero = request.POST.get('numero')
        posicion = request.POST.get('posicion')

        # Validar datos obligatorios
        if not numero or not posicion or not tipo_habitacion_id:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('creador_embarcaciones:cubierta_detail', embarcacion_pk=embarcacion.pk, cubierta_pk=cubierta.pk)

        # Crear la habitación
        habitacion = Habitaciones(
            tipo_habitacion_estandar=tipo_estandar,
            numero=int(numero),
            posicion=posicion,
            area_metros_cuadrados=tipo_estandar.area_metros_cuadrados if tipo_estandar else 0,
            cubierta=cubierta,
            n_cubierta=cubierta.numero,
            estado=tipo_estandar.estado_default if tipo_estandar else 'disponible',
            precio=tipo_estandar.precio_base if tipo_estandar else 0,
        )

        # Establecer fechas de mantenimiento basadas en el tipo estándar
        if tipo_estandar:
            from datetime import datetime, timedelta
            hoy = datetime.now().date()
            habitacion.ultimo_mantenimiento = hoy - timedelta(days=tipo_estandar.ultimo_mantenimiento_dias)
            habitacion.proximo_mantenimiento = hoy + timedelta(days=tipo_estandar.proximo_mantenimiento_dias)

        habitacion.save()

        messages.success(request, f'Habitación {habitacion.numero} creada exitosamente con ID: {habitacion.ID_local}')
        return redirect('creador_embarcaciones:cubierta_detail', embarcacion_pk=embarcacion.pk, cubierta_pk=cubierta.pk)

    context = {
        'embarcacion': embarcacion,
        'cubierta': cubierta,
    }

    return render(request, 'creador_embarcaciones/habitacion_form.html', context)


def habitacion_update(request, pk):
    """
    Vista para editar una habitación existente
    """
    habitacion = get_object_or_404(Habitaciones, pk=pk)
    cubierta = habitacion.cubierta
    embarcacion = cubierta.embarcacion

    if request.method == 'POST':
        # Actualizar la habitación con los datos del POST
        habitacion.numero = int(request.POST.get('numero'))
        habitacion.posicion = request.POST.get('posicion')
        habitacion.estado = request.POST.get('estado', 'disponible')
        habitacion.precio = request.POST.get('precio')
        habitacion.id_persona = request.POST.get('id_persona', '')
        habitacion.ultimo_mantenimiento = request.POST.get('ultimo_mantenimiento')
        habitacion.proximo_mantenimiento = request.POST.get('proximo_mantenimiento')
        habitacion.save()

        messages.success(request, f'Habitación {habitacion.numero} actualizada exitosamente.')
        return redirect('creador_embarcaciones:cubierta_detail', embarcacion_pk=embarcacion.pk, cubierta_pk=cubierta.pk)

    context = {
        'embarcacion': embarcacion,
        'cubierta': cubierta,
        'habitacion': habitacion,
        'estado_choices': Habitaciones.ESTADO_CHOICES,
        'posicion_choices': Habitaciones.POSICION_CHOICES,
    }

    return render(request, 'creador_embarcaciones/habitacion_form.html', context)


def habitacion_delete(request, pk):
    """
    Vista para eliminar una habitación
    """
    habitacion = get_object_or_404(Habitaciones, pk=pk)
    cubierta = habitacion.cubierta
    embarcacion = cubierta.embarcacion

    if request.method == 'POST':
        numero_habitacion = habitacion.numero
        habitacion.delete()
        messages.success(request, f'Habitación {numero_habitacion} eliminada exitosamente.')
        return redirect('creador_embarcaciones:cubierta_detail', embarcacion_pk=embarcacion.pk, cubierta_pk=cubierta.pk)

    context = {
        'embarcacion': embarcacion,
        'cubierta': cubierta,
        'habitacion': habitacion,
    }

    return render(request, 'creador_embarcaciones/habitacion_confirm_delete.html', context)


def habitacion_detail(request, pk):
    """
    Vista para mostrar detalles específicos de una habitación
    """
    habitacion = get_object_or_404(Habitaciones, pk=pk)
    cubierta = habitacion.cubierta
    embarcacion = cubierta.embarcacion

    context = {
        'embarcacion': embarcacion,
        'cubierta': cubierta,
        'habitacion': habitacion,
    }

    return render(request, 'creador_embarcaciones/habitacion_detail.html', context)


# ========== VISTAS MODALES PARA ESTÁNDARES ==========

def crear_tipo_habitacion(request):
    """
    Vista modal para crear un nuevo tipo de habitación estándar
    """
    if request.method == 'POST':
        # Debug: Imprimir todos los datos POST
        print("DEBUG - Datos POST recibidos:")
        for key, value in request.POST.items():
            print(f"  {key}: {value}")

        try:
            # Verificar que tenemos todos los campos requeridos
            nombre = request.POST.get('nombre')
            tipo = request.POST.get('tipo')
            area = request.POST.get('area_metros_cuadrados')

            print(f"DEBUG - Campos requeridos: nombre={nombre}, tipo={tipo}, area={area}")

            if not nombre or not tipo or not area:
                messages.error(request, 'Faltan campos requeridos: nombre, tipo, área')
                return redirect('creador_embarcaciones:home')

            tipo_habitacion = TipoHabitacion(
                nombre=nombre,
                descripcion=request.POST.get('descripcion'),
                tipo=tipo,
                area_metros_cuadrados=area,
                precio_base=request.POST.get('precio_base') or None,
                estado_default=request.POST.get('estado_default', 'disponible'),
                # Especificaciones
                capacidad_personas=request.POST.get('capacidad_personas', 2),
                numero_camas=request.POST.get('numero_camas', 1),
                tiene_bano_privado=request.POST.get('tiene_bano_privado') == 'on',
                tiene_balcon=request.POST.get('tiene_balcon') == 'on',
                tiene_vista_mar=request.POST.get('tiene_vista_mar') == 'on',
                # Mantenimiento
                ultimo_mantenimiento_dias=request.POST.get('ultimo_mantenimiento_dias', 30),
                proximo_mantenimiento_dias=request.POST.get('proximo_mantenimiento_dias', 180)
            )

            print(f"DEBUG - Guardando TipoHabitacion: {tipo_habitacion.nombre}")
            tipo_habitacion.save()
            print(f"DEBUG - TipoHabitacion guardado con ID: {tipo_habitacion.id}")

            messages.success(request, f'Tipo de habitación "{tipo_habitacion.nombre}" creado exitosamente.')
            return redirect('creador_embarcaciones:home')

        except Exception as e:
            print(f"DEBUG - Error al guardar: {str(e)}")
            messages.error(request, f'Error al crear el tipo de habitación: {str(e)}')
            return redirect('creador_embarcaciones:home')

    context = {
        'tipo_choices': TipoHabitacion.POSICION_CHOICES,
        'estado_choices': TipoHabitacion.ESTADO_CHOICES,
    }

    return render(request, 'creador_embarcaciones/modals/crear_tipo_habitacion.html', context)


def crear_tipo_local(request):
    """
    Vista modal para crear un nuevo tipo de local estándar
    """
    if request.method == 'POST':
        # Debug: Imprimir todos los datos POST
        print("DEBUG - Datos POST recibidos para TipoLocal:")
        for key, value in request.POST.items():
            print(f"  {key}: {value}")

        try:
            # Verificar que tenemos todos los campos requeridos
            nombre = request.POST.get('nombre')
            tipo = request.POST.get('tipo')
            area = request.POST.get('area_metros_cuadrados')

            print(f"DEBUG - Campos requeridos: nombre={nombre}, tipo={tipo}, area={area}")

            if not nombre or not tipo or not area:
                messages.error(request, 'Faltan campos requeridos: nombre, tipo, área')
                return redirect('creador_embarcaciones:home')

            tipo_local = TipoLocal(
                nombre=nombre,
                descripcion=request.POST.get('descripcion'),
                tipo=tipo,
                area_metros_cuadrados=area,
                estado_default=request.POST.get('estado_default', 'operativo'),
                # Especificaciones
                capacidad_personas=request.POST.get('capacidad_personas', 50),
                tiene_ventilacion=request.POST.get('tiene_ventilacion') == 'on',
                tiene_iluminacion_especial=request.POST.get('tiene_iluminacion_especial') == 'on',
                # Mantenimiento
                ultimo_mantenimiento_dias=request.POST.get('ultimo_mantenimiento_dias', 30),
                proximo_mantenimiento_dias=request.POST.get('proximo_mantenimiento_dias', 90)
            )

            print(f"DEBUG - Guardando TipoLocal: {tipo_local.nombre}")
            tipo_local.save()
            print(f"DEBUG - TipoLocal guardado con ID: {tipo_local.id}")

            messages.success(request, f'Tipo de local "{tipo_local.nombre}" creado exitosamente.')
            return redirect('creador_embarcaciones:home')

        except Exception as e:
            print(f"DEBUG - Error al guardar TipoLocal: {str(e)}")
            messages.error(request, f'Error al crear el tipo de local: {str(e)}')
            return redirect('creador_embarcaciones:home')

    context = {
        'tipo_choices': Locales.TIPO_CHOICES,
        'estado_choices': Locales.ESTADO_CHOICES,
    }

    return render(request, 'creador_embarcaciones/modals/crear_tipo_local.html', context)


def obtener_tipos_habitacion(request):
    """
    Vista AJAX para obtener la lista de tipos de habitación disponibles
    """
    tipos = TipoHabitacion.objects.all().order_by('nombre')
    data = []
    for tipo in tipos:
        data.append({
            'id': tipo.id,
            'nombre': tipo.nombre,
            'tipo': tipo.get_tipo_display(),
            'area': str(tipo.area_metros_cuadrados),
            'precio': str(tipo.precio_base) if tipo.precio_base else None,
            'estado_default': tipo.estado_default,
            # Especificaciones adicionales
            'capacidad_personas': tipo.capacidad_personas,
            'numero_camas': tipo.numero_camas,
            'tiene_bano_privado': tipo.tiene_bano_privado,
            'tiene_balcon': tipo.tiene_balcon,
            'tiene_vista_mar': tipo.tiene_vista_mar,
            # Mantenimiento
            'ultimo_mantenimiento_dias': tipo.ultimo_mantenimiento_dias,
            'proximo_mantenimiento_dias': tipo.proximo_mantenimiento_dias,
        })

    from django.http import JsonResponse
    return JsonResponse({'tipos': data})


def obtener_tipos_local(request):
    """
    Vista AJAX para obtener la lista de tipos de local disponibles
    """
    tipos = TipoLocal.objects.all().order_by('nombre')
    data = []
    for tipo in tipos:
        data.append({
            'id': tipo.id,
            'nombre': tipo.nombre,
            'tipo': tipo.get_tipo_display(),
            'area': str(tipo.area_metros_cuadrados),
            'estado_default': tipo.estado_default,
            # Especificaciones adicionales
            'capacidad_personas': tipo.capacidad_personas,
            'tiene_ventilacion': tipo.tiene_ventilacion,
            'tiene_iluminacion_especial': tipo.tiene_iluminacion_especial,
            # Mantenimiento
            'ultimo_mantenimiento_dias': tipo.ultimo_mantenimiento_dias,
            'proximo_mantenimiento_dias': tipo.proximo_mantenimiento_dias,
        })

    from django.http import JsonResponse
    return JsonResponse({'tipos': data})
