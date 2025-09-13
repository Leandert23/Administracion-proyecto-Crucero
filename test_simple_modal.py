#!/usr/bin/env python
"""
Test simple para verificar que el servidor Django está funcionando
"""
import os
import sys

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(__file__))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Administrador_Cruceros.settings')

import django
django.setup()

# Ahora podemos usar Django
from django.urls import reverse
from django.test import Client

def test_urls():
    print("🔍 TEST SIMPLE DE DJANGO")
    print("=" * 30)

    client = Client()

    # Test 1: Página principal
    print("1. Probando página principal...")
    try:
        response = client.get('/embarcaciones/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Página principal OK")
        else:
            print("   ❌ Error en página principal")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: URL del modal
    print("\n2. Probando URL del modal...")
    try:
        response = client.get('/embarcaciones/tipos/habitacion/crear/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            if 'tipoHabitacionForm' in content:
                print("   ✅ Modal template OK")
            else:
                print("   ❌ Template del modal no encontrado")
                print(f"   Contenido (primeros 200 chars): {content[:200]}")
        else:
            print("   ❌ Error en URL del modal")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: Verificar URL reverse
    print("\n3. Probando reverse URL...")
    try:
        url = reverse('creador_embarcaciones:crear_tipo_habitacion')
        print(f"   URL generada: {url}")
        print("   ✅ Reverse URL OK")
    except Exception as e:
        print(f"   ❌ Error en reverse URL: {e}")

    print("\n" + "=" * 30)
    print("FIN DEL TEST")

if __name__ == "__main__":
    test_urls()
