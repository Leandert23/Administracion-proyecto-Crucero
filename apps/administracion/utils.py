from .models import Administracion, Alerta

def calcular_presupuesto(administracion):
    compras = Administracion.compras.all()
    total_compras = sum([c.monto for c in compras])
    return Administracion.presupuesto_estimado - total_compras

def generar_alerta_si_excede_presupuesto(administracion):
    if calcular_presupuesto(administracion) < 0:
        Alerta.objects.create(
            mensaje='¡Presupuesto excedido!',
            administracion=administracion
        )