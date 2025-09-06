from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, date
from django.contrib import messages
from .models import (
    Entretenimiento,
    Mesa,
    EventoPersonalizado,
    Reserva,
    Restaurante
)
from ..cruceros.models import Crucero, Habitacion, Viaje
from ..cruceros.Services.fecha_general import obtener_fecha_actual

def crucero_se_encuentra_en_planificacion():
    return True  # Aquí después vendrá la lógica real del otro módulo

# PÁGINAS PRINCIPALES

def inicio(request):
    return render(request, "App/inicio")


def reservas(request, crucero=None):
    # Si la URL pasa el nombre del crucero, se usa ese; si no, se intenta por GET o sesión
    crucero_nombre = crucero or request.GET.get("crucero") or request.session.get("crucero_seleccionado")
    crucero_obj = None
    if crucero_nombre:
        crucero_obj = Crucero.objects.filter(nombre=crucero_nombre).first()
        request.session["crucero_seleccionado"] = crucero_nombre
    viaje = Viaje.objects.filter(crucero=crucero_obj, estado="activo").first() if crucero_obj else None

    return render(request, "App/reservas.html", {
        "crucero": crucero_obj,
        "viaje": viaje,
    })

# HABITACIONES

#@login_required
def reservacion_habitaciones(request, crucero):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    viaje = Viaje.objects.filter(crucero=crucero_obj, estado="planificacion").first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero_obj})

    if not crucero_obj.se_encuentra_en_planificacion:
        messages.warning(request, "Ya no puedes reservar habitaciones, el crucero zarpó.")
        return redirect("reservas")

    habitaciones = Habitacion.objects.filter(
        crucero=crucero_obj,
        reservada=False
    ).order_by("tipo_habitacion__precio_base")

    return render(request, "App/reservacion_habitaciones.html", {
        "habitaciones": habitaciones,
        "viaje": viaje,
        "crucero": crucero_obj,
    })


#@login_required
def reservar_habitacion(request, crucero, habitacion_id):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    viaje = Viaje.objects.filter(crucero=crucero_obj, estado="planificacion").first()
    habitacion = get_object_or_404(Habitacion, id=habitacion_id, crucero=crucero_obj)

    if not habitacion.reservada:
        fecha_inicio = viaje.fecha_inicio
        fecha_fin = viaje.fecha_fin

        Reserva.objects.create(
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

#@login_required
def catalogo_entretenimiento(request, crucero):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    viaje = Viaje.objects.filter(crucero=crucero_obj, estado__in=["activo", "planificacion"]).first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero_obj})

    if crucero_obj.se_encuentra_en_planificacion:
        return render(request, "App/no_viaje.html", {"crucero": crucero_obj})
    else:
        actividades = Entretenimiento.objects.filter(
            crucero=crucero_obj,
            dia=crucero_obj.dia_actual_de_viaje,
            reservada=False
        ).order_by("precio")

    return render(request, "App/catalogo_entretenimiento.html", {
        "actividades": actividades,
        "viaje": viaje,
        "crucero": crucero_obj,
    })


#@login_required
def reservar_entretenimiento(request, crucero, entretenimiento_id):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    actividad = get_object_or_404(Entretenimiento, id=entretenimiento_id, crucero=crucero_obj)

    if not actividad.reservada:
        Reserva.objects.create(
            entretenimiento=actividad,
            estado="confirmada",
        )
        actividad.reservada = True
        actividad.save()

    return redirect("mis_reservas", crucero=crucero)

# MESAS (Restaurantes)

#@login_required
def reservar_restaurante(request, crucero):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    restaurantes = Restaurante.objects.filter(crucero=crucero_obj)

    viaje = Viaje.objects.filter(crucero=crucero_obj, estado__in=["activo", "planificacion"]).first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero_obj})

    if crucero_obj.se_encuentra_en_planificacion:
        return render(request, "App/no_viaje.html", {"crucero": crucero_obj})
    else:
        return render(request, "App/reservar_restaurante.html", {
        "restaurantes": restaurantes,
        "crucero": crucero_obj,
    })


