from decimal import Decimal
from django.core.exceptions import ValidationError

from ..models import InventarioProducto


def consumir_producto(producto, tipo_crucero, cantidad: Decimal, crucero=None):
    """Descuenta stock del inventario, validando disponibilidad.

    Args:
        producto: instancia de Producto
        tipo_crucero: instancia de TipoCrucero
        cantidad: Decimal cantidad a consumir
        crucero: instancia opcional de Crucero para multi-barco
    """
    filtros = {'producto': producto, 'tipo_crucero': tipo_crucero}
    if crucero is not None:
        filtros['crucero'] = crucero

    try:
        inv = InventarioProducto.objects.get(**filtros)
    except InventarioProducto.DoesNotExist:
        raise ValidationError('Inventario no encontrado para este producto y crucero.')

    nuevo = inv.stock_actual - cantidad
    if nuevo < 0:
        raise ValidationError('Stock insuficiente para consumo.')

    inv.stock_actual = nuevo
    inv.save(update_fields=['stock_actual', 'fecha_ultima_actualizacion'])
    return inv


