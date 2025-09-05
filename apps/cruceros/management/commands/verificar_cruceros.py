from django.core.management.base import BaseCommand
from apps.cruceros.models import Crucero
from django.db.models import Count

class Command(BaseCommand):
    help = 'Verifica el estado de los cruceros en la base de datos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== VERIFICACIÓN DE CRUCEROS ===\n'))
        
        # Contar total de cruceros
        total_cruceros = Crucero.objects.count()
        self.stdout.write(f'Total de cruceros: {total_cruceros}')
        
        # Verificar códigos duplicados
        codigos_duplicados = self.verificar_codigos_duplicados()
        if codigos_duplicados:
            self.stdout.write(self.style.ERROR(f'\n⚠️  CÓDIGOS DUPLICADOS ENCONTRADOS: {len(codigos_duplicados)}'))
            for codigo, cruceros in codigos_duplicados.items():
                self.stdout.write(f'  Código: {codigo}')
                for crucero in cruceros:
                    self.stdout.write(f'    - ID: {crucero.id}, Nombre: {crucero.nombre}')
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ No hay códigos duplicados'))
        
        # Mostrar cruceros por tipo
        self.mostrar_cruceros_por_tipo()
        
        # Mostrar códigos existentes
        self.mostrar_codigos_existentes()

    def verificar_codigos_duplicados(self):
        """Verifica si hay códigos de identificación duplicados"""
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

    def mostrar_cruceros_por_tipo(self):
        """Muestra la distribución de cruceros por tipo"""
        self.stdout.write('\n--- CRUCEROS POR TIPO ---')
        tipos = Crucero.objects.values('tipo_crucero').annotate(count=Count('tipo_crucero'))
        for tipo in tipos:
            self.stdout.write(f'  {tipo["tipo_crucero"]}: {tipo["count"]} cruceros')

    def mostrar_codigos_existentes(self):
        """Muestra todos los códigos de identificación existentes"""
        self.stdout.write('\n--- CÓDIGOS DE IDENTIFICACIÓN EXISTENTES ---')
        cruceros = Crucero.objects.all().order_by('codigo_identificacion')
        for crucero in cruceros:
            self.stdout.write(f'  {crucero.codigo_identificacion}: {crucero.nombre} ({crucero.tipo_crucero})')
