from django.dispatch import Signal
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from apps.almacen.models import Producto, MensajeParaCompras
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
	if producto.cantidad < 0.7 * producto.cantidad_ideal:
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


#Comunicacion con Compras

from django.dispatch import receiver
from apps.compras.signals import lote_signal
from django.dispatch import receiver
@receiver(lote_signal)
def receiver_lote(sender, compra_lote, **kwargs):
	from apps.almacen.models import OrdenCompra, Producto
	resultado_lines = []
	for item in compra_lote.items.all():
		try:
			producto = Producto.objects.get(pk=item.producto_id)
		except Producto.DoesNotExist:
			resultado_lines.append(f"{item.nombre} ({item.producto_id}): PRODUCTO NO ENCONTRADO")
			continue
		OrdenCompra.objects.create(
			producto=producto,
			cantidad_productos=item.cantidad,
			estado="POR_REGISTRAR",
			compra_lote=compra_lote
		)
		resultado_lines.append(f"{producto.nombre} ({producto.pk}): OrdenCompra creada x{item.cantidad}")

	# Crear un mensaje resumen para Compras vinculado a la CompraLote
	try:
		from apps.almacen.models import MensajeParaCompras
		descripcion = ""

		MensajeParaCompras.objects.create(
			compra_lote=compra_lote,
			descripcion=descripcion,
		)
	except Exception:
		pass

# --- Atributos de CompraLote ---
# id (autogenerado por Django)
# empresa_nombre
# empresa_contacto
# empresa_ubicacion
# proveedor (ForeignKey a Proveedores)
# puerto_entrega
# notas_compra
# presupuesto_lote
# estado
# fecha (auto_now_add)

# --- Atributos de CompraLoteItem ---
# id (autogenerado por Django)
# compra_lote (ForeignKey a CompraLote)
# producto_id
# nombre
# medida
# cantidad

#Decision final

from django.dispatch import Signal

decision_solicitud_almacen = Signal()

def enviar_decision_solicitud_almacen(orden_compra, mensaje=None):
	"""
	Recibe una OrdenCompra. Si todas las ordenes_compra_en_almacen del mismo compra_lote están APROBADAS,
	envía la señal de aceptado. Si alguna está DENEGADA, envía la señal de denegado.
	"""
	compra_lote = orden_compra.compra_lote
	ordenes = compra_lote.ordenes_compra_en_almacen.all()
	total = ordenes.count()
	aprobadas = ordenes.filter(estado="APROBADA").count()
	denegadas = ordenes.filter(estado="DENEGADA").count()

	# Intentar recuperar la descripción vinculada a la compra_lote (MensajeParaCompras)
	try:
		mensaje_compra = MensajeParaCompras.objects.filter(compra_lote=compra_lote).order_by('-id').first()
		descripcion_compra = mensaje_compra.descripcion.strip() if (mensaje_compra and getattr(mensaje_compra, 'descripcion', None)) else ''
	except Exception:
		descripcion_compra = ''

	# Si existe una descripción del mensaje de compra, usarla o concatenarla
	if descripcion_compra:
		if mensaje:
			# conservar el mensaje pasado y añadir la descripción de la compra
			mensaje = f"{mensaje}\n\n{descripcion_compra}"
		else:
			mensaje = descripcion_compra

	if denegadas > 0:
		# Si alguna está denegada, señal de denegado
		if mensaje is None:
			mensaje = "Solicitud denegada"
		decision_solicitud_almacen.send(
			sender=None,
			id=compra_lote.id,
			aceptado=False,
			mensaje=mensaje
		)
	elif total > 0 and aprobadas == total:
		# Todas aprobadas
		if mensaje is None:
			mensaje = "Solicitud aceptada"
		decision_solicitud_almacen.send(
			sender=None,
			id=compra_lote.id,
			aceptado=True,
			mensaje=mensaje
		)
	# Si hay pendientes, no se envía señal aún