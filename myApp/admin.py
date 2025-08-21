from django.contrib import admin
from .models import Crucero, TipoHabitacion, Habitacion, Instalacion

admin.site.register(Crucero)
admin.site.register(TipoHabitacion)
admin.site.register(Habitacion)
admin.site.register(Instalacion)
