from django.contrib import admin
from .models import Administracion, Alerta, Habitaciones

admin.register(Administracion)
admin.register(Habitaciones)
admin.register(Alerta)