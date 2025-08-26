from django.contrib import admin
from .models import Crucero, TipoHabitacion, Habitacion, Instalacion, Almacen, SeccionAlmacen, Producto

admin.site.register(Crucero)
admin.site.register(TipoHabitacion)
admin.site.register(Habitacion)
admin.site.register(Instalacion)
admin.site.register(Almacen)
admin.site.register(SeccionAlmacen)
admin.site.register(Producto)
