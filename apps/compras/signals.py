from django.dispatch import Signal
from django.dispatch import receiver

### ADMINISTRACION

##  Senders

# Signal para administración de solicitud de compra
solicitud_compra_administracion_signal = Signal()

def solicitud_compra_administracion(id, monto, mensaje=None):
	"""
	Envía un signal con un id, monto y mensaje usando Django signals.
	"""
	if mensaje is None:
		mensaje = "Solicitud de Compra"
	solicitud_compra_administracion_signal.send(sender=None, id=id, monto=monto, mensaje=mensaje)

# Ejemplo de uso del sender:
# solicitud_compra_administracion(id=123, monto=5000, mensaje="Nueva solicitud de compra")

##  Receivers

# from compras.signals import decision_solicitud_signal

# @receiver(decision_solicitud_signal)
from .models import CompraLote
def manejar_decision_solicitud(sender, id, aceptado, mensaje, **kwargs):
	try:
		compra_lote = CompraLote.objects.get(id=id)
		if aceptado:
			compra_lote.estado = 'En espera por revisión'
			# Enviar signal con el lote completo
			lote_signal = Signal()
			compra_lote.notas_compra = mensaje
			lote_signal.send(sender=None, compra_lote=compra_lote)
		else:
			compra_lote.estado = 'Cancelada'
			solicitud = compra_lote.solicitud
			compra_lote.notas_compra = mensaje
			if solicitud and solicitud.procesada:
				solicitud.procesada = False
				solicitud.save()
		compra_lote.save()
	except CompraLote.DoesNotExist:
		print(f"No se encontró CompraLote con id={id}")

###  ALMACEN

# Importacion para poder tener los tipos y subtipos
from apps.almacen.models import Producto
from apps.almacen.signals import falta_stock_signal
from .models import SolicitudSubtipo, SolicitudSubtipoItem

@receiver(falta_stock_signal)
def manejar_productos_signal(sender, productos, **kwargs):

	query_set_base_productos = productos

	if not query_set_base_productos.exists():
		return

	# Si el queryset contiene exactamente un solo producto, se puede procesar directo y terminar.
	if query_set_base_productos.count() == 1:
		# Placeholder: generar orden de compra para el único producto
		# generar_orden_compra(query_set_base_productos)
		return

	# Iterar por tipos definidos en el modelo
	for nombre_del_tipo, _ in Producto.TIPOS_PRODUCTO:
		query_set_de_productos_por_tipo = query_set_base_productos.filter(tipo=nombre_del_tipo)
		if not query_set_de_productos_por_tipo.exists():
			continue
		# Aca tendrían una función van a generar orden solo por tipo
		# generar_orden_compra(query_set_de_productos_por_tipo)

		# Subtipos válidos para este tipo (Si existen)
		subtipos_validos = Producto.SUBTIPOS_POR_TIPO.get(nombre_del_tipo, [])
		for subtipo_code in subtipos_validos:
			query_set_del_subtipo = query_set_de_productos_por_tipo.filter(subtipo=subtipo_code)
			if not query_set_del_subtipo.exists():
				continue
			# Generar la solicitud para este subtipo
			primer_producto = query_set_del_subtipo.first()
			tipo = primer_producto.tipo
			subtipo = primer_producto.subtipo
			solicitud = SolicitudSubtipo.objects.create(tipo=tipo, subtipo=subtipo)
			for producto in query_set_del_subtipo:
				cantidad_a_comprar = getattr(producto, 'cantidad_ideal', 0) - getattr(producto, 'cantidad', 0)
				SolicitudSubtipoItem.objects.create(
                    solicitud=solicitud,
                    producto_id=producto.id,
                    nombre=producto.nombre,
                    cantidad_a_comprar=cantidad_a_comprar,
                    medida=producto.medida,
                    tipo=tipo,
                    subtipo=subtipo
                )

    # Atributos que les puede interesar
    # producto.id
    # producto.nombre
    # producto.tipo
    # producto.subtipo
    # producto.cantidad (No es un atributo, se calcula según la cantidad que tiene cada lote registrado de ese producto)
    # producto.cantidad_ideal
    # producto.medida

# receptor para recibir la decision de la solicitud de compra desde almacen
from almacen.signals import decision_solicitud_almacen

@receiver(decision_solicitud_almacen)
def manejar_decision_solicitud_almacen(sender, id, aceptado, mensaje, **kwargs):
	try:
		compra_lote = CompraLote.objects.get(id=id)
		if aceptado:
			compra_lote.estado = 'Exitosa'
			compra_lote.notas_compra = mensaje
		else:
			compra_lote.estado = 'Defectuosa'
			# Buscar y actualizar la solicitud asociada usando la relación directa
			solicitud = compra_lote.solicitud
			if solicitud and solicitud.procesada:
				compra_lote.notas_compra = mensaje
				solicitud.procesada = False
				solicitud.save()
				# Nuevo signal para compras defectuosas
				compra_defectosa = Signal()
				# Enviar el nuevo signal compra_defectosa con monto y mensaje
				compra_defectosa.send(sender=None, monto=compra_lote.presupuesto_lote, mensaje=mensaje)
		compra_lote.save()
	except CompraLote.DoesNotExist:
		print(f"No se encontró CompraLote con id={id}")
