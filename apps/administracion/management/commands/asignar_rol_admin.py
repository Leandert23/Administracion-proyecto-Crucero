from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.administracion.models import UsuarioRol, Rol, Modulo

class Command(BaseCommand):
    help = 'Asigna rol de administrador a un usuario específico'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nombre de usuario al que asignar el rol')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            # Obtener el usuario
            user = User.objects.get(username=username)
            self.stdout.write(f'Usuario encontrado: {user.username}')
            
            # Obtener el módulo de administración
            modulo_admin = Modulo.objects.get(nombre='administracion')
            
            # Obtener el rol de administrador general
            rol_admin = Rol.objects.get(nombre='Administrador General', modulo=modulo_admin)
            
            # Asignar el rol
            usuario_rol, created = UsuarioRol.objects.get_or_create(
                usuario=user,
                rol=rol_admin,
                defaults={'asignado_por': user}
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Rol de administrador asignado exitosamente a {username}'))
            else:
                self.stdout.write(f'⚠ El usuario {username} ya tenía el rol de administrador')
            
            # Verificar el estado del rol
            self.stdout.write(f'Estado del rol: Activo={usuario_rol.activo}, Válido={usuario_rol.esta_activo}')
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'✗ Usuario {username} no encontrado'))
        except Modulo.DoesNotExist:
            self.stdout.write(self.style.ERROR('✗ Módulo de administración no encontrado'))
        except Rol.DoesNotExist:
            self.stdout.write(self.style.ERROR('✗ Rol de Administrador General no encontrado'))
