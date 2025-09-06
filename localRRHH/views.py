from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import random
import string
from .models import Personal, Amonestacion
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Sum, Count

def index(request):
    error_message = ''
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre', '').strip()
            apellido = request.POST.get('apellido', '').strip()
            salario = request.POST.get('salario')
            edad = request.POST.get('edad')
            anios_experiencia = request.POST.get('anios_experiencia')
            categoria = request.POST.get('categoria')
            puesto = request.POST.get('puesto')
            pStatus = request.POST.get('pStatus')

            personal = Personal(
                nombre=nombre,
                apellido=apellido,
                salario=int(salario) if salario else 0,
                edad=int(edad) if edad else 0,
                anios_experiencia=int(anios_experiencia) if anios_experiencia else 0,
                categoria=categoria,
                puesto=puesto,
                pStatus=int(pStatus) if pStatus else 1,
            )

            personal.full_clean()  # Invoca validaciones
            personal.save()
            return redirect('index')

        except (ValidationError, ValueError, IntegrityError) as e:
            error_message = str(e)

    # Obtener todos los objetos Personal para mostrar
    personal_list = Personal.objects.select_related('amonestacion').all()

    # Calcular estadísticas
    total_salarios = Personal.objects.aggregate(total=Sum('salario'))['total'] or 0
    personal_activo = Personal.objects.filter(pStatus=1).count()
    personal_inactivo = Personal.objects.filter(pStatus=2).count()
    personal_de_baja = Personal.objects.filter(pStatus=3).count()
    personal_amonestado = Amonestacion.objects.filter(estado=True).count()

    return render(request, 'index.html', {
        'personal_list': personal_list,
        'error_message': error_message,
        'total_salarios': total_salarios,
        'personal_activo': personal_activo,
        'personal_inactivo': personal_inactivo,
        'personal_de_baja': personal_de_baja,
        'personal_amonestado': personal_amonestado,
    })


@csrf_exempt
@require_POST
def generar_plantel(request):
    try:
        data = json.loads(request.body)
        cantidad = data.get('cantidad', 0)

        if cantidad not in [630, 1300, 1950]:
            return JsonResponse({'error': 'Cantidad inválida. Debe ser 630, 1300 o 1950.'}, status=400)

        # Prioridades según especificación:
        # 1. Mantenimiento, 2. Restaurantes (Culinario), 3. Entretenimiento, 4. Médico, 5. Administrativo
        prioridades = [
            ('Mantenimiento', 30),      # 30%
            ('Culinario', 25),          # 25%
            ('Entretenimiento', 20),    # 20%
            ('Medico', 15),            # 15%
            ('Administrativo', 10),    # 10%
        ]

        # Calcular distribución por categoría
        distribucion = {}
        restantes = cantidad

        for categoria, porcentaje in prioridades:
            asignados = int(cantidad * porcentaje / 100)
            distribucion[categoria] = asignados
            restantes -= asignados

        # Asignar los restantes al último módulo (Mantenimiento)
        if restantes > 0:
            distribucion['Mantenimiento'] += restantes

        # Mapeo de puestos por categoría
        puestos_por_categoria = {
            'Mantenimiento': ['Plomero', 'Ingeniero', 'Conserje', 'Tecnico'],
            'Culinario': ['Cocinero', 'Mesero', 'Chef', 'Barista', 'Repostero', 'Bartender', 'Chef Ejecutivo', 'Chef de Partie', 'Auxiliares de cocina', 'Maitre d\'', 'Jefe de meseros'],
            'Entretenimiento': ['Animadores', "DJ's", 'Musicos', 'Bailarines', 'Guias Turisticos'],
            'Medico': ['Enfermero', 'Medico General', 'Medico en Jefe', 'Paramedico'],
            'Administrativo': ['Gerente', 'Cajero']
        }

        creados = 0
        errores = []

        # Generar personal por categoría
        for categoria, num_personal in distribucion.items():
            puestos = puestos_por_categoria[categoria]

            for i in range(num_personal):
                try:
                    # Generar nombre y apellido aleatorios
                    nombre = ''.join(random.choices(string.ascii_uppercase, k=1)) + ''.join(random.choices(string.ascii_lowercase, k=random.randint(2, 8)))
                    apellido = ''.join(random.choices(string.ascii_uppercase, k=1)) + ''.join(random.choices(string.ascii_lowercase, k=random.randint(2, 8)))

                    # Generar datos aleatorios
                    salario = random.randint(15000, 80000)
                    edad = random.randint(21, 65)
                    anios_experiencia = random.randint(0, min(edad - 21, 40))
                    puesto = random.choice(puestos)

                    # Crear registro
                    personal = Personal(
                        nombre=nombre,
                        apellido=apellido,
                        salario=salario,
                        edad=edad,
                        anios_experiencia=anios_experiencia,
                        categoria=categoria,
                        puesto=puesto,
                        pStatus=1  # Activo por defecto
                    )

                    personal.full_clean()
                    personal.save()
                    creados += 1

                except Exception as e:
                    errores.append(f"Error creando {categoria}: {str(e)}")
                    continue

        return JsonResponse({
            'success': True,
            'creados': creados,
            'distribucion': distribucion,
            'errores': errores
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def vaciar_plantel(request):
    try:
        # Contar registros antes de eliminar
        personal_count = Personal.objects.count()
        amonestacion_count = Amonestacion.objects.count()
        total_registros = personal_count + amonestacion_count

        # Eliminar todas las amonestaciones primero (por las claves foráneas)
        Amonestacion.objects.all().delete()

        # Eliminar todo el personal
        Personal.objects.all().delete()

        return JsonResponse({
            'success': True,
            'eliminados': total_registros,
            'personal_eliminado': personal_count,
            'amonestaciones_eliminadas': amonestacion_count,
            'mensaje': f'Se eliminaron {total_registros} registros exitosamente'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
