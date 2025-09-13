from django.db import transaction
from ..models import Producto, MovimientoAlmacen
from apps.almacen.signals import emitir_señal_si_falta_stock_de 
from typing import List, Tuple

# Conjunto de módulos válidos según MovimientoAlmacen.TIPO_MODULO
_MODULOS_VALIDOS = {
    "RESTAURANTE","VENTAS","COMPRAS","BARES_SNACKS","MANTENIMIENTO","ENTRETENIMIENTO",
    "RECURSOS_HUMANOS","RESERVACIONES","ALMACEN","SERVICIO_MEDICO","ADMINISTRACION","FUERA_BARCO"
}

def _normalizar_modulo(modulo: str | None) -> str:
    if not modulo:
        return "ALMACEN"
    limpio = modulo.strip().upper().replace(' ', '_').replace('-', '_')
    if limpio not in _MODULOS_VALIDOS:
        return "ALMACEN"
    return limpio

def _procesar_lotes(lotes, cantidad_necesaria, modulo, producto, descripcion=None):
    modulo_norm = _normalizar_modulo(modulo)
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
            modulo=modulo_norm,
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
    # Después de registrar la salida y actualizar lotes, emitir señal para evaluar si ahora falta stock de este producto
    emitir_señal_si_falta_stock_de(producto)

def retirar_producto_fifo(producto_id, cantidad, modulo, descripcion=None):
    _realizar_retiro(producto_id, cantidad, modulo, _obtener_lotes_fifo, descripcion=descripcion)

def retirar_producto_fefo(producto_id, cantidad, modulo, descripcion=None):
    _realizar_retiro(producto_id, cantidad, modulo, _obtener_lotes_fefo, descripcion=descripcion)


def calcular_asignacion_lotes(producto_id: int, cantidad: int):
    """Calcula y devuelve una asignación de lotes (sin modificar la BD).

    Retorna una tupla (asignaciones, disponible_total) donde asignaciones es una
    lista de dicts: { 'lote_id', 'numero_lote', 'cantidad', 'fecha_caducidad' }
    El algoritmo usa FEFO cuando existen lotes con fecha_caducidad, en otro caso FIFO.
    """
    if cantidad <= 0:
        return [], 0

    producto = Producto.objects.select_related('seccion__almacen').get(pk=producto_id)

    # Decidir método
    lotes_con_fecha = list(producto.lotes.filter(cantidad_productos__gt=0, fecha_caducidad__isnull=False).order_by("fecha_caducidad", "fecha_ingreso", "id"))
    if lotes_con_fecha:
        lotes_ordenados = lotes_con_fecha + list(producto.lotes.filter(cantidad_productos__gt=0, fecha_caducidad__isnull=True).order_by("fecha_ingreso", "id"))
    else:
        lotes_ordenados = list(producto.lotes.filter(cantidad_productos__gt=0).order_by("fecha_ingreso", "id"))

    asignaciones = []
    restante = cantidad
    disponible_total = sum(l.cantidad_productos for l in lotes_ordenados)

    for lote in lotes_ordenados:
        if restante <= 0:
            break
        dispo = lote.cantidad_productos
        if dispo <= 0:
            continue
        tomar = min(restante, dispo)
        asignaciones.append({
            'lote_id': lote.id,
            'numero_lote': getattr(lote, 'numero_lote', None),
            'cantidad': int(tomar),
            'fecha_caducidad': lote.fecha_caducidad.isoformat() if lote.fecha_caducidad else None,
            # ubicación aproximada basada en la sección/almacén del producto
            'ubicacion': f"{getattr(producto.seccion.almacen, 'nombre', '')} - {getattr(producto.seccion, 'nombre', '')}" if getattr(producto, 'seccion', None) else ''
        })
        restante -= tomar

    return asignaciones, disponible_total
