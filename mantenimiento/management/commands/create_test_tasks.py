from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from mantenimiento.models import (
    TareaMantenimiento,
    TipoCrucero,
    Ubicacion,
    Equipo,
    Personal
)

class Command(BaseCommand):
    help = 'Crea tareas de prueba desde diferentes módulos para visualizar el sistema universal'

    def handle(self, *args, **options):
        self.stdout.write('Creando tareas de prueba desde diferentes módulos...')

        # Crear usuario de prueba si no existe
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Usuario',
                'last_name': 'Prueba'
            }
        )
        if created:
            user.set_password('test123')
            user.save()
            self.stdout.write('  - Usuario de prueba creado')

        # Crear tareas de ejemplo desde diferentes módulos
        self.create_tasks_from_modules(user)

        self.stdout.write(
            self.style.SUCCESS('Tareas de prueba creadas exitosamente!')
        )

    def create_tasks_from_modules(self, user):
        """Crear tareas de ejemplo desde diferentes módulos"""

        # Definir tareas de ejemplo por módulo
        tasks_data = [
            # Servicios Médicos
            {
                'titulo': 'Reparar equipo de rayos X en sala de emergencias',
                'descripcion': 'El equipo de rayos X presenta fallos en el sistema de calibración. No se puede utilizar para diagnósticos de emergencia.',
                'tipo': 'correctivo',
                'prioridad': 'critica',
                'ubicacion_solicitud': 'Cubierta 1 - Sala de Emergencias',
                'equipo_afectado': 'Equipo de Rayos X Philips',
                'tiempo_estimado': 4.0,
                'modulo_origen': 'servicios_medicos',
                'origen_url': '/servicios-medicos/equipos/rx-001',
                'estado': 'en_progreso'
            },
            {
                'titulo': 'Mantenimiento preventivo desfibriladores',
                'descripcion': 'Revisión mensual de baterías y funcionamiento de desfibriladores en todo el barco.',
                'tipo': 'preventivo',
                'prioridad': 'alta',
                'ubicacion_solicitud': 'Múltiples ubicaciones - Servicio Médico',
                'equipo_afectado': 'Desfibriladores portátiles',
                'tiempo_estimado': 2.5,
                'modulo_origen': 'servicios_medicos',
                'origen_url': '/servicios-medicos/mantenimiento/',
                'estado': 'asignada'
            },

            # Restaurante
            {
                'titulo': 'Reparar refrigerador industrial en cocina principal',
                'descripcion': 'El refrigerador industrial presenta fallos en el sistema de enfriamiento. Temperatura interna elevada afectando conservación de alimentos.',
                'tipo': 'correctivo',
                'prioridad': 'alta',
                'ubicacion_solicitud': 'Cubierta 3 - Cocina Principal',
                'equipo_afectado': 'Refrigerador Industrial Whirlpool',
                'tiempo_estimado': 3.0,
                'modulo_origen': 'restaurante',
                'origen_url': '/restaurante/equipos/refrigerador-001',
                'estado': 'creada'
            },
            {
                'titulo': 'Limpieza y mantenimiento de campana extractora',
                'descripcion': 'La campana extractora de la cocina presenta acumulación de grasa y disminución en la potencia de extracción.',
                'tipo': 'limpieza',
                'prioridad': 'media',
                'ubicacion_solicitud': 'Cubierta 3 - Cocina Principal',
                'equipo_afectado': 'Campana Extractora Industrial',
                'tiempo_estimado': 1.5,
                'modulo_origen': 'restaurante',
                'origen_url': '/restaurante/mantenimiento/cocina/',
                'estado': 'planificada'
            },

            # Almacén
            {
                'titulo': 'Reparar montacargas eléctrico en almacén principal',
                'descripcion': 'El montacargas presenta fallos en el motor eléctrico y no se eleva correctamente. Afectando operaciones de carga/descarga.',
                'tipo': 'correctivo',
                'prioridad': 'alta',
                'ubicacion_solicitud': 'Cubierta 5 - Almacén Principal',
                'equipo_afectado': 'Montacargas Eléctrico BT',
                'tiempo_estimado': 4.5,
                'modulo_origen': 'almacen',
                'origen_url': '/almacen/equipos/montacargas-001',
                'estado': 'esperando_materiales'
            },
            {
                'titulo': 'Inspección mensual de estanterías metálicas',
                'descripcion': 'Revisión de estabilidad y fijaciones de estanterías en almacén principal. Verificar carga máxima soportada.',
                'tipo': 'inspeccion',
                'prioridad': 'media',
                'ubicacion_solicitud': 'Cubierta 5 - Almacén Principal',
                'equipo_afectado': 'Sistema de Estanterías',
                'tiempo_estimado': 2.0,
                'modulo_origen': 'almacen',
                'origen_url': '/almacen/mantenimiento/estanterias/',
                'estado': 'creada'
            },

            # Recursos Humanos
            {
                'titulo': 'Reparar aire acondicionado en sala de reuniones',
                'descripcion': 'El sistema de aire acondicionado no enfría correctamente, temperatura ambiente elevada afecta reuniones del personal.',
                'tipo': 'correctivo',
                'prioridad': 'media',
                'ubicacion_solicitud': 'Cubierta 2 - Sala de Reuniones RRHH',
                'equipo_afectado': 'Aire Acondicionado Daikin',
                'tiempo_estimado': 2.0,
                'modulo_origen': 'recursos_humanos',
                'origen_url': '/rrhh/oficina/reuniones/',
                'estado': 'asignada'
            },

            # Entretenimiento
            {
                'titulo': 'Reparar sistema de sonido en teatro principal',
                'descripcion': 'El sistema de sonido presenta distorsión en altavoces principales. Afectando calidad de espectáculos.',
                'tipo': 'correctivo',
                'prioridad': 'alta',
                'ubicacion_solicitud': 'Cubierta 6 - Teatro Principal',
                'equipo_afectado': 'Sistema de Sonido JBL',
                'tiempo_estimado': 3.5,
                'modulo_origen': 'entretenimiento',
                'origen_url': '/entretenimiento/teatro/sonido/',
                'estado': 'en_progreso'
            },
            {
                'titulo': 'Mantenimiento preventivo máquinas recreativas',
                'descripcion': 'Revisión mensual de funcionamiento de máquinas recreativas y slots en área de juegos.',
                'tipo': 'preventivo',
                'prioridad': 'baja',
                'ubicacion_solicitud': 'Cubierta 6 - Área de Juegos',
                'equipo_afectado': 'Máquinas Recreativas',
                'tiempo_estimado': 1.0,
                'modulo_origen': 'entretenimiento',
                'origen_url': '/entretenimiento/juegos/mantenimiento/',
                'estado': 'creada'
            },

            # Bares
            {
                'titulo': 'Reparar máquina de hielo en bar principal',
                'descripcion': 'La máquina de hielo produce hielo de mala calidad y en cantidades insuficientes para el servicio.',
                'tipo': 'correctivo',
                'prioridad': 'media',
                'ubicacion_solicitud': 'Cubierta 4 - Bar Principal',
                'equipo_afectado': 'Máquina de Hielo Scotsman',
                'tiempo_estimado': 2.5,
                'modulo_origen': 'bares',
                'origen_url': '/bares/equipos/maquina-hielo-001',
                'estado': 'planificada'
            },

            # Ventas
            {
                'titulo': 'Reparar terminal punto de venta en recepción',
                'descripcion': 'El terminal de punto de venta presenta fallos en el lector de tarjetas y no procesa pagos correctamente.',
                'tipo': 'correctivo',
                'prioridad': 'critica',
                'ubicacion_solicitud': 'Cubierta 1 - Recepción Principal',
                'equipo_afectado': 'Terminal POS Verifone',
                'tiempo_estimado': 1.5,
                'modulo_origen': 'ventas',
                'origen_url': '/ventas/terminales/pos-001',
                'estado': 'esperando_personal'
            },

            # Compras
            {
                'titulo': 'Mantenimiento sistema de inventario electrónico',
                'descripcion': 'El sistema de inventario electrónico presenta lentitud en las consultas y posibles fallos en la base de datos.',
                'tipo': 'correctivo',
                'prioridad': 'alta',
                'ubicacion_solicitud': 'Cubierta 2 - Oficina de Compras',
                'equipo_afectado': 'Servidor de Inventario',
                'tiempo_estimado': 3.0,
                'modulo_origen': 'compras',
                'origen_url': '/compras/sistema/inventario/',
                'estado': 'creada'
            }
        ]

        # Obtener tipo de crucero por defecto (mediano)
        tipo_crucero_default = TipoCrucero.objects.filter(tipo='mediano').first()
        if not tipo_crucero_default:
            tipo_crucero_default = TipoCrucero.objects.first()

        # Obtener ubicación por defecto
        ubicacion_default = Ubicacion.objects.first()

        # Crear tareas
        for i, task_data in enumerate(tasks_data):
            # Calcular fecha programada (algunas en el pasado, otras en el futuro)
            if task_data['estado'] in ['creada', 'planificada']:
                fecha_programada = timezone.now() + timedelta(hours=random.randint(1, 24))
            elif task_data['estado'] == 'asignada':
                fecha_programada = timezone.now() + timedelta(hours=random.randint(1, 12))
            elif task_data['estado'] == 'en_progreso':
                fecha_programada = timezone.now() - timedelta(hours=random.randint(1, 6))
            else:
                fecha_programada = timezone.now() + timedelta(hours=random.randint(1, 48))

            # Crear tarea
            tarea, created = TareaMantenimiento.objects.get_or_create(
                titulo=task_data['titulo'],
                defaults={
                    'descripcion': task_data['descripcion'],
                    'tipo': task_data['tipo'],
                    'prioridad': task_data['prioridad'],
                    'estado': task_data['estado'],
                    'ubicacion': ubicacion_default,
                    'tipo_crucero': tipo_crucero_default,
                    'creado_por': user,
                    'fecha_programada': fecha_programada,
                    'tiempo_estimado_horas': task_data['tiempo_estimado'],
                    'observaciones': f"{task_data['ubicacion_solicitud']} - {task_data['equipo_afectado']}",
                    'modulo_origen': task_data['modulo_origen'],
                    'origen_url': task_data['origen_url'],
                }
            )

            if created:
                # Si la tarea está en progreso o completada, actualizar fechas
                if task_data['estado'] == 'en_progreso':
                    tarea.fecha_inicio = timezone.now() - timedelta(hours=random.randint(1, 4))
                    tarea.save()

                self.stdout.write(f'  - Creada tarea: {task_data["titulo"]} ({task_data["modulo_origen"]})')
            else:
                self.stdout.write(f'  - Tarea ya existe: {task_data["titulo"]}')

        self.stdout.write(f'  - Total tareas procesadas: {len(tasks_data)}')
