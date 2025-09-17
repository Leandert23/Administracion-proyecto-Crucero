from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Embarcacion


def precargar_embarcacion_desde_id_2(request):
    """
    Vista para crear una nueva embarcación con datos predeterminados, asignando automáticamente un ID disponible.
    """
    from .models import TipoEmbarcacion, Ruta
    from datetime import date, timedelta
    from decimal import Decimal
    
    # Verificar que existan rutas y tipos de embarcación
    if not Ruta.objects.exists():
        messages.error(request, 'No hay rutas disponibles. Debe crear al menos una ruta antes de precargar embarcaciones.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    # Obtener o crear un tipo de embarcación por defecto
    tipo_embarcacion, created = TipoEmbarcacion.objects.get_or_create(
        nombre='Crucero',
        defaults={
            'descripcion': 'Tipo de embarcación estándar para cruceros'
        }
    )
    
    # Obtener la primera ruta disponible
    ruta_default = Ruta.objects.first()
    
    # Crear nueva embarcación con datos predeterminados
    nueva_embarcacion = Embarcacion(
        nombre='Vision',
        tipo=tipo_embarcacion,
        fecha_botadura=date.today() - timedelta(days=365),  # Hace 1 año
        fecha_adquisicion=date.today() - timedelta(days=300),  # Hace 10 meses
        capacidad_pasajeros=2000,
        capacidad_tripulacion=700,
        tonelaje=Decimal('78340.00'),
        eslora=Decimal('278.00'),
        manga=Decimal('33.00'),
        altura=Decimal('60.00'),
        numero_cubiertas=12,
        maximo_habitacion_pasajeros=825,
        maximo_habitacion_tripulantes=490,
        bandera='Venezuela',
        puerto_base='Colón',
        estado_operativo='operativo',
        descripcion='',
        modelo_motor='Motor Diesel MAN 12V48/60CR',
        velocidad_maxima=Decimal('22.50'),
        ultimo_mantenimiento=date.today() - timedelta(days=30),
        proximo_mantenimiento=date.today() + timedelta(days=90),
        tipo_combustible='diesel',
        consumo_combustible=Decimal('2500.00'),
        capacidad_combustible=Decimal('80000.00'),
        ruta=ruta_default
    )
    
    # Guardar la embarcación (el identificador se genera automáticamente)
    nueva_embarcacion.save()
    
    messages.success(request, f'Se ha creado una nueva embarcación precargada: "{nueva_embarcacion.nombre}" con ID {nueva_embarcacion.pk} e identificador {nueva_embarcacion.identificador}')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
