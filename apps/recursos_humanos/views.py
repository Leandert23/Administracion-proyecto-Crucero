from django.shortcuts import render
from django.http import HttpResponse

def recursos_humanos_view(request):
    """
    Vista para la página de Recursos Humanos
    """
    # Por ahora, solo renderizamos la página HTML
    # En el futuro aquí se pueden agregar los modelos y lógica de negocio
    context = {
        'personal_list': [],  # Lista vacía por ahora
    }
    return render(request, 'recursos_humanos/index.html', context)
