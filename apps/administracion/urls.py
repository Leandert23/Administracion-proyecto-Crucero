from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('empresa/', views.dashboard_empresa, name='dashboard'),
    path('<int:crucero_id>/', views.cruceros_dashboard_data, name='cruceros_dashboard_data'),
    # Formulario de solicitud de mantenimiento para habitaciones
    path('decision-solicitud/', views.decision_solicitud_view, name='decision_solicitud'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)