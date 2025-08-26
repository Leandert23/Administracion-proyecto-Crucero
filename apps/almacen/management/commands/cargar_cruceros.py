import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from typing import Dict, List, Optional

from apps.almacen.models import Crucero, TipoHabitacion, Habitacion

# Configuración de directorios y archivos
DIRECTORIO_FIXTURES = Path(__file__).resolve().parents[3] / 'almacen' / 'fixtures'
ARCHIVO_CRUCEROS = DIRECTORIO_FIXTURES / 'cruceros.json'
ARCHIVO_TIPOS_HABITACIONES = DIRECTORIO_FIXTURES / 'tiposHabitaciones.json'

# Nombres de tipos de habitación en español
NOMBRES_TIPOS_HABITACION = {
    'basico_sencillo_vista': 'Camarote básico sencillo vista mar',
    'basico_sencillo_interior': 'Camarote básico sencillo interior',
    'basico_doble_vista': 'Camarote básico doble vista mar',
    'basico_doble_interior': 'Camarote básico doble interior',
    'premium_sencillo_vista': 'Camarote premium sencillo vista mar',
    'premium_sencillo_interior': 'Camarote premium sencillo interior',
    'premium_doble_vista': 'Camarote premium doble vista mar',
    'premium_doble_interior': 'Camarote premium doble interior',
}

# Configuración de distribución de habitaciones por crucero
DISTRIBUCION_CRUCEROS = {
    'VSN-001': {
        'basico': {
            'pisos': [2, 3, 4, 5],
            'sencillos': 125,
            'dobles': 25,
        },
        'premium': {
            'pisos': [6, 7, 8],
            'sencillos': 50,
            'dobles': 25,
        },
        'porcentaje_vista': 0.6
    },
    'VGR-001': {
        'basico': {
            'pisos': list(range(2, 7)),
            'sencillos': 200,
            'dobles': 40,
        },
        'premium': {
            'pisos_7_8': {
                'pisos': [7, 8],
                'sencillos': 75,
                'dobles': 38,
            },
            'pisos_9_10': {
                'pisos': [9, 10],
                'sencillos': 75,
                'dobles': 37,
            }
        },
        'porcentaje_vista': 0.6
    },
    'OAS-001': {
        'basico': {
            'pisos': list(range(2, 8)),
            'sencillos': 250,
            'dobles': 50,
        },
        'premium': {
            'pisos': list(range(8, 13)),
            'sencillos': 90,
            'dobles': 45,
        },
        'porcentaje_vista': 0.6
    }
}


