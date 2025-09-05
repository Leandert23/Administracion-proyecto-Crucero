from .models import Habitacion, TipoHabitacion
from .models import Restaurante, Mesa

def rellenar_habitaciones(crucero):

    if Habitacion.objects.filter(crucero=crucero).exists():
        print(f"⚠ Ya existen habitaciones para el crucero {crucero}, no se agregaron nuevas.")
        return

    basico_sencillo = TipoHabitacion.objects.get(categoria="basico", subtipo="sencillo")
    basico_doble = TipoHabitacion.objects.get(categoria="basico", subtipo="doble")
    premium_sencillo = TipoHabitacion.objects.get(categoria="premium", subtipo="sencillo")
    premium_doble = TipoHabitacion.objects.get(categoria="premium", subtipo="doble")

    if crucero == "vision":  # pequeño
        pisos = range(2, 6)  
        habitaciones_por_piso = 150
    elif crucero == "voyager":  # mediano
        pisos = range(2, 9)  
        habitaciones_por_piso = 200
    elif crucero == "oasis":  # grande
        pisos = range(2, 11)  
        habitaciones_por_piso = 300
    else:
        print("❌ Crucero no válido")
        return

    for piso in pisos:
        for i in range(habitaciones_por_piso):
            lado = "babor" if i % 2 == 0 else "estribor"
            uso = "0" if lado == "babor" else "1"

            # Identificador CD
            identificador = f"{i:02d}"

            # Código de habitación
            numero = f"{piso}{uso}{identificador}"

            # 60% primeras habitaciones de cada piso
            vista = i < int(habitaciones_por_piso * 0.6)

            # selecciona el tipo de habitación
            if i < habitaciones_por_piso * 0.4:
                tipo = basico_sencillo
            elif i < habitaciones_por_piso * 0.7:
                tipo = basico_doble
            elif i < habitaciones_por_piso * 0.9:
                tipo = premium_sencillo
            else:
                tipo = premium_doble

            Habitacion.objects.create(
                crucero=crucero,
                numero=numero,
                piso=piso,
                lado=lado,
                vista_mar=vista,
                tipo_habitacion=tipo,
                reservada=False,
                precio=tipo.precio_base  # precio de acuerdo al tipo
            )


    print(f"✅ Habitaciones para el crucero {crucero} creadas exitosamente.")

def borrar_habitaciones(crucero):

    eliminadas, _ = Habitacion.objects.filter(crucero=crucero).delete()
    print(f"🗑 {eliminadas} habitaciones eliminadas del crucero {crucero}.")

def rellenar_restaurantes(crucero):

    if Restaurante.objects.filter(crucero=crucero).exists():
        print(f"⚠ Ya existen restaurantes para el crucero {crucero}, no se agregaron nuevos.")
        return

    # cantidad de mesas por crucero
    if crucero == "vision":
        mesas_por_restaurante = 60
    elif crucero == "voyager":
        mesas_por_restaurante = 80
    elif crucero == "oasis":
        mesas_por_restaurante = 120
    else:
        print("❌ Crucero no válido")
        return

    # los restaurantes
    restaurantes = [
        ("L'odissea della Toscana", "Italiano"),
        ("Odessa Al-Bahr", "Árabe"),
    ]

    for nombre, _ in restaurantes:
        restaurante = Restaurante.objects.create(
            crucero=crucero,
            nombre=nombre
        )
        for i in range(1, mesas_por_restaurante + 1):
            Mesa.objects.create(
                crucero=crucero,
                numero=f"M-{i+1}",
                capacidad=4,
                reservada=False,
                restaurante=restaurante,
                precio= 40 
            )


    print(f"✅ Restaurantes y mesas para el crucero {crucero} creados exitosamente.")


def borrar_restaurantes(crucero):

    eliminadas_mesas, _ = Mesa.objects.filter(crucero=crucero).delete()
    eliminados_restaurantes, _ = Restaurante.objects.filter(crucero=crucero).delete()
    print(f"🗑 {eliminadas_mesas} mesas y {eliminados_restaurantes} restaurantes eliminados del crucero {crucero}.")

