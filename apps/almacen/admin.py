from django.contrib import admin
from .models import SeccionAlmacen, Producto, Lote, MovimientoAlmacen, SolicitudSalida, ProductoSolicitado

admin.site.register(SeccionAlmacen)
admin.site.register(Producto)
admin.site.register(Lote)
admin.site.register(MovimientoAlmacen)
admin.site.register(SolicitudSalida)
admin.site.register(ProductoSolicitado)
