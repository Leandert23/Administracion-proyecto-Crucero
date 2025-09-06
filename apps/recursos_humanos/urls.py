from django.urls import path
from . import views

app_name = 'recursos_humanos'

urlpatterns = [
    path('', views.recursos_humanos_view, name='recursos_humanos'),
]
