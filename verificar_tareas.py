#!/usr/bin/env python
import os
import django
import sys

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crucero_admin.settings')
django.setup()

from mantenimiento.models import TareaMantenimiento
from django.db.models import Count

def verificar_tareas():
    print("🔍 Verificando tareas creadas desde diferentes módulos...")
    print("=" * 60)

    # Contar total de tareas
    tareas = TareaMantenimiento.objects.all()
    total_tareas = tareas.count()
    print(f"📊 Total de tareas en el sistema: {total_tareas}")

    if total_tareas == 0:
        print("❌ No se encontraron tareas. Ejecuta: python manage.py create_test_tasks")
        return

    # Agrupar por módulo de origen
    print("\n🏢 Tareas por módulo de origen:")
    modulos = tareas.values('modulo_origen').annotate(
        count=Count('modulo_origen')
    ).filter(modulo_origen__isnull=False).order_by('-count')

    for modulo in modulos:
        modulo_origen = modulo['modulo_origen']
        count = modulo['count']
        print(f"  • {modulo_origen}: {count} tareas")

    # Agrupar por estado
    print("\n📈 Tareas por estado:")
    estados = tareas.values('estado').annotate(
        count=Count('estado')
    ).order_by('-count')

    for estado in estados:
        estado_display = dict(TareaMantenimiento.ESTADOS)[estado['estado']]
        count = estado['count']
        print(f"  • {estado_display}: {count} tareas")

    # Mostrar primeras 10 tareas
    print("\n📋 Primeras 10 tareas creadas:")
    print("-" * 60)

    for i, tarea in enumerate(tareas[:10], 1):
        modulo = tarea.modulo_origen or 'mantenimiento'
        estado = tarea.get_estado_display()
        prioridad = tarea.get_prioridad_display()
        tipo = tarea.get_tipo_display()

        print(f"{i:2d}. {tarea.titulo}")
        print(f"    📍 Módulo: {modulo} | Estado: {estado} | Prioridad: {prioridad}")
        print(f"    🔧 Tipo: {tipo}")
        print(f"    📅 Programada: {tarea.fecha_programada.strftime('%Y-%m-%d %H:%M')}")
        if tarea.origen_url:
            print(f"    🔗 Origen: {tarea.origen_url}")
        print()

    print("✅ Verificación completada!")
    print("🌐 Para ver las tareas en el navegador, accede a:")
    print("   http://127.0.0.1:8000/mantenimiento/tareas/")

if __name__ == '__main__':
    verificar_tareas()
