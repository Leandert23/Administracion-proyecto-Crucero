from django.core.management.base import BaseCommand
from App.models import TipoHabitacion

class Command(BaseCommand):
    help = "Crea o corrige los tipos de habitación en todas las bases de datos"

    def handle(self, *args, **kwargs):
        cruceros = ["default", "vision", "voyager", "oasis"]

        tipos = [
            {"categoria": "basico", "subtipo": "sencillo", "capacidad": 2, "precio_base": 100},
            {"categoria": "basico", "subtipo": "doble", "capacidad": 4, "precio_base": 180},
            {"categoria": "premium", "subtipo": "sencillo", "capacidad": 2, "precio_base": 250},
            {"categoria": "premium", "subtipo": "doble", "capacidad": 4, "precio_base": 400},
        ]

        for crucero in cruceros:
            self.stdout.write(self.style.NOTICE(f"Procesando {crucero}..."))
            for t in tipos:
                # Elimina duplicados
                qs = TipoHabitacion.objects.using(crucero).filter(
                    categoria=t["categoria"],
                    subtipo=t["subtipo"]
                )
                if qs.count() > 1:
                    qs.delete()
                    self.stdout.write(self.style.WARNING(
                        f"[{crucero}] Duplicados eliminados para {t['categoria']} - {t['subtipo']}"
                    ))

                # Crea o actualiza el registro
                obj, created = TipoHabitacion.objects.using(crucero).update_or_create(
                    categoria=t["categoria"],
                    subtipo=t["subtipo"],
                    defaults={
                        "capacidad": t["capacidad"],
                        "precio_base": t["precio_base"],
                    },
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"[{crucero}] Tipo creado: {obj}"))
                else:
                    self.stdout.write(self.style.WARNING(f"[{crucero}] Tipo actualizado: {obj}"))

        self.stdout.write(self.style.SUCCESS("✔ Todos los tipos de camarotes creados o corregidos"))
