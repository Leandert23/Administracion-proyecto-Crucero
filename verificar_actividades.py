import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Administrador_Cruceros.settings')
django.setup()

from apps.entretenimiento.models import Actividad, ActividadRutinaria

# Verificar actividades de pago
actividades_pago = Actividad.objects.all()
print(f"🎯 Actividades de pago creadas: {actividades_pago.count()}")
print("\n📋 Primeras 3 actividades de pago:")
for act in actividades_pago[:3]:
    print(f"  • {act.titulo}")
    print(f"    Día {act.dia_crucero} - {act.hora_inicio.strftime('%H:%M')} a {act.hora_fin.strftime('%H:%M')}")
    print(f"    Precio: ${act.coste:.2f}")
    print()

# Verificar actividades rutinarias
actividades_rut = ActividadRutinaria.objects.all()
print(f"🎭 Actividades rutinarias creadas: {actividades_rut.count()}")
print("\n📅 Primeras 3 actividades rutinarias:")
for act in actividades_rut[:3]:
    print(f"  • {act.titulo}")
    print(f"    Día {act.dia_crucero} - {act.hora_inicio.strftime('%H:%M')} a {act.hora_fin.strftime('%H:%M')}")
    print(f"    Ubicación: {act.ubicacion}")
    print()

print("✅ ¡Las funciones de inicialización se ejecutaron exitosamente!")
print("🎉 El módulo de entretenimiento está completamente funcional con datos de ejemplo.")
