from django.shortcuts import render, redirect
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


