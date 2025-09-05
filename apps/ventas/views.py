from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Cliente, Venta, DetalleVenta, MetodoPago, Pago
from .forms import ClienteForm, VentaForm, DetalleVentaFormSet
from apps.cruceros.models import Crucero

def dashboard_ventas(request, crucero_id):
    """Vista del dashboard principal de ventas"""
    crucero = get_object_or_404(Crucero, id=crucero_id)
    hoy = timezone.now().date()
    ventas_hoy = Venta.objects.filter(fecha_venta__date=hoy, crucero_id=crucero_id)
    total_hoy = ventas_hoy.aggregate(total=Sum('monto_total'))['total'] or 0
    cantidad_hoy = ventas_hoy.count()
    
    # Estadísticas de la semana
    inicio_semana = hoy - timedelta(days=7)
    ventas_semana = Venta.objects.filter(fecha_venta__date__gte=inicio_semana, crucero_id=crucero_id)
    total_semana = ventas_semana.aggregate(total=Sum('monto_total'))['total'] or 0
    
    # Ventas por tipo
    ventas_por_tipo = Venta.objects.filter(crucero_id=crucero_id).values('tipo_venta').annotate(
        total=Sum('monto_total'),
        cantidad=Count('id')
    ).order_by('-total')
    
    # Últimas ventas
    ultimas_ventas = Venta.objects.filter(crucero_id=crucero_id).select_related('cliente').order_by('-fecha_venta')[:10]
    
    context = {
        'total_hoy': total_hoy,
        'cantidad_hoy': cantidad_hoy,
        'total_semana': total_semana,
        'ventas_por_tipo': ventas_por_tipo,
        'ultimas_ventas': ultimas_ventas,
        'crucero_id': crucero_id,
        'crucero': crucero,
    }
    return render(request, 'ventas/dashboard.html', context)

def lista_ventas(request, crucero_id):
    """Vista para listar todas las ventas"""
    crucero = get_object_or_404(Crucero, id=crucero_id)
    ventas = Venta.objects.select_related('cliente').filter(crucero_id=crucero_id).order_by('-fecha_venta')
    
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
        'crucero_id': crucero_id,
        'crucero': crucero,
    }
    
    return render(request, 'ventas/lista_ventas.html', context)

def detalle_venta(request, crucero_id, venta_id):
    """Vista para mostrar el detalle de una venta"""
    crucero = get_object_or_404(Crucero, id=crucero_id)
    venta = get_object_or_404(Venta, id=venta_id, crucero_id=crucero_id)
    detalles = venta.detalles.all()
    pagos = venta.pagos.all()
    
    context = {
        'venta': venta,
        'detalles': detalles,
        'pagos': pagos,
        'crucero_id': crucero_id,
        'crucero': crucero,
    }
    
    return render(request, 'ventas/detalle_venta.html', context)

def nueva_venta(request, crucero_id):
    """Vista para crear una nueva venta"""
    crucero = get_object_or_404(Crucero, id=crucero_id)
    if request.method == 'POST':
        form = VentaForm(request.POST)
        formset = DetalleVentaFormSet(request.POST, prefix='detalles')
        if form.is_valid() and formset.is_valid():
            venta = form.save(commit=False)
            venta.crucero_id = crucero_id
            # Calculate total BEFORE saving venta
            total = 0
            for detalle_form in formset:
                if detalle_form.cleaned_data:
                    cantidad = detalle_form.cleaned_data.get('cantidad', 0)
                    precio_unitario = detalle_form.cleaned_data.get('precio_unitario', 0)
                    total += cantidad * precio_unitario
            venta.monto_total = total
            venta.save()
            formset.instance = venta
            formset.save()
            messages.success(request, 'Venta creada exitosamente.')
            return redirect('ventas:detalle_venta', crucero_id=crucero_id, venta_id=venta.id)
    else:
        form = VentaForm()
        formset = DetalleVentaFormSet(prefix='detalles')
    context = {
        'form': form,
        'formset': formset,
        'tipos_venta': Venta.TIPO_VENTA_CHOICES,
        'crucero_id': crucero_id,
        'crucero': crucero,
    }
    return render(request, 'ventas/nueva_venta.html', context)

def editar_venta(request, crucero_id, venta_id):
    """Vista para editar una venta existente"""
    crucero = get_object_or_404(Crucero, id=crucero_id)
    venta = get_object_or_404(Venta, id=venta_id, crucero_id=crucero_id)
    
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
            return redirect('ventas:detalle_venta', crucero_id=crucero_id, venta_id=venta.id)
    else:
        form = VentaForm(instance=venta)
        formset = DetalleVentaFormSet(instance=venta, prefix='detalles')
    
    context = {
        'form': form,
        'formset': formset,
        'venta': venta,
        'tipos_venta': Venta.TIPO_VENTA_CHOICES,
        'crucero_id': crucero_id,
        'crucero': crucero,
    }
    
    return render(request, 'ventas/editar_venta.html', context)

def lista_clientes(request, crucero_id):
    """Vista para listar todos los clientes"""
    crucero = get_object_or_404(Crucero, id=crucero_id)
    clientes = Cliente.objects.all().order_by('nombre', 'apellido')
    
    # Búsqueda
    from django.db.models import Q
    query = request.GET.get('q')
    if query:
        clientes = clientes.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(email__icontains=query)
        )
    
    context = {
        'clientes': clientes,
        'query': query,
        'crucero_id': crucero_id,
        'crucero': crucero,
    }
    
    return render(request, 'ventas/lista_clientes.html', context)

def nuevo_cliente(request, crucero_id):
    """Vista para crear un nuevo cliente"""
    crucero = get_object_or_404(Crucero, id=crucero_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, 'Cliente creado exitosamente.')
            return redirect('ventas:lista_clientes', crucero_id=crucero_id)
    else:
        form = ClienteForm()
    context = {
        'form': form,
        'crucero_id': crucero_id,
        'crucero': crucero,
    }
    return render(request, 'ventas/nuevo_cliente.html', context)

def editar_cliente(request, crucero_id, cliente_id):
    """Vista para editar un cliente existente"""
    crucero = get_object_or_404(Crucero, id=crucero_id)
    cliente = get_object_or_404(Cliente, id=cliente_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente.')
            return redirect('ventas:lista_clientes', crucero_id=crucero_id)
    else:
        form = ClienteForm(instance=cliente)
    context = {
        'form': form,
        'cliente': cliente,
        'crucero_id': crucero_id,
        'crucero': crucero,
    }
    return render(request, 'ventas/editar_cliente.html', context)
