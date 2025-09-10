#!/usr/bin/env python
"""
Script simple para verificar el estado de los ingredientes
"""
import os
import sys

# Configurar Django de forma simple
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crucero_restaurant.settings')

print("🔍 VERIFICACIÓN RÁPIDA DEL SISTEMA DE INGREDIENTES")
print("="*60)

try:
    import django
    django.setup()
    print("✅ Django configurado correctamente")

    from restaurant.models import ComidasPreviu, Ingrediente
    print("✅ Modelos importados correctamente")

    # Verificar tabla ComidasPreviu
    print("\n📊 TABLA comidasPreviu:")
    try:
        count_previa = ComidasPreviu.objects.count()
        print(f"   📈 Registros: {count_previa}")
        if count_previa > 0:
            primer = ComidasPreviu.objects.first()
            print(f"   📋 Primer ingrediente: {primer.ingredientes}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Verificar tabla Ingrediente
    print("\n📊 TABLA Ingrediente:")
    try:
        count_ing = Ingrediente.objects.count()
        print(f"   📈 Registros: {count_ing}")
        if count_ing > 0:
            primer = Ingrediente.objects.first()
            print(f"   📋 Primer ingrediente: {primer.nombre}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n🚀 RECOMENDACIONES:")
    print("- El sistema debería funcionar con datos mockeados")
    print("- Si tienes tabla comidasPreviu, verifica que los campos coincidan")
    print("- Prueba: http://127.0.0.1:8000/restaurant/test-ingredientes-previa/")

except Exception as e:
    print(f"❌ Error general: {e}")
    print("💡 Posible problema con la configuración de Django")

print("\n✅ Verificación completada")
