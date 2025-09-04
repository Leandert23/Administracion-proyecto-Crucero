import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Administrador_Cruceros.settings')
django.setup()

from django.test import Client

# Crear un cliente de prueba
client = Client()

print("=== Probando endpoint de registro ===")

# Probar una petición POST sin datos
print("\n1. Probando POST sin datos...")
response = client.post('/entretenimiento/registro/',
                      data=json.dumps({}),
                      content_type='application/json',
                      HTTP_X_REQUESTED_WITH='XMLHttpRequest')

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type')}")
print(f"Response: {response.content.decode()[:300]}...")

# Probar con datos válidos
print("\n2. Probando POST con datos válidos...")
test_data = {
    'nombre': 'Juan',
    'apellido': 'Pérez',
    'n_habitacion': '101',
    'n_personas': 2,
    'actividad_id': 1,
    'actividad_tipo': 'rutinaria'
}

response = client.post('/entretenimiento/registro/',
                      data=json.dumps(test_data),
                      content_type='application/json',
                      HTTP_X_REQUESTED_WITH='XMLHttpRequest')

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type')}")
print(f"Response: {response.content.decode()[:300]}...")

print("\n=== Fin de pruebas ===")
