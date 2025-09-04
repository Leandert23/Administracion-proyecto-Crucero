from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from reservas.models import (
    Barco, Ruta, Viaje, TipoCabina, Cabina, 
    ServicioAdicional
)
from ventas.models import Cliente
from datetime import datetime, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Crea datos de prueba para la app de Reservas'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de prueba para Reservas...')
        
        # Crear usuario agente si no existe
        agente, created = User.objects.get_or_create(
            username='agente_reservas',
            defaults={
                'first_name': 'Agente',
                'last_name': 'Reservas',
                'email': 'agente@cruceros.com',
                'is_staff': True
            }
        )
        if created:
            agente.set_password('agente123')
            agente.save()
            self.stdout.write(f'Usuario agente creado: {agente.username}')
        
        # Crear barcos
        barcos_data = [
            {
                'nombre': 'Caribbean Paradise',
                'capacidad': 2500,
                'descripcion': 'Crucero de lujo con 15 cubiertas y múltiples restaurantes'
            },
            {
                'nombre': 'Mediterranean Dream',
                'capacidad': 1800,
                'descripcion': 'Crucero elegante para el Mediterráneo'
            },
            {
                'nombre': 'Pacific Explorer',
                'capacidad': 3200,
                'descripcion': 'Gran crucero para el Pacífico con entretenimiento de clase mundial'
            }
        ]
        
        barcos = []
        for barco_data in barcos_data:
            barco, created = Barco.objects.get_or_create(
                nombre=barco_data['nombre'],
                defaults=barco_data
            )
            barcos.append(barco)
            if created:
                self.stdout.write(f'Barco creado: {barco.nombre}')
        
        # Crear rutas
        rutas_data = [
            {
                'nombre': 'Caribe Oriental',
                'origen': 'Miami',
                'destino': 'San Juan',
                'duracion_dias': 7
            },
            {
                'nombre': 'Mediterráneo Occidental',
                'origen': 'Barcelona',
                'destino': 'Roma',
                'duracion_dias': 10
            },
            {
                'nombre': 'Pacífico Sur',
                'origen': 'Los Ángeles',
                'destino': 'Honolulu',
                'duracion_dias': 14
            }
        ]
        
        rutas = []
        for ruta_data in rutas_data:
            ruta, created = Ruta.objects.get_or_create(
                nombre=ruta_data['nombre'],
                defaults=ruta_data
            )
            rutas.append(ruta)
            if created:
                self.stdout.write(f'Ruta creada: {ruta.nombre}')
        
        # Crear tipos de cabina
        tipos_cabina_data = [
            {
                'nombre': 'Interior Básica',
                'capacidad_personas': 2,
                'precio_por_noche': Decimal('150.00'),
                'descripcion': 'Cabina interior estándar sin ventana'
            },
            {
                'nombre': 'Interior Premium',
                'capacidad_personas': 2,
                'precio_por_noche': Decimal('200.00'),
                'descripcion': 'Cabina interior con más espacio y comodidades'
            },
            {
                'nombre': 'Exterior con Ventana',
                'capacidad_personas': 2,
                'precio_por_noche': Decimal('250.00'),
                'descripcion': 'Cabina con ventana al mar'
            },
            {
                'nombre': 'Balcón Privado',
                'capacidad_personas': 2,
                'precio_por_noche': Decimal('350.00'),
                'descripcion': 'Cabina con balcón privado al mar'
            },
            {
                'nombre': 'Suite de Lujo',
                'capacidad_personas': 4,
                'precio_por_noche': Decimal('800.00'),
                'descripcion': 'Suite de lujo con múltiples habitaciones y balcón'
            }
        ]
        
        tipos_cabina = []
        for tipo_data in tipos_cabina_data:
            tipo, created = TipoCabina.objects.get_or_create(
                nombre=tipo_data['nombre'],
                defaults=tipo_data
            )
            tipos_cabina.append(tipo)
            if created:
                self.stdout.write(f'Tipo de cabina creado: {tipo.nombre}')
        
        # Crear cabinas para cada barco
        for barco in barcos:
            for i, tipo in enumerate(tipos_cabina):
                # Crear múltiples cabinas de cada tipo
                for j in range(1, 6):  # 5 cabinas de cada tipo
                    numero_cabina = f"{i+1:02d}{j:02d}"  # 0101, 0102, etc.
                    cabina, created = Cabina.objects.get_or_create(
                        barco=barco,
                        numero=numero_cabina,
                        defaults={
                            'tipo_cabina': tipo,
                            'estado': 'disponible',
                            'activa': True
                        }
                    )
                    if created:
                        self.stdout.write(f'Cabina creada: {barco.nombre} - {numero_cabina}')
        
        # Crear servicios adicionales
        servicios_data = [
            {
                'nombre': 'Paquete de Bebidas Ilimitadas',
                'precio': Decimal('25.00'),
                'descripcion': 'Bebidas no alcohólicas ilimitadas durante todo el viaje'
            },
            {
                'nombre': 'Paquete Premium de Bebidas',
                'precio': Decimal('45.00'),
                'descripcion': 'Bebidas alcohólicas y no alcohólicas ilimitadas'
            },
            {
                'nombre': 'Internet WiFi',
                'precio': Decimal('15.00'),
                'descripcion': 'Acceso a internet WiFi durante todo el viaje'
            },
            {
                'nombre': 'Excursión en Puerto',
                'precio': Decimal('75.00'),
                'descripcion': 'Excursión guiada en uno de los puertos de escala'
            },
            {
                'nombre': 'Spa y Masajes',
                'precio': Decimal('120.00'),
                'descripcion': 'Sesión de spa y masaje relajante'
            }
        ]
        
        for servicio_data in servicios_data:
            servicio, created = ServicioAdicional.objects.get_or_create(
                nombre=servicio_data['nombre'],
                defaults=servicio_data
            )
            if created:
                self.stdout.write(f'Servicio adicional creado: {servicio.nombre}')
        
        # Crear viajes futuros
        fecha_actual = datetime.now()
        for i, (barco, ruta) in enumerate(zip(barcos, rutas)):
            fecha_salida = fecha_actual + timedelta(days=30 + (i * 15))
            fecha_llegada = fecha_salida + timedelta(days=ruta.duracion_dias)
            
            viaje, created = Viaje.objects.get_or_create(
                barco=barco,
                ruta=ruta,
                fecha_salida=fecha_salida,
                defaults={
                    'fecha_llegada': fecha_llegada,
                    'precio_base': Decimal('1200.00'),
                    'estado': 'programado',
                    'capacidad_disponible': barco.capacidad
                }
            )
            if created:
                self.stdout.write(f'Viaje creado: {barco.nombre} - {ruta.nombre} - {fecha_salida.strftime("%d/%m/%Y")}')
        
        self.stdout.write(
            self.style.SUCCESS('¡Datos de prueba creados exitosamente!')
        )
        self.stdout.write('Puedes acceder al admin con:')
        self.stdout.write(f'Usuario: {agente.username}')
        self.stdout.write('Contraseña: agente123')
