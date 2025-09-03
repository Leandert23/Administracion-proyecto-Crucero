from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Personal
import json
from django.shortcuts import render

@csrf_exempt
def agregar_personal(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        persona = Personal.objects.create(
            nombre=data['nombre'],
            apellido=data['apellido'],
            edad=data['edad'],
            experiencia=data['experiencia'],
            salario=data['salario'],
            categoria=data['categoria'],
            puesto=data['puesto']
        )
        return JsonResponse({'id': persona.id, 'nombre': persona.nombre})

def index(request):
    return render(request, 'index.html')