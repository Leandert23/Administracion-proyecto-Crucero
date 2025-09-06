#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Administrador_Cruceros.settings')
django.setup()

from apps.administracion.models import Modulo, Rol

def create_initial_data():
    print("Creando datos iniciales...")

    # Crear módulos si no existen
    modulos_data = [
        {'nombre': 'Administración', 'descripcion': 'Sistema de administración general'},
        {'nombre': 'Cruceros', 'descripcion': 'Gestión de cruceros'},
        {'nombre': 'Almacén', 'descripcion': 'Control de inventario'},
        {'nombre': 'Mantenimiento', 'descripcion': 'Sistema de mantenimiento'},
        {'nombre': 'Reservaciones', 'descripcion': 'Gestión de reservas'},
        {'nombre': 'Servicio Médico', 'descripcion': 'Atención médica'},
        {'nombre': 'Ventas', 'descripcion': 'Sistema de ventas'},
    ]

    for modulo_data in modulos_data:
        modulo, created = Modulo.objects.get_or_create(
            nombre=modulo_data['nombre'],
            defaults={'descripcion': modulo_data['descripcion']}
        )
        if created:
            print(f"✓ Módulo '{modulo.nombre}' creado")
        else:
            print(f"✓ Módulo '{modulo.nombre}' ya existe")

    # Crear algunos roles si no existen
    roles_data = [
        {'nombre': 'Administrador', 'modulo': 'Administración', 'tipo': 'admin'},
        {'nombre': 'Editor', 'modulo': 'Cruceros', 'tipo': 'editor'},
        {'nombre': 'Supervisor', 'modulo': 'Almacén', 'tipo': 'editor'},
        {'nombre': 'Operador', 'modulo': 'Mantenimiento', 'tipo': 'especialista'},
    ]

    for rol_data in roles_data:
        try:
            modulo = Modulo.objects.get(nombre=rol_data['modulo'])
            rol, created = Rol.objects.get_or_create(
                nombre=rol_data['nombre'],
                modulo=modulo,
                defaults={'tipo': rol_data['tipo']}
            )
            if created:
                print(f"✓ Rol '{rol.nombre}' creado en módulo '{modulo.nombre}'")
            else:
                print(f"✓ Rol '{rol.nombre}' ya existe en módulo '{modulo.nombre}'")
        except Modulo.DoesNotExist:
            print(f"✗ Módulo '{rol_data['modulo']}' no encontrado")

    print("\n✅ Datos iniciales creados correctamente")

if __name__ == '__main__':
    create_initial_data()
