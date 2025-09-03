from django.core.management.base import BaseCommand
from App.models import TipoHabitacion, Habitacion


class Command(BaseCommand):
    help = "Genera automáticamente los camarotes para cada crucero"

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            type=str,
            help="Nombre del crucero (vision, voyager, oasis). Si no se pasa, se generan todos."
        )

    def handle(self, *args, **options):
        cruceros = (
            [options["database"]] if options["database"] else ["vision", "voyager", "oasis"]
        )

        for crucero in cruceros:
            self.stdout.write(self.style.WARNING(f"Generando camarotes para {crucero}..."))

            # borrar los anteriores para evitar duplicados
            Habitacion.objects.using(crucero).all().delete()

            # obtener tipos de camarote
            try:
                basico_sencillo = TipoHabitacion.objects.using(crucero).get(categoria="basico", subtipo="sencillo")
                basico_doble = TipoHabitacion.objects.using(crucero).get(categoria="basico", subtipo="doble")
                premium_sencillo = TipoHabitacion.objects.using(crucero).get(categoria="premium", subtipo="sencillo")
                premium_doble = TipoHabitacion.objects.using(crucero).get(categoria="premium", subtipo="doble")
            except TipoHabitacion.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    f"[{crucero}] ❌ No existen tipos de habitación, ejecuta primero `python manage.py crear_tipos`"
                ))
                continue

            # --- Vision (pequeño) ---
            if crucero == "vision":
                # Pisos 2-5 (no premium)
                for piso in range(2, 6):
                    for i in range(150):
                        tipo = basico_sencillo if i < 125 else basico_doble
                        lado = "babor" if i % 2 == 0 else "estribor"
                        vista = True if i < 90 else False
                        num = f"{piso}0{i:03d}"
                        Habitacion.objects.using(crucero).create(
                            crucero=crucero, numero=num, piso=piso,
                            lado=lado, vista_mar=vista, tipo_habitacion=tipo
                        )
                # Pisos 6-8 (premium)
                for piso in range(6, 9):
                    for i in range(75):
                        tipo = premium_sencillo if i < 50 else premium_doble
                        lado = "babor" if i % 2 == 0 else "estribor"
                        vista = True if i < 45 else False
                        num = f"{piso}0{i:03d}"
                        Habitacion.objects.using(crucero).create(
                            crucero=crucero, numero=num, piso=piso,
                            lado=lado, vista_mar=vista, tipo_habitacion=tipo
                        )

            # --- Voyager (mediano) ---
            if crucero == "voyager":
                # Pisos 2-6 (no premium)
                for piso in range(2, 7):
                    for i in range(240):
                        tipo = basico_sencillo if i < 200 else basico_doble
                        lado = "babor" if i % 2 == 0 else "estribor"
                        vista = True if i < 144 else False
                        num = f"{piso}0{i:03d}"
                        Habitacion.objects.using(crucero).create(
                            crucero=crucero, numero=num, piso=piso,
                            lado=lado, vista_mar=vista, tipo_habitacion=tipo
                        )
                # Pisos 7-10 (premium)
                distribucion = {7: (75, 38), 8: (75, 38), 9: (75, 37), 10: (75, 37)}
                for piso, (sencillos, dobles) in distribucion.items():
                    i = 0
                    for _ in range(sencillos):
                        lado = "babor" if i % 2 == 0 else "estribor"
                        vista = True if i < int(sencillos * 0.6) else False
                        num = f"{piso}0{i:03d}"
                        Habitacion.objects.using(crucero).create(
                            crucero=crucero, numero=num, piso=piso,
                            lado=lado, vista_mar=vista, tipo_habitacion=premium_sencillo
                        )
                        i += 1
                    for _ in range(dobles):
                        lado = "babor" if i % 2 == 0 else "estribor"
                        vista = True if i < int(dobles * 0.6) else False
                        num = f"{piso}0{i:03d}"
                        Habitacion.objects.using(crucero).create(
                            crucero=crucero, numero=num, piso=piso,
                            lado=lado, vista_mar=vista, tipo_habitacion=premium_doble
                        )
                        i += 1

            # --- Oasis (grande) ---
            if crucero == "oasis":
                # Pisos 2-7 (no premium)
                for piso in range(2, 8):
                    for i in range(300):
                        tipo = basico_sencillo if i < 250 else basico_doble
                        lado = "babor" if i % 2 == 0 else "estribor"
                        vista = True if i < 180 else False
                        num = f"{piso}0{i:03d}"
                        Habitacion.objects.using(crucero).create(
                            crucero=crucero, numero=num, piso=piso,
                            lado=lado, vista_mar=vista, tipo_habitacion=tipo
                        )
                # Pisos 8-12 (premium)
                for piso in range(8, 13):
                    for i in range(135):
                        tipo = premium_sencillo if i < 90 else premium_doble
                        lado = "babor" if i % 2 == 0 else "estribor"
                        vista = True if i < 81 else False
                        num = f"{piso}0{i:03d}"
                        Habitacion.objects.using(crucero).create(
                            crucero=crucero, numero=num, piso=piso,
                            lado=lado, vista_mar=vista, tipo_habitacion=tipo
                        )

            self.stdout.write(self.style.SUCCESS(f"✔ Camarotes generados para {crucero}"))