class Command(BaseCommand):
    help = "Carga cruceros y tipos de habitación desde archivos JSON de manera segura y repetible."

    def add_arguments(self, parser):
        opciones = [
            ('--reiniciar', {'action': 'store_true', 'help': 'Elimina todos los datos existentes antes de cargar nuevos'}),
            ('--solo-cruceros', {'action': 'store_true', 'help': 'Carga solamente los cruceros, omite tipos de habitación'}),
            ('--solo-tipos', {'action': 'store_true', 'help': 'Carga solamente tipos de habitación, omite cruceros'}),
            ('--prueba-seca', {'action': 'store_true', 'help': 'Muestra lo que haría sin guardar cambios reales'}),
            ('--actualizar', {'action': 'store_true', 'help': 'Actualiza registros existentes en lugar de omitirlos'}),
            ('--generar-habitaciones-primer-crucero', {'action': 'store_true', 
            'help': 'Genera habitaciones para el primer crucero (VSN-001)'}),
            ('--generar-habitaciones-segundo-crucero', {'action': 'store_true', 
            'help': 'Genera habitaciones para el segundo crucero (VGR-001)'}),
            ('--generar-habitaciones-tercer-crucero', {'action': 'store_true', 
            'help': 'Genera habitaciones para el tercer crucero (OAS-001)'}),
            ('--forzar-habitaciones', {'action': 'store_true', 
            'help': 'Elimina habitaciones existentes y genera nuevas'}),
            ('--sin-habitaciones', {'action': 'store_true', 'help': 'Omite la generación automática de habitaciones'}),
        ]
        for bandera, argumentos in opciones:
            parser.add_argument(bandera, **argumentos)

    def handle(self, *args, **opciones):
        self.validar_opciones(opciones)
        self.validar_archivos(opciones)
        
        self.stdout.write('Iniciando proceso de carga...')

        try:
            with transaction.atomic():
                self.ejecutar_operaciones(opciones)
                if opciones['prueba_seca']:
                    raise CommandError('Prueba seca: Los cambios no se han guardado permanentemente')
        except CommandError as error:
            if 'Prueba seca' in str(error):
                self.stdout.write(self.style.WARNING(str(error)))
            else:
                raise

        self.stdout.write(self.style.SUCCESS('Proceso completado exitosamente.'))

    def validar_opciones(self, opciones):
        """Verifica que las opciones proporcionadas sean coherentes"""
        if opciones['solo_cruceros'] and opciones['solo_tipos']:
            raise CommandError('No se pueden usar --solo-cruceros y --solo-tipos simultáneamente')

    def validar_archivos(self, opciones):
        """Confirma que los archivos necesarios existan"""
        if not ARCHIVO_CRUCEROS.exists() and not opciones['solo_tipos']:
            raise CommandError(f'No se encuentra el archivo: {ARCHIVO_CRUCEROS}')
        if not ARCHIVO_TIPOS_HABITACIONES.exists() and not opciones['solo_cruceros']:
            raise CommandError(f'No se encuentra el archivo: {ARCHIVO_TIPOS_HABITACIONES}')

    def ejecutar_operaciones(self, opciones):
        """Coordina la ejecución de todas las operaciones según las opciones"""
        es_prueba_seca = opciones['prueba_seca']
        
        if opciones['reiniciar']:
            self.reiniciar_datos(es_prueba_seca, opciones['solo_cruceros'], opciones['solo_tipos'])
        
        if not opciones['solo_tipos']:
            self.cargar_cruceros(es_prueba_seca, opciones['actualizar'])
        
        if not opciones['solo_cruceros']:
            self.cargar_tipos_habitacion(es_prueba_seca, opciones['actualizar'])
        
        if not opciones['sin_habitaciones']:
            self.generar_habitaciones_automaticamente(opciones)
        else:
            self.stdout.write('Generación de habitaciones omitida (--sin-habitaciones).')

    def generar_habitaciones_automaticamente(self, opciones):
        """Gestiona la generación automática de habitaciones según las opciones"""
        orden_cruceros = ['VSN-001', 'VGR-001', 'OAS-001']
        codigos_cruceros_seleccionados = []
        
        if opciones['generar_habitaciones_primer_crucero']:
            codigos_cruceros_seleccionados.append('VSN-001')
        if opciones['generar_habitaciones_segundo_crucero']:
            codigos_cruceros_seleccionados.append('VGR-001')
        if opciones['generar_habitaciones_tercer_crucero']:
            codigos_cruceros_seleccionados.append('OAS-001')
        
        if not codigos_cruceros_seleccionados:
            self.stdout.write('Generando habitaciones para todos los cruceros...')
            codigos_cruceros_seleccionados = orden_cruceros
        
        cruceros_procesados = set()
        for codigo_crucero in codigos_cruceros_seleccionados:
            if codigo_crucero in cruceros_procesados:
                continue
            cruceros_procesados.add(codigo_crucero)
            self.generar_habitaciones_para_crucero(codigo_crucero, opciones['prueba_seca'], opciones['forzar_habitaciones'])

    def cargar_archivo_json(self, ruta_archivo: Path):
        """Carga y devuelve el contenido de un archivo JSON"""
        with ruta_archivo.open(encoding='utf-8') as archivo:
            return json.load(archivo)

    def reiniciar_datos(self, es_prueba_seca: bool, solo_cruceros: bool, solo_tipos: bool):
        """Elimina datos existentes según las opciones especificadas"""
        if not solo_tipos:
            self.stdout.write('Eliminando cruceros existentes...')
            if not es_prueba_seca:
                Crucero.objects.all().delete()
        
        if not solo_cruceros:
            self.stdout.write('Eliminando tipos de habitación existentes...')
            if not es_prueba_seca:
                TipoHabitacion.objects.all().delete()

    def cargar_cruceros(self, es_prueba_seca: bool, actualizar_existentes: bool):
        """Carga los cruceros desde el archivo JSON a la base de datos"""
        datos = self.cargar_archivo_json(ARCHIVO_CRUCEROS)
        cruceros_creados = 0
        cruceros_actualizados = 0
        
        for entrada in datos:
            campos = entrada['fields']
            codigo_identificacion = campos['codigo_identificacion']
            
            crucero, fue_creado = Crucero.objects.get_or_create(
                codigo_identificacion=codigo_identificacion, 
                defaults=campos
            )
            
            if fue_creado:
                cruceros_creados += 1
            elif actualizar_existentes:
                for atributo, valor in campos.items():
                    setattr(crucero, atributo, valor)
                if not es_prueba_seca:
                    crucero.save()
                    cruceros_actualizados += 1
        
        self.stdout.write(f'Cruceros creados: {cruceros_creados}, actualizados: {cruceros_actualizados}')

    def cargar_tipos_habitacion(self, es_prueba_seca: bool, actualizar_existentes: bool):
        """Carga los tipos de habitación desde el archivo JSON a la base de datos"""
        datos = self.cargar_archivo_json(ARCHIVO_TIPOS_HABITACIONES)
        tipos_creados = 0
        tipos_actualizados = 0
        
        for entrada in datos:
            campos = entrada['fields']
            nombre_tipo = campos['nombre']
            
            tipo_habitacion, fue_creado = TipoHabitacion.objects.get_or_create(
                nombre=nombre_tipo, 
                defaults=campos
            )
            
            if fue_creado:
                tipos_creados += 1
            elif actualizar_existentes:
                for atributo, valor in campos.items():
                    setattr(tipo_habitacion, atributo, valor)
                if not es_prueba_seca:
                    tipo_habitacion.save()
                    tipos_actualizados += 1
        
        self.stdout.write(f'Tipos de habitación creados: {tipos_creados}, actualizados: {tipos_actualizados}')

    def obtener_tipos_habitacion(self) -> Optional[Dict[str, TipoHabitacion]]:
        """Obtiene todos los tipos de habitación necesarios desde la base de datos"""
        try:
            return {
                clave: TipoHabitacion.objects.get(nombre=nombre)
                for clave, nombre in NOMBRES_TIPOS_HABITACION.items()
            }
        except TipoHabitacion.DoesNotExist as error:
            self.stdout.write(f'Error: No se encontró un tipo de habitación necesario - {error}')
            return None

    def generar_habitaciones_para_crucero(self, codigo_crucero: str, es_prueba_seca: bool, forzar_generacion: bool):
        """Genera habitaciones para un crucero específico según su distribución"""
        crucero = self.obtener_crucero_por_codigo(codigo_crucero)
        if not crucero:
            return
        
        if not self.validar_habitaciones_existentes(crucero, forzar_generacion, es_prueba_seca):
            return
        
        tipos_habitacion = self.obtener_tipos_habitacion()
        if not tipos_habitacion:
            return
        
        lista_habitaciones = self.generar_habitaciones_segun_distribucion(crucero, tipos_habitacion, codigo_crucero)
        
        if es_prueba_seca:
            self.stdout.write(f'PRUEBA SECA: Se crearían {len(lista_habitaciones)} habitaciones para {crucero.nombre}.')
            return
        
        self.guardar_habitaciones(lista_habitaciones, crucero)

    def obtener_crucero_por_codigo(self, codigo_identificacion: str) -> Optional[Crucero]:
        """Busca y devuelve un crucero por su código de identificación"""
        try:
            return Crucero.objects.get(codigo_identificacion=codigo_identificacion)
        except Crucero.DoesNotExist:
            self.stdout.write(f'Crucero {codigo_identificacion} no encontrado. No se crearán habitaciones.')
            return None

    def validar_habitaciones_existentes(self, crucero: Crucero, forzar_generacion: bool, es_prueba_seca: bool) -> bool:
        """Verifica y maneja las habitaciones existentes para un crucero"""
        cantidad_habitaciones_existentes = Habitacion.objects.filter(crucero=crucero).count()
        
        if cantidad_habitaciones_existentes and not forzar_generacion:
            self.stdout.write(
                f'Ya existen {cantidad_habitaciones_existentes} habitaciones para {crucero.nombre}. '
                f'Use --forzar-habitaciones para regenerarlas.'
            )
            return False
        
        if cantidad_habitaciones_existentes and forzar_generacion and not es_prueba_seca:
            habitaciones_eliminadas = Habitacion.objects.filter(crucero=crucero).delete()[0]
            self.stdout.write(f'Eliminadas {habitaciones_eliminadas} habitaciones existentes de {crucero.nombre}.')
        
        return True

    def generar_habitaciones_segun_distribucion(self, crucero: Crucero, tipos_habitacion: Dict[str, TipoHabitacion], 
                                                codigo_crucero: str) -> List[Habitacion]:
        """Genera habitaciones según la distribución específica de cada crucero"""
        configuracion = DISTRIBUCION_CRUCEROS[codigo_crucero]
        habitaciones = []
        
        if codigo_crucero == 'VSN-001':
            habitaciones.extend(self.generar_habitaciones_crucero_vsn_001(crucero, tipos_habitacion, configuracion))
        elif codigo_crucero == 'VGR-001':
            habitaciones.extend(self.generar_habitaciones_crucero_vgr_001(crucero, tipos_habitacion, configuracion))
        elif codigo_crucero == 'OAS-001':
            habitaciones.extend(self.generar_habitaciones_crucero_oas_001(crucero, tipos_habitacion, configuracion))
        
        return habitaciones

    def generar_habitaciones_crucero_vsn_001(self, crucero: Crucero, tipos_habitacion: Dict[str, TipoHabitacion], 
                                            configuracion: Dict) -> List[Habitacion]:
        """Genera habitaciones para el crucero VSN-001 según su distribución"""
        habitaciones = []
        porcentaje_vista = configuracion['porcentaje_vista']
        
        # Habitaciones básicas
        for numero_piso in configuracion['basico']['pisos']:
            habitaciones.extend(self.generar_habitaciones_para_piso(
                crucero, numero_piso, tipos_habitacion, 
                configuracion['basico']['sencillos'], 
                configuracion['basico']['dobles'], 
                porcentaje_vista, 'basico'
            ))
        
        # Habitaciones premium
        for numero_piso in configuracion['premium']['pisos']:
            habitaciones.extend(self.generar_habitaciones_para_piso(
                crucero, numero_piso, tipos_habitacion, 
                configuracion['premium']['sencillos'], 
                configuracion['premium']['dobles'], 
                porcentaje_vista, 'premium'
            ))
        
        return habitaciones

    def generar_habitaciones_crucero_vgr_001(self, crucero: Crucero, tipos_habitacion: Dict[str, TipoHabitacion], 
                                            configuracion: Dict) -> List[Habitacion]:
        """Genera habitaciones para el crucero VGR-001 según su distribución"""
        habitaciones = []
        porcentaje_vista = configuracion['porcentaje_vista']
        
        # Pisos básicos (2-6)
        for numero_piso in configuracion['basico']['pisos']:
            habitaciones.extend(self.generar_habitaciones_para_piso(
                crucero, numero_piso, tipos_habitacion, 
                configuracion['basico']['sencillos'], 
                configuracion['basico']['dobles'], 
                porcentaje_vista, 'basico'
            ))
        
        # Pisos premium 7-8
        for numero_piso in configuracion['premium']['pisos_7_8']['pisos']:
            habitaciones.extend(self.generar_habitaciones_para_piso(
                crucero, numero_piso, tipos_habitacion, 
                configuracion['premium']['pisos_7_8']['sencillos'], 
                configuracion['premium']['pisos_7_8']['dobles'], 
                porcentaje_vista, 'premium'
            ))
        
        # Pisos premium 9-10
        for numero_piso in configuracion['premium']['pisos_9_10']['pisos']:
            habitaciones.extend(self.generar_habitaciones_para_piso(
                crucero, numero_piso, tipos_habitacion, 
                configuracion['premium']['pisos_9_10']['sencillos'], 
                configuracion['premium']['pisos_9_10']['dobles'], 
                porcentaje_vista, 'premium'
            ))
        
        return habitaciones

    def generar_habitaciones_crucero_oas_001(self, crucero: Crucero, tipos_habitacion: Dict[str, TipoHabitacion], 
                                            configuracion: Dict) -> List[Habitacion]:
        """Genera habitaciones para el crucero OAS-001 según su distribución"""
        habitaciones = []
        porcentaje_vista = configuracion['porcentaje_vista']
        
        # Pisos básicos (2-7)
        for numero_piso in configuracion['basico']['pisos']:
            habitaciones.extend(self.generar_habitaciones_para_piso(
                crucero, numero_piso, tipos_habitacion, 
                configuracion['basico']['sencillos'], 
                configuracion['basico']['dobles'], 
                porcentaje_vista, 'basico'
            ))
        
        # Pisos premium (8-12)
        for numero_piso in configuracion['premium']['pisos']:
            habitaciones.extend(self.generar_habitaciones_para_piso(
                crucero, numero_piso, tipos_habitacion, 
                configuracion['premium']['sencillos'], 
                configuracion['premium']['dobles'], 
                porcentaje_vista, 'premium'
            ))
        
        return habitaciones

    def generar_habitaciones_para_piso(self, crucero: Crucero, numero_piso: int, tipos_habitacion: Dict[str, TipoHabitacion],
                                    total_sencillos: int, total_dobles: int, porcentaje_vista: float,
                                    categoria: str) -> List[Habitacion]:
        """Genera todas las habitaciones para un piso específico"""
        habitaciones_del_piso = []
        
        # Calcular distribución entre vistas al mar e interiores
        sencillos_vista = round(total_sencillos * porcentaje_vista)
        sencillos_interior = total_sencillos - sencillos_vista
        dobles_vista = round(total_dobles * porcentaje_vista)
        dobles_interior = total_dobles - dobles_vista
        
        # Definir tipos de habitación según categoría
        tipo_sencillo_vista = f'{categoria}_sencillo_vista'
        tipo_sencillo_interior = f'{categoria}_sencillo_interior'
        tipo_doble_vista = f'{categoria}_doble_vista'
        tipo_doble_interior = f'{categoria}_doble_interior'
        
        # Generar habitaciones para cada tipo
        habitaciones_del_piso.extend(self.crear_lote_habitaciones_piso(crucero, numero_piso, tipos_habitacion[tipo_sencillo_vista], sencillos_vista))
        habitaciones_del_piso.extend(self.crear_lote_habitaciones_piso(crucero, numero_piso, tipos_habitacion[tipo_sencillo_interior], sencillos_interior))
        habitaciones_del_piso.extend(self.crear_lote_habitaciones_piso(crucero, numero_piso, tipos_habitacion[tipo_doble_vista], dobles_vista))
        habitaciones_del_piso.extend(self.crear_lote_habitaciones_piso(crucero, numero_piso, tipos_habitacion[tipo_doble_interior], dobles_interior))
        
        return habitaciones_del_piso

    def crear_lote_habitaciones_piso(self, crucero: Crucero, numero_cubierta: int, tipo_habitacion: TipoHabitacion, 
                                    cantidad_habitaciones: int) -> List[Habitacion]:
        """Crea un lote de habitaciones para un piso, distribuyéndolas entre babor y estribor"""
        if cantidad_habitaciones <= 0:
            return []
        
        habitaciones = []
        habitaciones_babor = cantidad_habitaciones // 2 + (cantidad_habitaciones % 2)
        habitaciones_estribor = cantidad_habitaciones - habitaciones_babor
        
        # Crear habitaciones en el lado de babor
        for numero_habitacion in range(1, habitaciones_babor + 1):
            habitaciones.append(Habitacion(
                crucero=crucero,
                tipo_habitacion=tipo_habitacion,
                cubierta=numero_cubierta,
                lado='babor',
                codigo_ubicacion=f"{numero_cubierta:02d}0{numero_habitacion:02d}",
                numero=f"{numero_habitacion:02d}"
            ))

        # Crear habitaciones en el lado de estribor
        for numero_habitacion in range(1, habitaciones_estribor + 1):
            habitaciones.append(Habitacion(
                crucero=crucero,
                tipo_habitacion=tipo_habitacion,
                cubierta=numero_cubierta,
                lado='estribor',
                codigo_ubicacion=f"{numero_cubierta:02d}1{numero_habitacion:02d}",
                numero=f"{numero_habitacion:02d}"
            ))
        
        return habitaciones

    def guardar_habitaciones(self, lista_habitaciones: List[Habitacion], crucero: Crucero):
        """Guarda las habitaciones en la base de datos de manera eficiente"""
        tamaño_lote = 1000
        for indice_inicio in range(0, len(lista_habitaciones), tamaño_lote):
            lote_habitaciones = lista_habitaciones[indice_inicio:indice_inicio + tamaño_lote]
            Habitacion.objects.bulk_create(lote_habitaciones) #
        
        self.stdout.write(f'Habitaciones creadas para {crucero.nombre}: {len(lista_habitaciones)}')