from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.administracion.models import ConfiguracionSistema, LogActividad, BackupSistema, ReporteSistema
from apps.cruceros.models import Crucero
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de ejemplo para el módulo de administración'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de ejemplo para administración...')
        
        # Crear configuraciones de ejemplo
        configuraciones = [
            ('nombre_empresa', 'Cruceros del Caribe S.A.', 'Nombre de la empresa'),
            ('email_contacto', 'admin@cruceros.com', 'Email de contacto principal'),
            ('telefono_emergencia', '+1-800-CRUISER', 'Teléfono de emergencia 24/7'),
            ('moneda_base', 'USD', 'Moneda base del sistema'),
            ('zona_horaria', 'America/Caribbean', 'Zona horaria del sistema'),
            ('max_reservas_dia', '50', 'Máximo de reservas por día'),
            ('tiempo_limpieza_cabinas', '2', 'Tiempo en horas para limpieza de cabinas'),
        ]
        
        for nombre, valor, descripcion in configuraciones:
            config, created = ConfiguracionSistema.objects.get_or_create(
                nombre=nombre,
                defaults={'valor': valor, 'descripcion': descripcion}
            )
            if created:
                self.stdout.write(f'✓ Configuración creada: {nombre}')
        
        # Obtener o crear crucero
        crucero, created = Crucero.objects.get_or_create(
            id=1,
            defaults={
                'nombre': 'Caribbean Dream',
                'capacidad': 2000,
                'descripcion': 'Crucero de lujo con todas las comodidades'
            }
        )
        
        # Crear usuario de ejemplo si no existe
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@cruceros.com',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write('✓ Usuario admin creado (usuario: admin, contraseña: admin123)')
        
        # Crear logs de actividad de ejemplo
        tipos_actividad = ['login', 'logout', 'crear', 'editar', 'eliminar', 'configurar', 'reporte', 'backup']
        modulos = ['administracion', 'ventas', 'almacen', 'cruceros', 'reservaciones', 'entretenimiento']
        descripciones = [
            'Usuario inició sesión en el sistema',
            'Usuario cerró sesión',
            'Nuevo producto creado en inventario',
            'Información de crucero actualizada',
            'Reserva cancelada por cliente',
            'Configuración de sistema modificada',
            'Reporte de ventas generado',
            'Respaldo automático completado',
            'Nueva actividad de entretenimiento agregada',
            'Stock de producto actualizado'
        ]
        
        # Crear logs de los últimos 7 días
        for i in range(50):
            fecha = timezone.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            LogActividad.objects.create(
                usuario=user if random.choice([True, False]) else None,
                crucero=crucero,
                tipo_actividad=random.choice(tipos_actividad),
                descripcion=random.choice(descripciones),
                modulo=random.choice(modulos),
                fecha_hora=fecha,
                ip_address=f'192.168.1.{random.randint(1, 254)}',
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
        
        self.stdout.write('✓ 50 logs de actividad creados')
        
        # Crear respaldos de ejemplo
        estados = ['completado', 'en_proceso', 'fallido']
        for i in range(5):
            fecha = timezone.now() - timedelta(days=i*2)
            estado = random.choice(estados)
            
            backup = BackupSistema.objects.create(
                nombre_archivo=f'backup_caribbean_dream_{fecha.strftime("%Y%m%d_%H%M%S")}.sql',
                ruta_archivo='/backups/',
                tamaño_archivo=random.randint(1024*1024, 100*1024*1024),  # 1MB a 100MB
                estado=estado,
                fecha_creacion=fecha,
                fecha_completado=fecha + timedelta(hours=1) if estado == 'completado' else None,
                usuario=user,
                descripcion=f'Respaldo {"automático" if i % 2 == 0 else "manual"} del sistema'
            )
        
        self.stdout.write('✓ 5 respaldos de ejemplo creados')
        
        # Crear reportes de ejemplo
        tipos_reporte = ['ventas', 'inventario', 'usuarios', 'actividades', 'financiero']
        nombres_reporte = [
            'Reporte de Ventas Mensual',
            'Análisis de Inventario',
            'Estadísticas de Usuarios',
            'Log de Actividades del Sistema',
            'Reporte Financiero Trimestral'
        ]
        
        for i in range(8):
            fecha = timezone.now() - timedelta(days=i*3)
            tipo = random.choice(tipos_reporte)
            nombre = random.choice(nombres_reporte)
            
            ReporteSistema.objects.create(
                nombre=f'{nombre} - {fecha.strftime("%B %Y")}',
                tipo_reporte=tipo,
                parametros={
                    'fecha_inicio': (fecha - timedelta(days=30)).strftime('%Y-%m-%d'),
                    'fecha_fin': fecha.strftime('%Y-%m-%d'),
                    'formato': random.choice(['pdf', 'excel', 'csv'])
                },
                archivo_generado=f'/reports/{nombre.lower().replace(" ", "_")}_{fecha.strftime("%Y%m%d")}.pdf' if random.choice([True, False]) else '',
                fecha_generacion=fecha,
                usuario=user,
                crucero=crucero
            )
        
        self.stdout.write('✓ 8 reportes de ejemplo creados')
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 ¡Datos de ejemplo creados exitosamente!\n'
                'Ahora puedes probar el módulo de administración en:\n'
                'http://127.0.0.1:8000/administracion/1/\n\n'
                'Usuario de prueba: admin\n'
                'Contraseña: admin123'
            )
        )
