from datetime import time
from .models import Actividad, ActividadRutinaria, RegistroActividadPago, RegistroActividadRut
from ..cruceros.models import Viaje

def cargar_actividades_entretenimiento(viaje: Viaje):
    """Carga actividades (pago y rutinarias) asociándolas al viaje según el tipo de crucero.
    Evita duplicados si ya existen para ese viaje. Devuelve dict con listas creadas."""
    crucero = viaje.crucero
    if crucero.tipo_crucero == "pequeno":
        pago = actividadPagoPeqInit(viaje)
        rut = actividadRutPequenoInit(viaje)
    elif crucero.tipo_crucero == "mediano":
        pago = actividadPagoMedianoInit(viaje)
        rut = actividadRutMedianoInit(viaje)
    else:
        pago = actividadPagoGrandeInit(viaje)
        rut = actividadRutGrandeInit(viaje)
    return {"pago": pago, "rutinarias": rut}

def actividadPagoGrandeInit(viaje: Viaje):
    """
    Función que inicializa la tabla de actividades con datos de ejemplo
    """
    # Verificar si ya existen actividades para evitar duplicados
    if Actividad.objects.filter(viaje=viaje).exists():
        return []

    # Crear actividades de ejemplo
    actividades_data = [
        {
            "titulo": "Excursión a las Islas del Rosario",
            "descripcion": "Disfruta de un día en el paraíso con un viaje a las famosas Islas del Rosario, un archipiélago conocido por sus playas de arena blanca y aguas cristalinas. La excursión de 7 horas incluye el transporte y el almuerzo.",
            "dia_crucero":2,
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
            "img_src": "ciudadmuralla.jpg"
        },
        {
            "titulo": "Excursión de Cuatrimoto en la playa",
            "descripcion": "Siente la adrenalina mientras conduces una cuatrimoto a través de la playa. Explora los paisajes costeros de una manera emocionante y divertida. ¡Una aventura para los amantes de la velocidad y la naturaleza!",
            "dia_crucero":2,
            "coste": 240.00,
            "hora_inicio": time(10, 0), # 10:00
            "hora_fin": time(13, 0),     # 1:00 PM
            "maximoActividad": 90,
            "img_src": "excursioncuatrimoto.jpg"
        },
        {
            "titulo": "Día de playa con Snorkel y Buceo en el Naufragio de Antilla",
            "descripcion": "Disfruta de un día de sol y mar en una playa paradisíaca. La actividad incluye una experiencia de snorkel y buceo para explorar el famoso Naufragio de Antilla, un tesoro sumergido lleno de vida marina. ¡Una aventura inolvidable bajo el agua!",
            "dia_crucero": 4,
            "coste": 95.00,
            "hora_inicio": time(9, 0),
            "hora_fin": time(15, 0),
            "maximoActividad": 25,
            "img_src": "naufragioantilla.jpg"
        },
        {
            "titulo": "Jeep al Parque Nacional Arikok",
            "descripcion": "Embárcate en una emocionante aventura en jeep por el Parque Nacional Arikok. Descubre los paisajes áridos, las formaciones rocosas y las cuevas escondidas de este impresionante parque natural. Una experiencia ideal para los amantes de la naturaleza y la aventura.",
            "dia_crucero": 4,
            "coste": 75.00,
            "hora_inicio": time(9, 30),
            "hora_fin": time(12, 30),
            "maximoActividad": 18,
            "img_src": "parquenacionalarikok.jpg"
        },
        {
            "titulo": "Paseo a Caballo por la costa",
            "descripcion": "Disfruta de un tranquilo y pintoresco paseo a caballo a lo largo de la costa. Admira las vistas panorámicas del océano mientras cabalgas por la orilla. Una actividad relajante y memorable para todos los niveles de jinetes.",
            "dia_crucero": 4,
            "coste": 60.00,
            "hora_inicio": time(10, 0),
            "hora_fin": time(12, 0),
            "maximoActividad": 10,
            "img_src": "paseocaballo.jpg"
        },
        {
            "titulo": "Día de playa con Snorkel y Buceo en el Parque Marino",
            "descripcion": "Disfruta de un día de relajación en la playa y exploración submarina en un hermoso parque marino. Practica snorkel y buceo para descubrir la colorida vida marina y los arrecifes de coral. Una experiencia acuática ideal para todas las edades.",
            "dia_crucero": 5,
            "coste": 105.00,
            "hora_inicio": time(9, 0),
            "hora_fin": time(15, 0),
            "maximoActividad": 30,
            "img_src": "snorkelbonaire.jpg"
        },
        {
            "titulo": "Tour Terrestre por Salinas y Flamencos",
            "descripcion": "Explora los fascinantes paisajes de salinas y admira las colonias de flamencos en su hábitat natural. Este tour terrestre te llevará a través de un ecosistema único, perfecto para la fotografía y la observación de aves. ¡No olvides tu cámara!",
            "dia_crucero": 5,
            "coste": 65.00,
            "hora_inicio": time(9, 30),
            "hora_fin": time(11, 30),
            "maximoActividad": 20,
            "img_src": "salinas.jpg"
        },
        {
            "titulo": "Paseo en Barco con Fondo de Cristal",
            "descripcion": "Observa el mundo submarino sin mojarte en un emocionante paseo en barco con fondo de cristal. Podrás ver peces tropicales, corales y otras especies marinas a través del suelo transparente de la embarcación. Una actividad ideal para toda la familia.",
            "dia_crucero": 5,
            "coste": 55.00,
            "hora_inicio": time(11, 30),
            "hora_fin": time(13, 30),
            "maximoActividad": 45,
            "img_src": "paseobarcocristal.jpg"
        },
        {
            "titulo": "Paseo en catamaran por la costa",
            "descripcion": "Disfruta de un paseo en catamaran por la costa. Podrás disfrutar de las vistas al mar y del sol mientras navegas por la costa.",
            "dia_crucero": 6,
            "coste": 55.00,
            "hora_inicio": time(9, 30),
            "hora_fin": time(13, 30),
            "maximoActividad": 45,
            "img_src": "catamaran.jpg"
        },
        {
            "titulo": "Tour por el acuario marino y nado con delfines",
            "descripcion": "Disfruta de un tour por el acuario marino de Curacao y nado con delfines. Podrás disfrutar de las vistas al mar y del sol mientras navegas por la costa.",
            "dia_crucero": 6,
            "coste": 55.00,
            "hora_inicio": time(9, 30),
            "hora_fin": time(13, 30),
            "maximoActividad": 45,
            "img_src": "acuariocurazao.jpg"
        },
        {
            "titulo": "Tour por Willemstad",
            "descripcion": "Disfruta de un tour por Willemstad. Podrás disfrutar de las vistas al mar y del sol mientras navegas por la costa.",
            "dia_crucero": 6,
            "coste": 55.00,
            "hora_inicio": time(9, 30),
            "hora_fin": time(13, 30),
            "maximoActividad": 45,
            "img_src": "willemstad.jpg"
        }
    ]

    # Crear las actividades en la base de datos
    actividades_creadas = []
    for actividad_data in actividades_data:
        actividad = Actividad.objects.create(viaje=viaje, **actividad_data)
        actividades_creadas.append(actividad)
    
    return actividades_creadas

