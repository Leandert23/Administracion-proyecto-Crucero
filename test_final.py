import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Administrador_Cruceros.settings')
django.setup()

from django.test import Client

client = Client()

print("=== PRUEBA FINAL DEL SISTEMA DE REGISTRO ===")

# Datos de prueba
test_data = {
    'nombre': 'María',
    'apellido': 'García',
    'n_habitacion': '205',
    'n_personas': 2,
    'actividad_id': 1,
    'actividad_tipo': 'rutinaria'
}

print(f"Enviando datos: {test_data}")

# Hacer la petición
response = client.post('/entretenimiento/registro/',
                      data=json.dumps(test_data),
                      content_type='application/json',
                      HTTP_X_REQUESTED_WITH='XMLHttpRequest')

print(f"\nStatus Code: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type')}")

# Intentar parsear como JSON
try:
    response_data = response.json()
    print(f"\n✅ RESPUESTA JSON EXITOSA:")
    print(f"Success: {response_data.get('success')}")
    print(f"Message: {response_data.get('message')}")
    if 'registro_id' in response_data:
        print(f"Registro ID: {response_data.get('registro_id')}")

except json.JSONDecodeError as e:
    print(f"\n❌ ERROR: No se pudo parsear como JSON")
    print(f"Error: {e}")
    print(f"Contenido de respuesta (primeros 300 caracteres):")
    print(response.content.decode()[:300])

print("\n=== FIN DE PRUEBA ===")