#@login_required
def primer_restaurante(request, crucero):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    mesas = Mesa.objects.filter(crucero=crucero_obj, restaurante__nombre="L'odissea della Toscana", reservada=False)
    viaje = Viaje.objects.filter(crucero=crucero_obj).first()

    return render(request, "App/primer_restaurante.html", {
        "mesas": mesas,
        "crucero": crucero_obj,
        "viaje": viaje,
    })


#@login_required
def segundo_restaurante(request, crucero):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    mesas = Mesa.objects.filter(crucero=crucero_obj, restaurante__nombre="Odessa Al-Bahr", reservada=False)
    viaje = Viaje.objects.filter(crucero=crucero_obj).first()

    return render(request, "App/segundo_restaurante.html", {
        "mesas": mesas,
        "crucero": crucero_obj,
        "viaje": viaje,
    })

#@login_required
def reservar_mesa(request, crucero, mesa_id):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    mesa = get_object_or_404(Mesa, id=mesa_id, crucero=crucero_obj)

    if not mesa.reservada:
        Reserva.objects.create(
            mesa=mesa,
            estado="confirmada",
        )
        mesa.reservada = True
        mesa.save()

    return redirect("mis_reservas", crucero=crucero)

# EVENTOS PERSONALIZADOS

#@login_required
def organizar_evento(request, crucero):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    viaje = Viaje.objects.filter(crucero=crucero_obj).first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero_obj})

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        materiales = request.POST.get("materiales")
        dia = int(request.POST.get("dia"))

        if crucero_obj.se_encuentra_en_viaje:
            if dia < crucero_obj.dia_actual_de_viaje:
                messages.error(
                    request,
                    f"No puedes organizar eventos para días anteriores al día {crucero.dia_actual_de_viaje}."
                )
                return redirect("organizar_evento", crucero=crucero)

        evento = EventoPersonalizado.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            materiales=materiales,
            dia=dia,
            crucero=crucero_obj,
        )

        Reserva.objects.create(
            evento_personalizado=evento,
            estado="pendiente",
        )

        return redirect("mis_reservas", crucero=crucero)

    dias = range(1, 9)
    viaje = Viaje.objects.filter(crucero=crucero_obj, estado__in=["activo", "planificacion"]).first()
    if not viaje:
        return render(request, "App/no_viaje.html", {"crucero": crucero_obj})

    return render(request, "App/organizar_evento.html", {
        "crucero": crucero_obj,
        "viaje": viaje,
        "dias": dias
    })

# MIS RESERVAS

#@login_required
def mis_reservas(request, crucero):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    reservas_habitaciones = Reserva.objects.filter(habitacion__isnull=False, habitacion__crucero=crucero_obj
    )
    reservas_entretenimiento = Reserva.objects.filter(entretenimiento__isnull=False, entretenimiento__crucero=crucero_obj
    )
    reservas_mesas = Reserva.objects.filter(mesa__isnull=False, mesa__crucero=crucero_obj
    )
    reservas_eventos = Reserva.objects.filter(evento_personalizado__isnull=False, evento_personalizado__crucero=crucero_obj
    )

    total = 0

    for r in reservas_habitaciones:
        total += int(r.habitacion.tipo_habitacion.precio_base)

    for r in reservas_entretenimiento:
        total += int(r.entretenimiento.precio)

    for r in reservas_mesas:
        total += int(r.mesa.restaurante.precio) if hasattr(r.mesa.restaurante, "precio") else 40

    for r in reservas_eventos:
        total += 700.00

    return render(request, "App/mis_reservas.html", {
        "crucero": crucero_obj,
        "reservas_habitaciones": reservas_habitaciones,
        "reservas_entretenimiento": reservas_entretenimiento,
        "reservas_mesas": reservas_mesas,
        "reservas_eventos": reservas_eventos,
        "total": total,
    })

# CANCELAR RESERVA

#@login_required
def cancelar_reserva(request, crucero, reserva_id):
    crucero_obj = get_object_or_404(Crucero, nombre=crucero)
    reserva = get_object_or_404(Reserva, id=reserva_id)

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
