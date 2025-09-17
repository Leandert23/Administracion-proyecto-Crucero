#!/usr/bin/env python
"""
Script para configurar embarcaciones y rutas necesarias para el sistema
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Administrador_Cruceros.settings')
django.setup()

from apps.creador_embarcaciones.models import Ruta, Embarcacion, TipoEmbarcacion
from datetime import date, timedelta
from decimal import Decimal

def main():
    print("=== Configurando datos básicos ===")
    
    # Verificar rutas existentes
    rutas_count = Ruta.objects.count()
    print(f"Rutas existentes: {rutas_count}")
    
    # Crear ruta si no existe
    if rutas_count == 0:
        print("Creando ruta por defecto...")
        ruta = Ruta.objects.create(
            titulo="Caribe Oriental",
            numero_dias=7,
            descripcion="Ruta de 7 días por el Caribe Oriental visitando las mejores islas",
            fecha_inicio=date.today() + timedelta(days=30)
        )
        print(f"Ruta creada: {ruta.titulo}")
    else:
        ruta = Ruta.objects.first()
        print(f"Usando ruta existente: {ruta.titulo}")
    
    # Verificar embarcaciones existentes
    embarcaciones_count = Embarcacion.objects.count()
    print(f"Embarcaciones existentes: {embarcaciones_count}")
    
    # Crear embarcación si no existe
    if embarcaciones_count == 0:
        print("Creando embarcación por defecto...")
        
        # Obtener o crear tipo de embarcación
        tipo_embarcacion, created = TipoEmbarcacion.objects.get_or_create(
            nombre='Crucero',
            defaults={
                'descripcion': 'Tipo de embarcación estándar para cruceros'
            }
        )
        
        # Crear embarcación
        embarcacion = Embarcacion.objects.create(
            nombre='Vision',
            tipo=tipo_embarcacion,
            fecha_botadura=date.today() - timedelta(days=365),
            fecha_adquisicion=date.today() - timedelta(days=300),
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
            descripcion='Embarcación de crucero de lujo',
            modelo_motor='Motor Diesel MAN 12V48/60CR',
            velocidad_maxima=Decimal('22.50'),
            ultimo_mantenimiento=date.today() - timedelta(days=30),
            proximo_mantenimiento=date.today() + timedelta(days=90),
            tipo_combustible='diesel',
            consumo_combustible=Decimal('2500.00'),
            capacidad_combustible=Decimal('80000.00'),
            ruta=ruta
        )
        print(f"Embarcación creada: {embarcacion.nombre} (ID: {embarcacion.id})")
    else:
        embarcacion = Embarcacion.objects.first()
        print(f"Usando embarcación existente: {embarcacion.nombre} (ID: {embarcacion.id})")
    
    print("\n=== Configuración completada ===")
    print(f"Ahora puedes acceder al módulo de bares usando la embarcación ID: {embarcacion.id}")
    print(f"URL: http://127.0.0.1:8000/bares-snacks/{embarcacion.id}/")

if __name__ == '__main__':
    main()
