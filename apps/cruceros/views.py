from django.shortcuts import render, redirect
from .models import Crucero
from .forms import creacionCruceroForm

def lista_cruceros(request):
    cruceros = Crucero.objects.all()
    if request.method == 'POST':
        form = creacionCruceroForm(request.POST)
        if form.is_valid():
            form.crear_crucero()
            return redirect('lista_cruceros')
    else:
        form = creacionCruceroForm()
    return render(request, 'cruceros/lista_cruceros.html', {
        'cruceros': cruceros,
        'form': form,
    })
