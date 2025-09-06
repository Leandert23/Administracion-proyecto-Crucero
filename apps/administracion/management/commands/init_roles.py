from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.administracion.models import Modulo, Rol, UsuarioRol

class Command(BaseCommand):
    help = 'Inicializa los módulos y roles básicos del sistema'

    def handle(self, *args, **options):
        self.stdout.write('Inicializando módulos y roles del sistema...')
        
        # Crear módulos básicos
        modulos_data = [
            {
                'nombre': 'administracion',
                'descripcion': 'Módulo de administración general del sistema de cruceros'
            },
            {
                'nombre': 'cruceros',
                'descripcion': 'Módulo de gestión de cruceros'
            },
            {
                'nombre': 'almacen',
                'descripcion': 'Módulo de gestión de almacén e inventario'
            },
            {
                'nombre': 'bares_snacks',
                'descripcion': 'Módulo de gestión de bares y snacks'
            },
        ]
        
        for modulo_data in modulos_data:
            modulo, created = Modulo.objects.get_or_create(
                nombre=modulo_data['nombre'],
                defaults=modulo_data
            )
            if created:
                self.stdout.write(f'  ✓ Módulo creado: {modulo.nombre}')
            else:
                self.stdout.write(f'  - Módulo ya existe: {modulo.nombre}')
        
        # Crear roles básicos para cada módulo
        roles_data = [
            # Administración
            {
                'nombre': 'Administrador General',
                'tipo': 'admin',
                'modulo': 'administracion',
                'descripcion': 'Administrador con acceso completo al módulo de administración'
            },
            {
                'nombre': 'Analista Financiero',
                'tipo': 'especialista',
                'modulo': 'administracion',
                'descripcion': 'Especialista en análisis financiero y presupuestos'
            },
            {
                'nombre': 'Consultor Administrativo',
                'tipo': 'lector',
                'modulo': 'administracion',
                'descripcion': 'Acceso de solo lectura a información administrativa'
            },
            
            # Cruceros
            {
                'nombre': 'Administrador de Cruceros',
                'tipo': 'admin',
                'modulo': 'cruceros',
                'descripcion': 'Administrador del módulo de cruceros'
            },
            {
                'nombre': 'Capitán',
                'tipo': 'editor',
                'modulo': 'cruceros',
                'descripcion': 'Capitán de crucero con permisos de edición'
            },
            {
                'nombre': 'Tripulante',
                'tipo': 'lector',
                'modulo': 'cruceros',
                'descripcion': 'Tripulante con acceso de lectura'
            },
            
            # Almacén
            {
                'nombre': 'Administrador de Almacén',
                'tipo': 'admin',
                'modulo': 'almacen',
                'descripcion': 'Administrador del módulo de almacén'
            },
            {
                'nombre': 'Encargado de Inventario',
                'tipo': 'editor',
                'modulo': 'almacen',
                'descripcion': 'Encargado de gestionar el inventario'
            },
            {
                'nombre': 'Operario de Almacén',
                'tipo': 'lector',
                'modulo': 'almacen',
                'descripcion': 'Operario con acceso de lectura al inventario'
            },
            
            # Bares y Snacks
            {
                'nombre': 'Administrador de Bares',
                'tipo': 'admin',
                'modulo': 'bares_snacks',
                'descripcion': 'Administrador del módulo de bares y snacks'
            },
            {
                'nombre': 'Gerente de Bar',
                'tipo': 'editor',
                'modulo': 'bares_snacks',
                'descripcion': 'Gerente de bar con permisos de edición'
            },
            {
                'nombre': 'Bartender',
                'tipo': 'lector',
                'modulo': 'bares_snacks',
                'descripcion': 'Bartender con acceso de lectura'
            },
        ]
        
        for rol_data in roles_data:
            try:
                modulo = Modulo.objects.get(nombre=rol_data['modulo'])
                rol, created = Rol.objects.get_or_create(
                    nombre=rol_data['nombre'],
                    modulo=modulo,
                    defaults={
                        'tipo': rol_data['tipo'],
                        'descripcion': rol_data['descripcion']
                    }
                )
                if created:
                    self.stdout.write(f'  ✓ Rol creado: {rol.nombre} ({modulo.nombre})')
                else:
                    self.stdout.write(f'  - Rol ya existe: {rol.nombre} ({modulo.nombre})')
            except Modulo.DoesNotExist:
                self.stdout.write(f'  ✗ Error: Módulo {rol_data["modulo"]} no encontrado')
        
        # Crear un superusuario si no existe
        if not User.objects.filter(is_superuser=True).exists():
            self.stdout.write('\nNo se encontró ningún superusuario.')
            self.stdout.write('Para crear un superusuario, ejecuta: python manage.py createsuperuser')
        else:
            # Asignar rol de administrador al primer superusuario
            superuser = User.objects.filter(is_superuser=True).first()
            try:
                modulo_admin = Modulo.objects.get(nombre='administracion')
                rol_admin = Rol.objects.get(nombre='Administrador General', modulo=modulo_admin)
                
                usuario_rol, created = UsuarioRol.objects.get_or_create(
                    usuario=superuser,
                    rol=rol_admin,
                    defaults={'asignado_por': superuser}
                )
                
                if created:
                    self.stdout.write(f'  ✓ Rol de administrador asignado a: {superuser.username}')
                else:
                    self.stdout.write(f'  - Usuario {superuser.username} ya tiene el rol de administrador')
                    
            except (Modulo.DoesNotExist, Rol.DoesNotExist):
                self.stdout.write('  ✗ Error: No se pudo asignar el rol de administrador')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Inicialización de roles completada exitosamente'))
        self.stdout.write('\nPróximos pasos:')
        self.stdout.write('1. Ejecuta las migraciones: python manage.py migrate')
        self.stdout.write('2. Crea un superusuario: python manage.py createsuperuser')
        self.stdout.write('3. Accede al panel de administración para gestionar roles')
