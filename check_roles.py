import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Administrador_Cruceros.settings')
django.setup()

from apps.usuarios.models_custom import RolCustom

print("Roles custom existentes:")
roles = RolCustom.objects.all()
if not roles:
    print("No hay roles custom creados.")
else:
    for rol in roles:
        print(f"Nombre: {rol.nombre}")
        print(f"Módulos: {rol.modulos}")
        print("---")
