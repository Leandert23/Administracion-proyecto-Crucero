from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('<int:crucero_id>', views.dashboard_empresa, name='dashboard'),
    path('api/cruceros-dashboard/', views.cruceros_dashboard_data, name='cruceros_dashboard_data'),
    path('gestion-roles/', views.gestion_roles, name='gestion_roles'),
    # Agregar URLs para manejar solicitudes de compra
    path('api/purchase-requests/<int:request_id>/approve/', views.approve_purchase_request, name='approve_purchase_request'),
    path('api/purchase-requests/<int:request_id>/reject/', views.reject_purchase_request, name='reject_purchase_request'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)