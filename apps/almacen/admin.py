from django.contrib import admin
from .models import Almacen, SeccionAlmacen, Producto

admin.site.register(Almacen)
admin.site.register(SeccionAlmacen)
admin.site.register(Producto)
