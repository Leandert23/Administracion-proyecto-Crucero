from django.shortcuts import render, redirect
from apps.ventas.Services.sales import SalesService
from apps.almacen.models import Producto
from django.contrib.auth.models import User
from apps.ventas.models import Cliente

def sell_product_view(request):
    products = Producto.objects.all()
    users = User.objects.all()
    clientes = Cliente.objects.all()
    from apps.cruceros.models import Crucero
    cruceros = Crucero.objects.all()
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        user_id = request.POST.get('user_id')
        cliente_id = request.POST.get('cliente_id')
        crucero_id = request.POST.get('crucero_id')
        quantity = int(request.POST.get('quantity'))
        venta = SalesService.sell_product(product_id, user_id, cliente_id, crucero_id, quantity)
        if venta:
            return render(request, 'ventas/sale_success.html', {'venta': venta})
        else:
            return render(request, 'ventas/sale_fail.html', {'error': 'Stock insuficiente'})
    return render(request, 'ventas/sell_product.html', {'products': products, 'users': users, 'clientes': clientes, 'cruceros': cruceros})
