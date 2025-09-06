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
from apps.administracion.views import LoginPersonalizado,logout_usuario, registro_usuario

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.cruceros.urls')),
    path('almacen/', include('apps.almacen.urls')),
    path('entretenimiento/', include('apps.entretenimiento.urls')),
    path('mantenimiento/', include('apps.mantenimiento.mantenimiento.urls')),
    path('reservaciones/', include('apps.reservaciones.urls')),
    path('ventas/', include('apps.ventas.urls')),
    path("compras/", include(("apps.compras.urls", "compras"), namespace="compras")),
    path('dashboard/', include(('apps.administracion.urls', 'administracion'), namespace='administracion')),
    path("login/", LoginPersonalizado.as_view(), name="login"),
    path("logout/", logout_usuario, name="logout"),
    path('registro/', registro_usuario, name='registro'),
    path('servicio-medico/', include('apps.servicio_medico.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
