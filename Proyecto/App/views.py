from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Viaje
from .models import Habitacion, Reserva, Viaje, Entretenimiento
from App.models import TipoHabitacion,Habitacion

def generar_camarotes(crucero):
    if crucero == "vision":  
        for piso in range(2, 6):
            for i in range(150): 
                if i < 125:
                    tipo = TipoHabitacion.objects.get(categoria="basico", subtipo="sencillo")
                else:
                    tipo = TipoHabitacion.objects.get(categoria="basico", subtipo="doble")

                lado = "babor" if i % 2 == 0 else "estribor"
                vista = True if i < 90 else False 
                num = f"{piso}0{i:02d}"

                Habitacion.objects.using(crucero).create(
                    crucero=crucero,
                    numero=num,
                    piso=piso,
                    lado=lado,
                    vista_mar=vista,
                    tipo_habitacion=tipo,
                )

        for piso in range(6, 9):
            for i in range(75):
                if i < 50:
                    tipo = TipoHabitacion.objects.get(categoria="premium", subtipo="sencillo")
                else:
                    tipo = TipoHabitacion.objects.get(categoria="premium", subtipo="doble")

                lado = "babor" if i % 2 == 0 else "estribor"
                vista = True if i < 45 else False
                num = f"{piso}0{i:02d}"

                Habitacion.objects.using(crucero).create(
                    crucero=crucero,
                    numero=num,
                    piso=piso,
                    lado=lado,
                    vista_mar=vista,
                    tipo_habitacion=tipo,
                )

def estado_viaje(request, crucero):
    viaje = Viaje.objects.using(crucero).first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero})
    return render(request, "App/estado_viaje.html", {"viaje": viaje})

def inicio(request):
    return render(request, "App/preview.html")

def reservas(request):
    crucero = request.GET.get("crucero")
    if not crucero:
        crucero = request.session.get('crucero_seleccionado')
    
    viaje = None
    if crucero:
        request.session['crucero_seleccionado'] = crucero
        viaje = Viaje.objects.using(crucero).first()
    
    return render(request, "App/reservas.html", {
        "crucero": crucero,
        "viaje": viaje,
    })

def reservacion_habitaciones(request, crucero):
    viaje = Viaje.objects.using(crucero).first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero})

    habitaciones = Habitacion.objects.using(crucero).filter(
        reservada=False
    ).order_by("tipo_habitacion__precio_base")

    return render(request, "App/reservacion_habitaciones.html", {
        "habitaciones": habitaciones,
        "viaje": viaje,
        "crucero": crucero, 
    })


def catalogo_entretenimiento(request, crucero):
    viaje = Viaje.objects.using(crucero).first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero})

    actividades = Entretenimiento.objects.using(crucero).filter(
        dia=viaje.dia_actual,
        reservada=False
    ).order_by("precio")

    return render(request, "App/catalogo_entretenimiento.html", {
        "actividades": actividades,
        "viaje": viaje,
        "crucero": crucero, 
    })

@login_required
def reservar_habitacion(request, crucero):
    habitacion = get_object_or_404(Habitacion.objects.using(crucero))

    if not habitacion.reservada:
        fecha_inicio = timezone.now().date()
        fecha_fin = fecha_inicio + timedelta(days=7)

        Reserva.objects.using(crucero).create(
            usuario_id=request.user.id,   
            habitacion=habitacion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado="confirmada"
        )

        habitacion.reservada = True
        habitacion.save(using=crucero)

        return redirect("mis_reservas", crucero=crucero)

    return redirect("reservacion_habitaciones", crucero=crucero)

@login_required
def reservar_entretenimiento(request, crucero):
    actividad = get_object_or_404(Entretenimiento.objects.using(crucero))

    if not actividad.reservada:
        Reserva.objects.using(crucero).create(
            usuario=request.user,
            entretenimiento=actividad, 
            estado="confirmada"
        )
        actividad.reservada = True
        actividad.save(using=crucero)

    return redirect("mis_reservas", crucero=crucero)

@login_required
def mis_reservas(request, crucero):
    reservas_habitaciones = Reserva.objects.using(crucero).filter(
        usuario=request.user, habitacion__isnull=False
    )
    reservas_entretenimiento = Reserva.objects.using(crucero).filter(
        usuario=request.user, entretenimiento__isnull=False
    )

    return render(request, "App/mis_reservas.html", {
        "crucero": crucero,
        "reservas_habitaciones": reservas_habitaciones,
        "reservas_entretenimiento": reservas_entretenimiento,
    })

@login_required
def cancelar_reserva(request, crucero, reserva_id):
    reserva = get_object_or_404(Reserva.objects.using(crucero), id=reserva_id, usuario=request.user)

    if reserva.habitacion:
        habitacion = reserva.habitacion
        habitacion.reservada = False
        habitacion.save(using=crucero)

    if reserva.entretenimiento:
        actividad = reserva.entretenimiento
        actividad.reservada = False
        actividad.save(using=crucero)

    reserva.delete(using=crucero)

    return redirect("mis_reservas", crucero=crucero)


