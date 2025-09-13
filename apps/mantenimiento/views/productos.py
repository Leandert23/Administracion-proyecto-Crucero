from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator

from ..models import Producto
from ..forms import ProductoForm


def producto_list(request):
    productos = Producto.objects.all()
    paginator = Paginator(productos, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'mantenimiento/producto_list.html', {'page_obj': page_obj})


def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado correctamente.')
            return redirect('mantenimiento:producto_list')
    else:
        form = ProductoForm()
    return render(request, 'mantenimiento/producto_form.html', {'form': form, 'action': 'Crear'})


def producto_detail(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'mantenimiento/producto_detail.html', {'producto': producto})


def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado.')
            return redirect('mantenimiento:producto_detail', pk=pk)
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'mantenimiento/producto_form.html', {'form': form, 'action': 'Editar', 'producto': producto})


def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado.')
        return redirect('mantenimiento:producto_list')
    return render(request, 'mantenimiento/producto_confirm_delete.html', {'producto': producto})


