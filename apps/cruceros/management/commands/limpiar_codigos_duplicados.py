from django.core.management.base import BaseCommand
from django.db import transaction
from apps.cruceros.models import Crucero
from apps.cruceros.forms import generar_codigo_identificacion

class Command(BaseCommand):
    help = 'Limpia códigos de identificación duplicados en la base de datos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué cambios se harían sin ejecutarlos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN: No se realizarán cambios reales'))
        
        # Encontrar códigos duplicados
        codigos_duplicados = self.encontrar_codigos_duplicados()
        
        if not codigos_duplicados:
            self.stdout.write(self.style.SUCCESS('No se encontraron códigos duplicados'))
            return
        
        self.stdout.write(f'Se encontraron {len(codigos_duplicados)} códigos duplicados:')
        
        for codigo, cruceros in codigos_duplicados.items():
            self.stdout.write(f'\nCódigo duplicado: {codigo}')
            for crucero in cruceros:
                self.stdout.write(f'  - ID: {crucero.id}, Nombre: {crucero.nombre}, Tipo: {crucero.tipo_crucero}')
        
        if not dry_run:
            self.corregir_codigos_duplicados(codigos_duplicados)
        else:
            self.stdout.write(self.style.WARNING('\nPara ejecutar los cambios, ejecuta el comando sin --dry-run'))

    def encontrar_codigos_duplicados(self):
        """Encuentra códigos de identificación duplicados"""
        from django.db.models import Count
        
        # Obtener códigos que aparecen más de una vez
        codigos_duplicados = (
            Crucero.objects
            .values('codigo_identificacion')
            .annotate(count=Count('codigo_identificacion'))
            .filter(count__gt=1)
        )
        
        resultado = {}
        for item in codigos_duplicados:
            codigo = item['codigo_identificacion']
            cruceros = Crucero.objects.filter(codigo_identificacion=codigo).order_by('id')
            resultado[codigo] = list(cruceros)
        
        return resultado

    def corregir_codigos_duplicados(self, codigos_duplicados):
        """Corrige los códigos duplicados generando nuevos códigos únicos"""
        with transaction.atomic():
            for codigo_original, cruceros in codigos_duplicados.items():
                # Mantener el primer crucero con el código original
                crucero_principal = cruceros[0]
                self.stdout.write(f'Manteniendo código {codigo_original} para: {crucero_principal.nombre}')
                
                # Generar nuevos códigos para los demás
                for crucero in cruceros[1:]:
                    try:
                        nuevo_codigo = generar_codigo_identificacion(crucero.tipo_crucero)
                        crucero.codigo_identificacion = nuevo_codigo
                        crucero.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✓ {crucero.nombre}: {codigo_original} → {nuevo_codigo}'
                            )
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'  ✗ Error al corregir {crucero.nombre}: {str(e)}'
                            )
                        )
        
        self.stdout.write(self.style.SUCCESS('\n¡Corrección completada!'))