from .models import Entretenimiento

def rellenar_entretenimiento(crucero):

    if Entretenimiento.objects.filter(crucero=crucero).exists():
        print(f"⚠ Ya existen actividades para el crucero {crucero}, no se agregaron nuevas.")
        return

    actividades = []

    if crucero == "vision":  # Pequeño
        actividades = [
            ("Tour Histórico por la Ciudad Amurallada", "Recorrido guiado por la ciudad amurallada.", 2, 0, 2),
            ("Paseo a Caballo por la costa", "Paseo en caballo frente al mar.", 4, 0, 2),
            ("Tour Terrestre por Salinas y Flamencos", "Excursión en bus por las salinas.", 5, 0, 2),
            ("Tour a pie por Willemstad", "Caminata guiada por la ciudad.", 6, 0, 3),
        ]

    elif crucero == "voyager":  # Mediano
        actividades = [
            ("Excursión a las Islas del Rosario", "Viaje en lancha con almuerzo incluido.", 2, 0, 6),
            ("Excursión de cuatrimoto en la playa", "Tour en cuatrimoto por la playa, solo adultos.", 2, 0, 3),
            ("Jeep al parque nacional Arikok", "Excursión en jeep al parque nacional.", 4, 0, 3),
            ("Paseo a caballo por la costa", "Cabalgata frente al mar con refrigerio.", 4, 0, 2),
            ("Tour terrestre por salinas y flamencos", "Recorrido en bus con paradas fotográficas.", 5, 0, 2),
            ("Paseo en barco con fondo de cristal", "Tour en barco transparente para observar el mar.", 5, 0, 2),
            ("Paseo en catamarán por la costa", "Tour en catamarán con refrigerio incluido.", 6, 0, 4),
            ("Tour a pie por Willemstad", "Recorrido guiado a pie desde el puerto.", 6, 0, 3),
        ]

    elif crucero == "oasis":  # Grande
        actividades = [
            ("Excursión a las Islas del Rosario", "Excursión en lancha con almuerzo incluido.", 2, 0, 7),
            ("Tour Histórico por la Ciudad Amurallada", "Recorrido guiado por la ciudad amurallada.", 2, 0, 2),
            ("Excursión de Cuatrimoto en la playa", "Tour en cuatrimoto por la playa, solo adultos.", 2, 0, 3),
            ("Día de playa con Snorkel y Buceo en el Naufragio de Antilla", "Actividades acuáticas en naufragio.", 4, 0, 6),
            ("Jeep al Parque Nacional Arikok", "Excursión en jeep con refrigerio incluido.", 4, 0, 3),
            ("Paseo a Caballo por la costa", "Cabalgata frente al mar.", 4, 0, 2),
            ("Día de playa con Snorkel y Buceo en el Parque Marino", "Snorkel y buceo en arrecifes.", 5, 0, 6),
            ("Tour Terrestre por Salinas y Flamencos", "Recorrido en bus por las salinas.", 5, 0, 2),
            ("Paseo en Barco con Fondo de Cristal", "Excursión en barco transparente.", 5, 0, 2),
            ("Paseo en Catamarán por la costa", "Tour en catamarán con refrigerio.", 6, 0, 4),
            ("Tour por el Acuario Marino y nado con delfines", "Visita al acuario y experiencia con delfines.", 6, 0, 3),
            ("Tour a pie por Willemstad", "Caminata guiada por la ciudad.", 6, 0, 3),
        ]

    else:
        print("❌ Crucero no válido")
        return

    for nombre, descripcion, dia, precio, duracion in actividades:
        Entretenimiento.objects.create(
            crucero=crucero,   
            nombre=nombre,
            descripcion=descripcion,
            dia=dia,
            precio=precio if precio > 0 else (duracion * 15),  
            reservada=False
        )

    print(f"✅ Actividades de entretenimiento para {crucero} creadas exitosamente.")


def borrar_entretenimiento(crucero):

    eliminadas, _ = Entretenimiento.objects.filter(crucero=crucero).delete()
    print(f"🗑 {eliminadas} actividades de entretenimiento eliminadas del crucero {crucero}.")

