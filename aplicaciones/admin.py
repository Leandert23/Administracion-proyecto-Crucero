from django.contrib import admin
from .models import Medico, Paciente, Inventario, Solicitudmedicamento , Instrumentaria , Insumo

# Register your models here.
admin.site.register(Medico)
admin.site.register(Insumo)
admin.site.register(Paciente)
admin.site.register(Inventario)
admin.site.register(Solicitudmedicamento)
admin.site.register(Instrumentaria)

