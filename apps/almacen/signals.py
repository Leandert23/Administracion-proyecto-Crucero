from django.dispatch import Signal
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from apps.almacen.models import Producto
from apps.cruceros.models import Crucero

falta_stock_signal = Signal()

def emitir_señal_si_falta_stock_de(producto: Producto):
	if producto is None:
		return Producto.objects.none()
	if not isinstance(producto, Producto):
		raise TypeError("Error: 'producto' debe ser instancia de Producto")
	if producto.pk is None:
		return Producto.objects.none()
	if producto.cantidad_ideal <= 0:
		return Producto.objects.none()

	estado = producto.estado.upper()
	if estado == 'MEDIO':
		query_set = Producto.objects.filter(pk=producto.pk)
		falta_stock_signal.send(sender=Producto, productos=query_set)
		return query_set

	return Producto.objects.none()

def emitir_señal_si_falta_stock_general_en(crucero: Crucero):
	if crucero is None:
		return Producto.objects.none()
	if not isinstance(crucero, Crucero):
		raise TypeError("Error: 'crucero' debe ser instancia de Crucero")
	if crucero.pk is None:
		return Producto.objects.none()

	query_set = (
		Producto.objects
		.filter(seccion__almacen__crucero=crucero)
		.annotate(stock=Coalesce(Sum('lotes__cantidad_productos'), Value(0)))  # 'stock' = suma de cantidades en lotes; Coalesce reemplaza None por 0 si el producto no tiene lotes
		.filter(stock__lt=F('cantidad_ideal'), cantidad_ideal__gt=0)
	)
	if query_set.exists():
		falta_stock_signal.send(sender=Producto, productos=query_set)
	return query_set
