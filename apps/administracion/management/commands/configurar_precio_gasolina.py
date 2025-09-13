from django.core.management.base import BaseCommand
from django.db import transaction
from apps.administracion.models import Dashboard
from apps.cruceros.models import Crucero


class Command(BaseCommand):
    help = 'Configura el precio de gasolina para todos los cruceros o para un crucero específico'

    def add_arguments(self, parser):
        parser.add_argument(
            '--precio',
            type=float,
            required=True,
            help='Precio de la gasolina a configurar'
        )
        parser.add_argument(
            '--crucero-id',
            type=int,
            help='ID del crucero específico (opcional, si no se especifica se aplica a todos)'
        )
        parser.add_argument(
            '--solo-sin-configurar',
            action='store_true',
            help='Solo configurar cruceros que no tienen precio configurado (precio = 0)'
        )

    def handle(self, *args, **options):
        precio = options['precio']
        crucero_id = options.get('crucero_id')
        solo_sin_configurar = options.get('solo_sin_configurar', False)

        if precio <= 0:
            self.stdout.write(
                self.style.ERROR('El precio debe ser mayor a 0')
            )
            return

        with transaction.atomic():
            if crucero_id:
                # Configurar un crucero específico
                try:
                    crucero = Crucero.objects.get(id=crucero_id)
                    dashboard, created = Dashboard.objects.get_or_create(
                        crucero=crucero,
                        defaults={
                            'costos_totales': 0.00,
                            'ganancias_totales': 0.00,
                            'presupuesto_estimado': 0.00,
                            'precio_combustible': precio,
                            'num_pasajeros_actual': 0,
                            'num_empleados_actual': 0
                        }
                    )
                    
                    if not created:
                        if solo_sin_configurar and dashboard.precio_combustible > 0:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'El crucero {crucero.nombre} ya tiene precio configurado: ${dashboard.precio_combustible}'
                                )
                            )
                        else:
                            dashboard.precio_combustible = precio
                            dashboard.save()
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Precio actualizado para {crucero.nombre}: ${precio}'
                                )
                            )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Dashboard creado para {crucero.nombre} con precio: ${precio}'
                            )
                        )
                        
                except Crucero.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'No se encontró el crucero con ID {crucero_id}')
                    )
                    return
            else:
                # Configurar todos los cruceros
                cruceros = Crucero.objects.all()
                actualizados = 0
                creados = 0
                omitidos = 0

                for crucero in cruceros:
                    dashboard, created = Dashboard.objects.get_or_create(
                        crucero=crucero,
                        defaults={
                            'costos_totales': 0.00,
                            'ganancias_totales': 0.00,
                            'presupuesto_estimado': 0.00,
                            'precio_combustible': precio,
                            'num_pasajeros_actual': 0,
                            'num_empleados_actual': 0
                        }
                    )

                    if created:
                        creados += 1
                        self.stdout.write(
                            f'✓ Dashboard creado para {crucero.nombre} con precio: ${precio}'
                        )
                    else:
                        if solo_sin_configurar and dashboard.precio_combustible > 0:
                            omitidos += 1
                            self.stdout.write(
                                f'⚠ Omitido {crucero.nombre} (ya tiene precio: ${dashboard.precio_combustible})'
                            )
                        else:
                            dashboard.precio_combustible = precio
                            dashboard.save()
                            actualizados += 1
                            self.stdout.write(
                                f'✓ Precio actualizado para {crucero.nombre}: ${precio}'
                            )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nResumen: {creados} dashboards creados, {actualizados} actualizados, {omitidos} omitidos'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n¡Configuración completada! Precio de gasolina: ${precio}'
            )
        )
