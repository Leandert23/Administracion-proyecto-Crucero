from django.contrib import admin
from .models import Administracion, Compra, RecursoHumano, Alerta

admin.site.register(Administracion)
admin.site.register(Compra)
admin.site.register(RecursoHumano)
admin.site.register(Alerta)
