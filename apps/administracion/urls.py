from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('empresa/', views.dashboard_empresa, name='dashboard'),
    path('<int:crucero_id>/', views.cruceros_dashboard_data, name='cruceros_dashboard_data'),
    # Agregar URLs para manejar solicitudes de compra
    path('api/purchase-requests/<int:request_id>/approve/', views.approve_purchase_request, name='approve_purchase_request'),
    path('api/purchase-requests/<int:request_id>/reject/', views.reject_purchase_request, name='reject_purchase_request'),
    # Formulario de solicitud de mantenimiento para habitaciones
    path('solicitar-mantenimiento-habitacion/', views.solicitar_mantenimiento_habitacion, name='solicitar_mantenimiento_habitacion'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)