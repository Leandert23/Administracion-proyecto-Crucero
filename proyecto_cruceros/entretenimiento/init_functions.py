from datetime import time
from .models import Actividad, ActividadRutinaria

def actividadPagoInit():
    """
    Función que inicializa la tabla de actividades con datos de ejemplo
    """
    # Verificar si ya existen actividades para evitar duplicados
    if Actividad.objects.exists():
        print("ERROR: La tabla ya contiene actividades. No se crearán datos de ejemplo.")
        return

    # Crear actividades de ejemplo
    actividades_data = [
        {
            "titulo": "Excursión a las Islas del Rosario",
            "descripcion": "Disfruta de un día en el paraíso con un viaje a las famosas Islas del Rosario, un archipiélago conocido por sus playas de arena blanca y aguas cristalinas. La excursión de 7 horas incluye el transporte y el almuerzo.",
            "dia_crucero": 2,
            "coste": 120.00,
            "hora_inicio": time(9, 0),  # 9AM
            "hora_fin": time(16, 0),   #4 PM
            "maximoActividad": 180,
            "img_src": "islasdelrosario.jpg"
        },
        {
            "titulo": "Tour Histórico por la Ciudad Amurallada",
            "descripcion": "Recorre las calles históricas y los muros antiguos de la Ciudad Amurallada de Cartagena. Aprende sobre la historia colonial y la arquitectura de esta impresionante ciudad. Una visita guiada llena de cultura y belleza.",
            "dia_crucero": 2,
            "coste": 60.00,
            "hora_inicio": time(9, 30),  # 9:30 AM
            "hora_fin": time(11, 30),     # 11:30 AM
            "maximoActividad": 90,
            "img_src": "ciudadamurallada.jpg"
        },
        {
            "titulo": "Excursión de Cuatrimoto en la playa",
            "descripcion": "Siente la adrenalina mientras conduces una cuatrimoto a través de la playa. Explora los paisajes costeros de una manera emocionante y divertida. ¡Una aventura para los amantes de la velocidad y la naturaleza!",
            "dia_crucero": 2,
            "coste": 240.00,
            "hora_inicio": time(10, 0), # 10:00
            "hora_fin": time(13, 0),     # 1:00 PM
            "maximoActividad": 90,
            "img_src": "excursioncuatrimoto.jpg"
        }
    ]

    # Crear las actividades en la base de datos
    actividades_creadas = []
    for actividad_data in actividades_data:
        actividad = Actividad.objects.create(**actividad_data)
        actividades_creadas.append(actividad)
        print(f"✓ Creada actividad: {actividad.titulo}")

    print(f"\n🎉 Se han creado {len(actividades_creadas)} actividades exitosamente!")
    return actividades_creadas


def actividadRutInit():
    """
    Función que inicializa la tabla de actividades rutinarias con datos de ejemplo
    """
    # Verificar si ya existen actividades rutinarias para evitar duplicados
    if ActividadRutinaria.objects.exists():
        print("ERROR: La tabla ya contiene actividades rutinarias. No se crearán datos de ejemplo.")
        return

    # Crear actividades rutinarias de ejemplo (actividades diarias del crucero)
    actividades_rutinarias_data = [
        {
            "titulo": "Tour Guiado por el Barco",
            "descripcion": "Disfruta de un delicioso desayuno buffet con una amplia variedad de opciones: frutas frescas, cereales, pastelería, huevos preparados al momento y mucho más. ¡Empieza tu día con energía!",
            "dia_crucero": 1,
            "hora_inicio": time(15, 0),
            "hora_fin": time(16, 0),
            "maximo_actividad": 6000,
            "ubicacion": "Cubierta Principal",
            "img_src": "tourcrucero1.jpg"
        },
        {
            "titulo": "Estiramiento en cubierta.",
            "descripcion": "Comienza tu día con una relajante sesión de yoga en la cubierta superior. Perfecta para estirar el cuerpo y encontrar paz mental mientras disfrutas de las vistas al mar.",
            "dia_crucero": 2,
            "hora_inicio": time(10, 0),   # 8:00 AM
            "hora_fin": time(10, 45),      # 9:00 AM
            "maximo_actividad": 100,
            "ubicacion": "Cubierta Superior",
            "img_src": "estiramientocubierta.jpg"
        },
        {
            "titulo": "Taller de fotografía.",
            "descripcion": "Aprende a capturar los mejores momentos de tus vacaciones. Te daremos consejos y trucos para sacar fotos increíbles.",
            "dia_crucero": 2,
            "hora_inicio": time(10, 45),
            "hora_fin": time(11, 30),
            "maximo_actividad": 80,
            "ubicacion": "Piscina",
            "img_src": "tallerfotografia.jpg"
        }
    ]

    # Crear las actividades rutinarias en la base de datos
    actividades_rutinarias_creadas = []
    for actividad_data in actividades_rutinarias_data:
        actividad_rutinaria = ActividadRutinaria.objects.create(**actividad_data)
        actividades_rutinarias_creadas.append(actividad_rutinaria)
        print(f"✓ Creada actividad rutinaria: {actividad_rutinaria.titulo}")

    print(f"\n🎉 Se han creado {len(actividades_rutinarias_creadas)} actividades rutinarias exitosamente!")
    return actividades_rutinarias_creadas
