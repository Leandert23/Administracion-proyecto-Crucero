from .models import Dashboard, Alerta

def calcular_presupuesto(administracion):
    compras = Dashboard.compras.all()
    total_compras = sum([c.monto for c in compras])
    return Dashboard.presupuesto_estimado - total_compras

def generar_alerta_si_excede_presupuesto(administracion):
    if calcular_presupuesto(administracion) < 0:
        Alerta.objects.create(
            mensaje='¡Presupuesto excedido!',
            administracion=administracion
        )