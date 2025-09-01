from django.shortcuts import render
from .models import Administracion, Alerta, Compra

def dashboard_empresa(request):
    admin = Administracion.objects.first()
    contexto = {
        'presupuesto': admin.presupuesto_estimado if admin else 0,
        'compras': admin.compras.all() if admin else [],
        'recursos_humanos': admin.recursos_humanos.all() if admin else [],
        'alertas': Alerta.filter(leida=False) if admin else [],
    }
    return render(request, 'static/index.html', contexto)