def actividadRutMedianoInit(viaje: Viaje):
    """
    Función que inicializa la tabla de actividades rutinarias con datos de ejemplo
    """
    # Verificar si ya existen actividades rutinarias para este viaje
    if ActividadRutinaria.objects.filter(viaje=viaje).exists():
        return []

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
            "titulo": "Espectáculo de entretenimiento en el teatro (circo).",
            "descripcion": "Prepárate para un show increíble en el teatro principal con artistas de circo, acrobacias asombrosas y efectos especiales.",
            "dia_crucero": 1,
            "hora_inicio": time(20, 0), # 7:30 PM
            "hora_fin": time(21, 0),     # 10:00 PM
            "maximo_actividad": 350,
            "ubicacion": "Teatro Principal",
            "img_src": "espectaculomagiacrucero.jpg"
        },
        {
            "titulo": "Welcome Aboard Show en la discoteca para presentar a los artistas.",
            "descripcion": "Descubre a los increíbles artistas que te acompañarán durante el viaje. Música, baile y presentaciones en un ambiente vibrante.",
            "dia_crucero": 1,
            "hora_inicio": time(21, 0),
            "hora_fin": time(23, 0),     # 11:00 PM
            "maximo_actividad": 600,
            "ubicacion": "Discoteca",
            "img_src": "teatrodia1.jpg"
        },
        {
            "titulo": "Yoga en cubierta.",
            "descripcion": "Comienza tu día con una relajante sesión de yoga en la cubierta superior. Perfecta para estirar el cuerpo y encontrar paz mental mientras disfrutas de las vistas al mar.",
            "dia_crucero": 2,
            "hora_inicio": time(10, 0),   # 8:00 AM
            "hora_fin": time(10, 45),      # 9:00 AM
            "maximo_actividad": 100,
            "ubicacion": "Cubierta Superior",
            "img_src": "estiramientocubierta.jpg"
        },

        {
            "titulo": "Ambientación del País (Colombia) en la piscina. ",
            "descripcion": "Sumergete en una fiesta en la piscina con música y decoración colombiana. Baila al ritmo de la cumbia y el vallenato mientras disfrutas del sol.",
            "dia_crucero": 2,
            "hora_inicio": time(11, 30),  # 6:00 PM
            "hora_fin": time(14, 0),     # 8:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Piscina",
            "img_src": "fiestalatina.jpg"
        },
        {
            "titulo": "Happy hour en discoteca con música regional.",
            "descripcion": "Disfruta de la mejor música regional, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la discoteca del crucero.",
            "dia_crucero": 3,
            "hora_inicio": time(15, 0),
            "hora_fin": time(17, 0),
            "maximo_actividad": 200,
            "ubicacion": "Discoteca",
            "img_src": "happyhourdisco1.jpg"
        },
        {
            "titulo": "Torneo de voleibol en la piscina.",
            "descripcion": "Compite con otros pasajeros en un emocionante torneo de voleibol acuático. ¡Diversión, risas y sol garantizados mientras juegas en la piscina!",
            "dia_crucero": 2,
            "hora_inicio": time(16, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 40,
            "ubicacion": "Piscina",
            "img_src": "volleyballcrucero.jpg"
        },
        {
            "titulo": "Espectáculo de magia en el teatro.",
            "descripcion": "¡Descubre cómo magia y ilusiones pueden fascinar a cualquier persona! Un espectáculo lleno de misterio y emoción en el teatro principal.",
            "dia_crucero": 2,
            "hora_inicio": time(20, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 500,
            "ubicacion": "Teatro",
            "img_src": "espectaculomagiacrucero.jpg"
        },
        {
            "titulo": "Fiesta latina en la discoteca.",
            "descripcion": "Disfruta de la mejor música latina, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la discoteca del crucero.",
            "dia_crucero": 2,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Discoteca",
            "img_src": "fiestalatinaDisco.jpg"
        },

        {
            "titulo": "Caminata grupal en la cubierta.",
            "descripcion": "Unete a nuestros instructores para una caminata grupal en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 3,
            "hora_inicio": time(10, 0),  # 2:00 PM
            "hora_fin": time(11, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "caminatacubierta.jpg"
        },
        {
            "titulo": "Bingo en piscina",
            "descripcion": "¡Diviértete y gana premios en nuestro emocionante bingo en la piscina! Compite con otros pasajeros para ganar precios exclusivos mientras disfrutas de la adrenalina de las ruedas y las emocionantes actividades en la piscina.",
            "dia_crucero": 3,
            "hora_inicio": time(11, 0),  # 2:00 PM
            "hora_fin": time(13, 0),     # 4:00 PM
            "maximo_actividad": 200,
            "ubicacion": "Piscina",
            "img_src": "bingopiscina.jpg"
        },
        {
            "titulo": "Karaoke.",
            "descripcion": "¡Diviértete cantando con otros pasajeros en nuestro emocionante karaoke en la cubierta! Compite con otros viajeros para ganar precios exclusivos mientras disfrutas de la adrenalina de las ruedas y las emocionantes actividades en la piscina.",
            "dia_crucero": 3,
            "hora_inicio": time(16, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Cubierta Superior",
            "img_src": "karaokecrucero.jpg"
        },
        {
            "titulo": "Cata de quesos.",
            "descripcion": "Disfruta de una variedad de quesos de todo el mundo. ¡Un evento exclusivo para los amantes de la gastronomía!",
            "dia_crucero": 3,
            "hora_inicio": time(17, 0),  # 2:00 PM
            "hora_fin": time(18, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Buffet Principal",
            "img_src": "cataquesos.jpg"
        },
        {
            "titulo": "Espectáculo de comedia en el teatro.",
            "descripcion": "Disfruta de un espectáculo de comedia en el teatro. ¡Un evento exclusivo para los amantes de la comedia!",
            "dia_crucero": 3,
            "hora_inicio": time(20, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 500,
            "ubicacion": "Teatro",
            "img_src": "comediateatro.jpg"
        },
        {
            "titulo": "Discoteca abierta.",
            "descripcion": "Disfruta de la mejor música, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la discoteca del crucero.",
            "dia_crucero": 3,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Discoteca",
            "img_src": "discotecacrucero.jpg"
        },
        {
            "titulo": "Clase de aerobics",
            "descripcion": "Disfruta de una clase de aerobics en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 4,
            "hora_inicio": time(10, 0),  # 2:00 PM
            "hora_fin": time(11, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Piscina",
            "img_src": "clasesaerobics.jpg"
        },
        {
            "titulo": "Animadores en la piscina.",
            "descripcion": "Disfruta de animadores en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 4,
            "hora_inicio": time(12, 0),  # 2:00 PM
            "hora_fin": time(13, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Piscina",
            "img_src": "animadorespiscina.jpg"
        },
        {
            "titulo": "Zumba en la piscina.",
            "descripcion": "Disfruta de una clase de zumba en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 4,
            "hora_inicio": time(16, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Piscina",
            "img_src": "zumbapiscina.jpg"
        },
        {
            "titulo": "Torneo de Waterpolo.",
            "descripcion": "Compite con otros pasajeros en un emocionante torneo de waterpolo. ¡Diversión, risas y sol garantizados mientras juegas en la piscina!",
            "dia_crucero": 4,
            "hora_inicio": time(17, 0),  # 2:00 PM
            "hora_fin": time(18, 0),     # 4:00 PM
            "maximo_actividad": 80,
            "ubicacion": "Piscina",
            "img_src": "waterpolopiscina.jpg"
        },
        {
            "titulo": "Show de tambores en cubierta o piscina. ",
            "descripcion": "Disfruta de un espectáculo de tambores en la cubierta o piscina. ¡Un evento exclusivo para los amantes de la música!",
            "dia_crucero": 4,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(22, 0),     # 4:00 PM
            "maximo_actividad": 600,
            "ubicacion": "Cubierta Superior",
            "img_src": "showtambores.jpg"
        },
        {
            "titulo": "Fiesta con temática caribeña en la discoteca.",
            "descripcion": "Disfruta de la mejor música caribeña, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la discoteca del crucero.",
            "dia_crucero": 4,
            "hora_inicio": time(22, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Discoteca",
            "img_src": "fiestalatinaDisco.jpg"
        },
        {
            "titulo": "Clases de entrenamiento funcional.",
            "descripcion": "Disfruta de una clase de entrenamiento funcional en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(10, 0),  # 2:00 PM
            "hora_fin": time(11, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Cubierta Superior",
            "img_src": "funcionales.jpg"
        },
        {
            "titulo": "Rifa de premios variados.",
            "descripcion": "Disfruta de una rifa de premios variados en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(11, 0),  # 2:00 PM
            "hora_fin": time(12, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Cubierta Superior",
            "img_src": "rifa.jpg"
        },
        {
            "titulo": "Quién quiere ser millonario",
            "descripcion": "Disfruta de un juego de preguntas y respuestas en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(16, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Piscina",
            "img_src": "quienquieresermillonario.jpg"
        },
        {
            "titulo": "Competencia de bailes.",
            "descripcion": "Disfruta de un torneo de bailes en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(17, 0),  # 2:00 PM
            "hora_fin": time(18, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Piscina",
            "img_src": "clasedebaile.jpg"
        },
        {
            "titulo": "Concurso de talentos en cubierta.",
            "descripcion": "Disfruta de un espectáculo de talentos en la cubierta o piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(20, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 500,
            "ubicacion": "Cubierta Superior",
            "img_src": "concursotalentos.jpg"
        },
        {
            "titulo": "Fiesta Silent Disco",
            "descripcion": "Disfruta de la mejor música, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la piscina del crucero.",
            "dia_crucero": 5,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 1000,
            "ubicacion": "Piscina",
            "img_src": "silentparty.jpg"
        },
        {
            "titulo": "Clases de Tai Chi.",
            "descripcion": "Disfruta de un clase de tai chi en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(10, 0),  # 2:00 PM
            "hora_fin": time(11, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "taichi.jpg"
        },
        {
            "titulo": "Clases de respiración y mindfulness.",
            "descripcion": "Disfruta de un clase de respiración y mindfulness en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(11, 30),  # 2:00 PM
            "hora_fin": time(12, 30),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "yogacrucero.jpg"
        },
        {
            "titulo": "Taller y show de coctelería variada.",
            "descripcion": "Disfruta de un taller y show de coctelería variada en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(15, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Piscina",
            "img_src": "showcocteleria.jpg"
        },
        {
            "titulo": "Happy hour en la discoteca.",
            "descripcion": "Disfruta de un happy hour en la discoteca. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(17, 0),  # 2:00 PM
            "hora_fin": time(18, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Discoteca",
            "img_src": "happyhourdisco1.jpg"
        },
        {
            "titulo": "Cena con el capitán.",
            "descripcion": "Disfruta de un cena con el capitán en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(19, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 6000,
            "ubicacion": "Restaurante Principal",
            "img_src": "capitancrucero.jpg"
        },
        {
            "titulo": "Fiesta glow con temática Neon.",
            "descripcion": "Disfruta de un fiesta glow con temática Neon en la discoteca. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 800,
            "ubicacion": "Discoteca",
            "img_src": "fiestaglow.jpg"
        },
        {
            "titulo": "Taller de pintura rápida de paisajes.",
            "descripcion": "Disfruta de un taller de pintura rápida de paisajes en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(9, 0),  # 2:00 PM
            "hora_fin": time(10, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "tallerpinturarapida.jpg"
        },
        {
            "titulo": "Bingo en la piscina.",
            "descripcion": "Disfruta de un bingo en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(10, 0),  # 2:00 PM
            "hora_fin": time(11, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Piscina",
            "img_src": "bingopiscina.jpg"
        },
        {
            "titulo": "Family feud en el teatro.",
            "descripcion": "Disfruta de un family feud en el teatro. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(15, 0),  # 2:00 PM
            "hora_fin": time(16, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Teatro",
            "img_src": "familyfeud.jpg"
        },
        {
            "titulo": "Competencia de mímica en equipos en la piscina.",
            "descripcion": "Disfruta de un competencia de mímica en equipos en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(17, 0),  # 2:00 PM
            "hora_fin": time(18, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Piscina",
            "img_src": "competenciacharadas.jpg"
        },
        {
            "titulo": "Espectáculo de magia en el teatro.",
            "descripcion": "Disfruta de un espectáculo de magia en el teatro. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(20, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Teatro",
            "img_src": "espectaculomagiacrucero.jpg"
        },
        {
            "titulo": "Fiesta de los años 80/90.",
            "descripcion": "Disfruta de un fiesta de los años 80/90 en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 1500,
            "ubicacion": "Discoteca",
            "img_src": "fiestalatinaDisco.jpg"
        },
        {
            "titulo": "Desembarque",
            "descripcion": "El equipo de excursiones y animadores asisten a los pasajeros durante el proceso de salida.",
            "dia_crucero": 8,
            "hora_inicio": time(8, 0),  # 2:00 PM
            "hora_fin": time(13, 0),     # 4:00 PM
            "maximo_actividad": 6000,
            "ubicacion": "Barco",
            "img_src": "tourcrucero1.jpg"
        }
    ]

    # Crear las actividades rutinarias en la base de datos
    actividades_rutinarias_creadas = []
    for actividad_data in actividades_rutinarias_data:
        actividad_rutinaria = ActividadRutinaria.objects.create(viaje=viaje, **actividad_data)
        actividades_rutinarias_creadas.append(actividad_rutinaria)
    return actividades_rutinarias_creadas

def actividadPagoPeqInit(viaje: Viaje):
    """
    Función que inicializa la tabla de actividades con datos de ejemplo
    """
    # Verificar si ya existen actividades para evitar duplicados
    if Actividad.objects.filter(viaje=viaje).exists():
        return []

    # Crear actividades de ejemplo
    actividades_data = [
        {
            "titulo": "Tour Histórico por la Ciudad Amurallada",
            "descripcion": "Recorre las calles históricas y los muros antiguos de la Ciudad Amurallada de Cartagena. Aprende sobre la historia colonial y la arquitectura de esta impresionante ciudad. Una visita guiada llena de cultura y belleza.",
            "dia_crucero": 2,
            "coste": 60.00,
            "hora_inicio": time(9, 30),  # 9:30 AM
            "hora_fin": time(11, 30),     # 11:30 AM
            "maximoActividad": 90,
            "img_src": "ciudadmuralla.jpg"
        },
        {
            "titulo": "Paseo a Caballo por la costa",
            "descripcion": "Disfruta de un tranquilo y pintoresco paseo a caballo a lo largo de la costa. Admira las vistas panorámicas del océano mientras cabalgas por la orilla. Una actividad relajante y memorable para todos los niveles de jinetes.",
            "dia_crucero": 4,
            "coste": 60.00,
            "hora_inicio": time(10, 0),
            "hora_fin": time(12, 0),
            "maximoActividad": 10,
            "img_src": "paseocaballo.jpg"
        },
        {
            "titulo": "Tour Terrestre por Salinas y Flamencos",
            "descripcion": "Explora los fascinantes paisajes de salinas y admira las colonias de flamencos en su hábitat natural. Este tour terrestre te llevará a través de un ecosistema único, perfecto para la fotografía y la observación de aves. ¡No olvides tu cámara!",
            "dia_crucero": 5,
            "coste": 65.00,
            "hora_inicio": time(9, 30),
            "hora_fin": time(11, 30),
            "maximoActividad": 20,
            "img_src": "salinas.jpg"
        },
        {
            "titulo": "Tour por Willemstad",
            "descripcion": "Disfruta de un tour por Willemstad. Podrás disfrutar de las vistas al mar y del sol mientras navegas por la costa.",
            "dia_crucero": 6,
            "coste": 55.00,
            "hora_inicio": time(9, 30),
            "hora_fin": time(13, 30),
            "maximoActividad": 45,
            "img_src": "willemstad.jpg"
        } 
    ]

    # Crear las actividades en la base de datos
    actividades_creadas = []
    for actividad_data in actividades_data:
        actividad = Actividad.objects.create(viaje=viaje, **actividad_data)
        actividades_creadas.append(actividad)
    return actividades_creadas

def actividadPagoMedianoInit(viaje: Viaje):
    """
    Función que inicializa la tabla de actividades con datos de ejemplo
    """
    # Verificar si ya existen actividades para evitar duplicados
    if Actividad.objects.filter(viaje=viaje).exists():
        return []

    # Crear actividades de ejemplo
    actividades_data = [
        {
            "titulo": "Excursión a las Islas del Rosario",
            "descripcion": "Disfruta de un día en el paraíso con un viaje a las famosas Islas del Rosario, un archipiélago conocido por sus playas de arena blanca y aguas cristalinas. La excursión de 7 horas incluye el transporte y el almuerzo.",
            "dia_crucero":2,
            "coste": 120.00,
            "hora_inicio": time(9, 0),  # 9AM
            "hora_fin": time(16, 0),   #4 PM
            "maximoActividad": 180,
            "img_src": "islasdelrosario.jpg"
        },
        {
            "titulo": "Excursión de Cuatrimoto en la playa",
            "descripcion": "Siente la adrenalina mientras conduces una cuatrimoto a través de la playa. Explora los paisajes costeros de una manera emocionante y divertida. ¡Una aventura para los amantes de la velocidad y la naturaleza!",
            "dia_crucero":2,
            "coste": 240.00,
            "hora_inicio": time(10, 0), # 10:00
            "hora_fin": time(13, 0),     # 1:00 PM
            "maximoActividad": 90,
            "img_src": "excursioncuatrimoto.jpg"
        },
        {
            "titulo": "Jeep al Parque Nacional Arikok",
            "descripcion": "Embárcate en una emocionante aventura en jeep por el Parque Nacional Arikok. Descubre los paisajes áridos, las formaciones rocosas y las cuevas escondidas de este impresionante parque natural. Una experiencia ideal para los amantes de la naturaleza y la aventura.",
            "dia_crucero": 4,
            "coste": 75.00,
            "hora_inicio": time(9, 30),
            "hora_fin": time(12, 30),
            "maximoActividad": 18,
            "img_src": "parquenacionalarikok.jpg"
        },
        {
            "titulo": "Paseo a Caballo por la costa",
            "descripcion": "Disfruta de un tranquilo y pintoresco paseo a caballo a lo largo de la costa. Admira las vistas panorámicas del océano mientras cabalgas por la orilla. Una actividad relajante y memorable para todos los niveles de jinetes.",
            "dia_crucero": 4,
            "coste": 60.00,
            "hora_inicio": time(10, 0),
            "hora_fin": time(12, 0),
            "maximoActividad": 10,
            "img_src": "paseocaballo.jpg"
        },
        {
            "titulo": "Tour Terrestre por Salinas y Flamencos",
            "descripcion": "Explora los fascinantes paisajes de salinas y admira las colonias de flamencos en su hábitat natural. Este tour terrestre te llevará a través de un ecosistema único, perfecto para la fotografía y la observación de aves. ¡No olvides tu cámara!",
            "dia_crucero": 5,
            "coste": 65.00,
            "hora_inicio": time(9, 30),
            "hora_fin": time(11, 30),
            "maximoActividad": 20,
            "img_src": "salinas.jpg"
        },
        {
            "titulo": "Paseo en Barco con Fondo de Cristal",
            "descripcion": "Observa el mundo submarino sin mojarte en un emocionante paseo en barco con fondo de cristal. Podrás ver peces tropicales, corales y otras especies marinas a través del suelo transparente de la embarcación. Una actividad ideal para toda la familia.",
            "dia_crucero": 5,
            "coste": 55.00,
            "hora_inicio": time(11, 30),
            "hora_fin": time(13, 30),
            "maximoActividad": 45,
            "img_src": "paseobarcocristal.jpg"
        },
        {
            "titulo": "Tour por Willemstad",
            "descripcion": "Disfruta de un tour por Willemstad. Podrás disfrutar de las vistas al mar y del sol mientras navegas por la costa.",
            "dia_crucero": 6,
            "coste": 55.00,
            "hora_inicio": time(9, 30),
            "hora_fin": time(13, 30),
            "maximoActividad": 45,
            "img_src": "willemstad.jpg"
        },
        {
            "titulo": "Paseo en catamaran por la costa",
            "descripcion": "Disfruta de un paseo en catamaran por la costa. Podrás disfrutar de las vistas al mar y del sol mientras navegas por la costa.",
            "dia_crucero": 6,
            "coste": 55.00,
            "hora_inicio": time(9, 30),
            "hora_fin": time(13, 30),
            "maximoActividad": 45,
            "img_src": "catamaran.jpg"
        } 
    ]

    # Crear las actividades en la base de datos
    actividades_creadas = []
    for actividad_data in actividades_data:
        actividad = Actividad.objects.create(viaje=viaje, **actividad_data)
        actividades_creadas.append(actividad)
    return actividades_creadas

def actividadRutGrandeInit(viaje: Viaje):
    """
    Función que inicializa la tabla de actividades rutinarias con datos de ejemplo
    """
    # Verificar si ya existen actividades rutinarias para este viaje
    if ActividadRutinaria.objects.filter(viaje=viaje).exists():
        return []

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
            "titulo": "Espectáculo de entretenimiento en el teatro (circo).",
            "descripcion": "Prepárate para un show increíble en el teatro principal con artistas de circo, acrobacias asombrosas y efectos especiales.",
            "dia_crucero": 1,
            "hora_inicio": time(20, 0), # 7:30 PM
            "hora_fin": time(21, 0),     # 10:00 PM
            "maximo_actividad": 350,
            "ubicacion": "Teatro Principal",
            "img_src": "espectaculomagiacrucero.jpg"
        },
        {
            "titulo": "Welcome Aboard Show en la discoteca para presentar a los artistas.",
            "descripcion": "Descubre a los increíbles artistas que te acompañarán durante el viaje. Música, baile y presentaciones en un ambiente vibrante.",
            "dia_crucero": 1,
            "hora_inicio": time(21, 0),
            "hora_fin": time(23, 0),     # 11:00 PM
            "maximo_actividad": 600,
            "ubicacion": "Discoteca",
            "img_src": "teatrodia1.jpg"
        },
        {
            "titulo": "Yoga en cubierta.",
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
        },
        {
            "titulo": "Ambientación del País (Colombia) en la piscina. ",
            "descripcion": "Sumergete en una fiesta en la piscina con música y decoración colombiana. Baila al ritmo de la cumbia y el vallenato mientras disfrutas del sol.",
            "dia_crucero": 2,
            "hora_inicio": time(11, 30),  # 6:00 PM
            "hora_fin": time(14, 0),     # 8:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Piscina",
            "img_src": "fiestalatina.jpg"
        },
        {
            "titulo": "Happy hour en discoteca con música regional.",
            "descripcion": "Disfruta de la mejor música regional, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la discoteca del crucero.",
            "dia_crucero": 3,
            "hora_inicio": time(15, 0),
            "hora_fin": time(17, 0),
            "maximo_actividad": 200,
            "ubicacion": "Discoteca",
            "img_src": "happyhourdisco1.jpg"
        },
        {
            "titulo": "Clase de baile latino",
            "descripcion": "Aprende los pasos básicos de la salsa, bachata, vallenato y otros ritmos latinos. ¡Diviértete y presume de tus nuevos movimientos en la pista!",
            "dia_crucero": 2,
            "hora_inicio": time(14, 00),
            "hora_fin": time(15, 0),
            "maximo_actividad": 150,
            "ubicacion": "Piscina",
            "img_src": "clasedebaile.jpg"
        },
        {
            "titulo": "Torneo de voleibol en la piscina.",
            "descripcion": "Compite con otros pasajeros en un emocionante torneo de voleibol acuático. ¡Diversión, risas y sol garantizados mientras juegas en la piscina!",
            "dia_crucero": 2,
            "hora_inicio": time(16, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 40,
            "ubicacion": "Piscina",
            "img_src": "volleyballcrucero.jpg"
        },
        {
            "titulo": "Espectáculo de magia en el teatro.",
            "descripcion": "¡Descubre cómo magia y ilusiones pueden fascinar a cualquier persona! Un espectáculo lleno de misterio y emoción en el teatro principal.",
            "dia_crucero": 2,
            "hora_inicio": time(20, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 500,
            "ubicacion": "Teatro",
            "img_src": "espectaculomagiacrucero.jpg"
        },
        {
            "titulo": "Fiesta latina en la discoteca.",
            "descripcion": "Disfruta de la mejor música latina, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la discoteca del crucero.",
            "dia_crucero": 2,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Discoteca",
            "img_src": "fiestalatinaDisco.jpg"
        },
        {
            "titulo": "Clase de yoga en piscina.",
            "descripcion": "Comienza tu día con una relajante sesión de yoga en la piscina. Perfecta para estirar el cuerpo y encontrar paz mental mientras disfrutas de las vistas al mar.",
            "dia_crucero": 3,
            "hora_inicio": time(9, 0),  # 2:00 PM
            "hora_fin": time(10, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Piscina",
            "img_src": "yogacrucero.jpg"
        },
        {
            "titulo": "Caminata grupal en la cubierta.",
            "descripcion": "Unete a nuestros instructores para una caminata grupal en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 3,
            "hora_inicio": time(10, 0),  # 2:00 PM
            "hora_fin": time(11, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "caminatacubierta.jpg"
        },
        {
            "titulo": "Bingo en piscina",
            "descripcion": "¡Diviértete y gana premios en nuestro emocionante bingo en la piscina! Compite con otros pasajeros para ganar precios exclusivos mientras disfrutas de la adrenalina de las ruedas y las emocionantes actividades en la piscina.",
            "dia_crucero": 3,
            "hora_inicio": time(11, 0),  # 2:00 PM
            "hora_fin": time(13, 0),     # 4:00 PM
            "maximo_actividad": 200,
            "ubicacion": "Piscina",
            "img_src": "bingopiscina.jpg"
        },
        {
            "titulo": "Torneo de ping-pong.",
            "descripcion": "Compite con otros pasajeros en un emocionante torneo de ping-pong. ¡Diversión, risas y sol garantizados mientras juegas en la piscina!",
            "dia_crucero": 3,
            "hora_inicio": time(16, 0),  # 2:00 PM
            "hora_fin": time(18, 0),     # 4:00 PM
            "maximo_actividad": 90,
            "ubicacion": "Cubierta Superior",
            "img_src": "pingpongcrucero.jpg"
        },
        {
            "titulo": "Karaoke.",
            "descripcion": "¡Diviértete cantando con otros pasajeros en nuestro emocionante karaoke en la cubierta! Compite con otros viajeros para ganar precios exclusivos mientras disfrutas de la adrenalina de las ruedas y las emocionantes actividades en la piscina.",
            "dia_crucero": 3,
            "hora_inicio": time(16, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Cubierta Superior",
            "img_src": "karaokecrucero.jpg"
        },
        {
            "titulo": "Cata de quesos.",
            "descripcion": "Disfruta de una variedad de quesos de todo el mundo. ¡Un evento exclusivo para los amantes de la gastronomía!",
            "dia_crucero": 3,
            "hora_inicio": time(17, 0),  # 2:00 PM
            "hora_fin": time(18, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Buffet Principal",
            "img_src": "cataquesos.jpg"
        },
        {
            "titulo": "Espectáculo de comedia en el teatro.",
            "descripcion": "Disfruta de un espectáculo de comedia en el teatro. ¡Un evento exclusivo para los amantes de la comedia!",
            "dia_crucero": 3,
            "hora_inicio": time(20, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 500,
            "ubicacion": "Teatro",
            "img_src": "comediateatro.jpg"
        },
        {
            "titulo": "Discoteca abierta.",
            "descripcion": "Disfruta de la mejor música, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la discoteca del crucero.",
            "dia_crucero": 3,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Discoteca",
            "img_src": "discotecacrucero.jpg"
        },
        {
            "titulo": "Sesión de meditación con vista al mar.",
            "descripcion": "Disfruta de una sesión de meditación con vista al mar. Perfecta para encontrar paz mental y disfrutar de las vistas al mar.",
            "dia_crucero": 4,
            "hora_inicio": time(9, 0),  # 2:00 PM
            "hora_fin": time(10, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "meditacionencubierta.jpg"
        },
        {
            "titulo": "Clase de aerobics",
            "descripcion": "Disfruta de una clase de aerobics en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 4,
            "hora_inicio": time(10, 0),  # 2:00 PM
            "hora_fin": time(11, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Piscina",
            "img_src": "clasesaerobics.jpg"
        },
        {
            "titulo": "Animadores en la piscina.",
            "descripcion": "Disfruta de animadores en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 4,
            "hora_inicio": time(12, 0),  # 2:00 PM
            "hora_fin": time(13, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Piscina",
            "img_src": "animadorespiscina.jpg"
        },
        {
            "titulo": "Cata de licores.",
            "descripcion": "Disfruta de una variedad de licores de todo el mundo. ¡Un evento exclusivo para los amantes de la gastronomía!",
            "dia_crucero": 4,
            "hora_inicio": time(15, 0),  # 2:00 PM
            "hora_fin": time(16, 0),     # 4:00 PM
            "maximo_actividad": 200,
            "ubicacion": "Discoteca",
            "img_src": "catalicores.jpg"
        },
        {
            "titulo": "Zumba en la piscina.",
            "descripcion": "Disfruta de una clase de zumba en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 4,
            "hora_inicio": time(16, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Piscina",
            "img_src": "zumbapiscina.jpg"
        },
        {
            "titulo": "Torneo de Waterpolo.",
            "descripcion": "Compite con otros pasajeros en un emocionante torneo de waterpolo. ¡Diversión, risas y sol garantizados mientras juegas en la piscina!",
            "dia_crucero": 4,
            "hora_inicio": time(17, 0),  # 2:00 PM
            "hora_fin": time(18, 0),     # 4:00 PM
            "maximo_actividad": 80,
            "ubicacion": "Piscina",
            "img_src": "waterpolopiscina.jpg"
        },
        {
            "titulo": "Show de tambores en cubierta o piscina. ",
            "descripcion": "Disfruta de un espectáculo de tambores en la cubierta o piscina. ¡Un evento exclusivo para los amantes de la música!",
            "dia_crucero": 4,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(22, 0),     # 4:00 PM
            "maximo_actividad": 600,
            "ubicacion": "Cubierta Superior",
            "img_src": "showtambores.jpg"
        },
        {
            "titulo": "Fiesta con temática caribeña en la discoteca.",
            "descripcion": "Disfruta de la mejor música caribeña, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la discoteca del crucero.",
            "dia_crucero": 4,
            "hora_inicio": time(22, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Discoteca",
            "img_src": "fiestalatinaDisco.jpg"
        },
        {
            "titulo": "Sesión de fotos en cubierta.",
            "descripcion": "Disfruta de una sesión de fotos en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(9, 0),  # 2:00 PM
            "hora_fin": time(10, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "tallerfotografia.jpg"
        },
        {
            "titulo": "Clases de entrenamiento funcional.",
            "descripcion": "Disfruta de una clase de entrenamiento funcional en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(10, 0),  # 2:00 PM
            "hora_fin": time(11, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Cubierta Superior",
            "img_src": "funcionales.jpg"
        },
        {
            "titulo": "Rifa de premios variados.",
            "descripcion": "Disfruta de una rifa de premios variados en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(11, 0),  # 2:00 PM
            "hora_fin": time(12, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Cubierta Superior",
            "img_src": "rifa.jpg"
        },
        {
            "titulo": "Taller de caricaturas o dibujos humorísticos.",
            "descripcion": "Disfruta de un taller de caricaturas o dibujos humorísticos en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(15, 0),  # 2:00 PM
            "hora_fin": time(16, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Cubierta Superior",
            "img_src": "tallercaricatura.jpg"
        },
        {
            "titulo": "Quién quiere ser millonario",
            "descripcion": "Disfruta de un juego de preguntas y respuestas en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(16, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Piscina",
            "img_src": "quienquieresermillonario.jpg"
        },
        {
            "titulo": "Competencia de bailes.",
            "descripcion": "Disfruta de un torneo de bailes en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(17, 0),  # 2:00 PM
            "hora_fin": time(18, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Piscina",
            "img_src": "clasedebaile.jpg"
        },
        {
            "titulo": "Concurso de talentos en cubierta.",
            "descripcion": "Disfruta de un espectáculo de talentos en la cubierta o piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(20, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 500,
            "ubicacion": "Cubierta Superior",
            "img_src": "concursotalentos.jpg"
        },
        {
            "titulo": "Fiesta Silent Disco",
            "descripcion": "Disfruta de la mejor música, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la piscina del crucero.",
            "dia_crucero": 5,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 1000,
            "ubicacion": "Piscina",
            "img_src": "silentparty.jpg"
        },
        {
            "titulo": "Taller de origami.",
            "descripcion": "Disfruta de un taller de origami en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(9, 0),  # 2:00 PM
            "hora_fin": time(10, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "tallerorigami.jpg"
        },
        {
            "titulo": "Clases de Tai Chi.",
            "descripcion": "Disfruta de un clase de tai chi en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(10, 0),  # 2:00 PM
            "hora_fin": time(11, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "taichi.jpg"
        },
        {
            "titulo": "Clases de respiración y mindfulness.",
            "descripcion": "Disfruta de un clase de respiración y mindfulness en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(11, 30),  # 2:00 PM
            "hora_fin": time(12, 30),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "yogacrucero.jpg"
        },
        {
            "titulo": "Show de mentalismo.",
            "descripcion": "Disfruta de un show de mentalismo en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(15, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Teatro",
            "img_src": "mentalismo.jpg"
        },
        {
            "titulo": "Taller y show de coctelería variada.",
            "descripcion": "Disfruta de un taller y show de coctelería variada en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(15, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Piscina",
            "img_src": "showcocteleria.jpg"
        },
        {
            "titulo": "Happy hour en la discoteca.",
            "descripcion": "Disfruta de un happy hour en la discoteca. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(17, 0),  # 2:00 PM
            "hora_fin": time(18, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Discoteca",
            "img_src": "happyhourdisco1.jpg"
        },
        {
            "titulo": "Cena con el capitán.",
            "descripcion": "Disfruta de un cena con el capitán en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(19, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 6000,
            "ubicacion": "Restaurante Principal",
            "img_src": "capitancrucero.jpg"
        },
        {
            "titulo": "Fiesta glow con temática Neon.",
            "descripcion": "Disfruta de un fiesta glow con temática Neon en la discoteca. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 800,
            "ubicacion": "Discoteca",
            "img_src": "fiestaglow.jpg"
        },
        {
            "titulo": "Taller de pintura rápida de paisajes.",
            "descripcion": "Disfruta de un taller de pintura rápida de paisajes en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(9, 0),  # 2:00 PM
            "hora_fin": time(10, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "tallerpinturarapida.jpg"
        },
        {
            "titulo": "Bingo en la piscina.",
            "descripcion": "Disfruta de un bingo en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(10, 0),  # 2:00 PM
            "hora_fin": time(11, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Piscina",
            "img_src": "bingopiscina.jpg"
        },
        {
            "titulo": "Taller de baile o danza.",
            "descripcion": "Disfruta de un taller de baile o danza en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(11, 0),  # 2:00 PM
            "hora_fin": time(12, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "clasedebaile.jpg"
        },
        {
            "titulo": "Taller de peinados y estilismo.",
            "descripcion": "Disfruta de un taller de peinados y estilismo en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(14, 30),  # 2:00 PM
            "hora_fin": time(15, 30),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "tallerestilismo.jpg"
        },
        {
            "titulo": "Family feud en el teatro.",
            "descripcion": "Disfruta de un family feud en el teatro. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(15, 0),  # 2:00 PM
            "hora_fin": time(16, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Teatro",
            "img_src": "familyfeud.jpg"
        },
        {
            "titulo": "Competencia de mímica en equipos en la piscina.",
            "descripcion": "Disfruta de un competencia de mímica en equipos en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(17, 0),  # 2:00 PM
            "hora_fin": time(18, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Piscina",
            "img_src": "competenciacharadas.jpg"
        },
        {
            "titulo": "Espectáculo de magia en el teatro.",
            "descripcion": "Disfruta de un espectáculo de magia en el teatro. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(20, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Teatro",
            "img_src": "espectaculomagiacrucero.jpg"
        },
        {
            "titulo": "Fiesta de los años 80/90.",
            "descripcion": "Disfruta de un fiesta de los años 80/90 en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 1500,
            "ubicacion": "Discoteca",
            "img_src": "fiestalatinaDisco.jpg"
        },
        {
            "titulo": "Desembarque",
            "descripcion": "El equipo de excursiones y animadores asisten a los pasajeros durante el proceso de salida.",
            "dia_crucero": 8,
            "hora_inicio": time(8, 0),  # 2:00 PM
            "hora_fin": time(13, 0),     # 4:00 PM
            "maximo_actividad": 6000,
            "ubicacion": "Barco",
            "img_src": "tourcrucero1.jpg"
        }
    ]

    # Crear las actividades rutinarias en la base de datos
    actividades_rutinarias_creadas = []
    for actividad_data in actividades_rutinarias_data:
        actividad_rutinaria = ActividadRutinaria.objects.create(viaje=viaje, **actividad_data)
        actividades_rutinarias_creadas.append(actividad_rutinaria)
    return actividades_rutinarias_creadas

def actividadRutPequenoInit(viaje: Viaje):
    """
    Función que inicializa la tabla de actividades rutinarias con datos de ejemplo
    """
    # Verificar si ya existen actividades rutinarias para este viaje
    if ActividadRutinaria.objects.filter(viaje=viaje).exists():
        return []

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
            "titulo": "Espectáculo de entretenimiento en el teatro (circo).",
            "descripcion": "Prepárate para un show increíble en el teatro principal con artistas de circo, acrobacias asombrosas y efectos especiales.",
            "dia_crucero": 1,
            "hora_inicio": time(20, 0), # 7:30 PM
            "hora_fin": time(21, 0),     # 10:00 PM
            "maximo_actividad": 350,
            "ubicacion": "Teatro Principal",
            "img_src": "espectaculomagiacrucero.jpg"
        },
        {
            "titulo": "Welcome Aboard Show en la discoteca para presentar a los artistas.",
            "descripcion": "Descubre a los increíbles artistas que te acompañarán durante el viaje. Música, baile y presentaciones en un ambiente vibrante.",
            "dia_crucero": 1,
            "hora_inicio": time(21, 0),
            "hora_fin": time(23, 0),     # 11:00 PM
            "maximo_actividad": 600,
            "ubicacion": "Discoteca",
            "img_src": "teatrodia1.jpg"
        },


        {
            "titulo": "Ambientación del País (Colombia) en la piscina. ",
            "descripcion": "Sumergete en una fiesta en la piscina con música y decoración colombiana. Baila al ritmo de la cumbia y el vallenato mientras disfrutas del sol.",
            "dia_crucero": 2,
            "hora_inicio": time(11, 30),  # 6:00 PM
            "hora_fin": time(14, 0),     # 8:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Piscina",
            "img_src": "fiestalatina.jpg"
        },
        {
            "titulo": "Happy hour en discoteca con música regional.",
            "descripcion": "Disfruta de la mejor música regional, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la discoteca del crucero.",
            "dia_crucero": 3,
            "hora_inicio": time(15, 0),
            "hora_fin": time(17, 0),
            "maximo_actividad": 200,
            "ubicacion": "Discoteca",
            "img_src": "happyhourdisco1.jpg"
        },
        {
            "titulo": "Torneo de voleibol en la piscina.",
            "descripcion": "Compite con otros pasajeros en un emocionante torneo de voleibol acuático. ¡Diversión, risas y sol garantizados mientras juegas en la piscina!",
            "dia_crucero": 2,
            "hora_inicio": time(16, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 40,
            "ubicacion": "Piscina",
            "img_src": "volleyballcrucero.jpg"
        },
        {
            "titulo": "Espectáculo de magia en el teatro.",
            "descripcion": "¡Descubre cómo magia y ilusiones pueden fascinar a cualquier persona! Un espectáculo lleno de misterio y emoción en el teatro principal.",
            "dia_crucero": 2,
            "hora_inicio": time(20, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 500,
            "ubicacion": "Teatro",
            "img_src": "espectaculomagiacrucero.jpg"
        },
        {
            "titulo": "Fiesta latina en la discoteca.",
            "descripcion": "Disfruta de la mejor música latina, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la discoteca del crucero.",
            "dia_crucero": 2,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Discoteca",
            "img_src": "fiestalatinaDisco.jpg"
        },

        {
            "titulo": "Caminata grupal en la cubierta.",
            "descripcion": "Unete a nuestros instructores para una caminata grupal en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 3,
            "hora_inicio": time(10, 0),  # 2:00 PM
            "hora_fin": time(11, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "caminatacubierta.jpg"
        },

        {
            "titulo": "Karaoke.",
            "descripcion": "¡Diviértete cantando con otros pasajeros en nuestro emocionante karaoke en la cubierta! Compite con otros viajeros para ganar precios exclusivos mientras disfrutas de la adrenalina de las ruedas y las emocionantes actividades en la piscina.",
            "dia_crucero": 3,
            "hora_inicio": time(16, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Cubierta Superior",
            "img_src": "karaokecrucero.jpg"
        },
  
        {
            "titulo": "Espectáculo de comedia en el teatro.",
            "descripcion": "Disfruta de un espectáculo de comedia en el teatro. ¡Un evento exclusivo para los amantes de la comedia!",
            "dia_crucero": 3,
            "hora_inicio": time(20, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 500,
            "ubicacion": "Teatro",
            "img_src": "comediateatro.jpg"
        },
        {
            "titulo": "Discoteca abierta.",
            "descripcion": "Disfruta de la mejor música, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la discoteca del crucero.",
            "dia_crucero": 3,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Discoteca",
            "img_src": "discotecacrucero.jpg"
        },
        {
            "titulo": "Clase de aerobics",
            "descripcion": "Disfruta de una clase de aerobics en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 4,
            "hora_inicio": time(10, 0),  # 2:00 PM
            "hora_fin": time(11, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Piscina",
            "img_src": "clasesaerobics.jpg"
        },
        {
            "titulo": "Animadores en la piscina.",
            "descripcion": "Disfruta de animadores en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 4,
            "hora_inicio": time(12, 0),  # 2:00 PM
            "hora_fin": time(13, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Piscina",
            "img_src": "animadorespiscina.jpg"
        },
        {
            "titulo": "Zumba en la piscina.",
            "descripcion": "Disfruta de una clase de zumba en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 4,
            "hora_inicio": time(16, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 100,
            "ubicacion": "Piscina",
            "img_src": "zumbapiscina.jpg"
        },

        {
            "titulo": "Show de tambores en cubierta o piscina. ",
            "descripcion": "Disfruta de un espectáculo de tambores en la cubierta o piscina. ¡Un evento exclusivo para los amantes de la música!",
            "dia_crucero": 4,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(22, 0),     # 4:00 PM
            "maximo_actividad": 600,
            "ubicacion": "Cubierta Superior",
            "img_src": "showtambores.jpg"
        },
        {
            "titulo": "Fiesta con temática caribeña en la discoteca.",
            "descripcion": "Disfruta de la mejor música caribeña, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la discoteca del crucero.",
            "dia_crucero": 4,
            "hora_inicio": time(22, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Discoteca",
            "img_src": "fiestalatinaDisco.jpg"
        },
        {
            "titulo": "Clases de entrenamiento funcional.",
            "descripcion": "Disfruta de una clase de entrenamiento funcional en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(10, 0),  # 2:00 PM
            "hora_fin": time(11, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Cubierta Superior",
            "img_src": "funcionales.jpg"
        },
        {
            "titulo": "Competencia de bailes.",
            "descripcion": "Disfruta de un torneo de bailes en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(17, 0),  # 2:00 PM
            "hora_fin": time(18, 0),     # 4:00 PM
            "maximo_actividad": 300,
            "ubicacion": "Piscina",
            "img_src": "clasedebaile.jpg"
        },
        {
            "titulo": "Concurso de talentos en cubierta.",
            "descripcion": "Disfruta de un espectáculo de talentos en la cubierta o piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 5,
            "hora_inicio": time(20, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 500,
            "ubicacion": "Cubierta Superior",
            "img_src": "concursotalentos.jpg"
        },
        {
            "titulo": "Fiesta Silent Disco",
            "descripcion": "Disfruta de la mejor música, bebidas a precios especiales y el mejor ambiente para bailar y divertirte en la piscina del crucero.",
            "dia_crucero": 5,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 1000,
            "ubicacion": "Piscina",
            "img_src": "silentparty.jpg"
        },

        {
            "titulo": "Clases de respiración y mindfulness.",
            "descripcion": "Disfruta de un clase de respiración y mindfulness en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(11, 30),  # 2:00 PM
            "hora_fin": time(12, 30),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Cubierta Superior",
            "img_src": "yogacrucero.jpg"
        },
        {
            "titulo": "Taller y show de coctelería variada.",
            "descripcion": "Disfruta de un taller y show de coctelería variada en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(15, 0),  # 2:00 PM
            "hora_fin": time(17, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Piscina",
            "img_src": "showcocteleria.jpg"
        },

        {
            "titulo": "Cena con el capitán.",
            "descripcion": "Disfruta de un cena con el capitán en la cubierta. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(19, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 6000,
            "ubicacion": "Restaurante Principal",
            "img_src": "capitancrucero.jpg"
        },
        {
            "titulo": "Fiesta glow con temática Neon.",
            "descripcion": "Disfruta de un fiesta glow con temática Neon en la discoteca. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 6,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 800,
            "ubicacion": "Discoteca",
            "img_src": "fiestaglow.jpg"
        },

        {
            "titulo": "Bingo en la piscina.",
            "descripcion": "Disfruta de un bingo en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(10, 0),  # 2:00 PM
            "hora_fin": time(11, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Piscina",
            "img_src": "bingopiscina.jpg"
        },
        {
            "titulo": "Family feud en el teatro.",
            "descripcion": "Disfruta de un family feud en el teatro. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(15, 0),  # 2:00 PM
            "hora_fin": time(16, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Teatro",
            "img_src": "familyfeud.jpg"
        },

        {
            "titulo": "Espectáculo de magia en el teatro.",
            "descripcion": "Disfruta de un espectáculo de magia en el teatro. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(20, 0),  # 2:00 PM
            "hora_fin": time(21, 0),     # 4:00 PM
            "maximo_actividad": 150,
            "ubicacion": "Teatro",
            "img_src": "espectaculomagiacrucero.jpg"
        },
        {
            "titulo": "Fiesta de los años 80/90.",
            "descripcion": "Disfruta de un fiesta de los años 80/90 en la piscina. Perfecta para mantenerte en forma y disfrutar de las vistas al mar.",
            "dia_crucero": 7,
            "hora_inicio": time(21, 0),  # 2:00 PM
            "hora_fin": time(2, 0),     # 4:00 PM
            "maximo_actividad": 1500,
            "ubicacion": "Discoteca",
            "img_src": "fiestalatinaDisco.jpg"
        },
        {
            "titulo": "Desembarque",
            "descripcion": "El equipo de excursiones y animadores asisten a los pasajeros durante el proceso de salida.",
            "dia_crucero": 8,
            "hora_inicio": time(8, 0),  # 2:00 PM
            "hora_fin": time(13, 0),     # 4:00 PM
            "maximo_actividad": 6000,
            "ubicacion": "Barco",
            "img_src": "tourcrucero1.jpg"
        }
    ]

    # Crear las actividades rutinarias en la base de datos
    actividades_rutinarias_creadas = []
    for actividad_data in actividades_rutinarias_data:
        actividad_rutinaria = ActividadRutinaria.objects.create(viaje=viaje, **actividad_data)
        actividades_rutinarias_creadas.append(actividad_rutinaria)
    return actividades_rutinarias_creadas