from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import ConfiguracionSistema, LogActividad, BackupSistema, ReporteSistema
from apps.cruceros.models import Crucero


class AdministracionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.crucero = Crucero.objects.create(
            nombre='Test Crucero',
            capacidad=1000
        )

    def test_configuracion_sistema_creation(self):
        """Test creación de configuración del sistema"""
        config = ConfiguracionSistema.objects.create(
            nombre='test_config',
            valor='test_value',
            descripcion='Test configuration'
        )
        self.assertEqual(str(config), 'test_config')
        self.assertEqual(config.nombre, 'test_config')
        self.assertEqual(config.valor, 'test_value')

    def test_log_actividad_creation(self):
        """Test creación de log de actividad"""
        log = LogActividad.objects.create(
            usuario=self.user,
            crucero=self.crucero,
            tipo_actividad='crear',
            descripcion='Test activity',
            modulo='test'
        )
        self.assertIn('crear', str(log))
        self.assertEqual(log.usuario, self.user)
        self.assertEqual(log.crucero, self.crucero)

    def test_backup_sistema_creation(self):
        """Test creación de backup del sistema"""
        backup = BackupSistema.objects.create(
            nombre_archivo='test_backup.sql',
            ruta_archivo='/backups/',
            tamaño_archivo=1024,
            usuario=self.user,
            descripcion='Test backup'
        )
        self.assertIn('test_backup.sql', str(backup))
        self.assertEqual(backup.estado, 'iniciado')

    def test_reporte_sistema_creation(self):
        """Test creación de reporte del sistema"""
        reporte = ReporteSistema.objects.create(
            nombre='Test Report',
            tipo_reporte='ventas',
            usuario=self.user,
            crucero=self.crucero
        )
        self.assertEqual(str(reporte), 'Test Report - Reporte de Ventas')
        self.assertEqual(reporte.tipo_reporte, 'ventas')


class AdministracionViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.crucero = Crucero.objects.create(
            nombre='Test Crucero',
            capacidad=1000
        )

    def test_dashboard_administracion_requires_login(self):
        """Test que el dashboard requiere login"""
        url = reverse('administracion:dashboard', args=[self.crucero.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_dashboard_administracion_with_login(self):
        """Test acceso al dashboard con login"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('administracion:dashboard', args=[self.crucero.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Administración')

    def test_configuracion_sistema_view(self):
        """Test vista de configuración del sistema"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('administracion:configuracion', args=[self.crucero.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Configuración del Sistema')

    def test_logs_actividad_view(self):
        """Test vista de logs de actividad"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('administracion:logs', args=[self.crucero.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Logs de Actividad')

    def test_respaldos_view(self):
        """Test vista de respaldos"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('administracion:respaldos', args=[self.crucero.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Respaldos del Sistema')

    def test_reportes_view(self):
        """Test vista de reportes"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('administracion:reportes', args=[self.crucero.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reportes del Sistema')

    def test_estadisticas_view(self):
        """Test vista de estadísticas"""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('administracion:estadisticas', args=[self.crucero.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Estadísticas del Sistema')
