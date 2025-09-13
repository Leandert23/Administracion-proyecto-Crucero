"""
URL configuration for Administrador_Cruceros project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from apps.administracion.views import LoginPersonalizado,logout_usuario, registro_usuario
from apps.usuarios.views import custom_login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.cruceros.urls')),
    path('almacen/', include('apps.almacen.urls')),
    path('entretenimiento/', include('apps.entretenimiento.urls')),
    path('mantenimiento/', include('apps.mantenimiento.urls')),
    path('reservaciones/', include('apps.reservaciones.urls')),
    path('ventas/', include('apps.ventas.urls')),
    path("compras/", include(("apps.compras.urls", "compras"), namespace="compras")),
    path('dashboard/', include(('apps.administracion.urls', 'administracion'), namespace='administracion')),
    path('usuarios/', include('apps.usuarios.urls')),
    path("login/", custom_login, name="login"),
    path("logout/", logout_usuario, name="logout"),
    path('registro/', registro_usuario, name='registro'),
    # Página accesible cuando un usuario no tiene permisos
    path('acceso-denegado/', TemplateView.as_view(template_name='administracion/sin_permisos.html'), name='acceso_denegado'),
    path('servicio-medico/', include('apps.servicio_medico.urls')),
    path('bares-snacks/', include(('apps.bares_snacks.urls', 'bares_snacks'), namespace='bares_snacks')),
    path('recursos-humanos/', include(('apps.recursos_humanos.urls', 'recursos_humanos'), namespace='recursos_humanos')),
    path("restaurantes/", include(("apps.restaurante.urls", "restaurantes"), namespace="restaurantes")),
    path('embarcaciones/', include('apps.creador_embarcaciones.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
