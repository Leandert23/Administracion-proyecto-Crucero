from django.contrib import admin
from .models import SeccionAlmacen, Producto, Lote, MovimientoAlmacen

admin.site.register(SeccionAlmacen)
admin.site.register(Producto)
admin.site.register(Lote)
admin.site.register(MovimientoAlmacen)
