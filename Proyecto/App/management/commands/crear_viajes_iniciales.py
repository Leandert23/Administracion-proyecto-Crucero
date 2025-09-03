from django.core.management.base import BaseCommand
from App.models import Viaje, Itinerario

class Command(BaseCommand):
    help = "Crea un viaje inicial con itinerario de 8 días en las 3 bases (vision, voyager, oasis)."

    def handle(self, *args, **options):
        cruceros = ["vision", "voyager", "oasis"]

        itinerario = [
            (1, "Colón, Panamá", "Embarque y partida desde el puerto de Colón, Panamá."),
            (2, "Cartagena, Colombia", "Explora la histórica ciudad amurallada, sus fuertes y el encanto colonial."),
            (3, "Navegación", "Un día completo en el mar para disfrutar de las instalaciones del crucero."),
            (4, "Oranjestad, Aruba", "Descubre las playas de arena blanca y la arquitectura de influencia holandesa."),
            (5, "Kralendijk, Bonaire", "Famosa por sus sitios de buceo y snorkel, ideal para explorar la vida marina."),
            (6, "Willemstad, Curazao", "Visita esta vibrante ciudad con edificios de colores pastel declarados UNESCO."),
            (7, "Navegación", "Relájate y disfruta del viaje de regreso."),
            (8, "Colón, Panamá", "Desembarque en el puerto de Colón."),
        ]

        for crucero in cruceros:
            self.stdout.write(self.style.WARNING(f"Procesando {crucero}..."))

            # Borrar viajes previos para no duplicar
            Viaje.objects.using(crucero).all().delete()

            # Crear viaje
            viaje = Viaje.objects.using(crucero).create(
                nombre=f"Ruta Caribe ({crucero.title()})",
                dia_actual=1,
                total_dias=8
            )

            # Crear itinerario
            for dia, destino, desc in itinerario:
                Itinerario.objects.using(crucero).create(
                    viaje=viaje, dia=dia, destino=destino, descripcion=desc
                )

            self.stdout.write(self.style.SUCCESS(f"[{crucero}] ✔ Viaje y itinerario creados"))
