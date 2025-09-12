from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('empresa/', views.dashboard_empresa, name='dashboard'),
    path('<int:crucero_id>/', views.cruceros_dashboard_data, name='cruceros_dashboard_data'),
    # Formulario de solicitud de mantenimiento para habitaciones
    path('solicitar-mantenimiento-habitacion/', views.solicitar_mantenimiento_habitacion, name='solicitar_mantenimiento_habitacion'),
    # Endpoint para procesar decisiones de solicitudes de compra
    path('decision-solicitud/', views.decision_solicitud_view, name='decision_solicitud'),
    # Formulario para registrar habitaciones
    path('registrar-habitacion/', views.registrar_habitacion, name='registrar_habitacion'),
    # Lista de habitaciones registradas
    path('listar-habitaciones/', views.listar_habitaciones, name='listar_habitaciones'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)