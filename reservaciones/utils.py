from .models import Restaurante, Mesa

def rellenar_restaurantes(crucero):

    if Restaurante.objects.filter(crucero=crucero).exists():
        print(f"⚠ Ya existen restaurantes para el crucero {crucero}, no se agregaron nuevos.")
        return

    # cantidad de mesas por crucero
    if crucero.tipo_crucero == "pequeno":
        mesas_por_restaurante = 60
    elif crucero.tipo_crucero == "mediano":
        mesas_por_restaurante = 80
    elif crucero.tipo_crucero == "grande":
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

    if crucero.tipo_crucero == "pequeno":  # Pequeño
        actividades = [
            ("Tour Histórico por la Ciudad Amurallada", "Recorrido guiado por la ciudad amurallada.", 2, 0, 2),
            ("Paseo a Caballo por la costa", "Paseo en caballo frente al mar.", 4, 0, 2),
            ("Tour Terrestre por Salinas y Flamencos", "Excursión en bus por las salinas.", 5, 0, 2),
            ("Tour a pie por Willemstad", "Caminata guiada por la ciudad.", 6, 0, 3),
        ]

    elif crucero.tipo_crucero == "mediano":  # Mediano
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

    elif crucero.tipo_crucero == "grande":  # Grande
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

