#!/usr/bin/env python
"""
Script para crear migraciones con valor por defecto
"""
import os
import sys
import subprocess

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Administrador_Cruceros.settings')
sys.path.append('.')

# Ejecutar makemigrations de manera no interactiva
try:
    # Ejecutar makemigrations con input automático
    result = subprocess.run([
        'python', 'manage.py', 'makemigrations', 'creador_embarcaciones'
    ], capture_output=True, text=True, input='1\nbabor\n')

    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return code:", result.returncode)

except Exception as e:
    print(f"Error ejecutando makemigrations: {e}")
