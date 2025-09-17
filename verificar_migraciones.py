#!/usr/bin/env python
"""
Script para verificar el estado de las migraciones de ventas
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Administrador_Cruceros.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def verificar_tabla_ventahabitacion():
    """Verificar si la tabla ventas_ventahabitacion existe"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='ventas_ventahabitacion';
        """)
        result = cursor.fetchone()
        
        if result:
            print("✅ La tabla 'ventas_ventahabitacion' existe")
            
            # Verificar estructura de la tabla
            cursor.execute("PRAGMA table_info(ventas_ventahabitacion);")
            columns = cursor.fetchall()
            print("\n📋 Columnas de la tabla:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print("❌ La tabla 'ventas_ventahabitacion' NO existe")
            print("🔧 Necesitas ejecutar las migraciones:")
            print("   python manage.py makemigrations ventas")
            print("   python manage.py migrate ventas")

def verificar_migraciones():
    """Verificar estado de las migraciones"""
    print("🔍 Verificando migraciones de ventas...")
    try:
        execute_from_command_line(['manage.py', 'showmigrations', 'ventas'])
    except Exception as e:
        print(f"Error al verificar migraciones: {e}")

if __name__ == "__main__":
    print("🚀 Verificando estado de la base de datos...")
    verificar_tabla_ventahabitacion()
    print("\n" + "="*50)
    verificar_migraciones()
