from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.administracion.models import Modulo, Rol, UsuarioRol, Administracion
from apps.cruceros.models import Crucero

class Command(BaseCommand):
    help = 'Inicializa los datos necesarios para el dashboard de administración'

    def handle(self, *args, **options):
        self.stdout.write('Inicializando datos del dashboard...')
        
        # Crear módulo de administración
        modulo, created = Modulo.objects.get_or_create(
            nombre='administracion',
            defaults={'descripcion': 'Módulo de administración del sistema'}
        )
        if created:
            self.stdout.write('✅ Módulo de administración creado')
        else:
            self.stdout.write('ℹ️  Módulo de administración ya existe')
        
        # Crear rol de administrador
        rol, created = Rol.objects.get_or_create(
            nombre='admin',
            modulo=modulo,
            defaults={
                'tipo': 'admin',
                'descripcion': 'Administrador del sistema',
                'permisos': {'all': True}
            }
        )
        if created:
            self.stdout.write('✅ Rol de administrador creado')
        else:
            self.stdout.write('ℹ️  Rol de administrador ya existe')
        
        # Asignar rol al superusuario admin
        try:
            admin_user = User.objects.get(username='admin')
            usuario_rol, created = UsuarioRol.objects.get_or_create(
                usuario=admin_user,
                rol=rol,
                defaults={'activo': True}
            )
            if created:
                self.stdout.write('✅ Rol asignado al usuario admin')
            else:
                self.stdout.write('ℹ️  Usuario admin ya tiene el rol asignado')
        except User.DoesNotExist:
            self.stdout.write('⚠️  Usuario admin no encontrado. Ejecuta: python manage.py createsuperuser')
        
        # Crear datos de administración si no existen
        if not Administracion.objects.exists():
            # Obtener el primer crucero o crear uno de ejemplo
            crucero = Crucero.objects.first()
            if not crucero:
                self.stdout.write('⚠️  No hay cruceros en la base de datos')
                return
            
            admin_data = Administracion.objects.create(
                crucero=crucero,
                costos_totales=50000.00,
                ganancias_totales=75000.00,
                presupuesto_estimado=100000.00,
                precio_combustible=2.50,
                num_pasajeros_actual=150,
                num_empleados_actual=50
            )
            self.stdout.write('✅ Datos de administración creados')
        else:
            self.stdout.write('ℹ️  Datos de administración ya existen')
        
        self.stdout.write(self.style.SUCCESS('¡Inicialización completada!'))
        self.stdout.write('Puedes acceder al dashboard en: http://127.0.0.1:8000/administracion/')
        self.stdout.write('Usuario: admin, Contraseña: admin123')
