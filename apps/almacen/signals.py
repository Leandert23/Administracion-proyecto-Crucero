from django.dispatch import Signal
from apps.almacen.models import Producto
from apps.almacen.Services.products import productosPocasUnidades, cantidadesIniciales

productosSignal = Signal()

def enviar_productos_bajos():
    productosBajos = productosPocasUnidades(cantidadesIniciales)
    if productosBajos:
        productosSignal.send(
            sender=Producto,
            productos=productosBajos
        )