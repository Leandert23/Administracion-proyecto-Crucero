from models import Producto, SeccionAlmacen, MovimientoAlmacen


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
