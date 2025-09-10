#!/usr/bin/env python
"""
Script de diagnóstico para verificar el estado del sistema de ingredientes
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crucero_restaurant.settings')

try:
    django.setup()
    print("✅ Django configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

def diagnosticar_sistema():
    print("\n" + "="*60)
    print("🔍 DIAGNÓSTICO DEL SISTEMA DE INGREDIENTES")
    print("="*60)

    try:
        from restaurant.models import ComidasPreviu, Ingrediente
        print("✅ Modelos importados correctamente")
    except ImportError as e:
        print(f"❌ Error importando modelos: {e}")
        return

    # Verificar tabla ComidasPreviu
    print("\n📊 VERIFICANDO TABLA comidasPreviu:")
    try:
        count_previa = ComidasPreviu.objects.count()
        print(f"   📈 Registros en ComidasPreviu: {count_previa}")

        if count_previa > 0:
            primer_ing = ComidasPreviu.objects.first()
            print(f"   📋 Primer ingrediente: {primer_ing.ingredientes}")
            print(f"   🏷️  Tipo: {primer_ing.tipo}")
            print(f"   📝 Detalle: {primer_ing.detalle[:50]}...")
        else:
            print("   ⚠️  Tabla vacía - usando datos mockeados")

    except Exception as e:
        print(f"   ❌ Error accediendo a ComidasPreviu: {e}")
        print("   💡 Posible problema: tabla no existe o estructura incorrecta")

    # Verificar tabla Ingrediente
    print("\n📊 VERIFICANDO TABLA Ingrediente:")
    try:
        count_ing = Ingrediente.objects.count()
        print(f"   📈 Registros en Ingrediente: {count_ing}")

        if count_ing > 0:
            primer_ing = Ingrediente.objects.first()
            print(f"   📋 Primer ingrediente: {primer_ing.nombre}")
        else:
            print("   ⚠️  Tabla vacía")

    except Exception as e:
        print(f"   ❌ Error accediendo a Ingrediente: {e}")

    # Verificar URLs
    print("\n🔗 VERIFICANDO URLs:")
    try:
        from django.urls import reverse
        test_url = reverse('restaurant:test_ingredientes_previa')
        print(f"   ✅ URL test_ingredientes_previa: {test_url}")
    except Exception as e:
        print(f"   ❌ Error con URLs: {e}")

    # Verificar migraciones
    print("\n📋 VERIFICANDO MIGRACIONES:")
    try:
        from django.core.management import call_command
        from io import StringIO
        output = StringIO()
        call_command('showmigrations', 'restaurant', stdout=output, verbosity=0)
        migrations_output = output.getvalue()
        if migrations_output.strip():
            print("   📄 Migraciones encontradas:")
            for line in migrations_output.split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print("   ⚠️  No se encontraron migraciones")
    except Exception as e:
        print(f"   ❌ Error verificando migraciones: {e}")

    # Verificar estructura de base de datos
    print("\n🗄️  VERIFICANDO ESTRUCTURA DE BD:")
    try:
        from django.db import connection
        cursor = connection.cursor()

        # Ver tablas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'restaurant_%';")
        tables = cursor.fetchall()
        print(f"   📊 Tablas encontradas: {len(tables)}")
        for table in tables:
            print(f"   • {table[0]}")

        # Verificar si existe comidasPreviu
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comidasPreviu';")
        if cursor.fetchone():
            print("   ✅ Tabla 'comidasPreviu' existe")

            # Ver estructura de la tabla
            cursor.execute("PRAGMA table_info(comidasPreviu);")
            columns = cursor.fetchall()
            print(f"   📋 Columnas en comidasPreviu: {len(columns)}")
            for col in columns:
                print(f"      • {col[1]} ({col[2]})")
        else:
            print("   ❌ Tabla 'comidasPreviu' NO existe")

    except Exception as e:
        print(f"   ❌ Error verificando BD: {e}")

    print("\n" + "="*60)
    print("🎯 RECOMENDACIONES:")
    print("="*60)

    if ComidasPreviu.objects.count() == 0:
        print("• Si tienes datos reales en comidasPreviu, verifica la estructura")
        print("• Si no tienes la tabla, el sistema usa datos mockeados")
        print("• Revisa que los nombres de campos coincidan exactamente")

    print("• Prueba acceder a: http://127.0.0.1:8000/restaurant/test-ingredientes-previa/")
    print("• API disponible en: http://127.0.0.1:8000/restaurant/ajax/get-ingredientes-previa/")

    print("\n✅ Diagnóstico completado!")

if __name__ == '__main__':
    diagnosticar_sistema()
