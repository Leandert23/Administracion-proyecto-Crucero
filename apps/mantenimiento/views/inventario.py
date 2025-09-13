from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator

from ..models import InventarioProducto
from django.db.models import F
from ..forms import InventarioProductoForm


def inventario_list(request):
    inventarios = InventarioProducto.objects.select_related('producto', 'tipo_crucero').all()
    paginator = Paginator(inventarios, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'mantenimiento/inventario_list.html', {'page_obj': page_obj})


def inventario_update(request, pk):
    inventario = get_object_or_404(InventarioProducto, pk=pk)
    if request.method == 'POST':
        form = InventarioProductoForm(request.POST, instance=inventario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventario actualizado correctamente.')
            return redirect('mantenimiento:inventario_list')
    else:
        form = InventarioProductoForm(instance=inventario)
    return render(request, 'mantenimiento/inventario_form.html', {'form': form, 'action': 'Editar'})


def stock_bajo(request):
    try:
        items = InventarioProducto.objects.select_related('producto', 'tipo_crucero').filter(
            stock_actual__lte=F('stock_minimo')
        )
    except Exception:
        # Fallback si hay problemas con la comparación F
        items = []
        try:
            all_items = InventarioProducto.objects.select_related('producto', 'tipo_crucero').all()
            items = [item for item in all_items if item.stock_actual <= item.stock_minimo]
        except:
            items = []
    return render(request, 'mantenimiento/stock_bajo.html', {'items': items})


