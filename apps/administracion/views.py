from django.shortcuts import render
from django.http import JsonResponse
from apps.cruceros.models import Crucero
from .models import Administracion, Alerta

def cruceros_dashboard_data(request):
    cruceros = Crucero.objects.all()
    data = []
    for c in cruceros:
        data.append({
            "id": c.id,
            "name": c.nombre,
            "status": c.estado_operativo,
            "passengers": c.capacidad_pasajeros,
            "employees": c.capacidad_tripulacion,
            "location": c.puerto_base,
            "days": getattr(c, "dia_actual_de_viaje", 0) if hasattr(c, "dia_actual_de_viaje") else 0,
            "distance": 0,
            "budget": 0,
            "costs": {
                "total": 0,
                "categories": {}
            },
            "earnings": {
                "total": 0,
                "real": 0,
                "categories": {}
            },
            "alerts": []
        })
    return JsonResponse({"ships": data})

def dashboard_empresa(request):
    admin = Administracion.objects.first()
    contexto = {
        'presupuesto': admin.presupuesto_estimado if admin else 0,
        'compras': admin.compras.all() if admin else [],
        'recursos_humanos': admin.recursos_humanos.all() if admin else [],
        'alertas': Alerta.filter(leida=False) if admin else [],
    }
    return render(request, 'templates/index.html', contexto)
