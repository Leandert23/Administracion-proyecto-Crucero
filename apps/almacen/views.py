from django.shortcuts import render, redirect, get_object_or_404
from .models import Crucero
from .forms import creacionCruceroForm, cruceroEdicionParcialForm

def lista_cruceros(request):
	cruceros = Crucero.objects.all()
	return render(request, 'cruceros/lista_cruceros.html', {'cruceros': cruceros})

def crucero_creacion_rapida(request):
    # Esto es porque cuando se da en el botón de crear en el formulario se envía una petición POST a la misma vista
    if request.method == 'POST':
        form = creacionCruceroForm(request.POST)
        if form.is_valid():
            form.crear_crucero()
            return redirect('lista_cruceros')
    else:
        form = creacionCruceroForm()
    return render(request, 'cruceros/crucero_creacion_rapida.html', {'form': form})

def crucero_editar(request, pk):
    crucero = get_object_or_404(Crucero, pk=pk)
    if request.method == 'POST':
        if 'guardar_crucero' in request.POST:
            form = cruceroEdicionParcialForm(request.POST, request.FILES, instance=crucero)
            if form.is_valid():
                form.save()
                return redirect('lista_cruceros')
        else:
            form = cruceroEdicionParcialForm(instance=crucero)
    else:
        form = cruceroEdicionParcialForm(instance=crucero)
        
    return render(request, 'cruceros/crucero_form.html', {'form': form, 'crucero': crucero})
