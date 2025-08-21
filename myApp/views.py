from django.shortcuts import render, redirect, get_object_or_404
from .models import Crucero, Instalacion
from .forms import CruceroForm, InstalacionForm, CruceroCreateForm

# Vista para listar todos los cruceros
def lista_cruceros(request):
	cruceros = Crucero.objects.all()
	return render(request, 'cruceros/lista_cruceros.html', {'cruceros': cruceros})

# Vista para crear un nuevo crucero
def crucero_nuevo(request):
	if request.method == 'POST':
		form = CruceroCreateForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('lista_cruceros')
	else:
		form = CruceroCreateForm()
	return render(request, 'cruceros/crucero_create_form.html', {'form': form})


# Vista para editar un crucero existente
def crucero_editar(request, pk):
    crucero = get_object_or_404(Crucero, pk=pk)
    instalaciones = crucero.instalaciones.all()

    if request.method == 'POST':
        if 'guardar_crucero' in request.POST:
            form = CruceroForm(request.POST, request.FILES, instance=crucero)
            if form.is_valid():
                form.save()
                return redirect('lista_cruceros')
        elif 'agregar_instalacion' in request.POST:
            instalacion_form = InstalacionForm(request.POST)
            if instalacion_form.is_valid():
                nueva_instalacion = instalacion_form.save(commit=False)
                nueva_instalacion.crucero = crucero
                nueva_instalacion.save()
                return redirect('crucero_editar', pk=crucero.pk)
    else:
        form = CruceroForm(instance=crucero)
        instalacion_form = InstalacionForm()

    return render(request, 'cruceros/crucero_form.html', {
        'form': form,
        'crucero': crucero,
        'instalaciones': instalaciones,
        'instalacion_form': instalacion_form,
    })
