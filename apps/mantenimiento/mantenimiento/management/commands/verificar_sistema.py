"""
Comando optimizado para verificar el sistema
"""
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from decimal import Decimal

from ....models import (
    Ubicacion, Equipo, TareaMantenimiento, Personal,
    InventarioProducto, MedicionPiscina, Piscina
)


class Command(BaseCommand):
    help = 'Verificación optimizada del sistema de mantenimiento'
    
    def add_arguments(self, parser):
        parser.add_argument('--fix', action='store_true', help='Corregir problemas automáticamente')
        parser.add_argument('--quick', action='store_true', help='Verificación rápida solo errores críticos')
    
    def handle(self, *args, **options):
        self.fix_mode = options['fix']
        self.quick_mode = options['quick']
        self.errores = []
        self.warnings = []
        self.correcciones = []
        
        self.stdout.write(self.style.SUCCESS('🔍 Verificando sistema optimizado...'))
        
        # Verificaciones críticas
        self.verificar_criticos()
        
        if not self.quick_mode:
            # Verificaciones completas
            self.verificar_completo()
        
        self.mostrar_resultados()
    
    def verificar_criticos(self):
        """Verificaciones críticas optimizadas"""
        
        # 1. Stock negativo (crítico)
        stock_negativo = InventarioProducto.objects.filter(stock_actual__lt=0)
        for inv in stock_negativo:
            self.errores.append(f'❌ CRÍTICO: Stock negativo {inv.producto.nombre}')
            if self.fix_mode:
                inv.stock_actual = Decimal('0')
                inv.save()
                self.correcciones.append(f'✅ Corregido stock negativo: {inv.producto.nombre}')
        
        # 2. Personal en múltiples tareas (crítico)
        from django.db.models import Count
        personal_sobrecargado = Personal.objects.annotate(
            tareas_activas=Count('asignacionpersonal', filter=models.Q(
                asignacionpersonal__estado='en_progreso',
                asignacionpersonal__tarea__estado='en_progreso'
            ))
        ).filter(tareas_activas__gt=1)
        
        for personal in personal_sobrecargado:
            self.errores.append(f'❌ CRÍTICO: {personal.nombre} en múltiples tareas activas')
        
        # 3. Mediciones críticas de piscinas
        piscinas_criticas = []
        for piscina in Piscina.objects.all():
            ultima_medicion = piscina.mediciones.first()
            if ultima_medicion:
                ph = ultima_medicion.ph
                cloro = ultima_medicion.cloro_mg_l
                
                if ph and (ph < Decimal('6.8') or ph > Decimal('8.2')):
                    piscinas_criticas.append(f'{piscina.nombre}: pH crítico ({ph})')
                
                if cloro and (cloro < Decimal('0.5') or cloro > Decimal('5')):
                    piscinas_criticas.append(f'{piscina.nombre}: Cloro crítico ({cloro})')
        
        for alerta in piscinas_criticas:
            self.errores.append(f'❌ CRÍTICO: Piscina {alerta}')
    
    def verificar_completo(self):
        """Verificaciones completas"""
        
        # Tareas vencidas
        tareas_vencidas = TareaMantenimiento.objects.filter(
            estado__in=['creada', 'planificada', 'asignada'],
            fecha_programada__lt=timezone.now()
        ).count()
        
        if tareas_vencidas > 0:
            self.warnings.append(f'⚠️ {tareas_vencidas} tareas vencidas')
        
        # Equipos sin mantenimiento programado
        equipos_sin_mantenimiento = Equipo.objects.filter(
            proxima_revision__isnull=True,
            estado='operativo'
        ).count()
        
        if equipos_sin_mantenimiento > 0:
            self.warnings.append(f'⚠️ {equipos_sin_mantenimiento} equipos sin mantenimiento programado')
        
        # Stock bajo
        stock_bajo = InventarioProducto.objects.filter(
            stock_actual__lte=models.F('stock_minimo')
        ).count()
        
        if stock_bajo > 0:
            self.warnings.append(f'⚠️ {stock_bajo} productos con stock bajo')
    
    def mostrar_resultados(self):
        """Muestra resultados optimizados"""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 RESULTADOS DE VERIFICACIÓN')
        self.stdout.write('='*50)
        
        if self.errores:
            self.stdout.write(self.style.ERROR(f'\n❌ ERRORES CRÍTICOS ({len(self.errores)}):'))
            for error in self.errores[:10]:  # Mostrar solo los primeros 10
                self.stdout.write(self.style.ERROR(f'  {error}'))
        
        if self.warnings and not self.quick_mode:
            self.stdout.write(self.style.WARNING(f'\n⚠️ ADVERTENCIAS ({len(self.warnings)}):'))
            for warning in self.warnings[:10]:
                self.stdout.write(self.style.WARNING(f'  {warning}'))
        
        if self.correcciones:
            self.stdout.write(self.style.SUCCESS(f'\n✅ CORRECCIONES ({len(self.correcciones)}):'))
            for correccion in self.correcciones:
                self.stdout.write(self.style.SUCCESS(f'  {correccion}'))
        
        if not self.errores and not self.warnings:
            self.stdout.write(self.style.SUCCESS('\n🎉 ¡Sistema íntegro y optimizado!'))
        
        # Resumen
        self.stdout.write(f'\n📈 Resumen:')
        self.stdout.write(f'  • Errores críticos: {len(self.errores)}')
        self.stdout.write(f'  • Advertencias: {len(self.warnings)}')
        self.stdout.write(f'  • Correcciones: {len(self.correcciones)}')
        
        if self.errores and not self.fix_mode:
            self.stdout.write(self.style.WARNING('\n💡 Use --fix para corregir automáticamente'))
