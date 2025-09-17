#!/usr/bin/env python
"""
Script simple para probar el modelo VentaHabitacion
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Administrador_Cruceros.settings')
django.setup()

try:
    from apps.ventas.models import VentaHabitacion
    print("✅ Modelo VentaHabitacion importado correctamente")
    
    # Intentar hacer una consulta simple
    count = VentaHabitacion.objects.count()
    print(f"✅ Consulta exitosa: {count} ventas de habitaciones en la base de datos")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔧 Posibles soluciones:")
    print("1. Ejecutar: python manage.py makemigrations ventas")
    print("2. Ejecutar: python manage.py migrate ventas")
    print("3. Verificar que la tabla existe en la base de datos")
