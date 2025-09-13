from django.urls import path
from .views import index

app_name = "recursos_humanos"

urlpatterns = [
    path('', index, name='dashboard'),
]
