from django.contrib import admin
from .models import Actividad, ActividadRutinaria, RegistroActividadPago, RegistroActividadRut

admin.site.register(Actividad)
admin.site.register(ActividadRutinaria)
admin.site.register(RegistroActividadPago)
admin.site.register(RegistroActividadRut)