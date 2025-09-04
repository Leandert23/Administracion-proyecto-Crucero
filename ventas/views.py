from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Cliente, Venta, DetalleVenta, MetodoPago, Pago
from .forms import ClienteForm, VentaForm, DetalleVentaFormSet

@login_required
def dashboard_ventas(request):
    """Vista del dashboard principal de ventas"""
    # Estadísticas del día
    hoy = timezone.now().date()
    ventas_hoy = Venta.objects.filter(fecha_venta__date=hoy)
    total_hoy = ventas_hoy.aggregate(total=Sum('monto_total'))['total'] or 0
    cantidad_hoy = ventas_hoy.count()
    
    # Estadísticas de la semana
    inicio_semana = hoy - timedelta(days=7)
    ventas_semana = Venta.objects.filter(fecha_venta__date__gte=inicio_semana)
    total_semana = ventas_semana.aggregate(total=Sum('monto_total'))['total'] or 0
    
    # Ventas por tipo
    ventas_por_tipo = Venta.objects.values('tipo_venta').annotate(
        total=Sum('monto_total'),
        cantidad=Count('id')
    ).order_by('-total')
    
    # Últimas ventas
    ultimas_ventas = Venta.objects.select_related('cliente').order_by('-fecha_venta')[:10]
    
    context = {
        'total_hoy': total_hoy,
        'cantidad_hoy': cantidad_hoy,
        'total_semana': total_semana,
        'ventas_por_tipo': ventas_por_tipo,
        'ultimas_ventas': ultimas_ventas,
    }
    
    return render(request, 'ventas/dashboard.html', context)

@login_required
def lista_ventas(request):
    """Vista para listar todas las ventas"""
    ventas = Venta.objects.select_related('cliente', 'vendedor').order_by('-fecha_venta')
    
    # Filtros
    tipo_venta = request.GET.get('tipo_venta')
    estado = request.GET.get('estado')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if tipo_venta:
        ventas = ventas.filter(tipo_venta=tipo_venta)
    if estado:
        ventas = ventas.filter(estado=estado)
    if fecha_inicio:
        ventas = ventas.filter(fecha_venta__date__gte=fecha_inicio)
    if fecha_fin:
        ventas = ventas.filter(fecha_venta__date__lte=fecha_fin)
    
    context = {
        'ventas': ventas,
        'tipos_venta': Venta.TIPO_VENTA_CHOICES,
        'estados': Venta.ESTADO_CHOICES,
    }
    
    return render(request, 'ventas/lista_ventas.html', context)

@login_required
def detalle_venta(request, venta_id):
    """Vista para mostrar el detalle de una venta"""
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = venta.detalles.all()
    pagos = venta.pagos.all()
    
    context = {
        'venta': venta,
        'detalles': detalles,
        'pagos': pagos,
    }
    
    return render(request, 'ventas/detalle_venta.html', context)

@login_required
def nueva_venta(request):
    """Vista para crear una nueva venta"""
    if request.method == 'POST':
        form = VentaForm(request.POST)
        formset = DetalleVentaFormSet(request.POST, prefix='detalles')
        
        if form.is_valid() and formset.is_valid():
            venta = form.save(commit=False)
            venta.vendedor = request.user
            venta.save()
            
            # Guardar detalles
            formset.instance = venta
            formset.save()
            
            # Calcular monto total
            total = sum(detalle.subtotal for detalle in venta.detalles.all())
            venta.monto_total = total
            venta.save()
            
            messages.success(request, 'Venta creada exitosamente.')
            return redirect('ventas:detalle_venta', venta_id=venta.id)
    else:
        form = VentaForm()
        formset = DetalleVentaFormSet(prefix='detalles')
    
    context = {
        'form': form,
        'formset': formset,
        'tipos_venta': Venta.TIPO_VENTA_CHOICES,
    }
    
    return render(request, 'ventas/nueva_venta.html', context)

@login_required
def editar_venta(request, venta_id):
    """Vista para editar una venta existente"""
    venta = get_object_or_404(Venta, id=venta_id)
    
    if request.method == 'POST':
        form = VentaForm(request.POST, instance=venta)
        formset = DetalleVentaFormSet(request.POST, instance=venta, prefix='detalles')
        
        if form.is_valid() and formset.is_valid():
            venta = form.save()
            formset.save()
            
            # Recalcular monto total
            total = sum(detalle.subtotal for detalle in venta.detalles.all())
            venta.monto_total = total
            venta.save()
            
            messages.success(request, 'Venta actualizada exitosamente.')
            return redirect('ventas:detalle_venta', venta_id=venta.id)
    else:
        form = VentaForm(instance=venta)
        formset = DetalleVentaFormSet(instance=venta, prefix='detalles')
    
    context = {
        'form': form,
        'formset': formset,
        'venta': venta,
        'tipos_venta': Venta.TIPO_VENTA_CHOICES,
    }
    
    return render(request, 'ventas/editar_venta.html', context)

@login_required
def lista_clientes(request):
    """Vista para listar todos los clientes"""
    clientes = Cliente.objects.all().order_by('nombre', 'apellido')
    
    # Búsqueda
    query = request.GET.get('q')
    if query:
        clientes = clientes.filter(
            models.Q(nombre__icontains=query) |
            models.Q(apellido__icontains=query) |
            models.Q(email__icontains=query)
        )
    
    context = {
        'clientes': clientes,
        'query': query,
    }
    
    return render(request, 'ventas/lista_clientes.html', context)

@login_required
def nuevo_cliente(request):
    """Vista para crear un nuevo cliente"""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, 'Cliente creado exitosamente.')
            return redirect('ventas:lista_clientes')
    else:
        form = ClienteForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'ventas/nuevo_cliente.html', context)

@login_required
def editar_cliente(request, cliente_id):
    """Vista para editar un cliente existente"""
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente.')
            return redirect('ventas:lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'cliente': cliente,
    }
    
    return render(request, 'ventas/editar_cliente.html', context)
