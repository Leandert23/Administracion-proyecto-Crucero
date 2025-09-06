from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, date
from django.contrib import messages
from .models import (
    Viaje,
    Habitacion,
    TipoHabitacion,
    Entretenimiento,
    Mesa,
    EventoPersonalizado,
    Reserva,
    Restaurante
)

def crucero_se_encuentra_en_planificacion():
    return True  # Aquí después vendrá la lógica real del otro módulo

# PÁGINAS PRINCIPALES

def inicio(request):
    return render(request, "App/preview.html")


def reservas(request):
    crucero = request.GET.get("crucero") or request.session.get("crucero_seleccionado")

    request.session["crucero_seleccionado"] = crucero
    viaje = Viaje.objects.filter(crucero=crucero).first()

    return render(request, "App/reservas.html", {
        "crucero": crucero,
        "viaje": viaje,
    })

# HABITACIONES

@login_required
def reservacion_habitaciones(request, crucero):
    viaje = Viaje.objects.filter(crucero=crucero).first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero})

    if not crucero_se_encuentra_en_planificacion():
        messages.warning(request, "Ya no puedes reservar habitaciones, el crucero zarpó.")
        return redirect("reservas")

    habitaciones = Habitacion.objects.filter(
        crucero=crucero,
        reservada=False
    ).order_by("tipo_habitacion__precio_base")

    return render(request, "App/reservacion_habitaciones.html", {
        "habitaciones": habitaciones,
        "viaje": viaje,
        "crucero": crucero,
    })


@login_required
def reservar_habitacion(request, crucero, habitacion_id):
    habitacion = get_object_or_404(Habitacion, id=habitacion_id, crucero=crucero)

    if not habitacion.reservada:
        fecha_inicio = timezone.now().date()
        fecha_fin = fecha_inicio + timedelta(days=7)

        Reserva.objects.create(
            usuario=request.user,
            habitacion=habitacion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado="confirmada",
        )

        habitacion.reservada = True
        habitacion.save()

        return redirect("mis_reservas", crucero=crucero)

    return redirect("reservacion_habitaciones", crucero=crucero)

# ENTRETENIMIENTO

@login_required
def catalogo_entretenimiento(request, crucero):
    viaje = Viaje.objects.filter(crucero=crucero).first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero})

    actividades = Entretenimiento.objects.filter(
        crucero=crucero,
        dia=viaje.dia_actual,
        reservada=False
    ).order_by("precio")

    return render(request, "App/catalogo_entretenimiento.html", {
        "actividades": actividades,
        "viaje": viaje,
        "crucero": crucero,
    })


@login_required
def reservar_entretenimiento(request, crucero, entretenimiento_id):
    actividad = get_object_or_404(Entretenimiento, id=entretenimiento_id, crucero=crucero)

    if not actividad.reservada:
        Reserva.objects.create(
            usuario=request.user,
            entretenimiento=actividad,
            estado="confirmada",
        )
        actividad.reservada = True
        actividad.save()

    return redirect("mis_reservas", crucero=crucero)

# MESAS (Restaurantes)

@login_required
def reservar_restaurante(request, crucero):
    restaurantes = Restaurante.objects.filter(crucero=crucero)

    return render(request, "App/reservar_restaurante.html", {
        "restaurantes": restaurantes,
        "crucero": crucero,
    })


@login_required
def primer_restaurante(request, crucero):
    mesas = Mesa.objects.filter(crucero=crucero, restaurante__nombre="L'odissea della Toscana", reservada=False)
    viaje = Viaje.objects.filter(crucero=crucero).first()

    return render(request, "App/primer_restaurante.html", {
        "mesas": mesas,
        "crucero": crucero,
        "viaje": viaje,
    })


@login_required
def segundo_restaurante(request, crucero):
    mesas = Mesa.objects.filter(crucero=crucero, restaurante__nombre="Odessa Al-Bahr", reservada=False)
    viaje = Viaje.objects.filter(crucero=crucero).first()

    return render(request, "App/segundo_restaurante.html", {
        "mesas": mesas,
        "crucero": crucero,
        "viaje": viaje,
    })

@login_required
def reservar_mesa(request, crucero, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id, crucero=crucero)

    if not mesa.reservada:
        Reserva.objects.create(
            usuario=request.user,
            mesa=mesa,
            estado="confirmada",
        )
        mesa.reservada = True
        mesa.save()

    return redirect("mis_reservas", crucero=crucero)

# EVENTOS PERSONALIZADOS

@login_required
def organizar_evento(request, crucero):
    viaje = Viaje.objects.filter(crucero=crucero).first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero})

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        materiales = request.POST.get("materiales")
        dia = int(request.POST.get("dia"))

        if dia < viaje.dia_actual:
            messages.error(
                request,
                f"No puedes organizar eventos para días anteriores al día {viaje.dia_actual}."
            )
            return redirect("organizar_evento", crucero=crucero)

        evento = EventoPersonalizado.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            materiales=materiales,
            dia=dia,
            crucero=crucero,
        )

        Reserva.objects.create(
            usuario=request.user,
            evento_personalizado=evento,
            estado="pendiente",
        )

        return redirect("mis_reservas", crucero=crucero)

    dias = range(1, 9)
    return render(request, "App/organizar_evento.html", {
        "crucero": crucero,
        "viaje": viaje,
        "dias": dias
    })

# MIS RESERVAS

@login_required
def mis_reservas(request, crucero):
    reservas_habitaciones = Reserva.objects.filter(
        usuario=request.user, habitacion__isnull=False, habitacion__crucero=crucero
    )
    reservas_entretenimiento = Reserva.objects.filter(
        usuario=request.user, entretenimiento__isnull=False, entretenimiento__crucero=crucero
    )
    reservas_mesas = Reserva.objects.filter(
        usuario=request.user, mesa__isnull=False, mesa__crucero=crucero
    )
    reservas_eventos = Reserva.objects.filter(
        usuario=request.user, evento_personalizado__isnull=False, evento_personalizado__crucero=crucero
    )

    total = 0

    for r in reservas_habitaciones:
        total += r.habitacion.tipo_habitacion.precio_base

    for r in reservas_entretenimiento:
        total += r.entretenimiento.precio

    for r in reservas_mesas:
        total += r.mesa.restaurante.precio if hasattr(r.mesa.restaurante, "precio") else 40

    for r in reservas_eventos:
        total += 700.00

    return render(request, "App/mis_reservas.html", {
        "crucero": crucero,
        "reservas_habitaciones": reservas_habitaciones,
        "reservas_entretenimiento": reservas_entretenimiento,
        "reservas_mesas": reservas_mesas,
        "reservas_eventos": reservas_eventos,
        "total": total,
    })

# CANCELAR RESERVA

@login_required
def cancelar_reserva(request, crucero, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)

    if reserva.habitacion:
        reserva.habitacion.reservada = False
        reserva.habitacion.save()

    if reserva.entretenimiento:
        reserva.entretenimiento.reservada = False
        reserva.entretenimiento.save()

    if reserva.mesa:
        reserva.mesa.reservada = False
        reserva.mesa.save()

    if reserva.evento_personalizado:
        reserva.evento_personalizado.delete()

    reserva.delete()
    return redirect("mis_reservas", crucero=crucero)
