#!/usr/bin/env python
"""
Script de prueba para el API de tareas universales
Demuestra cómo crear tareas desde diferentes módulos del sistema
"""
import requests
import json
import time

# URL base del API
BASE_URL = 'http://127.0.0.1:8000'

def test_create_task_api():
    """Prueba la creación de tareas desde diferentes módulos"""

    print("🚀 Probando API de creación de tareas universales")
    print("=" * 60)

    # Datos de prueba para diferentes módulos
    test_tasks = [
        {
            'titulo': 'Reparar ascensor en cubierta 5 - Desde API',
            'descripcion': 'El ascensor principal presenta fallos en el sistema hidráulico. Los pasajeros reportan movimientos irregulares.',
            'tipo': 'correctivo',
            'prioridad': 'alta',
            'ubicacion_solicitud': 'Cubierta 5 - Área de Ascensores',
            'equipo_afectado': 'Ascensor Principal Hidráulico',
            'tiempo_estimado': 6.0,
            'modulo_origen': 'mantenimiento',
            'origen_url': '/mantenimiento/equipos/ascensor-001'
        },
        {
            'titulo': 'Sistema informático lento - Ventas',
            'descripcion': 'El sistema de punto de venta presenta lentitud excesiva, afectando el procesamiento de transacciones de pasajeros.',
            'tipo': 'correctivo',
            'prioridad': 'media',
            'ubicacion_solicitud': 'Cubierta 1 - Recepción Principal',
            'equipo_afectado': 'Servidor de Punto de Venta',
            'tiempo_estimado': 3.0,
            'modulo_origen': 'ventas',
            'origen_url': '/ventas/sistema/pos/'
        },
        {
            'titulo': 'Mantenimiento de iluminación LED - Entretenimiento',
            'descripcion': 'Varios focos LED en el teatro principal presentan parpadeo intermitente durante las funciones.',
            'tipo': 'preventivo',
            'prioridad': 'baja',
            'ubicacion_solicitud': 'Cubierta 6 - Teatro Principal',
            'equipo_afectado': 'Sistema de Iluminación LED',
            'tiempo_estimado': 2.0,
            'modulo_origen': 'entretenimiento',
            'origen_url': '/entretenimiento/teatro/iluminacion/'
        }
    ]

    # Probar creación de tareas
    created_tasks = []
    for i, task_data in enumerate(test_tasks, 1):
        print(f"\n📝 Creando tarea {i}/3: {task_data['titulo'][:50]}...")

        try:
            response = requests.post(
                f'{BASE_URL}/api/tasks/create/',
                json=task_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"  ✅ Éxito! ID de tarea: {result['task_id']}")
                    print(f"     URL: {result['task_url']}")
                    created_tasks.append(result)
                else:
                    print(f"  ❌ Error: {result.get('error', 'Error desconocido')}")
            else:
                print(f"  ❌ Error HTTP {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error de conexión: {e}")
        except json.JSONDecodeError as e:
            print(f"  ❌ Error de JSON: {e}")

        # Pequeña pausa entre requests
        time.sleep(0.5)

    # Probar obtención del conteo de tareas
    print("
📊 Probando API de conteo de tareas..."    try:
        response = requests.get(f'{BASE_URL}/api/tasks/count/', timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"  ✅ Total de tareas pendientes: {result['count']}")
            else:
                print(f"  ❌ Error en conteo: {result.get('error', 'Error desconocido')}")
        else:
            print(f"  ❌ Error HTTP {response.status_code} en conteo")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error de conexión en conteo: {e}")

    # Resumen final
    print("
🎯 Resumen de pruebas:"    print(f"  • Tareas creadas exitosamente: {len([t for t in created_tasks if t.get('success')])}")
    print(f"  • URLs de tareas creadas:")
    for task in created_tasks:
        if task.get('success'):
            print(f"    - {task.get('task_url', 'N/A')}")

    print("
💡 Para ver todas las tareas en el navegador:"    print(f"   {BASE_URL}/mantenimiento/tareas/")
    print("
💡 Para filtrar por módulo:"    print(f"   {BASE_URL}/mantenimiento/tareas/?modulo_origen=ventas")
    print(f"   {BASE_URL}/mantenimiento/tareas/?modulo_origen=entretenimiento")

    return len(created_tasks)

def test_universal_button_simulation():
    """Simula el comportamiento del botón universal"""

    print("
🎮 Simulando funcionamiento del botón universal..."    print("-" * 60)

    # Simular detección de módulos
    modules = ['restaurante', 'servicios_medicos', 'almacen', 'ventas']

    for module in modules:
        print(f"🏷️  Detectando módulo: {module}")

        # Simular creación de tarea desde este módulo
        task_data = {
            'titulo': f'Tarea de prueba desde {module}',
            'descripcion': f'Esta tarea fue creada automáticamente desde el módulo {module} usando el botón universal.',
            'tipo': 'correctivo',
            'prioridad': 'media',
            'ubicacion_solicitud': f'Área de {module}',
            'equipo_afectado': f'Equipo de {module}',
            'tiempo_estimado': 1.5,
            'modulo_origen': module,
            'origen_url': f'/{module}/test/'
        }

        try:
            response = requests.post(
                f'{BASE_URL}/api/tasks/create/',
                json=task_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"  ✅ Tarea creada: {result['task_id']}")
                else:
                    print(f"  ❌ Error: {result.get('error')}")
            else:
                print(f"  ❌ Error HTTP {response.status_code}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

        time.sleep(0.3)

def main():
    """Función principal"""
    print("🧪 SISTEMA UNIVERSAL DE GESTIÓN DE TAREAS - PRUEBAS")
    print("=" * 60)
    print("Asegúrate de que el servidor Django esté ejecutándose en:")
    print(f"  {BASE_URL}")
    print()

    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code != 200:
            print(f"❌ El servidor no responde correctamente (HTTP {response.status_code})")
            print("Ejecuta: python manage.py runserver")
            return
    except requests.exceptions.RequestException:
        print("❌ No se puede conectar al servidor")
        print("Ejecuta: python manage.py runserver")
        return

    print("✅ Servidor conectado correctamente")
    print()

    # Ejecutar pruebas
    tasks_created = test_create_task_api()

    if tasks_created > 0:
        print("
🎪 Probando simulación del botón universal..."        test_universal_button_simulation()

    print("
🎊 PRUEBAS COMPLETADAS"    print("=" * 60)
    print("📋 Instrucciones para verificar:")
    print("1. Abre tu navegador en:")
    print(f"   {BASE_URL}/mantenimiento/tareas/")
    print("2. Deberías ver todas las tareas creadas")
    print("3. Usa los filtros para ver tareas por módulo")
    print("4. Abre las páginas de ejemplo:")
    print("   file:///" + __file__.replace('test_api_tareas.py', 'test_modulo_ejemplo.html'))
    print("   file:///" + __file__.replace('test_api_tareas.py', 'test_modulo_medico.html'))

if __name__ == '__main__':
    main()
