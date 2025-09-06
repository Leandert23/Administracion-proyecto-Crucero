from django.db import transaction
from ..models import Producto, SeccionAlmacen, MovimientoAlmacen, Lote
from apps.almacen.models import Producto
from typing import List, Tuple

cantidadesIniciales = {}

def registrar_cantidad_inicial(producto: Producto):
    if producto.nombre not in cantidadesIniciales:
        cantidadesIniciales[producto.nombre] = producto.cantidad

def save_product(nombre, precio, tipo, cantidad, medida, seccion_almacen_id, modulo):
    secciones_almacen = SeccionAlmacen.objects.filter(id=seccion_almacen_id)
    if not secciones_almacen.exists():
        raise Exception("Sección de almacén no encontrada")

    # Comprobamos si el producto ya existe
    productoExistente = Producto.objects.filter(
        nombre=nombre, tipo=tipo, seccion_almacen=seccion_almacen_id
    ).first()
    # Si existe actualizamos la cantidad
    if productoExistente:
        Producto.objects.filter(producto=productoExistente).update(
            cantidad=productoExistente.cantidad + cantidad
        )
        MovimientoAlmacen.objects.create(
            producto=productoExistente, cantidad=cantidad, tipo="IN"
        )
    else:
        # Si no existe, lo creamos
        producto = Producto(
            nombre=nombre,
            precio=precio,
            tipo=tipo,
            cantidad=cantidad,
            medida=medida,
            seccion_almacen=seccion_almacen_id,
        )
        producto.save()
        MovimientoAlmacen.objects.create(
            producto=producto, cantidad=cantidad, tipo="NEW", modulo=modulo
        )
        registrar_cantidad_inicial(producto)


def remove_product(name, modulo, cantidad=1):
    producto = Producto.objects.filter(nombre=name).first()
    if not producto:
        raise Exception("Producto no encontrado")
    if producto.cantidad == 0:
        raise Exception("Producto no disponible")
    # Se resta 1 unidad a la cantidad del producto
    Producto.objects.filter(producto=producto).update(
        cantidad=producto.cantidad - cantidad
    )
    # Registrar el movimiento de salida del producto
    MovimientoAlmacen.objects.create(
        producto=producto, cantidad=cantidad, tipo="OUT", modulo=modulo
    )


def productosPocasUnidades(cantidadesIniciales: dict, porcentajeMinimo: float = 0.2) -> List[Tuple[str, int]]:
    productosPocos = []
    for producto in Producto.objects.all():
        inicial = cantidadesIniciales.get(producto.nombre, producto.cantidad)
        if inicial > 0 and producto.cantidad <= inicial * porcentajeMinimo:
            productosPocos.append((producto.nombre, producto.cantidad))
    return productosPocos


# -------------------------------------------------------------
# Nuevas funciones de retiro por lotes: FIFO y FEFO
# (No se modifican las funciones existentes solicitadas)
# -------------------------------------------------------------

def _recalcular_stock_producto(producto):
    total_stock = 0
    for lote in producto.lotes.all():
        total_stock += lote.cantidad_productos
        
    if producto.cantidad != total_stock:
        producto.cantidad = total_stock
        producto.save(update_fields=["cantidad"])

def _procesar_lotes(lotes, cantidad_necesaria, modulo, producto, descripcion=None):
    """Consume lotes en orden y registra movimientos.
    En lugar de eliminar el lote agotado (lo que rompe el historial y puede causar
    errores de FK si se intenta referenciar tras delete), se deja el lote con
    cantidad 0 para mantener la trazabilidad.
    """
    cantidad_restante = cantidad_necesaria

    for lote in lotes:
        if cantidad_restante <= 0:
            break

        disponible = lote.cantidad_productos
        if disponible <= 0:
            continue

        tomar = min(cantidad_restante, disponible)

        # Registrar movimiento ANTES de modificar el lote, preservando referencia
        MovimientoAlmacen.objects.create(
            producto=producto,
            cantidad=tomar,
            tipo="OUT",
            modulo=modulo,
            lote=lote,
            descripcion=descripcion or ''
        )

        lote.cantidad_productos = disponible - tomar
        # Mantener el lote (sin borrarlo) para historial; solo actualizar cantidad
        lote.save(update_fields=["cantidad_productos"])

        cantidad_restante -= tomar

    if cantidad_restante > 0:
        # Esto no debería ocurrir si se verificó stock antes; lanzar para rollback
        raise ValueError("Stock inconsistente durante el retiro (faltante tras procesar lotes)")

def _verificar_stock_suficiente(lotes, cantidad_solicitada):
    stock_disponible = sum(lote.cantidad_productos for lote in lotes)
    if stock_disponible < cantidad_solicitada:
        raise ValueError(f"Stock insuficiente: disponible {stock_disponible}, requerido {cantidad_solicitada}")

def _obtener_lotes_fifo(producto):
    return list(
        producto.lotes.filter(cantidad_productos__gt=0).order_by("fecha_ingreso", "id")
    )

def _obtener_lotes_fefo(producto):
    lotes_con_fecha = list(
        producto.lotes.filter(cantidad_productos__gt=0, fecha_caducidad__isnull=False)
        .order_by("fecha_caducidad", "fecha_ingreso", "id")
    )
    lotes_sin_fecha = list(
        producto.lotes.filter(cantidad_productos__gt=0, fecha_caducidad__isnull=True)
        .order_by("fecha_ingreso", "id")
    )
    return lotes_con_fecha + lotes_sin_fecha

def _realizar_retiro(producto_id, cantidad, modulo, metodo_ordenamiento, descripcion=None):
    if cantidad <= 0:
        raise ValueError("La cantidad debe ser mayor que 0")

    with transaction.atomic():
        producto = Producto.objects.select_for_update().get(pk=producto_id)
        lotes_ordenados = metodo_ordenamiento(producto)
        _verificar_stock_suficiente(lotes_ordenados, cantidad)
        _procesar_lotes(lotes_ordenados, cantidad, modulo, producto, descripcion=descripcion)
        # No es necesario recalcular porque cantidad es property (suma dinámica)

def retirar_producto_fifo(producto_id, cantidad, modulo, descripcion=None):
    _realizar_retiro(producto_id, cantidad, modulo, _obtener_lotes_fifo, descripcion=descripcion)

def retirar_producto_fefo(producto_id, cantidad, modulo, descripcion=None):
    _realizar_retiro(producto_id, cantidad, modulo, _obtener_lotes_fefo, descripcion=descripcion)
