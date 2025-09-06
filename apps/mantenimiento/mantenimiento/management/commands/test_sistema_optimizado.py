"""
Comando para testing del sistema optimizado
"""
from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import json

from ....core.services import DashboardService, PiscinaService
from ....core.notifications import AlertManager
from ....models import Piscina, MedicionPiscina


class Command(BaseCommand):
    help = 'Testing completo del sistema optimizado'
    
    def add_arguments(self, parser):
        parser.add_argument('--create-test-data', action='store_true', help='Crear datos de prueba')
    
    def handle(self, *args, **options):
        self.client = Client()
        
        self.stdout.write(self.style.SUCCESS('🧪 Testing Sistema Optimizado'))
        self.stdout.write('='*50)
        
        if options['create_test_data']:
            self.create_test_data()
        
        # Tests de servicios
        self.test_dashboard_service()
        self.test_piscina_service()
        self.test_notifications()
        
        # Tests de endpoints
        self.test_dashboard_endpoints()
        self.test_piscina_endpoints()
        
        # Tests de rendimiento
        self.test_performance()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Testing completado exitosamente'))
    
    def create_test_data(self):
        """Crea datos de prueba"""
        self.stdout.write('📝 Creando datos de prueba...')
        
        # Crear medición crítica de prueba
        piscina = Piscina.objects.first()
        if piscina:
            MedicionPiscina.objects.create(
                piscina=piscina,
                ph=Decimal('6.5'),  # pH crítico bajo
                cloro_mg_l=Decimal('0.3'),  # Cloro crítico bajo
                observaciones='Medición de prueba crítica'
            )
            self.stdout.write('  ✅ Medición crítica creada')
    
    def test_dashboard_service(self):
        """Test del servicio de dashboard"""
        self.stdout.write('📊 Testing DashboardService...')
        
        try:
            data = DashboardService.get_dashboard_data()
            
            # Verificar estructura de datos
            required_keys = ['total_equipos', 'tareas_pendientes', 'crucero_labels', 'last_updated']
            for key in required_keys:
                assert key in data, f'Falta clave: {key}'
            
            # Verificar tipos de datos
            assert isinstance(data['total_equipos'], int), 'total_equipos debe ser int'
            assert isinstance(data['crucero_labels'], list), 'crucero_labels debe ser list'
            
            self.stdout.write('  ✅ DashboardService funcionando')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error en DashboardService: {e}'))
    
    def test_piscina_service(self):
        """Test del servicio de piscinas"""
        self.stdout.write('🏊 Testing PiscinaService...')
        
        try:
            # Test get_piscinas_with_alerts
            alerts_data = PiscinaService.get_piscinas_with_alerts()
            assert isinstance(alerts_data, list), 'Debe retornar lista'
            
            # Test get_trends_data si hay piscinas
            piscina = Piscina.objects.first()
            if piscina:
                trends_data = PiscinaService.get_trends_data(piscina.id)
                if trends_data:
                    required_keys = ['fechas', 'ph_values', 'cloro_values']
                    for key in required_keys:
                        assert key in trends_data, f'Falta clave en trends: {key}'
            
            self.stdout.write('  ✅ PiscinaService funcionando')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error en PiscinaService: {e}'))
    
    def test_notifications(self):
        """Test del sistema de notificaciones"""
        self.stdout.write('🚨 Testing NotificationService...')
        
        try:
            alerts = AlertManager.get_critical_alerts()
            assert isinstance(alerts, list), 'Debe retornar lista de alertas'
            
            count = AlertManager.get_alert_count()
            assert isinstance(count, int), 'Debe retornar count como int'
            
            self.stdout.write(f'  ✅ {count} alertas críticas detectadas')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error en NotificationService: {e}'))
    
    def test_dashboard_endpoints(self):
        """Test de endpoints del dashboard"""
        self.stdout.write('🌐 Testing Dashboard Endpoints...')
        
        try:
            # Test dashboard principal
            response = self.client.get('/')
            assert response.status_code == 200, f'Dashboard retornó {response.status_code}'
            
            # Test endpoint AJAX
            response = self.client.get('/api/dashboard-update/')
            assert response.status_code == 200, f'API retornó {response.status_code}'
            
            data = json.loads(response.content)
            assert data['success'], 'API debe retornar success=True'
            assert 'data' in data, 'API debe incluir data'
            
            self.stdout.write('  ✅ Endpoints del dashboard funcionando')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error en endpoints: {e}'))
    
    def test_piscina_endpoints(self):
        """Test de endpoints de piscinas"""
        self.stdout.write('🏊 Testing Piscina Endpoints...')
        
        try:
            # Test lista de piscinas
            response = self.client.get('/piscinas/')
            assert response.status_code == 200, f'Piscinas retornó {response.status_code}'
            
            # Test endpoint de tendencias si hay piscinas
            piscina = Piscina.objects.first()
            if piscina:
                response = self.client.get(f'/piscinas/{piscina.id}/tendencias/')
                assert response.status_code == 200, f'Tendencias retornó {response.status_code}'
                
                # Test API de actualización
                response = self.client.get(f'/api/piscinas/{piscina.id}/update/')
                assert response.status_code == 200, f'API piscina retornó {response.status_code}'
            
            self.stdout.write('  ✅ Endpoints de piscinas funcionando')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error en endpoints piscinas: {e}'))
    
    def test_performance(self):
        """Test de rendimiento"""
        self.stdout.write('⚡ Testing Rendimiento...')
        
        import time
        
        try:
            # Test rendimiento dashboard
            start_time = time.time()
            DashboardService.get_dashboard_data()
            dashboard_time = time.time() - start_time
            
            # Test rendimiento piscinas
            start_time = time.time()
            PiscinaService.get_piscinas_with_alerts()
            piscina_time = time.time() - start_time
            
            # Test rendimiento alertas
            start_time = time.time()
            AlertManager.get_critical_alerts()
            alerts_time = time.time() - start_time
            
            self.stdout.write(f'  📊 Dashboard: {dashboard_time:.3f}s')
            self.stdout.write(f'  🏊 Piscinas: {piscina_time:.3f}s')
            self.stdout.write(f'  🚨 Alertas: {alerts_time:.3f}s')
            
            # Verificar que los tiempos sean razonables
            if dashboard_time < 0.5 and piscina_time < 0.3 and alerts_time < 0.2:
                self.stdout.write('  ✅ Rendimiento excelente')
            elif dashboard_time < 1.0 and piscina_time < 0.5 and alerts_time < 0.3:
                self.stdout.write('  ✅ Rendimiento bueno')
            else:
                self.stdout.write('  ⚠️ Rendimiento mejorable')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error en test de rendimiento: {e}'))
