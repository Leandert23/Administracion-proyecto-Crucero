from django.urls import path
from . import views

app_name = 'administracion'

urlpatterns = [
    # Vista principal
    path('<int:crucero_id>/', views.dashboard_administracion, name='dashboard'),
    
    # Configuración del sistema
    path('<int:crucero_id>/configuracion/', views.configuracion_sistema, name='configuracion'),
    
    # Logs de actividad
    path('<int:crucero_id>/logs/', views.logs_actividad, name='logs'),
    
    # Respaldos
    path('<int:crucero_id>/respaldos/', views.respaldos, name='respaldos'),
    
    # Reportes
    path('<int:crucero_id>/reportes/', views.reportes, name='reportes'),
    
    # Estadísticas
    path('<int:crucero_id>/estadisticas/', views.estadisticas_sistema, name='estadisticas'),
]
