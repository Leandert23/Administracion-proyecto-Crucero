from apps.almacen.models import Producto
from django.contrib.auth.models import User
from apps.ventas.models import Venta, DetalleVenta, Cliente
from django.db import transaction

class SalesService:
    @staticmethod
    @transaction.atomic
    def sell_product(product_id, user_id, cliente_id, crucero_id, quantity, tipo_venta='otro', descripcion='Venta de producto'):
        """
        Realiza la venta de un producto, actualiza el stock y registra la venta y su detalle.
        """
        product = Producto.objects.select_for_update().get(id=product_id)
        user = User.objects.get(id=user_id)
        cliente = Cliente.objects.get(id=cliente_id)
        from apps.cruceros.models import Crucero
        crucero = Crucero.objects.get(id=crucero_id)
        if product.stock >= quantity:
            product.stock -= quantity
            product.save()
            venta = Venta.objects.create(
                crucero=crucero,
                cliente=cliente,
                tipo_venta=tipo_venta,
                descripcion=descripcion,
                monto_total=quantity * product.precio,
                vendedor=user,
                estado='confirmada'
            )
            DetalleVenta.objects.create(
                venta=venta,
                concepto=product.nombre,
                cantidad=quantity,
                precio_unitario=product.precio,
                subtotal=quantity * product.precio
            )
            return venta
        return None
