#!/usr/bin/env python
"""
Script para probar que el modal se carga correctamente
"""
import requests

def test_modal():
    try:
        # URL del servidor Django
        url = "http://127.0.0.1:8000/embarcaciones/tipos/habitacion/crear/"

        print("🔍 Probando carga del modal de tipo habitación...")
        print(f"URL: {url}")

        response = requests.get(url)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            content = response.text

            # Verificar que contiene los elementos esperados
            checks = [
                '<form id="tipoHabitacionForm"' in content,
                'name="nombre"' in content,
                'name="tipo"' in content,
                'name="area_metros_cuadrados"' in content,
                '<select name="tipo"' in content
            ]

            print(f"✅ Contiene formulario: {checks[0]}")
            print(f"✅ Contiene campo nombre: {checks[1]}")
            print(f"✅ Contiene campo tipo: {checks[2]}")
            print(f"✅ Contiene campo área: {checks[3]}")
            print(f"✅ Contiene select tipo: {checks[4]}")

            if all(checks):
                print("🎉 ¡Modal funcionando correctamente!")
                return True
            else:
                print("❌ Faltan elementos en el modal")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor Django")
        print("   Asegúrate de que el servidor esté corriendo con: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_modal()</content>
</xai:function_call">The file Administracion-proyecto-crucero/test_modal.py has been created.
