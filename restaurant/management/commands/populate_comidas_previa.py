from django.core.management.base import BaseCommand
from restaurant.models import ComidasPreviu

class Command(BaseCommand):
    help = 'Poblar la tabla comidasPreviu con datos de prueba'

    def handle(self, *args, **options):
        # Datos de prueba para simular una tabla comidasPreviu real
        datos_prueba = [
            {
                'nombre': 'Tomate cherry',
                'precio': 3.50,
                'unidad': 'kg',
                'stock_disponible': 25.0,
                'stock_minimo': 5.0,
                'descripcion': 'Tomates cherry frescos importados'
            },
            {
                'nombre': 'Cebolla blanca',
                'precio': 1.80,
                'unidad': 'kg',
                'stock_disponible': 15.0,
                'stock_minimo': 3.0,
                'descripcion': 'Cebollas blancas de calidad premium'
            },
            {
                'nombre': 'Pechuga de pollo',
                'precio': 8.90,
                'unidad': 'kg',
                'stock_disponible': 50.0,
                'stock_minimo': 10.0,
                'descripcion': 'Pechuga de pollo sin hueso ni piel'
            },
            {
                'nombre': 'Arroz basmati',
                'precio': 4.20,
                'unidad': 'kg',
                'stock_disponible': 30.0,
                'stock_minimo': 8.0,
                'descripcion': 'Arroz basmati premium para platos principales'
            },
            {
                'nombre': 'Aceite de oliva virgen',
                'precio': 12.50,
                'unidad': 'l',
                'stock_disponible': 20.0,
                'stock_minimo': 5.0,
                'descripcion': 'Aceite de oliva virgen extra primera prensada'
            },
            {
                'nombre': 'Sal marina',
                'precio': 0.80,
                'unidad': 'kg',
                'stock_disponible': 100.0,
                'stock_minimo': 10.0,
                'descripcion': 'Sal marina yodada fina'
            },
            {
                'nombre': 'Pimienta negra molida',
                'precio': 15.00,
                'unidad': 'kg',
                'stock_disponible': 5.0,
                'stock_minimo': 1.0,
                'descripcion': 'Pimienta negra molida de Malabar'
            },
            {
                'nombre': 'Leche entera',
                'precio': 1.50,
                'unidad': 'l',
                'stock_disponible': 40.0,
                'stock_minimo': 8.0,
                'descripcion': 'Leche entera pasteurizada'
            }
        ]

        try:
            # Limpiar datos existentes
            ComidasPreviu.objects.all().delete()
            self.stdout.write('Tabla comidasPreviu limpiada')

            # Insertar datos de prueba
            for i, dato in enumerate(datos_prueba, 1):
                comida = ComidasPreviu.objects.create(**dato)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Creado: {comida.nombre} (ID: {comida.id})'
                    )
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Población completada: {len(datos_prueba)} ingredientes creados'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error al poblar comidasPreviu: {str(e)}')
            )
