#!/usr/bin/env python
"""
Script para probar que el sistema de habitaciones funciona correctamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Administrador_Cruceros.settings')
sys.path.append('.')

try:
    django.setup()

    from apps.creador_embarcaciones.models import TipoHabitacion, Habitaciones

    print("✅ Django configurado correctamente")
    print()

    # Verificar que los choices están disponibles
    print("=== VERIFICACIÓN DE CHOICES ===")
    print(f"TipoHabitacion.POSICION_CHOICES: {len(TipoHabitacion.POSICION_CHOICES)} opciones")
    print(f"TipoHabitacion.ESTADO_CHOICES: {len(TipoHabitacion.ESTADO_CHOICES)} opciones")
    print(f"Habitaciones.POSICION_CHOICES: {len(Habitaciones.POSICION_CHOICES)} opciones")
    print(f"Habitaciones.ESTADO_CHOICES: {len(Habitaciones.ESTADO_CHOICES)} opciones")
    print()

    # Verificar tipos de habitación disponibles
    tipos = TipoHabitacion.objects.all()
    print(f"✅ Tipos de habitación disponibles: {tipos.count()}")
    for tipo in tipos:
        print(f"   • {tipo.nombre} - {tipo.get_tipo_display()}")
    print()

    print("🎉 ¡Sistema de habitaciones funcionando correctamente!")
    print("El error AttributeError ha sido corregido.")

except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)</content>
</xai:function_call">The file Administracion-proyecto-crucero/test_habitaciones.py has been created.
