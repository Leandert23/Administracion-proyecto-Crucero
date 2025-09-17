#!/usr/bin/env python
"""
Script para diagnosticar problemas con el modal de tipo de habitación
"""
import requests
import sys
import os

def diagnosticar_modal():
    print("🔍 DIAGNOSTICANDO MODAL DE TIPO DE HABITACIÓN")
    print("=" * 50)

    # Verificar si el servidor está corriendo
    print("\n1. Verificando servidor...")
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"✅ Servidor responde - Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ SERVIDOR NO ESTÁ CORRIENDO")
        print("Solución: Ejecuta 'python manage.py runserver' en el directorio Administracion-proyecto-crucero")
        return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False

    # Verificar página principal
    print("\n2. Verificando página principal...")
    try:
        response = requests.get("http://127.0.0.1:8000/embarcaciones/", timeout=5)
        if response.status_code == 200:
            print("✅ Página principal funciona")
        else:
            print(f"❌ Error en página principal: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accediendo a página principal: {e}")
        return False

    # Verificar URL del modal
    print("\n3. Verificando URL del modal...")
    try:
        url_modal = "http://127.0.0.1:8000/embarcaciones/tipos/habitacion/crear/"
        print(f"Probando URL: {url_modal}")

        response = requests.get(url_modal, timeout=5)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            content = response.text

            # Verificaciones del contenido
            checks = [
                '<form' in content,
                'id="tipoHabitacionForm"' in content,
                'name="nombre"' in content,
                'name="tipo"' in content,
                'name="area_metros_cuadrados"' in content,
                '<select name="tipo"' in content,
                '<option value="babor"' in content,
                '<option value="estribor"' in content
            ]

            print("\nVerificaciones del contenido:")
            print(f"✅ Contiene formulario: {checks[0]}")
            print(f"✅ ID correcto del form: {checks[1]}")
            print(f"✅ Campo nombre: {checks[2]}")
            print(f"✅ Campo tipo: {checks[3]}")
            print(f"✅ Campo área: {checks[4]}")
            print(f"✅ Select tipo: {checks[5]}")
            print(f"✅ Opción babor: {checks[6]}")
            print(f"✅ Opción estribor: {checks[7]}")

            if all(checks):
                print("\n🎉 ¡MODAL FUNCIONANDO CORRECTAMENTE!")
                print("Longitud del contenido:", len(content), "caracteres")
                return True
            else:
                print("\n❌ Faltan elementos en el modal")
                print("\nContenido del modal (primeros 500 chars):")
                print(content[:500])
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print("Respuesta:", response.text[:200])
            return False

    except requests.exceptions.Timeout:
        print("❌ Timeout al cargar el modal")
        return False
    except Exception as e:
        print(f"❌ Error cargando modal: {e}")
        return False

if __name__ == "__main__":
    success = diagnosticar_modal()
    if not success:
        print("\n" + "="*50)
        print("SOLUCIONES POSIBLES:")
        print("1. Asegúrate de que el servidor esté corriendo:")
        print("   cd Administracion-proyecto-crucero")
        print("   python manage.py runserver")
        print("\n2. Verifica que no haya errores en la consola del navegador")
        print("\n3. Revisa los logs del servidor Django")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("¡TODO FUNCIONA CORRECTAMENTE!")
        print("El modal debería cargarse sin problemas.")
        print("="*50)
