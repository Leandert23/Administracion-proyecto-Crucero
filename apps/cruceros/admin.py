from django.contrib import admin
from .models import Crucero, TipoHabitacion, Habitacion, Instalacion, Ruta, EtapaRuta, Viaje, EstadoViaje

admin.site.register(Crucero)
admin.site.register(TipoHabitacion)
admin.site.register(Habitacion)
admin.site.register(Instalacion)
admin.site.register(Ruta)
admin.site.register(EtapaRuta)      
admin.site.register(Viaje)
admin.site.register(EstadoViaje)