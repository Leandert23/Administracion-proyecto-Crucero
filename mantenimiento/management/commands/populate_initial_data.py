from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mantenimiento.models import (
    TipoCrucero, CategoriaProducto, Producto, Ubicacion, TipoEquipo, Equipo
)
from django.utils import timezone
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos iniciales del sistema de mantenimiento'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando población de datos iniciales...')
        
        # Crear tipos de crucero
        self.create_tipos_crucero()
        
        # Crear categorías de productos
        self.create_categorias_productos()
        
        # Crear productos basados en el Excel
        self.create_productos()
        
        # Crear ubicaciones de ejemplo
        self.create_ubicaciones()
        
        # Crear tipos de equipos
        self.create_tipos_equipos()
        
        # Crear equipos de ejemplo
        self.create_equipos()
        
        # Crear superusuario si no existe
        self.create_superuser()
        
        self.stdout.write(
            self.style.SUCCESS('Datos iniciales creados exitosamente!')
        )

    def create_tipos_crucero(self):
        self.stdout.write('Creando tipos de crucero...')
        
        tipos_data = [
            {
                'tipo': 'pequeño',
                'capacidad_pasajeros': 2000,
                'numero_tripulantes': 667,
                'numero_cubiertas': 12
            },
            {
                'tipo': 'mediano',
                'capacidad_pasajeros': 4000,
                'numero_tripulantes': 1333,
                'numero_cubiertas': 15
            },
            {
                'tipo': 'grande',
                'capacidad_pasajeros': 6000,
                'numero_tripulantes': 2000,
                'numero_cubiertas': 18
            }
        ]
        
        for tipo_data in tipos_data:
            tipo, created = TipoCrucero.objects.get_or_create(
                tipo=tipo_data['tipo'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(f'  - Creado: {tipo}')

    def create_categorias_productos(self):
        self.stdout.write('Creando categorías de productos...')
        
        categorias_data = [
            {
                'categoria': 'quimicos_limpieza',
                'descripcion': 'Productos químicos para limpieza e higiene del crucero'
            },
            {
                'categoria': 'consumibles_higiene',
                'descripcion': 'Consumibles descartables para higiene'
            },
            {
                'categoria': 'repuestos_criticos',
                'descripcion': 'Repuestos críticos y filtros para equipos'
            },
            {
                'categoria': 'fluidos_lubricantes',
                'descripcion': 'Fluidos y lubricantes para motores y equipos'
            },
            {
                'categoria': 'herramientas_seguridad',
                'descripcion': 'Herramientas y equipos de seguridad'
            }
        ]
        
        for cat_data in categorias_data:
            categoria, created = CategoriaProducto.objects.get_or_create(
                categoria=cat_data['categoria'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  - Creado: {categoria}')

    def create_productos(self):
        self.stdout.write('Creando productos...')
        
        # Obtener categorías
        quimicos = CategoriaProducto.objects.get(categoria='quimicos_limpieza')
        consumibles = CategoriaProducto.objects.get(categoria='consumibles_higiene')
        repuestos = CategoriaProducto.objects.get(categoria='repuestos_criticos')
        fluidos = CategoriaProducto.objects.get(categoria='fluidos_lubricantes')
        herramientas = CategoriaProducto.objects.get(categoria='herramientas_seguridad')
        
        productos_data = [
            # Productos Químicos de Limpieza
            {
                'nombre': 'Lejía (Hipoclorito)',
                'categoria': quimicos,
                'unidad': 'litro',
                'descripcion': 'Desinfectante general para piscinas y tratamiento de agua',
                'notas': 'Alto consumo diario. Mantener stock mínimo de 100L para crucero pequeño.'
            },
            {
                'nombre': 'Jabón Líquido Manos',
                'categoria': quimicos,
                'unidad': 'litro',
                'descripcion': 'Jabón para dispensadores en baños públicos y áreas de tripulación',
                'notas': 'Consumo muy alto. Revisar dispensadores semanalmente.'
            },
            {
                'nombre': 'Detergente Desengrasante',
                'categoria': quimicos,
                'unidad': 'litro',
                'descripcion': 'Detergente para cocinas y áreas de preparación de alimentos',
                'notas': 'Uso intensivo en cocinas y restaurantes.'
            },
            {
                'nombre': 'Desinfectante Multiusos',
                'categoria': quimicos,
                'unidad': 'litro',
                'descripcion': 'Desinfectante para limpieza diaria de camarotes y áreas comunes',
                'notas': 'Limpieza diaria de más de 900 camarotes en crucero pequeño.'
            },
            {
                'nombre': 'Cloro (Piscinas/Jacuzzis)',
                'categoria': quimicos,
                'unidad': 'kg',
                'descripcion': 'Cloro para mantenimiento de niveles en piscinas grandes',
                'notas': 'Dosis diaria para mantener niveles químicos en piscinas.'
            },
            {
                'nombre': 'Correctores de pH (Piscina)',
                'categoria': quimicos,
                'unidad': 'kg',
                'descripcion': 'Ácidos y bases para balancear químicos del agua',
                'notas': 'Ácido y base para balancear pH del agua de piscinas.'
            },
            {
                'nombre': 'Amonio Cuaternario',
                'categoria': quimicos,
                'unidad': 'litro',
                'descripcion': 'Desinfección de alto nivel en cocinas y áreas médicas',
                'notas': 'Desinfección de alto nivel en áreas críticas.'
            },
            
            # Consumibles de Higiene
            {
                'nombre': 'Papel Higiénico',
                'categoria': consumibles,
                'unidad': 'rollo',
                'descripcion': 'Papel higiénico para todos los baños del crucero',
                'notas': 'Consumo muy alto. Producto más crítico de esta categoría.'
            },
            {
                'nombre': 'Toallas de Papel',
                'categoria': consumibles,
                'unidad': 'rollo',
                'descripcion': 'Toallas para dispensadores en baños públicos y cocinas',
                'notas': 'Para dispensadores en baños públicos y cocinas.'
            },
            {
                'nombre': 'Papel Servilletas',
                'categoria': consumibles,
                'unidad': 'paquete',
                'descripcion': 'Servilletas para todos los restaurantes y bares',
                'notas': 'Paquetes de 500 unidades para restaurantes y bares.'
            },
            {
                'nombre': 'Gel Desinfectante',
                'categoria': consumibles,
                'unidad': 'litro',
                'descripcion': 'Gel para dispensadores en entradas de restaurantes',
                'notas': 'Recarga para dispensadores en entradas de restaurantes.'
            },
            
            # Repuestos Críticos
            {
                'nombre': 'Filtros Aceite (Motores/Gen.)',
                'categoria': repuestos,
                'unidad': 'unidad',
                'descripcion': 'Filtros de aceite para motores principales y generadores',
                'notas': 'Mayor número y tamaño en motores/generadores más grandes.'
            },
            {
                'nombre': 'Filtros Combustible',
                'categoria': repuestos,
                'unidad': 'unidad',
                'descripcion': 'Filtros para calidad del combustible en motores grandes',
                'notas': 'Crítico para calidad del combustible en motores grandes.'
            },
            {
                'nombre': 'Filtros Aire HVAC',
                'categoria': repuestos,
                'unidad': 'unidad',
                'descripcion': 'Filtros para sistema de aire acondicionado',
                'notas': 'Sistema HVAC mucho más grande y complejo en cruceros grandes.'
            },
            {
                'nombre': 'Filtros Agua (Osmosis)',
                'categoria': repuestos,
                'unidad': 'unidad',
                'descripcion': 'Filtros para planta de tratamiento de agua',
                'notas': 'Planta de tratamiento debe ser más grande y potente.'
            },
            {
                'nombre': 'Membranas Osmosis',
                'categoria': repuestos,
                'unidad': 'unidad',
                'descripcion': 'Membranas para sistema de osmosis inversa',
                'notas': 'Vida útil larga, pero se lleva un repuesto por sistema.'
            },
            {
                'nombre': 'Sensores Temperatura/Presión',
                'categoria': repuestos,
                'unidad': 'unidad',
                'descripcion': 'Sensores para motores principales y generadores',
                'notas': 'Para motores principales y generadores.'
            },
            {
                'nombre': 'Correas HVAC/Motores',
                'categoria': repuestos,
                'unidad': 'unidad',
                'descripcion': 'Correas para sistemas HVAC y motores',
                'notas': 'Stock de tamaños más comunes. Ajustado por complejidad.'
            },
            
            # Fluidos y Lubricantes
            {
                'nombre': 'Aceite Lubricante',
                'categoria': fluidos,
                'unidad': 'litro',
                'descripcion': 'Aceite lubricante para motores y generadores',
                'notas': 'Motores y generadores más grandes = mayor capacidad y consumo de aceite.'
            },
            {
                'nombre': 'Aceite Hidráulico',
                'categoria': fluidos,
                'unidad': 'litro',
                'descripcion': 'Aceite hidráulico para timones y estabilizadores',
                'notas': 'Timones y estabilizadores más grandes y potentes.'
            },
            
            # Herramientas y Seguridad
            {
                'nombre': 'Juegos de Llaves',
                'categoria': herramientas,
                'unidad': 'set',
                'descripcion': 'Juegos de llaves para equipos de mantenimiento',
                'notas': 'Para equipos de mantenimiento en diferentes cubiertas/zonas.'
            },
            {
                'nombre': 'Multímetros Digitales',
                'categoria': herramientas,
                'unidad': 'unidad',
                'descripcion': 'Multímetros para diagnóstico eléctrico',
                'notas': 'Herramienta esencial para diagnóstico eléctrico.'
            },
            {
                'nombre': 'Termómetros Infrarrojos',
                'categoria': herramientas,
                'unidad': 'unidad',
                'descripcion': 'Termómetros para medición de temperatura sin contacto',
                'notas': 'Medición de temperatura sin contacto en equipos.'
            },
            {
                'nombre': 'Guantes de Seguridad',
                'categoria': herramientas,
                'unidad': 'par',
                'descripcion': 'Guantes de seguridad para trabajos de mantenimiento',
                'notas': 'Consumible de seguridad. Reposición periódica.'
            },
            {
                'nombre': 'Gafas de Protección',
                'categoria': herramientas,
                'unidad': 'unidad',
                'descripcion': 'Gafas de protección para trabajos de mantenimiento',
                'notas': 'Consumible de seguridad. Reposición periódica.'
            }
        ]
        
        for prod_data in productos_data:
            producto, created = Producto.objects.get_or_create(
                nombre=prod_data['nombre'],
                defaults=prod_data
            )
            if created:
                self.stdout.write(f'  - Creado: {producto}')

    def create_ubicaciones(self):
        self.stdout.write('Creando ubicaciones de ejemplo...')
        
        # Crear algunas ubicaciones de ejemplo siguiendo el formato XABCD
        ubicaciones_data = [
            # Cubierta 2 - Habitaciones Babor
            {'cubierta': 2, 'uso': 0, 'identificador': 'A', 'numero': '01', 'descripcion': 'Habitación 201 - Babor'},
            {'cubierta': 2, 'uso': 0, 'identificador': 'A', 'numero': '02', 'descripcion': 'Habitación 202 - Babor'},
            {'cubierta': 2, 'uso': 0, 'identificador': 'B', 'numero': '01', 'descripcion': 'Habitación 203 - Babor'},
            
            # Cubierta 2 - Habitaciones Estribor
            {'cubierta': 2, 'uso': 1, 'identificador': 'A', 'numero': '01', 'descripcion': 'Habitación 204 - Estribor'},
            {'cubierta': 2, 'uso': 1, 'identificador': 'A', 'numero': '02', 'descripcion': 'Habitación 205 - Estribor'},
            
            # Cubierta 3 - Restaurantes
            {'cubierta': 3, 'uso': 2, 'identificador': 'A', 'numero': '01', 'descripcion': 'Restaurante Principal'},
            {'cubierta': 3, 'uso': 2, 'identificador': 'B', 'numero': '01', 'descripcion': 'Restaurante Especializado'},
            
            # Cubierta 4 - Bares/Cafés
            {'cubierta': 4, 'uso': 3, 'identificador': 'A', 'numero': '01', 'descripcion': 'Bar Principal'},
            {'cubierta': 4, 'uso': 3, 'identificador': 'B', 'numero': '01', 'descripcion': 'Café Lounge'},
            
            # Cubierta 5 - Almacenes
            {'cubierta': 5, 'uso': 4, 'identificador': 'A', 'numero': '01', 'descripcion': 'Almacén Principal'},
            {'cubierta': 5, 'uso': 4, 'identificador': 'B', 'numero': '01', 'descripcion': 'Almacén de Repuestos'},
            
            # Cubierta 6 - Entretenimiento
            {'cubierta': 6, 'uso': 5, 'identificador': 'A', 'numero': '01', 'descripcion': 'Teatro Principal'},
            {'cubierta': 6, 'uso': 5, 'identificador': 'B', 'numero': '01', 'descripcion': 'Gimnasio'},
            {'cubierta': 6, 'uso': 5, 'identificador': 'C', 'numero': '01', 'descripcion': 'Piscina Principal'},
        ]
        
        for ubi_data in ubicaciones_data:
            ubicacion, created = Ubicacion.objects.get_or_create(
                cubierta=ubi_data['cubierta'],
                uso=ubi_data['uso'],
                identificador=ubi_data['identificador'],
                numero=ubi_data['numero'],
                defaults={'descripcion': ubi_data['descripcion']}
            )
            if created:
                self.stdout.write(f'  - Creado: {ubicacion}')

    def create_tipos_equipos(self):
        self.stdout.write('Creando tipos de equipos...')
        
        tipos_data = [
            {
                'nombre': 'Motor Principal',
                'descripcion': 'Motores principales de propulsión del crucero',
                'requiere_mantenimiento_programado': True,
                'frecuencia_mantenimiento_dias': 30
            },
            {
                'nombre': 'Generador Eléctrico',
                'descripcion': 'Generadores de energía eléctrica',
                'requiere_mantenimiento_programado': True,
                'frecuencia_mantenimiento_dias': 15
            },
            {
                'nombre': 'Sistema HVAC',
                'descripcion': 'Sistema de calefacción, ventilación y aire acondicionado',
                'requiere_mantenimiento_programado': True,
                'frecuencia_mantenimiento_dias': 7
            },
            {
                'nombre': 'Sistema de Agua',
                'descripcion': 'Sistema de tratamiento y distribución de agua',
                'requiere_mantenimiento_programado': True,
                'frecuencia_mantenimiento_dias': 14
            },
            {
                'nombre': 'Sistema de Incendios',
                'descripcion': 'Sistema de detección y extinción de incendios',
                'requiere_mantenimiento_programado': True,
                'frecuencia_mantenimiento_dias': 30
            },
            {
                'nombre': 'Ascensores',
                'descripcion': 'Sistema de ascensores del crucero',
                'requiere_mantenimiento_programado': True,
                'frecuencia_mantenimiento_dias': 7
            },
            {
                'nombre': 'Sistema de Navegación',
                'descripcion': 'Equipos de navegación y comunicación',
                'requiere_mantenimiento_programado': True,
                'frecuencia_mantenimiento_dias': 30
            }
        ]
        
        for tipo_data in tipos_data:
            tipo, created = TipoEquipo.objects.get_or_create(
                nombre=tipo_data['nombre'],
                defaults=tipo_data
            )
            if created:
                self.stdout.write(f'  - Creado: {tipo}')

    def create_equipos(self):
        self.stdout.write('Creando equipos de ejemplo...')
        
        # Obtener ubicaciones y tipos
        almacen_principal = Ubicacion.objects.get(descripcion__icontains='Almacén Principal')
        motor_tipo = TipoEquipo.objects.get(nombre='Motor Principal')
        generador_tipo = TipoEquipo.objects.get(nombre='Generador Eléctrico')
        hvac_tipo = TipoEquipo.objects.get(nombre='Sistema HVAC')
        
        equipos_data = [
            {
                'codigo': 'MOT-001',
                'nombre': 'Motor Principal 1',
                'tipo_equipo': motor_tipo,
                'ubicacion': almacen_principal,
                'estado': 'operativo',
                'fecha_instalacion': datetime.now().date() - timedelta(days=365),
                'proxima_revision': timezone.now() + timedelta(days=15),
                'observaciones': 'Motor principal de estribor'
            },
            {
                'codigo': 'MOT-002',
                'nombre': 'Motor Principal 2',
                'tipo_equipo': motor_tipo,
                'ubicacion': almacen_principal,
                'estado': 'operativo',
                'fecha_instalacion': datetime.now().date() - timedelta(days=365),
                'proxima_revision': timezone.now() + timedelta(days=20),
                'observaciones': 'Motor principal de babor'
            },
            {
                'codigo': 'GEN-001',
                'nombre': 'Generador Principal',
                'tipo_equipo': generador_tipo,
                'ubicacion': almacen_principal,
                'estado': 'operativo',
                'fecha_instalacion': datetime.now().date() - timedelta(days=180),
                'proxima_revision': timezone.now() + timedelta(days=5),
                'observaciones': 'Generador de 2000kW'
            },
            {
                'codigo': 'HVAC-001',
                'nombre': 'Sistema HVAC Principal',
                'tipo_equipo': hvac_tipo,
                'ubicacion': almacen_principal,
                'estado': 'mantenimiento',
                'fecha_instalacion': datetime.now().date() - timedelta(days=90),
                'proxima_revision': timezone.now() + timedelta(days=2),
                'observaciones': 'En mantenimiento preventivo'
            }
        ]
        
        for eq_data in equipos_data:
            equipo, created = Equipo.objects.get_or_create(
                codigo=eq_data['codigo'],
                defaults=eq_data
            )
            if created:
                self.stdout.write(f'  - Creado: {equipo}')

    def create_superuser(self):
        self.stdout.write('Verificando superusuario...')
        
        # Nota: Para crear un superusuario, ejecuta: python manage.py createsuperuser
        self.stdout.write('  - Datos iniciales cargados correctamente')
