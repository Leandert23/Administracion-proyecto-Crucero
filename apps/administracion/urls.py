from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.dashboard_empresa, name='dashboard'),
    path('api/cruceros-dashboard/', views.cruceros_dashboard_data, name='cruceros_dashboard_data'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)